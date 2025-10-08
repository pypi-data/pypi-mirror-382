"""Module helper for the CLI of lemmings"""

import os
import sys
import shutil
import subprocess as sbp
from lemmings.lemmingslogging import lemlog

from pathlib import Path
import importlib.util
import random
import string


import logging


from lemmings import __version__ as lemver
from lemmings import __name__ as lemname

from lemmings.base.database import Database
from lemmings.base.machine import build_machine, get_machine_cmd
from lemmings.base.user import get_user_params
from lemmings.chain.chain import Lemmings
from lemmings.lemmingslogging import lemlog


def main_run(workflow, inputfile, machine_file, job_prefix, status, log_mode):
    """Unique creation of a lemming obj for both run and run_farming  CLIs

    Args:
        workflow (str): basename of the workflow
        inputfile (str): path to workflow input file
        machine_file (str): path to machine file
        job_prefix (str): prefix to add to the job
        status (str): job status among : start, spawn_job, post_job, exit

    Returns:
        lemmings_instance (obj) : a Lemmings object
    """

    wf_py_path = os.path.abspath(workflow)
    wf_yml_path = os.path.abspath(inputfile)
    user_params = get_user_params(wf_yml_path)

    database = Database()
    if status == "start":
        chain_name = custom_name()
    else:
        chain_name = database.latest_chain_name.split("_")[-1]

    job_name = job_prefix + "_" + chain_name
    # base_dir = Path(wf_yml_path).parent
    lemlog(Path.cwd() / Path(job_name + ".log"))
    try:
        os.mkdir(job_name)
    except FileExistsError:
        pass

    if status == "start":
        database.initialise_new_chain(job_name)
    loop_count = database.count

    splitter = "\n" + 30 * "#" + "\n"
    lemlog(f"{splitter}Starting Lemmings {lemver}...{splitter}")
    lemlog(f"    Job name     :{job_name}")
    lemlog(f"    Loop         :{loop_count}")
    lemlog(f"    Status       :{status}")
    lemlog(f"    Worflow path :{os.path.abspath(wf_py_path)}")
    lemlog(f"    Imput path   :{os.path.abspath(wf_yml_path)}")
    lemlog(f"    Machine path :{os.path.abspath(machine_file)}")

    machine_file = get_machine_file(machine_file)
    machine = build_machine(
        user_params,
        job_name,
        machine_file,
    )

    spec = importlib.util.spec_from_file_location("module.name", wf_py_path)
    if spec is None:
        msg = f"Could not find workflow from path {wf_py_path}"
        lemlog(msg, level="critical")
        raise RuntimeError(msg)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    lemming_job = module.LemmingJob(
        workflow,
        machine,
        database,
        wf_yml_path,
        job_prefix,
        user_params,
        loop_count,
        status=status,
        log_mode=log_mode,
    )

    lemlog(f"    Farming mode :{str(lemming_job.is_farming)}")

    lemmings_instance = Lemmings(lemming_job)
    return lemmings_instance


def add_version(f):
    """
    Add the version of the tool to the help heading.
    :param f: function to decorate
    :return: decorated function
    """
    doc = f.__doc__
    f.__doc__ = "Package " + lemname + " v" + lemver + "\n\n" + doc
    return f


def get_machine_file(machine_file):
    env_var = dict(os.environ)
    if machine_file is None:
        try:
            machine_file = env_var["LEMMINGS_MACHINE"]
        except KeyError:
            raise RuntimeError(
                "No machine file provided, neither in $LEMMINGS_MACHINE, nor trough --machine-file. aborting..."
            )

    if not os.path.isfile(machine_file):
        raise RuntimeError(f"Machine file {machine_file} does not exist, Aborting...")

    return machine_file


# def get_workflow(workflow, inputfile):
#     # get path of the WorkFlow desired
#     if workflow.lower().endswith((".yml", ".py")):
#         raise ValueError(
#             "A workflow name can't contain an extension like '.yml', "
#             + "please enter a valid workflow name. "
#         )

#     wf_path = _get_workflow_py(workflow)
#     if inputfile is None:
#         wf_yaml = _get_workflow_yml(workflow)
#     else:
#         wf_yaml = inputfile
#     return wf_path, wf_yaml


# def _get_workflow_py(workflow):
#     """
#     *Get the path of the {workflow}.py file.*

#     :param workflow: workflow name
#     :type workflow: str
#     """
#     path_tool = PathTools()
#     if Path("./" + workflow + ".py").is_file():
#         wf_py_path = path_tool.abspath(workflow + ".py")
#     else:
#         msg = f"Your specified workflow '{ workflow}' doesn't exist in  current directory\n"
#         raise EnvironmentError(msg)
#     return wf_py_path


# def _get_workflow_yml(workflow, user_yaml=False):
#     """
#     *Get the path of the {workflow}.yml file.*

#     :param workflow: workflow name
#     :type workflow: str
#     """
#     path_tool = PathTools()
#     if user_yaml:
#         if Path(workflow + ".yml").is_file():
#             wf_yml_path = path_tool.abspath(workflow + ".yml")
#         else:
#             raise FileNotFoundError(
#                 "Oops!  Couldn't find the %s.yml file relative to your current directory. Please generate it."
#                 % workflow
#             )
#     else:
#         if Path("./" + workflow + ".yml").is_file():
#             wf_yml_path = path_tool.abspath(workflow + ".yml")
#         else:
#             raise FileNotFoundError(
#                 "Oops!  Couldn't find the %s.yml file in your current directory. Please generate it."
#                 % workflow
#             )

#     return wf_yml_path


