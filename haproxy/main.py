from gevent import monkey

monkey.patch_all()

import logging
import os
import sys
import signal
import gevent
import time
import dockercloud
from compose.cli.docker_client import docker_client
from gevent import queue

import config
from config import DEBUG, PID_FILE, HAPROXY_CONTAINER_URI, HAPROXY_SERVICE_URI, API_AUTH
from eventhandler import on_user_reload, listen_docker_events_compose_mode, listen_dockercloud_events, \
    listen_docker_events_swarm_mode
from haproxy import __version__
import haproxycfg
from haproxycfg import add_haproxy_run_task, run_haproxy, Haproxy
from utils import save_to_file
from config import RunningMode

dockercloud.user_agent = "dockercloud-haproxy/%s" % __version__

logger = logging.getLogger("haproxy")

haproxycfg.tasks = queue.Queue()


def create_pid_file():
    pid = str(os.getpid())
    save_to_file(PID_FILE, pid)
    return pid


def main():
    logging.basicConfig(stream=sys.stdout)
    logging.getLogger("haproxy").setLevel(logging.DEBUG if DEBUG else logging.INFO)
    if DEBUG:
        logging.getLogger("python-dockercloud").setLevel(logging.DEBUG)

    config.RUNNING_MODE = check_running_mode(HAPROXY_CONTAINER_URI, HAPROXY_SERVICE_URI, API_AUTH)

    gevent.signal(signal.SIGUSR1, on_user_reload)
    gevent.signal(signal.SIGTERM, sys.exit)

    gevent.spawn(run_haproxy)

    pid = create_pid_file()
    logger.info("dockercloud/haproxy PID: %s" % pid)

    if config.RUNNING_MODE == RunningMode.CloudMode:
        gevent.spawn(listen_dockercloud_events)
    elif config.RUNNING_MODE == RunningMode.ComposeMode:
        add_haproxy_run_task("Initial start - Compose Mode")
        gevent.spawn(listen_docker_events_compose_mode)
    elif config.RUNNING_MODE == RunningMode.SwarmMode:
        add_haproxy_run_task("Initial start - Swarm Mode")
        gevent.spawn(listen_docker_events_swarm_mode)
    elif config.RUNNING_MODE == RunningMode.LegacyMode:
        add_haproxy_run_task("Initial start - Legacy Mode")

    while True:
        time.sleep(5)
        if Haproxy.cls_process:
            if is_process_running(Haproxy.cls_process):
                continue
            Haproxy.cls_cfg = None
            add_haproxy_run_task("haproxy %s died , restart" % Haproxy.cls_process.pid)


def is_process_running(p):
    try:
        os.kill(p.pid, 0)
        return True
    except OSError:
        return False


def check_running_mode(container_uri, service_uri, api_auth):
    mode, msg = None, ""
    if container_uri and service_uri and api_auth:
        if container_uri and service_uri:
            if api_auth:
                msg = "dockercloud/haproxy %s has access to the Docker Cloud API - will reload list of backends " \
                      " in real-time" % __version__
            else:
                msg = "dockercloud/haproxy %s is unable to access the Docker Cloud API - you might want to" \
                      " give an API role to this service for automatic backend reconfiguration" % __version__
        mode = RunningMode.CloudMode
    else:
        reason = ""
        try:
            try:
                docker = docker_client()
            except:
                docker = docker_client(os.environ)
            docker.ping()
        except Exception as e:
            reason = "unable to connect to docker daemon %s" % e
            mode = RunningMode.LegacyMode

        if mode != RunningMode.LegacyMode:
            container_id = os.environ.get("HOSTNAME", "")
            if not container_id:
                reason = "unable to get dockercloud/haproxy container ID, is HOSTNAME envvar overwritten?"
                mode = RunningMode.LegacyMode
            else:
                try:
                    container = docker.inspect_container(container_id)
                    if container.get("HostConfig", {}).get("Links", []):
                        reason = "dockercloud/haproxy container is running on default bridge"
                        mode = RunningMode.LegacyMode
                    else:
                        labels = container.get("Config", {}).get("Labels", {})
                        if labels.get("com.docker.swarm.service.id", ""):
                            mode = RunningMode.SwarmMode
                        elif labels.get("com.docker.compose.project", ""):
                            mode = RunningMode.ComposeMode
                        else:
                            reason = "dockercloud/haproxy container doesn't contain any compose or swarm labels"
                            mode = RunningMode.LegacyMode
                except Exception as e:
                    reason = "unable to get dockercloud/haproxy container inspect information, %s" % e
                    mode = RunningMode.LegacyMode

        logger.info("dockercloud/haproxy %s is running outside Docker Cloud" % __version__)
        if mode == RunningMode.LegacyMode:
            msg = "Haproxy is running using legacy link, loading HAProxy definition from environment variables: %s" % reason
        elif mode == RunningMode.ComposeMode:
            msg = "Haproxy is running by docker-compose, loading HAProxy definition through docker api"
        elif mode == RunningMode.SwarmMode:
            msg = "Haproxy is running in SwarmMode, loading HAProxy definition through docker api"

    logger.info(msg)
    return mode


if __name__ == "__main__":
    main()
