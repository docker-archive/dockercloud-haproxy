import logging

import config
from haproxycfg import run_haproxy, Haproxy
from utils import get_uuid_from_resource_uri

logger = logging.getLogger("haproxy")


def on_cloud_event(event):
    logger.debug(event)
    logger.debug(Haproxy.cls_linked_services)
    # When service scale up/down or container start/stop/terminate/redeploy, reload the service
    if event.get("state", "") not in ["In progress", "Pending", "Terminating", "Starting", "Scaling", "Stopping"] and \
                    event.get("type", "").lower() in ["container", "service"] and \
                    len(set(Haproxy.cls_linked_services).intersection(set(event.get("parents", [])))) > 0:
        msg = "Event: %s %s is %s" % (
            event["type"], get_uuid_from_resource_uri(event.get("resource_uri", "")), event["state"].lower())
        run_haproxy(msg)

    # Add/remove services linked to haproxy
    if event.get("state", "") == "Success" and config.HAPROXY_SERVICE_URI in event.get("parents", []):
        run_haproxy("Event: New action is executed on the Haproxy container")


def on_websocket_open():
    Haproxy.LINKED_CONTAINER_CACHE.clear()
    run_haproxy("Websocket open")


def on_websocket_close():
    logger.info("Websocket close")


def on_user_reload(signum, frame):
    run_haproxy("User reload")
