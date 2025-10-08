""" The lemmings base class containing the methods which get inherited by LemmingJob
"""

import json
from lemmings.base.path_tool import PathTools
from lemmings.base.database import Database
from lemmings.base.machine import Machine
from lemmings.chain.lemmingsstop import switch_to_exit

from typing import NamedTuple


class LemmingJobBase:
    """Class containing the different lemmings methods
    and allowing access to database and other information
    """

    def __init__(
        self,
        workflow: str,
        machine: Machine,
        database: Database,
        path_yml: str,
        job_prefix: str,
        user: NamedTuple,
        loop_count: int,
        status="start",
        base_dir=None,
        log_mode="loguru",
    ):
        self.pathtools = PathTools(base_dir)
        self.database = database
        self.machine = machine
        self.workflow = workflow
        self.path_yml = path_yml
        self.job_prefix = job_prefix
        self.user = user  # Required to provide initial info to workflow for users
        self.log_mode = log_mode
        self.status = status  # start, spawn_job, post_job, exit
        self.loop_count = loop_count
        # add explicitly in first loop of chain the machine path if user defined
        # current loop important in case of restart

        try:
            self.is_farming = user.farming["active"]
        except Exception:
            self.is_farming = False

        if self.status == "start":
            self.database.update_current_loop("loop_count", self.loop_count)
            self.database.update_current_loop("machine_path", self.machine.path_machine)
            # self.database.update_current_loop("end_message", None)
            # self.database.update_current_loop("start_cpu_time", 0.0)
            # self.database.set_progress_quantity("completion")

    """
    A lemming job follows always the same pattern.
    START > SPAWN JOB> POST JOB > SPAWN JOB > POST JOB > EXIT

    each step can be customized in the present class.
    e.g. you control the nb. of SPAWN JOB>POST JOB with the 'Check on end` function.


                 Prior to job  +---------+             Prepare run
                     +--------->SPAWN JOB+---------------------+
                     |         +------^--+                     |
                     |                |                      +-v------+
                   True               |                      |POST JOB|
    +-----+          |                |                      +--------+
    |START+--->Check on start         |                          v
    +-----+          |                +---------------False-Check on end
                   False            Prior to new iteration       +
                     |                                         True
                     |                                           |
                     |                                           |
                     |           +----+                          |
                     +---------->|EXIT|<-------------------------+
               Abort on start    +----+                After end job

    you can use the database if you need to store info from one job to the other.

    The following definition of methods allows a single lemmings run to be performed without any other user input
    except for the required .yml file information.
    """

    def prior_to_job(self):
        """
        Function that prepares the run when the user launches the Lemmings command.
        """

        pass

    def abort_on_start(self):
        """
        What lemmings does if the criterion is reached in the first loop.
        """

        pass

    def prepare_run(self):
        """
        Prepare the run before submission.
        """

        pass

    def prior_to_new_iteration(self):
        """
        Prepare the new loop specific actions if criterion is not reached.
        """

        pass

    def after_end_job(self):
        """
        Actions just before lemmings ends.
        """

        pass

    def check_on_start(self):
        """
        Verify if the condition is already satisfied before launching a lemmings chain.

        Function returns a boolean which starts the chain run. Default set to True.

        A minimum required action is to set the 'start_cpu_time' so that lemmings can check
        if the max cpu condition is reached.

        """

        return True

    def check_on_end(self):
        """
        Verifications after each job loop

         The function check_on_end needs to return a boolean (default True) with three options:
             - False: we continue lemmings
             - True: target reached, we stop lemmings (default setting)
             - None: crash, we stop lemmings

        Default verification by lemmings:
             - is the cpu condition (.yml file) reached?
        """

        condition_reached = True

        return condition_reached

    def set_progress_var(self, value):
        """Update progress of the workflow with a custom value"""

        # Reformat the output to avoid numbers with too many decimals
        formatted_variable = (
            "{:.2f}".format(float(value)) if isinstance(value, (float, int)) else value
        )
        self.database.update_current_loop("completion", formatted_variable)

    def set_progress_name(self, name):
        """Update progress of the workflow with a custom value"""
        self.database.update_first_loop("progress_name", name)

    def exit(self, msg):
        """Stop the workflow"""
        switch_to_exit(self, msg, lemmings_stop=True)


def read_farming_params():
    """Load locally the farming_params, returns None if no file is available"""
    try:
        with open("_farming_params.json", "r") as fin:
            params = json.load(fin)
    except FileNotFoundError:
        params = None

    return params
