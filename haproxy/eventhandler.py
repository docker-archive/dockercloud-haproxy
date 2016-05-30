import json
import logging
import time
import os

import dockercloud
from compose.cli.docker_client import docker_client
from docker.errors import APIError

import config
import helper.cloud_link_helper
from haproxycfg import run_haproxy, Haproxy
from utils import get_uuid_from_resource_uri

logger = logging.getLogger("haproxy")


def on_cloud_event(message):
    logger.debug(message)
    logger.debug(Haproxy.cls_linked_services)
    try:
        event = json.loads(message)
    except ValueError:
        logger.info("event is not a valid json message")
        return

    # When service scale up/down or container start/stop/terminate/redeploy, reload the service
    if event.get("state", "") not in ["In progress", "Pending", "Terminating", "Starting", "Scaling", "Stopping"] and \
                    event.get("type", "").lower() in ["container", "service"] and \
                    len(Haproxy.cls_linked_services.intersection(set(event.get("parents", [])))) > 0:
        msg = "Docker Cloud Event: %s %s is %s" % (
            event["type"], get_uuid_from_resource_uri(event.get("resource_uri", "")), event["state"].lower())
        run_haproxy(msg)

    # Add/remove services linked to haproxy
    if event.get("state", "") == "Success" and config.HAPROXY_SERVICE_URI in event.get("parents", []):
        run_haproxy("Docker Cloud Event: New action is executed on the Haproxy container")


def on_websocket_open():
    helper.cloud_link_helper.LINKED_CONTAINER_CACHE.clear()
    run_haproxy("Websocket open")


def on_websocket_close():
    logger.info("Websocket close")


def on_user_reload(signum, frame):
    Haproxy.cls_cfg = None
    if config.LINK_MODE == "legacy":
        logger.info("User reload is not supported in legacy link mode")
    else:
        run_haproxy("User reload")


def on_cloud_error(e):
    if isinstance(e, KeyboardInterrupt):
        exit(0)


def listen_dockercloud_events():
    events = dockercloud.Events()
    events.on_open(on_websocket_open)
    events.on_close(on_websocket_close)
    events.on_message(on_cloud_event)
    events.on_error(on_cloud_error)
    while True:
        try:
            events.run_forever()
        except dockercloud.AuthError as e:
            logger.info("Auth error: %s, retry in 1 hour" % e)
            time.sleep(3600)


def listen_docker_events():
    try:

        try:
            docker = docker_client()
        except:
            docker = docker_client(os.environ)

        docker.ping()
        for event in docker.events(decode=True):
            logger.debug(event)
            attr = event.get("Actor", {}).get("Attributes")
            compose_project = attr.get("com.docker.compose.project", "")
            compose_service = attr.get("com.docker.compose.service", "")
            container_name = attr.get("name", "")
            event_action = event.get("Action", "")
            service = "%s_%s" % (compose_project, compose_service)
            if service in Haproxy.cls_linked_services and event_action in ["start", "die"]:
                msg = "Docker event: container %s %s" % (container_name, event_action)
                run_haproxy(msg)
    except APIError as e:
        logger.info("Docker API error: %s" % e)
