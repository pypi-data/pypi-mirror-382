"""
CLI for Lemmings
"""

import os
import click
import traceback
from lemmings.lemmingslogging import lemlog
from lemmings.cli_main import add_version


@click.group()
@add_version
def main_cli():
    """
    *Lemmings workflow CLI  -FARMING MODE-*
    """
    pass


@click.command()
@click.argument("workflow", type=str, nargs=1)
@click.option(
    "--job-prefix",
    required=False,
    type=str,
    default="lemjob",
    help="Job prefix to be used in chain name",
)
@click.option(
    "--inputfile",
    required=True,
    type=str,
    default=None,
    help="Path to .yml file associated with workflow",
)
@click.option(
    "--machine-file",
    required=False,
    type=str,
    default=None,
    help="Allows user specification of  path to {machine}.yml file. "
    + "This will totally override your machine file  $LEMMINGS_MACHINE",
)
@click.option(
    "-l",
    "--log_mode",
    required=False,
    type=str,
    default="loguru",
    help="Specify the logging module to use",
)
def run(workflow, inputfile, machine_file, job_prefix, log_mode):
    """Launch farming mode of lemmings
    'lemmings-farming run {workflow_name}'
    """
    import logging
    from lemmings.cli_main import main_run, disclaimer
    from lemmings.chain.farming import run_farming
    from lemmings.chain.lemmingsstop import LemmingsStop

    # Reverse compatibilty
    if not workflow.endswith(".py"):
        workflow = workflow + ".py"
        logging.warning(
            "Deprecation : Specify your workflow with the .py extension from now on..."
        )
        logging.info(f"Using worflow :{ workflow}")

    try:
        lemmings = main_run(
            workflow, inputfile, machine_file, job_prefix, "start", log_mode
        )
        print(disclaimer())
        run_farming(lemmings.lemmings_job)
    except LemmingsStop as exp:
        logging.info(exp)
    except Exception as exp:
        msg = traceback.format_exc() + "\n" + str(exp)
        logging.warning(msg)


main_cli.add_command(run)


@click.command()
def kill():
    """
    Kills all active Workflows.
    """

    import yaml
    from lemmings.base.database import Database
    from lemmings.cli_main import kill_chain

    if not os.path.isfile("database.json"):
        print("ERROR: Can't use this command")
        print("       no database.json file in the current directory.")
        return

    database = Database()

    # First check that we are in the correct directory to launch this command
    try:
        (par_dict,) = database.get_current_loop_val("parallel_runs")
    except KeyError:
        print("ERROR: this command can't be called from this directory")
        print("       Try 'lemmings kill' instead")
        return

    env_var = dict(os.environ)
    try:  # need to know how to kill jobs
        machine_path = env_var["LEMMINGS_MACHINE"]
    except KeyError:
        print("No LEMMINGS_MACHINE environment variable specified")
        return

    with open(machine_path) as fin:
        machine_dict = yaml.load(fin, Loader=yaml.SafeLoader)

    # check first if there is any chain to kill
    workflows_to_kill = [key for key, val in par_dict.items() if val == "start"]
    if not workflows_to_kill:
        print("No workflows to kill")
        return

    # we have to do two things:
    #   1) update status from jobs that are waiting to killed "K"
    #   2) kill the jobs that are running

    # Change status of jobs that haven't been launched yet to 'kill'
    par_dict = dict(
        [
            (key, val) if val != "wait" else (key, "kill")
            for key, val in par_dict.items()
        ]
    )
    database.update_current_loop("parallel_runs", [par_dict])

    main_dir = os.getcwd()
    for wf_dir in workflows_to_kill:
        os.chdir(wf_dir)
        kill_chain(database, machine_dict)
        os.chdir(main_dir)

    # now we'll update the database as we successfully killed the active chains
    par_dict = dict(
        [
            (key, val) if val != "start" else (key, "kill")
            for key, val in par_dict.items()
        ]
    )
    database.update_current_loop("parallel_runs", [par_dict])


main_cli.add_command(kill)


@click.command()
@click.option(
    "--database",
    "-db",
    required=False,
    type=str,
    default=None,
    help="Path to database  YAML file (or directory) to read",
)
@click.option(
    "--progress",
    "-p",
    is_flag=True,
    help="If activated, the latest progress will also be shown.",
)
@click.option(
    "-l",
    "--log_mode",
    required=False,
    type=str,
    default="loguru",
    help="Specify the logging module to use",
)
def status(database, progress, log_mode):
    """
    Show the status during runtime
    """
    from lemmings.base.database import Database
    from lemmings.cli_status import get_current_status

    try:
        if database is not None:
            if os.path.isdir(database):  # try find database.json in directory
                database = os.path.join(database, "database.json")
            if not os.path.isfile(database):
                raise FileNotFoundError(database + " does not exist")
        else:
            if not os.path.isfile("database.json"):
                raise FileNotFoundError("database.json does not exist")
    except FileNotFoundError as excep:
        print("Error: ", excep)
        return

    if database is not None:
        db = Database(database)
    else:
        ## this init will generate a database.json file,
        ## so if not present we should check before
        db = Database()

    # First check that we are in the correct directory to launch this command
    try:
        (par_dict,) = db.get_current_loop_val("parallel_runs")
    except KeyError:
        print("ERROR: this command can't be called from this directory")
        print("       Try 'lemmings status' instead")
        return

    try:
        # TODO: split get_current_status in two function calls -> farming and normal
        _ = [print(string) for string in get_current_status(db, with_progress=progress)]
    except ValueError as excep:
        print("ValueError:", excep)
        return
    except TypeError as excep:
        print("Database currently not accessible, try again shortly")
        print("Make sure it is not corrupted")
        return  # might be that database chain not found instead!!!
    except KeyError as excep:
        print("Database currently not accessible, try again shortly")
        return


main_cli.add_command(status)


@click.command()
@click.option(
    "--database",
    "-db",
    required=False,
    type=str,
    default=None,
    help="Path to database  YAML file to read",
)
@click.option(
    "-l",
    "--log_mode",
    required=False,
    type=str,
    default="loguru",
    help="Specify the logging module to use",
)
def clean(database, log_mode):
    """
    Clean lemmings run files in current folder
    """
    from lemmings.cli_main import (
        remove_files_folders,
        gather_default_files_folders_to_clean,
    )

    try:
        lst_remove, db = gather_default_files_folders_to_clean(database, farming=True)
    except FileNotFoundError as excep:
        print("Error: ", excep)
        return
    except KeyError as excep:
        if "use lemmings clean" in str(excep):
            return
    try:
        (par_dict,) = db.get_current_loop_val("parallel_runs")
        lst_remove.extend(list(par_dict))
    except KeyError:
        pass

    for path in lst_remove:
        remove_files_folders(path)


main_cli.add_command(clean)
