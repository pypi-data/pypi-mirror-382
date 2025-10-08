import traceback
from lemmings.lemmingslogging import lemlog


def switch_to_exit(lemmings_job, exception, lemmings_stop=False):
    """Function that performs the updates in case an exception is raised through
    LemmingsStop or other

    Input:
        lemmings_job: lemmings_job class object
        database: database class object
        exception: raised exception class message
        lemmings_stop: boolean, whether exception raised through LemmingsStop or not
    Output:
        None: performs updates in database and ends the lemmings chain
    """
    lemlog("         Switch to exit")

    end_msg = str(exception)
    if not lemmings_stop:
        end_msg = traceback.format_exc() + "\n" + str(exception)
        # traceback.print_exc()
        lemlog(f"         Reason : {end_msg}", level="warning")
    else:
        lemlog(f"         Reason : {end_msg}")

    lemmings_job.database.update_current_loop("end_message", end_msg)
    lemmings_job.status = "exit"


class LemmingsStop(Exception):
    """Definition of a class to allow exit of Lemmings safely upon exceptions"""

    pass
