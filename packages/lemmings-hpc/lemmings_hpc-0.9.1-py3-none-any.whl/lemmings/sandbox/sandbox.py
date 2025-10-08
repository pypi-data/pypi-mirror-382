""" module to execute a lemming command in a sandbox"""

import os
import sys
import json
import logging
import subprocess
import time as libtime

from pathlib import Path
from lemmings.lemmingslogging import lemlog
from datetime import datetime as dt
from prettytable import PrettyTable

SBX_INTERNAL_PROPERTIES = [
    "pid",
    "time",
    "state",
    "after",
    "batchfile",
    "cwd",
]
SBX_EXTERNAL_PROPERTIES = [
    "job_name",
    "queue",
]


DATETIME_FORMAT = "%m/%d/%y %H:%M:%S"


#### DAEMON SANDBOX
def start_sandbox(
    db_file=None, frequency=3, max_duration=9, stdout_log=True, max_parallel_jobs=2
):
    """Start sandbox"""

    db = SmallDb(db_file, cleanup=True)
    f_log = os.path.splitext(db.db_file)[0] + ".log"
    lemlog(f_log)
    # _logging_start_sandbox(db.db_file, stdout_log)

    lemlog("Starting sandbox...")
    lemlog(f"Freq: {frequency}s")
    lemlog(f"Max duration: {max_duration}s")

    sandbox_time = 0
    while sandbox_time < max_duration:
        _sandbox_daemon(db, max_parallel_jobs)
        libtime.sleep(frequency)
        sandbox_time += frequency

    lemlog("Sandbox shutting down")


def submit_sandbox(batchfile, db_file=None, after=None):
    """Submit run"""

    if not os.path.isfile(batchfile):
        raise FileNotFoundError(f"batch {batchfile} not found")

    db = SmallDb(db_file)

    pid = str(os.getpid())
    cwd = os.getcwd()
    item = {
        "pid": pid,
        "time": _now_str(),
        "state": "pending",
        "after": after,
        "batchfile": batchfile,
        "job_name": "dummy",
        "queue": "dummy",
        "cwd": cwd,
    }

    with open(cwd + "/" + batchfile, "r") as fin:
        for line in fin.readlines():
            if line.startswith("#SBX"):
                key, val = line[4:].strip().split("=")
                if key not in SBX_EXTERNAL_PROPERTIES:
                    return (
                        f"-{key}- is not part of allowed properties:\n - "
                        + "\n - ".join(SBX_EXTERNAL_PROPERTIES)
                    )
                item[key] = val
    jname = item["job_name"] + "_" + str(item["pid"])
    lemlog(f"queue job {jname}")

    db.insert(item)
    return pid


def cancel_sandbox(pid, db_file=None):
    """Cancel run"""

    db = SmallDb(db_file)

    dict_ = _db_as_dict(db)

    if pid not in dict_.keys():
        return f"PID {pid} not in the queue"

    item = dict_[pid]

    if item["state"] in ["pending", "running"]:
        msg = f"PID {pid} was cancelled by user..."
        with open(_tracker(item) + ".o", "a") as fout:
            fout.write(msg)
        with open(_tracker(item) + ".e", "a") as fout:
            fout.write(msg)

        Path(_tracker(item) + ".done").touch()
        return f"PID {pid} cancelled"
    elif item["state"] in ["done"]:
        return f"PID {pid} already finished"
    else:
        raise RuntimeError(f"Unexpected situation for state {item['state']}")


def acct_sandbox(pid, db_file=None):
    """Accounting run"""

    db = SmallDb(db_file)

    dict_ = _db_as_dict(db)

    if pid not in dict_.keys():
        raise ValueError("Pid {pid} not known")

    start = None
    end = None
    for item in db:
        if item["pid"] == pid:
            if item["state"] == "running":
                start = dt.strptime(item["time"], DATETIME_FORMAT)
            if item["state"] == "done":
                end = dt.strptime(item["time"], DATETIME_FORMAT)

    if start is None:
        return f"Process {pid} has not stated yet"
    if end is None:
        end = dt.now()

    acct = str((end - start).seconds)
    return acct


def qstat_sandbox(
    db_file=None,
):
    """Qstat"""
    db = SmallDb(db_file)
    qstat = PrettyTable()
    qstat.field_names = ["job name", "queue", "pid", "state", "last update", "after"]
    for item in _db_as_dict(db).values():
        after = item["after"]
        if after is None:
            after = "-"

        qstat.add_row(
            [
                item["job_name"],
                item["queue"],
                item["pid"],
                item["state"],
                item["time"],
                after,
            ]
        )
    lemlog(qstat)


