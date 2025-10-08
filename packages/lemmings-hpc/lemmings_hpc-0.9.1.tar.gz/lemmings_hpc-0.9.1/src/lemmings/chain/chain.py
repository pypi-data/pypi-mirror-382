f"""
This script executes the fundamentals functions of lemmings workflows.
"""
from lemmings.lemmingslogging import lemlog
from datetime import datetime as dt
from lemmings.chain.farming import continue_farming
from lemmings.chain.lemmingsstop import switch_to_exit, LemmingsStop
from lemmings.chain.lemmingscmd import lemmings_run_cmd

from lemmings.chain.lemmingjob_base import LemmingJobBase

DATETIME_FORMAT = "%m/%d/%y %H:%M:%S"


class Lemmings:
    """
    Lemmings assemble
    - lemmingJob : the workflow to do
    - machine : the machine file, specialized on the queues
    - database : a persistent information for lemmings
    """

    def __init__(self, lemmings_job: LemmingJobBase):
        """
        :param lemmings_job: An Object that contains all actions/
                             made in the different classical lemmings function:
                             --> function that check conditon(s)
                             --> function that do some actions before update status
                            For example, function "start_to_spawn_job()" can save a file, a fig ...
        """
        self.lemmings_job = lemmings_job
        self.machine = self.lemmings_job.machine
        self.database = self.lemmings_job.database

    def run(self):
        """*Submit the chain of computations.*"""

        while self.lemmings_job.status != "exit":
            self.next()

    def next(self):
        """
        Execute all necessary functions depending on its status
        There are 2 kind of function:
        - Functions that check some conditions
        - Functions that pass from a status to another

        ::

                         - - - > spawn_job - - - -
                        |             ^             |
                        |             |             V
                      start             - - - - - post_job
                <check_condition>             <check_condition>
                        |                           |
                        |                           |
                        |                           |
                         - - - - - > Exit < - - - -
        """
        if self.lemmings_job.status == "start":
            self._perform_lemmings_job_start()

        elif self.lemmings_job.status == "spawn_job":
            self._perform_lemmings_job_spawn()

        elif self.lemmings_job.status == "post_job":
            self._perform_lemmings_job_post()
        else:
            raise NotImplementedError("Lemmings reached unknown status")
        return

    def _create_batch(
        self, batch_j: str = "./batch_job", batch_pj: str = "./batch_pjob"
    ):
        """
        Create the batch that will launch the job and postjob loop of lemmings.
        The construction is based on namedtuple that are unique for each machine.
        So the user, if not already done, have to set up those namedtuple for his machine(cluster).
        """
        lemlog("===Creating batch files===")

        batch_job = self.machine.job_template.batch
        batch_pjob = (
            self.machine.pj_template.batch
            + "\n"
            + lemmings_run_cmd(self.lemmings_job, post_job=True)
            + "\n"
        )

        with open(batch_j, "w") as fout:
            fout.write(batch_job)

        lemlog("---Batch job---")
        lemlog(batch_job)

        with open(batch_pj, "w") as fout:
            fout.write(batch_pjob)

        lemlog("---Batch Post-job---")
        lemlog(batch_pjob)

    def _perform_lemmings_job_start(self):
        """call sequence associated with the 'start' part of lemmings"""
        lemlog("    Lemmings START")

        try:
            start_chain = self.lemmings_job.check_on_start()
            lemlog(f"         Check on start{str(start_chain)} (False -> Exit)")

            if start_chain:
                self.lemmings_job.prior_to_job()
                lemlog("         Prior to job")
                self._create_batch()

                self.lemmings_job.status = "spawn_job"
            else:
                self.lemmings_job.abort_on_start()
                lemlog("         Abort on start")
                self.lemmings_job.status = "exit"
        except LemmingsStop as stop:
            switch_to_exit(self.lemmings_job, stop, lemmings_stop=True)
            self.lemmings_job.status = "exit"  # -> can probably remove, to check
        except Exception as any_other_exception:
            switch_to_exit(
                self.lemmings_job,
                any_other_exception,
                lemmings_stop=False,
            )

    def _perform_lemmings_job_spawn(self):
        """call sequence associated with the 'spawn_job' part of lemmings"""
        lemlog("    Lemmings SPAWN")

        # ADN : what is this "Safe-stop" ???

        try:
            # Defined as one of the methods
            self.lemmings_job.prepare_run()
            lemlog("         Prepare run")

            safe_stop = self.database.get_previous_loop_val("safe_stop")
        except LemmingsStop as stop:
            switch_to_exit(self.lemmings_job, stop, lemmings_stop=True)
            safe_stop = True
        except Exception as any_other_exception:
            switch_to_exit(
                self.lemmings_job,
                any_other_exception,
                lemmings_stop=False,
            )
            safe_stop = True

        if safe_stop is False:
            submit_path = self.database.get_current_loop_val("submit_path")
            job_id = self.machine.submit(
                batch_name="batch_job", submit_path=submit_path
            )
            lemlog(
                f"         Submit batch {job_id} / time : {dt.now().strftime(DATETIME_FORMAT)}"
            )

            pjob_id = self.machine.submit(
                batch_name="batch_pjob", dependency=job_id, submit_path="./"
            )
            lemlog(
                f"         Submit batch post job {pjob_id} / time : {dt.now().strftime(DATETIME_FORMAT)}"
            )

            self.database.update_current_loop("job_id", job_id)
            self.database.update_current_loop("pjob_id", pjob_id)
        else:
            self.database.update_current_loop("safe_stop", True)
        self.lemmings_job.status = "exit"

    def _perform_lemmings_job_post(self):
        """Function controls the call sequence associated with the 'post_job' part of lemmings

        Input:
            :lemmings: Lemmings object

        Output:
            :None
        """
        lemlog("    Lemmings POST")
        # A lemmings job is finished if
        #       1) the target condition is reached (e.g. simulation end time)
        #       2) the simulation crashed for some reason
        # condition_reached can take 3 values:
        #       - False: we continue lemmings
        #       - True: target reached, we stop lemmings
        #       - None: crash, we stop lemmings

        condition_reached = self.lemmings_job.check_on_end()
        lemlog(f"         Check on end : {str(condition_reached)} (True -> Exit)")

        if condition_reached is True or condition_reached is None:
            if condition_reached is None:
                lemlog("Run crashed")
            else:
                lemlog("Target condition reached")

            self.lemmings_job.after_end_job()
            lemlog("         After end job")
            self.database.update_current_loop(
                "end_status", f"Chain {self.database.latest_chain_name} is completed"
            )

            if self.lemmings_job.is_farming:
                continue_farming(self.lemmings_job)
                lemlog("         Continue Farming")

            self.lemmings_job.status = "exit"
        else:
            self.database.initialise_new_loop()
            self.lemmings_job.loop_count += 1
            lemlog(f"         Move to loop {str(self.lemmings_job.loop_count)}")

            # increment loop count by 1 as we'll start a new spawn job

            self.database.update_current_loop(
                "loop_count", self.lemmings_job.loop_count
            )

            self.lemmings_job.prior_to_new_iteration()
            lemlog(f"         Prior to new iteration")

            self._create_batch()
            self.lemmings_job.status = "spawn_job"
