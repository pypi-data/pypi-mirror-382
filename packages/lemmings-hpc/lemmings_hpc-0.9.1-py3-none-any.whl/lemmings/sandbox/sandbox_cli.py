"""
CLI for Lemmings
"""

import os
import click
from lemmings.lemmingslogging import lemlog
from lemmings.cli_main import add_version

from lemmings.sandbox.sandbox import (
    start_sandbox,
    submit_sandbox,
    qstat_sandbox,
    acct_sandbox,
    cancel_sandbox,
)


def _default_db_file():
    return os.environ["HOME"] + "/" + "sandbox_lem_ddb.json"


@click.group()
@add_version
def sandbox_cli():
    """
    CLI of lemming sandbox to emulate a job scheduler
    """
    pass


@click.command()
@click.option(
    "--db_file",
    type=str,
    default=_default_db_file(),
    help="Where to store sandbox file ddb",
)
@click.option(
    "--frequency",
    "-f",
    type=float,
    default=3,
    help="Demon frequency, in seconds",
)
@click.option(
    "--max_duration",
    "-d",
    type=int,
    default=9,
    help="Demon duration, in seconds",
)
@click.option(
    "--max_jobs",
    "-m",
    type=int,
    default=2,
    help="Maximum of simultaneous jobs",
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
def start(db_file, frequency, max_duration, max_jobs, verbose, log_mode):
    """start the sandbox"""
    from lemmings.lemmingslogging import startlog

    startlog("start", verbose, log_mode=log_mode)

    start_sandbox(
        db_file=db_file,
        frequency=frequency,
        max_duration=max_duration,
        max_parallel_jobs=max_jobs,
    )


sandbox_cli.add_command(start)


@click.command()
@click.option(
    "--db_file",
    type=str,
    default=_default_db_file(),
    help="Where to store sandbox file ddb",
)
@click.option(
    "--after",
    "-a",
    type=str,
    default="no",
    help="PID conditioning the start of this run",
)
@click.argument("batchfile", type=str, nargs=1)
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
def submit(batchfile, db_file, after, verbose, log_mode):
    """Job submission"""
    from lemmings.lemmingslogging import startlog

    startlog("submit", verbose, log_mode=log_mode)
    if after == "no":
        after = None
    pid = submit_sandbox(batchfile, db_file=db_file, after=after)
    lemlog(f"Job submitted with PID {pid}")


sandbox_cli.add_command(submit)


@click.command()
@click.option(
    "--db_file",
    type=str,
    default=_default_db_file(),
    help="Where to store sandbox file ddb",
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
def qstat(db_file, verbose, log_mode):
    """Show queuing state"""
    from lemmings.lemmingslogging import startlog

    startlog("qstat", verbose, log_mode=log_mode)
    qstat_sandbox(db_file)


sandbox_cli.add_command(qstat)


@click.command()
@click.option(
    "--db_file",
    type=str,
    default=_default_db_file(),
    help="Where to store sandbox file ddb",
)
@click.argument("pid", type=str, nargs=1)
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
def cancel(pid, db_file, verbose, log_mode):
    """Cancel job"""
    from lemmings.lemmingslogging import startlog

    startlog("cancel", verbose, log_mode=log_mode)
    out = cancel_sandbox(pid, db_file=db_file)
    lemlog(out)


sandbox_cli.add_command(cancel)


@click.command()
@click.option(
    "--db_file",
    type=str,
    default=_default_db_file(),
    help="Where to store sandbox file ddb",
)
@click.argument("pid", type=str, nargs=1)
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
def acct(pid, db_file, verbose, log_mode):
    """Show accounting in seconds elapsed"""
    from lemmings.lemmingslogging import startlog

    startlog("acct", verbose, log_mode=log_mode)
    lemlog(acct_sandbox(pid, db_file=db_file))


sandbox_cli.add_command(acct)
