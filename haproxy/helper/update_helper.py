import logging
import subprocess
import threading
import time
import errno

from haproxy.config import HAPROXY_RUN_COMMAND, RELOAD_TIMEOUT, HAPROXY_CONFIG_CHECK_COMMAND

logger = logging.getLogger("haproxy")


# RELOAD_TIMEOUT has the following values and effect:
# -1 : Reload haproxy with "-st" which will immediately kill the previous process
# 0 : Reload haproxy with "-sf" and no timeout.  This can potentially leave 
#     "broken" processes (where the backends have changed) hanging around 
#     with existing connections.
# > 0 : Reload haproxy with "-sf" but if it takes longer than RELOAD_TIMEOUT then kill it
#       This gives existing connections a chance to finish.  RELOAD_TIMEOUT should be set to 
#       the approximate time it takes docker to finish updating services.  By this point the
#       existing configuration will be invalid, and any connections still using it will 
#       have invalid backends.
#
def run_reload(old_process, timeout=int(RELOAD_TIMEOUT)):
    if old_process:
        p = subprocess.Popen(HAPROXY_CONFIG_CHECK_COMMAND, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = p.communicate()
        return_code = p.returncode
        if (return_code != 0):
          logger.error("Config check failed. NOT reloading haproxy")
          logger.error(output)
          logger.error(err)
          return
        else:
          logger.info("Config check passed")
        # Reload haproxy
        logger.info("Reloading HAProxy")
        if timeout == -1:
            flag = "-st"
            logger.info("Restarting HAProxy immediately")
        else:
            flag = "-sf"
            logger.info("Restarting HAProxy gracefully")

        new_process = subprocess.Popen(HAPROXY_RUN_COMMAND + [flag, str(old_process.pid)])
        logger.info("HAProxy is reloading (new PID: %s)", str(new_process.pid))

        thread = threading.Thread(target=wait_pid, args=[old_process, timeout])
        thread.start()

        # Block only if we have a timeout.  If we don't it could take forever, and so
        # returning immediately maintains the original behaviour of no timeout.
        if timeout > 0:
            thread.join()

    else:
        # Launch haproxy
        logger.info("Launching HAProxy")
        new_process = subprocess.Popen(HAPROXY_RUN_COMMAND)
        logger.info("HAProxy has been launched(PID: %s)", str(new_process.pid))

    return new_process


def wait_pid(process, timeout):
    start = time.time()

    timer = None

    if timeout > 0:
        timer = threading.Timer(timeout, timeout_handler, [process])
        timer.start()

    process.wait()

    if timer is not None:
        timer.cancel();

    duration = time.time() - start
    logger.info("Old HAProxy(PID: %s) ended after %s sec", str(process.pid), str(duration))


def timeout_handler(processs):
    if processs.poll() is None:
        try:
            processs.terminate()
            logger.info("Old HAProxy process taking too long to complete - terminating")
        except OSError as e:
            if e.errno != errno.ESRCH:
                raise