def kill_chain(machine_file):
    """Function running subprocess to kill an active job and post job

    Input:
        :database: Database object
        :machine_dict: dict, containing commands to enable killing of jobs

    Output:
        :None
    """
    database = Database()
    machine_file = get_machine_file(machine_file)
    cmd = get_machine_cmd(machine_file)
    try:
        job_id = database.get_loop_val("job_id", 0)  # latest loop
        pjob_id = database.get_loop_val("pjob_id", 0)
    except KeyError:
        lemlog(
            "No job and / or post job to kill in current database loop", level="warning"
        )
        return
    lemlog("Killing the current job and post-job...", level="warning")

    try:
        cmd.cancel
    except KeyError:
        lemlog("No 'cancel' command specified in the machine file", level="warning")
        return
    sbp.run([f"{cmd.cancel}", f"{job_id}"], stdout=sbp.PIPE)
    lemlog("   job  " + str(job_id) + " was killed", level="warning")
    sbp.run([f"{cmd.cancel}", f"{pjob_id}"], stdout=sbp.PIPE)
    lemlog("   pjob " + str(pjob_id) + " was killed", level="warning")


def remove_files_folders(my_path):
    """
    Clean removal of file/folders based on the database.json file info
    """

    if os.path.exists(my_path):
        if os.path.isfile(my_path):
            lemlog("> Remove file: %s" % my_path)
            os.remove(my_path)
            return

        if os.path.isdir(my_path):
            lemlog("> Remove folder: %s" % my_path)
            shutil.rmtree(my_path)
            return


def gather_default_files_folders_to_clean(database, farming=False):
    """Standard lemmings files to remove by the clean function

    Input:
        :database: Database object of lemmings

    Output:
        :lst_remove: list of string, contains files and folders to remove
    """

    lst_remove = [
        "__pycache__",
        "batch_job",
        "batch_pjob",
        "database.json",
    ]

    if database is not None:
        if not os.path.isfile(database):
            raise FileNotFoundError(database + " does not exist")
        lst_remove = [
            string.replace("database.json", database) for string in lst_remove
        ]
    else:
        if not os.path.isfile("database.json"):
            raise FileNotFoundError("database.json does not exist")

    if database is not None:
        db = Database(database)
    else:
        ## this init will generate a database.json file,
        ## so if not present we should check before
        db = Database()

    # First check that we are in the correct directory to launch this command
    try:
        # AD Crete test "is_farming database"
        (par_dict,) = db.get_current_loop_val("parallel_runs")
        if not farming:
            lemlog("ERROR: you're in farming main directory", level="warning")
            lemlog("       Use 'lemmings-farming clean' instead", level="warning")
            raise KeyError("use lemmings-farming clean")
    except KeyError as excep:
        if "use lemmings-farming clean" in str(excep):
            raise KeyError("use lemmings-farming clean")
        if farming:
            lemlog("ERROR: you're not in farming main directory", level="warning")
            lemlog("       Use 'lemmings clean' instead", level="warning")
            raise KeyError("use lemmings clean")

    try:  # perhaps redundant as  db.get_current_loop_val will already
        # try access latest chain name
        db.latest_chain_name
    except UnboundLocalError as excep:
        lemlog("'lemmings clean' aborted", level="warning")
        return
    except TypeError as excep:
        lemlog("'lemmings clean' aborted", level="warning")
        return 2

    # Todo: add later option to remove only latest chain name
    try:
        chain_names = db.get_chain_names()
    except TypeError as excep:
        lemlog(f"ValueError: {excep}", level="warning")
        lemlog(
            "Your file database.json is corrupted, I can't automatically clean this folder\n",
            level="warning",
        )
        return

    lst_remove.extend(chain_names)
    if farming:
        return (lst_remove, db)
    return lst_remove


# ERROR_CODE = {
#     "OK": 0,
#     "WRONGCLI": 1,
#     "ENVERROR": 2,
#     "FILENOTFOUND": 2,
#     "OTHER": 99
# }


def _logging_lemmings(f_log):
    """
    TO BE DEPRECATED IN FAVOR OF LOGURU

    General logging function of lemmings

    All logs are dumped in their Curredn Working directories.
    Meaning the Farmings logs are scattered over several workflow folders.
    But that's the cold truth man...

    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s - %(message)s",
        # format="%(message)s",
        handlers=[
            logging.FileHandler(f_log, mode="a"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def disclaimer():
    try:
        user = os.environ["USER"]
    except KeyError:
        user = "Unknown (gitlab CI probably)"
    return f"""
Disclaimer: this automated job has been submitted by user {user}
under his/her scrutiny. In case of a wasteful usage of this computer ressources,
the aforementionned user will be found, and forced to take responsibility...

- use `lemmings(-farming) status` to follow your jobs
- use `lemmings(-farming) cancel` to cancel it 
- use `find . -name *.log` to see the log files created
"""


def custom_name():
    """
    Random Name generator --> Cons + Vowels + Cons + Vowels + 2*Int
    """
    vowels = list("AEIOU")
    consonants = list(set(string.ascii_uppercase) - set(vowels))

    # Try to avoid offensive namings. Here in french
    forbid = [
        "",
        "PUTE",
        "PEDE",
        "BITE",
        "CACA",
        "ZIZI",
        "CUCU",
        "PIPI",
        "CONE",
        "CULE",
        "PENE",
        "SODO",
        "SUCE",
        "SUCA",
        "KUKU",
        "CUNI",
    ]
    name = ""
    while name in forbid:
        name = ""
        name += random.choice(consonants)
        name += random.choice(vowels)
        name += random.choice(consonants)
        name += random.choice(vowels)

    name += str(random.randrange(1, 10))
    name += str(random.randrange(1, 10))
    return name
