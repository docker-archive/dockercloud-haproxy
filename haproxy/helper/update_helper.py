import logging
import subprocess
import thread

from haproxy.config import HAPROXY_RUN_COMMAND

logger = logging.getLogger("haproxy")


def run_once():
    logger.info("Launching HAProxy")
    p = subprocess.Popen(HAPROXY_RUN_COMMAND)
    logger.info("HAProxy has been launched(PID: %s)", str(p.pid))
    logger.info("===========END===========")
    p.wait()


def run_reload(old_process):
    if old_process:
        # Reload haproxy
        logger.info("Reloading HAProxy")
        new_process = subprocess.Popen(HAPROXY_RUN_COMMAND + ["-sf", str(old_process.pid)])
        thread.start_new_thread(wait_pid, (old_process,))
        logger.info("HAProxy has been reloaded(PID: %s)", str(new_process.pid))
    else:
        # Launch haproxy
        logger.info("Launching HAProxy")
        new_process = subprocess.Popen(HAPROXY_RUN_COMMAND)
        logger.info("HAProxy has been launched(PID: %s)", str(new_process.pid))

    return new_process


def wait_pid(process):
    process.wait()
    logger.info("HAProxy(PID:%s) has been terminated" % str(process.pid))
