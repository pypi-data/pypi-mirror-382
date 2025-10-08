import os
import numpy as np
from lemmings.cli_status import check_job_state
from loguru import logger
import subprocess as sbp
from lemmings.base.database import Database
from lemmings.base.machine import get_machine_cmd


# Check job status to avoid restart running job
def check_chain_status(db_content, chain_name):
    """Check if the last lemmings chain is still running by checking
    the slurm state of the job and post job using their ids

    Args:
        dataBase: current lemmings database

    Returns:
        string : chain status (Over, Running, undetermined)
    """

    last_loop = db_content[chain_name][-1]
    job_state = check_job_state(last_loop)
    pjob_state = check_job_state(last_loop, job_type="pjob_id")

    if "COMPLETED" not in (job_state, pjob_state):
        print(
            f"Some jobs of the chain {chain_name} are still pending or running, please kill them if you want to restart"
        )
        chain_state = "Running"
    else:
        print(f"Chain {chain_name} is finished")
        chain_state = "Over"
    return chain_state


# restart loop ?

# restart job


# restart pjob
def restart_post_job(dataBase, batch_name="./batch_pjob", submit_path="./"):
    chain_state = "undetermined"
    try:
        db_content = dataBase._database
    except FileNotFoundError as excep:
        raise FileNotFoundError("LemmingsError: " + excep)

    chain_name = dataBase.latest_chain_name
    if chain_name is None:
        raise ValueError(
            "No chain found. Check database.json file in your current directory ..."
        )

    chain_state = check_chain_status(db_content, chain_name)

    if chain_state != "Over":
        machine_file = db_content[chain_name][0].get("machine_path")
        machine_cmd = get_machine_cmd(machine_file)  # This is a named tuple !!!!

        if not os.path.isfile(os.path.join(submit_path, batch_name)):
            raise FileNotFoundError(
                "Batch file not found. Did you activate user_batch in expert_params?"
            )
        cmd_line = f"{machine_cmd.submit} {batch_name}"

        logger.info(f"job scheduler command: {cmd_line}")

        subp = sbp.run(
            cmd_line, stdout=sbp.PIPE, stderr=sbp.STDOUT, cwd=submit_path, shell=True
        )
        out = subp.stdout
        logger.info(f"===Job submission===")
        logger.info(f"Subproccess of {cmd_line}")
        logger.info(f"Performed in {submit_path}")
        logger.info(f"Standard output : {subp.stdout}")
        if subp.stderr == None:
            logger.info(f"Standard error : {subp.stderr} (No standard error)")
        else:
            logger.info(f"Standard error : {subp.stderr}")

        # assume stdout of sumission ends with pid behind a space "#### #### ### 03458"
        job_id = out.decode("utf-8")[:-1].split(" ")[-1]
        dataBase.update_current_loop("pjob_id", job_id)


# clean folders ( use the func in cli_main)

# clean database ?

"""
Si les job_id n'existe pas dans la nouvelle boucle ça veut dire que soit: 
- prior_to_new_iteration ou prepare run a planté si on est pas dans la 1ere loop
- prior to job ou prepare run a planté si on est dans la première boucle

Si le post job a planté c'est donc que les job_id sont inexistant dans la nouvelle loop

Si le check_on_end a reussi c'est:
- nouvelle boucle vierge ( date, safe_stop et submit_path='./')
- after_end_job > end_status dans la dernière boucle
"""
