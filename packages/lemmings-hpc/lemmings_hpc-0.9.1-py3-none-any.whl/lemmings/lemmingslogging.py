import sys
import logging

LOGURU = True

"""
    General idea is to use logger instead of loguru in specific cases where loguru generates issues.
    This means creating a wrapper of the log in lemmings that automatically uses the right logging tool 

    """


def lemlog(msg: str, level: str = "info"):
    global LOGURU

    # Set the log var as an alias for either logger object(loguru) or logging object
    if LOGURU:
        from loguru import logger

        log = logger
    else:
        log = logging

    # Print the log following the level specified
    if level == "info":
        log.info(msg)
    elif level == "warning":
        log.warning(msg)
    elif level == "error":
        log.error(msg)
    elif level == "debug":
        log.debug(msg)
    elif level == "critical":
        log.critical(msg)
    else:
        log.error(f"The log level {level} is not defined !")


def startlog(f_log, verbose, log_mode="loguru"):
    """General logging function of lemmings

    All logs are dumped in their Current Working directories.
    """
    global LOGURU
    try:
        from loguru import logger

        LOGURU = True
    except ImportError:
        LOGURU = False

    if log_mode == "loguru" and LOGURU:
        format_verbose = "<d><green>{elapsed}</green> : <level>{level}</level> - <blue>{file}:{function}:{line}</blue></d> - <level>{message}</level>"
        format_normal = "<level>{message}</level>"
        logger.remove()
        if verbose:
            file = "lemmings_verbose_" + f_log
            logger.add(sys.stdout, format=format_verbose)
            logger.add(file, format=format_verbose, retention="1 day")
        else:
            file = "lemmings.log"
            logger.warning(f"Log stored in {file}")
            logger.add(sys.stdout, format=format_normal, level="INFO")
            logger.add(file, format=format_normal, level="INFO", retention="1 day")

        logger.warning(f"Loguru will store the log in {file}")
    else:
        LOGURU = False
        # Configure logging to write to a file
        log_file_name = "lemmings.log"
        logging.basicConfig(
            filename=log_file_name,
            level=logging.INFO,
            format="%(levelname)s - %(message)s",
            filemode="a",
        )
        # Create a console handler and set its level
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Create a formatter and add it to the console handler
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        console_handler.setFormatter(formatter)

        # Add the console handler to the root logger
        logging.getLogger().addHandler(console_handler)
