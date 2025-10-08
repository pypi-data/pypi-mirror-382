from lemmings.chain.lemmingjob_base import LemmingJobBase


def lemmings_run_cmd(lemmings_job: LemmingJobBase, post_job: bool = False) -> str:
    """Build a lemmings run command line"""
    post_option = ""
    if post_job:
        post_option = " -s post_job"
    log_option = ""
    if lemmings_job.log_mode != "loguru":
        log_option = (
            " -l logging"  # Allow the usage of logging as log module instead of loguru
        )
    command = [
        f"lemmings run {lemmings_job.workflow}"
        + post_option
        + log_option
        + f" --inputfile={lemmings_job.path_yml}"
        + f" --job-prefix={lemmings_job.job_prefix}"
        + f" --machine-file={lemmings_job.machine.path_machine}"
    ][0]
    return command
