import logging
import os
import signal
import sys

import dockercloud

from config import DEBUG, PID_FILE, HAPROXY_SERVICE_URI, HAPROXY_CONTAINER_URI, API_AUTH
from eventhandler import on_cloud_event, on_websocket_open, on_user_reload, on_websocket_close
from haproxy import __version__
from haproxycfg import run_haproxy
from utils import save_to_file

dockercloud.user_agent = "dockercloud-haproxy/%s" % __version__

logger = logging.getLogger("haproxy")


def create_pid_file():
    pid = str(os.getpid())
    save_to_file(PID_FILE, pid)
    return pid


def set_autoreload(haproxy_container_uri, haproxy_service_uri, api_auth):
    autoreload = False
    if haproxy_container_uri and haproxy_service_uri:
        if api_auth:
            msg = "dockercloud/haproxy %s has access to the cloud API - will reload list of backends" \
                  " in real-time" % __version__
            autoreload = True
        else:
            msg = "dockercloud/haproxy %s doesn't have access to the cloud API - you might want to" \
                  " give an API role to this service for automatic backend reconfiguration" % __version__
    else:
        msg = "dockercloud/haproxy %s is not running in Docker Cloud" % __version__
    logger.info(msg)
    return autoreload


def listen_remote_events():
    events = dockercloud.Events()
    events.on_open(on_websocket_open)
    events.on_close(on_websocket_close)
    events.on_message(on_cloud_event)
    events.run_forever()


def main():
    logging.basicConfig(stream=sys.stdout)
    logging.getLogger("haproxy").setLevel(logging.DEBUG if DEBUG else logging.INFO)
    if DEBUG:
        requests_log = logging.getLogger("python-dockercloud").setLevel(logging.DEBUG)

    signal.signal(signal.SIGUSR1, on_user_reload)
    signal.signal(signal.SIGTERM, sys.exit)

    autoreload = set_autoreload(HAPROXY_CONTAINER_URI, HAPROXY_SERVICE_URI, API_AUTH)

    pid = create_pid_file()
    logger.info("HAProxy PID: %s" % pid)

    if autoreload:
        listen_remote_events()
    else:
        run_haproxy("Initial start")


if __name__ == "__main__":
    main()
