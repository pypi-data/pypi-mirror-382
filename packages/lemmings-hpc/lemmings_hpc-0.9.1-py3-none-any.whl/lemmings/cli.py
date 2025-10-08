"""
CLI for Lemmings
"""

import os
import click
import traceback
from lemmings.cli_main import add_version


@click.group()
@add_version
def main_cli():
    """
    *Lemmings workflow CLI*
    """
    pass


@click.command()
@click.argument("workflow", type=str, nargs=1)
@click.option(
    "--status",
    "-s",
    type=str,
    default="start",
    help="Your job status, Expert users only",
)
@click.option(
    "--inputfile",
    required=True,
    type=str,
    default=None,
    help="Path to .yml file associated with workflow",
)
@click.option(
    "--job-prefix",
    required=False,
    type=str,
    default="lemjob",
    help="Job prefix to be used in chain name.",
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
    "-v",
    "--verbose",
    is_flag=True,
    show_default=True,
    default=False,
    help="Verbose mode",
)
@click.option(
    "-l",
    "--log_mode",
    required=False,
    type=str,
    default="loguru",
    help="Specify the logging module to use",
)
def run(workflow, status, inputfile, job_prefix, machine_file, verbose, log_mode):
    """
    This is the command to launch your workflow with Lemmings.
    ' lemmings run {workflow_name} '
    """

    from lemmings.lemmingslogging import startlog, lemlog
    from lemmings.cli_main import main_run, disclaimer
    from lemmings.chain.lemmingsstop import LemmingsStop

    startlog("run", verbose, log_mode=log_mode)

    # Reverse compatibilty
    if not workflow.endswith(".py"):
        workflow = workflow + ".py"
        lemlog(
            "Deprecation : Specify your workflow with the .py extension from now on..."
        )
        lemlog(f"Using worflow :{ workflow}")

    try:
        lemmings = main_run(
            workflow, inputfile, machine_file, job_prefix, status, log_mode
        )
        if status == "start":
            lemlog(disclaimer())
        lemmings.run()
    except LemmingsStop as exp:
        lemlog("cli.run:" + str(exp))
        lemlog(traceback.format_exc())
    except Exception as exp:
        lemlog("cli.run:" + str(exp))
        lemlog(traceback.format_exc())


main_cli.add_command(run)


@click.command()
@click.option(
    "--machine-file",
    required=False,
    type=str,
    default=None,
    help="Allows user specification of  path to {machine}.yml file. "
    + "This will totally override your machine file  $LEMMINGS_MACHINE",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    show_default=True,
    default=False,
    help="Verbose mode",
)
@click.option(
    "-l",
    "--log_mode",
    required=False,
    type=str,
    default="loguru",
    help="Specify the logging module to use",
)
def kill(machine_file, verbose, log_mode):
    """
    Kill the current job and pjob of lemmings
    """
    from lemmings.lemmingslogging import startlog, lemlog
    from lemmings.base.database import Database
    from lemmings.cli_main import kill_chain

    startlog("kill", verbose, log_mode=log_mode)

    if not os.path.isfile("database.json"):
        lemlog("ERROR: Can't use this command")
        lemlog("       no database.json file in the current directory.")
        return
    database = Database()
    # First check that we are in the correct directory to launch this command
    try:
        (par_dict,) = database.get_current_loop_val("parallel_runs")
        lemlog("ERROR: this command can't be called from this directory")
        lemlog("       Try 'lemmings-farming kill' instead")
        return
    except KeyError:
        # we are indeed in a normal lemmings chain
        pass

    kill_chain(machine_file)


main_cli.add_command(kill)


@click.command()
@click.option(
    "--database",
    "-db",
    required=False,
    type=str,
    default=None,
    help="Path to database.json file to read",
)
@click.option(
    "--progress",
    "-p",
    is_flag=True,
    help="If activated, the latest progress will also be shown.",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    show_default=True,
    default=False,
    help="Verbose mode",
)
@click.option(
    "-l",
    "--log_mode",
    required=False,
    type=str,
    default="loguru",
    help="Specify the logging module to use",
)
def status(database, progress, verbose, log_mode):
    """
    Show the status during runtime
    """
    from lemmings.lemmingslogging import startlog, lemlog
    from lemmings.base.database import Database
    from lemmings.cli_status import get_status

    startlog("status", verbose, log_mode=log_mode)

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
        lemlog(f"Error: {excep}", level="warning")
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
        lemlog(
            "ERROR: this command can't be called from this directory", level="warning"
        )
        lemlog("       Try 'lemmings-farming status' instead", level="warning")
        return
    except KeyError:
        pass

    try:
        # TODO: split get_current_status in two function calls -> farming and normal
        _ = [lemlog(string) for string in get_status(db)]
    except ValueError as excep:
        lemlog(f"ValueError:{excep}", level="warning")
        return
    except TypeError as excep:
        lemlog("Database currently not accessible, try again shortly", level="warning")
        lemlog("Make sure it is not corrupted", level="warning")
        lemlog(f"TypeError:{excep}", level="warning")
        return  # might be that database chain not found instead!!!
    except KeyError as excep:
        lemlog("Database currently not accessible, try again shortly", level="warning")
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
    "-v",
    "--verbose",
    is_flag=True,
    show_default=True,
    default=False,
    help="Verbose mode",
)
@click.option(
    "-l",
    "--log_mode",
    required=False,
    type=str,
    default="loguru",
    help="Specify the logging module to use",
)
def clean(database, verbose, log_mode):
    """
    Clean lemmings run files in current folder
    """
    from lemmings.lemmingslogging import startlog, lemlog
    from lemmings.cli_main import (
        remove_files_folders,
        gather_default_files_folders_to_clean,
    )

    startlog("clean", verbose, log_mode=log_mode)

    # need to add option to have other database.json name to look at
    # cfr. lemmings status of FEATURE/parallel branch

    try:
        lst_remove = gather_default_files_folders_to_clean(database)
    except FileNotFoundError as excep:
        lemlog(f"Error: {excep}", level="error")
        return
    except KeyError as excep:
        lemlog(excep, level="error")
        if "use lemmings-farming clean" in str(excep):
            return
    for path in lst_remove:
        remove_files_folders(path)


main_cli.add_command(clean)


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
    "-v",
    "--verbose",
    is_flag=True,
    show_default=True,
    default=False,
    help="Verbose mode",
)
def restart(database, verbose):
    """
    Show the status during runtime
    """
    from lemmings.lemmingslogging import startlog
    from lemmings.base.database import Database
    from lemmings.cli_restart import restart_post_job

    startlog("restart", verbose)

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
        logger.warning("Error: ", excep)
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
        logger.warning("ERROR: this command can't be called from this directory")
        logger.warning("       Try 'lemmings-farming status' instead")
        return
    except KeyError:
        pass

    try:
        # TODO: split get_current_status in two function calls -> farming and normal
        # _ = [logger.info(string) for string in get_status(db)]
        restart_post_job(db)
    except ValueError as excep:
        logger.warning("ValueError:", excep)
        return
    except TypeError as excep:
        logger.warning("Database currently not accessible, try again shortly")
        logger.warning("Make sure it is not corrupted")
        return  # might be that database chain not found instead!!!
    except KeyError as excep:
        logger.warning("Database currently not accessible, try again shortly")
        return


main_cli.add_command(restart)
