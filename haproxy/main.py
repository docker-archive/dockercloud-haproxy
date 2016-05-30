import logging
import os
import signal
import sys

import dockercloud
from compose.cli.docker_client import docker_client

import config
from config import DEBUG, PID_FILE, HAPROXY_CONTAINER_URI, HAPROXY_SERVICE_URI, API_AUTH
from eventhandler import on_user_reload, listen_docker_events, listen_dockercloud_events
from haproxy import __version__
from haproxycfg import run_haproxy
from utils import save_to_file


from gevent import monkey
monkey.patch_all()

dockercloud.user_agent = "dockercloud-haproxy/%s" % __version__

logger = logging.getLogger("haproxy")


def create_pid_file():
    pid = str(os.getpid())
    save_to_file(PID_FILE, pid)
    return pid


def main():
    logging.basicConfig(stream=sys.stdout)
    logging.getLogger("haproxy").setLevel(logging.DEBUG if DEBUG else logging.INFO)
    if DEBUG:
        logging.getLogger("python-dockercloud").setLevel(logging.DEBUG)

    config.LINK_MODE = check_link_mode(HAPROXY_CONTAINER_URI, HAPROXY_SERVICE_URI, API_AUTH)
    signal.signal(signal.SIGUSR1, on_user_reload)
    signal.signal(signal.SIGTERM, sys.exit)

    pid = create_pid_file()
    logger.info("dockercloud/haproxy PID: %s" % pid)

    if config.LINK_MODE == "cloud":
        listen_dockercloud_events()
    elif config.LINK_MODE == "new":
        run_haproxy("Initial start")
        while True:
            listen_docker_events()
            run_haproxy("Reconnect docker events")

    elif config.LINK_MODE == "legacy":
        run_haproxy()


def check_link_mode(container_uri, service_uri, api_auth):
    if container_uri and service_uri and api_auth:
        if container_uri and service_uri:
            if api_auth:
                logger.info("dockercloud/haproxy %s has access to the Docker Cloud API - will reload list of backends" \
                            " in real-time" % __version__)
            else:
                logger.info("dockercloud/haproxy %s is unable to access the Docker cloud API - you might want to" \
                            " give an API role to this service for automatic backend reconfiguration" % __version__)
        return "cloud"
    else:

        link_mode = "new"
        reason = ""
        try:
            try:
                docker = docker_client()
            except:
                docker = docker_client(os.environ)
            docker.ping()
        except Exception as e:
            reason = "unable to connect to docker daemon %s" % e
            link_mode = "legacy"

        if link_mode == "new":
            container_id = os.environ.get("HOSTNAME", "")
            if not container_id:
                reason = "unable to get dockercloud/haproxy container ID, is HOSTNAME envvar overwritten?"
                link_mode = "legacy"
            else:
                try:
                    container = docker.inspect_container(container_id)
                    if container.get("HostConfig", {}).get("Links", []):
                        reason = "dockercloud/haproxy container is running on default bridge"
                        link_mode = "legacy"
                except Exception as e:
                    reason = "unable to get dockercloud/haproxy container inspect information, %s" % e
                    link_mode = "legacy"

        logger.info("dockercloud/haproxy %s is running outside Docker Cloud" % __version__)
        if link_mode == "new":
            logger.info("New link mode, loading HAProxy definition through docker api")
        else:
            logger.info("Legacy link mode, loading HAProxy definition from environment variables: %s", reason)
        return link_mode


if __name__ == "__main__":
    main()
