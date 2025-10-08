"""all code concerning the status of lemmings jobs"""

import os
import subprocess
import numpy as np
from prettytable import PrettyTable
from lemmings.base.database import Database
from lemmings.lemmingslogging import lemlog

PROGRESS_VAR = "completion"
PROGRESS_NAME = "progress_name"


def _handle_loop(loop, loop_num, keys):
    """Function rendering the lemmings status in case of a first loop
    of a chain of a first loop after a --restart
    """
    value_list = []

    for key in keys:
        if key in loop:
            if key in ["submit_path"]:
                tmp_path = loop[key].split("/")[0]
                if tmp_path == ".":
                    tmp_path = "./"
                value_list.append(tmp_path)
            elif key in ["job_id", "pjob_id"]:
                value_list.append(loop[key])
            elif key is PROGRESS_VAR:
                value_list.append(loop[key])
            else:
                value_list.append("Submitted")
        elif key in ["Job Status"]:
            value_list.append(check_job_state(loop))
        else:
            value_list.append("Undefined")
    value_list = [str(loop_num)] + value_list

    return value_list


def check_job_state(loop: dict, job_type: str = "job_id") -> str:
    """Run command to retrieve the state of a slurm job using its ID from

    Args:
        loop (dict): dict containing the database loop infos

    Returns:
        str: state of the job
    """
    job_id = loop.get(job_type)
    job_state = "Not Submitted"
    command = f"sacct -j {job_id} --format=JobID,JobName,State"
    states = ["RUNNING", "PENDING", "COMPLETED"]

    if job_id:
        try:
            # Run the shell command and capture its output
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Check if the target string is present in the output
            job_state = [state for state in states if state in result.stdout]
            if len(job_state) == 1:
                # print(f"Job {job_id} is in state '{job_state[0]}'")
                job_state = job_state[0]
            else:
                # print(f"Job {job_id} has no definitive state")
                job_state = "Undefined"

        except subprocess.CalledProcessError as e:
            # Handle errors if the command fails
            # print(f"Error: {e}")
            # print("Command Output (stderr):")
            # print(e.stderr)
            job_state = "No slurm !"

    return job_state


def get_status(dataBase):
    status_string = []
    try:
        db_content = dataBase._database
    except FileNotFoundError as excep:
        status_string.append("LemmingsError: " + excep)
        return status_string

    chain_name = dataBase.latest_chain_name
    if chain_name is None:
        raise ValueError(
            "No chain found. Check database.json file in your current directory ..."
        )
    status_string.append("Status for chain %s " % (chain_name))
    try:
        progress_title = dataBase.get_first_loop_val(PROGRESS_NAME)
    except KeyError:
        progress_title = "Progress"

    keys = [
        "submit_path",
        "job_id",
        "Job Status",
        PROGRESS_VAR,
    ]
    names_keys = [
        "Run Path",
        "Job ID",
        "Job Status",
        progress_title,
    ]

    table = PrettyTable()
    table.field_names = ["Loop"] + names_keys
    for ii, loop in enumerate(db_content[chain_name]):
        value_list = _handle_loop(loop, ii, keys)
        table.add_row(value_list)

    status_string.append(table)
    end_status = db_content[chain_name][-1].get("end_status")
    if end_status:
        status_string.append(end_status)

    return status_string


def get_farming_status():
    pass


def parallel_status(with_progress, par_dict):
    status_string = []
    table = PrettyTable()

    symbol = {
        "start": "S",
        "wait": "W",
        "end": "F",
        "error": "E",
        "kill": "K",
    }
    if not with_progress:
        table.field_names = ["Workflow number", "Status"]
        table.add_rows([(key, symbol.get(val, "?")) for key, val in par_dict.items()])
    else:
        # case with progress variable
        table.field_names = ["Workflow number", "Status", "Progress"]
        _string = [(key, symbol.get(val, "?"), "NA") for key, val in par_dict.items()]
        main_dir = os.getcwd()
        for ii, keys in enumerate(_string):
            if keys[1] in ["W"]:
                break
            os.chdir(keys[0])
            tmp_dataBase = Database()
            try:
                tmp_progress = tmp_dataBase.get_current_loop_val(PROGRESS_VAR)
            except KeyError:
                # case when progress var not yet added in current loop
                # we will then instead use the previous loop
                if tmp_dataBase.get_current_loop_val("loop_count") == 1:
                    break
                tmp_progress = tmp_dataBase.get_previous_loop_val(PROGRESS_VAR)

            if isinstance(tmp_progress, float):
                tmp_progress = np.round(tmp_progress, 5)
            _string[ii] = (_string[ii][0], _string[ii][1], tmp_progress)
            os.chdir(main_dir)
        table.add_rows(_string)
    status_string.append("S: Submitted, F: Finished, W: Wait, E: Error, K: Killed")
    status_string.append(table)

    return status_string


def customise_end_message(dataBase, loop_num, end_msg):
    """Function handling the end message output shown in 'lemmings status'

    Input:
        :database: database class object
        :loop_num: int, number of the loop calling this functionality
    Output:
        :end_message: str, ouput to be provided
    """

    if not isinstance(loop_num, int):
        loop_num = int(loop_num)

    end_message = "\n  Latest loop = %1d \n" % loop_num

    try:
        # Starts counting at 1!!
        end_message += [
            "  Latest job and pjob IDs = "
            + dataBase.get_loop_val("job_id", (loop_num + 1))
            + " and "
            + dataBase.get_loop_val("pjob_id", (loop_num + 1))
        ][0]
    except KeyError:
        pass

    end_message += "\n  Final status: " + end_msg
    end_message = "# " + "\n # ".join(end_message.splitlines())
    return end_message
