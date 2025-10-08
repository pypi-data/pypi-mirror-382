"""Farming functionalities for the lemmings object"""

import os
import shutil
import json
import subprocess
import numpy as np
from lemmings.lemmingslogging import lemlog
from datetime import datetime as dt

from nob import Nob

from lemmings.chain.lemmingjob_base import LemmingJobBase
from lemmings.chain.lemmingsstop import switch_to_exit, LemmingsStop
from lemmings.chain.lemmingscmd import lemmings_run_cmd

DATETIME_FORMAT = "%m/%d/%y %H:%M:%S"


def run_farming(lemmings_job: LemmingJobBase):
    """Method that controls the generation of multiple workflows for parallel mode
    and submits them according to user settings

    Split in smaller functions
    1) check if all is well activated in workflow.yml
    -> _check_correct_parallel_settings()
    2) perform the workflow copies
    -> _generate_workflow_replicates
    3) launch workflows
    3.1) check if max parallel workflow specied
    3.2) launch workflows
    3.3) update the database
    -> _launch_workflows_parallel
    4) raise LemmingsStop as we did what we had to do at this point
    """

    lemmings_job.database.add_farming_list()

    num_workflows = len(lemmings_job.user.farming["parameter_array"])
    max_par_wf = lemmings_job.user.farming["max_parallel_workflows"]

    # Generation of different workflow folder replicates
    workflows_list = _generate_workflow_replicates(
        num_workflows,
        lemmings_job,
    )

    _launch_workflows_parallel(workflows_list, lemmings_job, max_par_wf)

    stop = (
        f"Replicate workflows launched according to max parallel chains {max_par_wf} "
    )
    switch_to_exit(lemmings_job, stop, lemmings_stop=True)
    return


def continue_farming(lemmings_job: LemmingJobBase):
    """Function that monitors the number of parallel jobs currently run

    Idea is to update the job status in the main database.json.
    Status should be either: start, hold, end
    So:
    1) I must be able to access the main database.json
    2) I must be able to submit new lemming jobs
    3) I must update database status
    """
    lemlog(f"Continue farming ...")
    workflow_path = lemmings_job.path_yml

    wf_dir = os.getcwd()  # need ton know where I am to update the main database
    wf_current = wf_dir.split("/")[-1]

    # absolute path to main directory --> considers a fixed structure!
    base_run_path = "/" + os.path.join(*workflow_path.split("/")[0:-1])
    os.chdir(base_run_path)

    # Do stuff with our database
    # db_info = Nob(self.database._database)
    # Modify status of current workflow: from start to end
    lemmings_job.database.update_farming_list(wf_current, "end")
    db_info = Nob(lemmings_job.database._database)  # required for full status

    # Find next lemmings chain to launch through 'wait' keyword
    status_list = []
    db_subtree = db_info[lemmings_job.database.latest_chain_name]
    for key in db_subtree.parallel_runs[:][0].keys():
        if db_subtree[key][:] == "wait":
            lemmings_job.database.update_farming_list(key, "start")
            lemlog(
                f"         Launch workflow {key} / time : {dt.now().strftime(DATETIME_FORMAT)}"
            )
            os.chdir(key)
            # Launch the new workflow
            subprocess.call(lemmings_run_cmd(lemmings_job), shell=True)
            os.chdir(base_run_path)  # back to main directory
            break
        status_list.append(db_subtree[key][:])
        lemmings_job.database.update_current_loop(
            "end_message", "All lemmings chains have been submitted"
        )
    if len(np.unique(status_list)) == 1:
        lemmings_job.database.update_current_loop(
            "end_message", "All lemmings chains have ended"
        )

    os.chdir(wf_dir)


def _generate_workflow_replicates(workflow_nbs, lemmings_job: LemmingJobBase):
    """Function performing the actual replication of the current work folder structure
    for separate lemmings calls

    Input:
        :workflow_nbs: int, number of copies to create
        :lemmings_job: lemmings_job object
        :database:    Database object

    Output:
        :workflows_list: list of type string containing workflow folders generated
    """

    param_arr = lemmings_job.user.farming["parameter_array"]
    workflows_list = []

    dir_info = os.listdir()
    for wf_index in np.arange(workflow_nbs):
        tmp_workflow = "WF_%03d" % wf_index
        tmp_workflow += "_" + lemmings_job.job_prefix

        try:
            tmp_workflow += (
                "_"
                + lemmings_job.user.farming["parameter_array"][wf_index][
                    "add_farming_suffix"
                ]
            )
        except KeyError:
            pass

        try:  # TODO: need to handle case when workflows already exist and not overwrite
            #  -> what should we do then?
            if (
                os.path.isdir(tmp_workflow)
                and lemmings_job.user.farming["overwrite_dirs"]
            ):
                shutil.rmtree(tmp_workflow)
            os.mkdir(tmp_workflow)
        except KeyError:
            raise LemmingsStop(
                "Overwrite directory option not specified, please do so through\n"
                + "farming:\n"
                + "  overwrite_dirs: True or False\n"
                + "\n"
                + "in the workflow.yml"
            )
        except FileExistsError as excep:
            switch_to_exit(lemmings_job, excep, lemmings_stop=False)
            return
        with open(tmp_workflow + "/_farming_params.json", "w") as fout:
            json.dump(param_arr[wf_index], fout)

        for item in dir_info:
            if os.path.isfile(item):
                # we need to ensure we do not copy the {workflow}.yml file
                # as the parallel mode is activated in it.
                # we will keep it centralised instead in the main folder
                if item in ["database.json", "_farming_params.json"]:
                    pass
                elif item.endswith(".log"):
                    pass
                else:
                    # Refactor note  : symlinks would also help if files are big.
                    shutil.copy(item, tmp_workflow)
            else:
                if item not in [lemmings_job.database.latest_chain_name]:
                    if item in lemmings_job.database.get_chain_names():
                        pass
                    else:
                        # Refactor note  : moving dir to a simpler function would be nicer
                        # Use symlinks would also help.
                        lemmings_job.pathtools.copy_dir(item, tmp_workflow + "/")
        workflows_list.append(tmp_workflow)

    return workflows_list


def _launch_workflows_parallel(
    workflows_list: list, lemmings_job: LemmingJobBase, max_par_wf: int
):
    """Function performing the actual launch of the lemmings chains in farming mode

    Input:
        :workflow_list: list of type string containing names of workflows to consider
        :lemmings_job: lemmings_job object
        :database:    Database object

    Output:
        :max_par_wf: None or int with number of max nb of simultaneous workflows to launch
    """
    root_path = os.getcwd()
    for wf_index, workflow in enumerate(workflows_list):
        lemmings_job.database.update_farming_list(workflow, "wait")
        if wf_index + 1 <= max_par_wf:
            lemmings_job.database.update_farming_list(workflow, "preparing")
        else:
            lemmings_job.database.update_farming_list(workflow, "wait")

    for wf_index, workflow in enumerate(workflows_list):
        if wf_index + 1 <= max_par_wf:
            os.chdir(workflow)
            subprocess.call(lemmings_run_cmd(lemmings_job), shell=True)
            lemlog(
                f"         Launch workflow {workflow} / time : {dt.now().strftime(DATETIME_FORMAT)}"
            )
            os.chdir(root_path)
            lemmings_job.database.update_farming_list(workflow, "start")

    return