class SmallDb:
    """Because tinyDb cannot handle several processes"""

    def __init__(self, db_file=None, cleanup=False):
        if db_file is None:
            db_file = "./sandbox_lem_ddb.json"

        if not os.path.isfile(db_file):
            Path(db_file).touch()

        if cleanup:
            with open(db_file, "w") as fout:
                fout.write("")

        self.db_file = db_file

    def insert(self, dict_):
        """Add line to ddb"""
        str_ = json.dumps(dict_)
        with open(self.db_file, "a") as fout:
            fout.write(str_ + "\n")

    def __iter__(self):
        """iterable"""
        with open(self.db_file, "r") as fin:
            for line in fin.readlines():
                yield json.loads(line)


def _logging_start_sandbox(db_file, stdout_log=False):
    f_log = os.path.splitext(db_file)[0] + ".log"

    hand_list = [logging.FileHandler(f_log, mode="w")]

    if stdout_log:
        hand_list.append(logging.StreamHandler(sys.stdout))

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s - %(message)s",
        # format="%(message)s",
        handlers=hand_list,
    )


def _db_as_dict(db):
    dict_ = {}
    for item in db:
        pid = item["pid"]
        if pid not in dict_:
            dict_[pid] = {}
        dict_[pid] = item
    return dict_


def _items_running(db):
    items_running = []
    for item in _db_as_dict(db).values():
        if item["state"] == "running":
            items_running.append(item)
    return items_running


def _items_pending(db):
    items_pending = []
    for item in _db_as_dict(db).values():
        if item["state"] == "pending":
            items_pending.append(item)
    return items_pending


def _pids_done(db):
    pids_done = []
    for item in _db_as_dict(db).values():
        if item["state"] == "done":
            pids_done.append(item["pid"])
    return pids_done


def _sandbox_daemon(db, max_parallel_jobs):
    lemlog(f"Daemon spawn.")

    # set running jobs to done if time is elapsed or job cancelled
    for item in _items_running(db):
        _sandbox_testdone(db, item)
    for item in _items_pending(db):
        _sandbox_testdone(db, item)
    # set pending jobs to running if allowed

    for item in _items_pending(db):
        if item["after"] is None:
            _sandbox_startjob(db, item, max_parallel_jobs)
        else:
            if item["after"] in _pids_done(db):
                _sandbox_startjob(db, item, max_parallel_jobs)


def _sandbox_startjob(db, item, max_parallel_jobs):
    """Start a job if allowed jobs agrees"""

    free_processes = max_parallel_jobs - len(_items_running(db))
    if free_processes <= 0:
        return

    item["state"] = "running"
    item["time"] = _now_str()
    db.insert(item)
    jname = item["job_name"] + "_" + str(item["pid"])
    lemlog(f"start job {jname}")

    batch_actions = []

    with open(item["cwd"] + "/" + item["batchfile"], "r") as fin:
        for line in fin.readlines():
            if line.startswith("#!"):
                pass  # remove shebang
            elif line.startswith("#SBX"):
                pass  # remove sandbox intrisic params
            elif line.strip() == "":
                pass  # remove blank lines
            else:
                batch_actions.append(line.replace("\n", ""))

    fstdout = open(_tracker(item) + ".o", "w")
    fstderr = open(_tracker(item) + ".e", "w")

    cmd = " ; ".join(batch_actions)

    rebatch = "\n|     " + "\n|    ".join(cmd.split(";"))
    lemlog(f"Current workdir: {item['cwd']}")
    lemlog(f"Command executed: {rebatch}")
    subp = subprocess.run(
        cmd, stdout=fstdout, stderr=fstderr, shell=True, cwd=item["cwd"]
    )

    fstdout.close()
    fstderr.close()

    # add a file to say its done
    Path(_tracker(item) + ".done").touch()

    return


def _sandbox_testdone(db, item):
    """Set a job to done if the duration is elapsed"""
    if os.path.isfile(_tracker(item) + ".done"):
        os.remove(_tracker(item) + ".done")
        item["state"] = "done"
        item["time"] = _now_str()
        db.insert(item)
        jname = item["job_name"] + "_" + str(item["pid"])
        lemlog(f"stop job {jname}")
    return


def _tracker(item):
    return f"{item['cwd']}/{item['job_name']}_{str(item['pid'])}"


def _now_str():
    return dt.now().strftime(DATETIME_FORMAT)
