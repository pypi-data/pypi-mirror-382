"""
The machine class that contains user parameter
+ machine cmd
+ machine template.
"""

import os
import sys
import yaml
import subprocess as sbp
from datetime import datetime
from collections import namedtuple
from lemmings.lemmingslogging import lemlog


def convert(dictionary):
    """
    *Convert a dict( ) to a NamedTuple( ).*
    """
    return namedtuple("NamedTupleJJH", dictionary.keys())(**dictionary)


def template_parser(exec_j, exec_pj, queue_template, job_name):
    """
    Machine template parser that remplace some keys by the user parameters
    """
    lines = queue_template["header"].split("\n")
    content = ""
    for line in lines:
        if "-LEMMING-JOB_NAME-" in line:
            line = line.replace("-LEMMING-JOB_NAME-", job_name)
        if "-LEMMING-POSTJOB_NAME-" in line:
            line = line.replace("-LEMMING-POSTJOB_NAME-", job_name + "_pj")
        if "-LEMMING-WALL-TIME-" in line:
            line = line.replace("-LEMMING-WALL-TIME-", str(queue_template["wall_time"]))
        if "-EXEC-" in line:
            line = line.replace("-EXEC-", exec_j)
        if "-EXEC_PJ-" in line:
            line = line.replace("-EXEC_PJ-", exec_pj)

        content += line + "\n"
    return content


def get_machine_cmd(path_machine):
    # pylint: disable=line-too-long
    """
    Get the machine template + cmd and generate a NamedTuple with it

    TODO: split in functions to get job, pjob, and commands
    """

    with open(path_machine) as fin:
        tmp = yaml.load(fin, Loader=yaml.SafeLoader)

    cmd = convert(tmp["commands"])

    return cmd


def get_machine_template(user_tuple, path_machine, job_name):
    # pylint: disable=line-too-long
    """
    Get the machine template + cmd and generate a NamedTuple with it

    TODO: split in functions to get job, pjob, and commands
    """

    with open(path_machine) as fin:
        tmp = yaml.load(fin, Loader=yaml.SafeLoader)

    queues_list = list(tmp["queues"].keys())
    if user_tuple.job_queue not in queues_list:
        msg = f"user queue '{user_tuple.job_queue}' not part of available queues: {queues_list}"
        raise ValueError(msg)
    if user_tuple.pjob_queue not in queues_list:
        msg = f"user queue '{user_tuple.pjob_queue}' not part of available queues: {queues_list}"
        raise ValueError(msg)

    job_queue_template = tmp["queues"][user_tuple.job_queue]
    pjob_queue_template = tmp["queues"][user_tuple.pjob_queue]

    # add the batch key, with substitutions

    job_queue_template["batch"] = template_parser(
        user_tuple.exec,
        user_tuple.exec_pj,
        job_queue_template,
        job_name,
    )

    pjob_queue_template["batch"] = template_parser(
        user_tuple.exec,
        user_tuple.exec_pj,
        pjob_queue_template,
        job_name,
    )

    job_template = convert(job_queue_template)
    pj_template = convert(pjob_queue_template)

    return job_template, pj_template


def build_machine(user_params, job_name, path_machine):
    cmd = get_machine_cmd(path_machine)

    job_template, pj_template = get_machine_template(
        user_params, path_machine, job_name
    )

    return Machine(
        cmd,
        job_template,
        pj_template,
        job_name,
        path_machine=path_machine,
    )


class Machine:
    """
    Machine class of Lemmings
    """

    def __init__(
        self,
        cmd,
        job_template,
        pj_template,
        job_name,
        path_machine,
    ):
        """
        :param path_yml: path to the user parameters file {workflow}.yml
        :type path_yml: str
        :param job_name: The name of the current Lemmings job
        :type job_name: str
        """

        self.job_name = job_name
        self.path_machine = path_machine
        self.cmd = cmd
        self.job_template = job_template
        self.pj_template = pj_template

    def submit(self, batch_name, dependency=None, submit_path=None):
        """
        Submit a job on a NFS machine.

        :param batch_name: Name of the batch
        :type batch_name: str
        :param dependency: Job ID of the job to be depend with.
        :type dependency: int
        """

        # check if batch exists
        if not os.path.isfile(os.path.join(submit_path, batch_name)):
            raise FileNotFoundError(
                "Batch file not found. Did you activate user_batch in expert_params?"
            )

        if dependency is None:
            cmd_line = f"{self.cmd.submit} {batch_name}"
        else:
            cmd_line = (
                f"{self.cmd.submit} {self.cmd.dependency}{dependency} {batch_name}"
            )
        lemlog(f"job scheduler command: {cmd_line}")

        subp = sbp.run(
            cmd_line, stdout=sbp.PIPE, stderr=sbp.STDOUT, cwd=submit_path, shell=True
        )
        out = subp.stdout
        lemlog(f"===Job submission===")
        lemlog(f"Subproccess of {cmd_line}")
        lemlog(f"Performed in {submit_path}")
        lemlog(f"Standard output : {subp.stdout}")
        if subp.stderr == None:
            lemlog(f"Standard error : {subp.stderr} (No standard error)")
        else:
            lemlog(f"Standard error : {subp.stderr}")

        # assume stdout of sumission ends with pid behind a space "#### #### ### 03458"
        job_id = out.decode("utf-8")[:-1].split(" ")[-1]
        return job_id

    def cancel(self, job_id):
        """
        Cancel a job on a NFS machine.
        """
        sbp.run([self.cmd.cancel, job_id], stdout=sbp.PIPE)

        lemlog(f"===Job cancellation===")
        lemlog(f"Standard output\n {subp.stdout}")

    def get_cpu_cost(self, job_id):
        """
        *Get the CPU cost of the previous Run.*

        :param job_id: Job ID of the previous run
        :type job_id: int
        """
        command_cpu = self.cmd.get_cpu_time.replace("-LEMMING-JOBID-", str(job_id))

        core_nb = 1  # Dangerous, consider something else,
        # and add a check in machine file before

        try:
            core_nb = self.job_template.core_nb
        except AttributeError:
            pass

        out = sbp.run(command_cpu, shell=True, stdout=sbp.PIPE)
        out = out.stdout
        out = out.decode("utf-8")[:-1].strip().split(" ")[0]
        out_day = 0
        try_sec = False
        if "-" in out:  # we have a format with day as D-H:M:S
            out_day = out.split("-")[0]
            out = out.split("-")[1:][0]
        try:
            out = datetime.strptime(out, "%H:%M:%S").time()
        except ValueError:
            try:
                out = datetime.strptime(out, "%M:%S").time()
            except ValueError:
                try_sec = True

        if not try_sec:
            out_sec = (
                float(out_day) * 24 * 3600
                + out.hour * 3600  # in seconds
                + out.minute * 60
                + out.second
            )
        else:
            try:
                out_sec = float(out)
            except ValueError as excep:
                lemlog(
                    f"Error, unknown scheduler CPU format. Job stopped due to infinite loop danger. {excep}",
                    level="error",
                )
                sys.exit()

        return (core_nb * out_sec) / 3600

        # NEED TO HANDLE:
        # 1-00:00:00
        # 00:30:00    hours min seconds
        # 7-01:00:00    day hours min seconds
        # 3:34    min and seconds
        # 3600     seconds
