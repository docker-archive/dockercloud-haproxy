import logging

import compose_mode_link_helper
from haproxy.config import SERVICE_PORTS_ENVVAR_NAME, LABEL_SWARM_MODE_DEACTIVATE

logger = logging.getLogger("haproxy")


def get_swarm_mode_haproxy_id_nets(docker, haproxy_container_short_id):
    try:
        haproxy_container = docker.inspect_container(haproxy_container_short_id)
    except Exception as e:
        logger.info("Docker API error, regressing to legacy links mode: %s" % e)
        return "", set()
    labels = haproxy_container.get("Config", {}).get("Labels", {})
    haproxy_service_id = labels.get("com.docker.swarm.service.id", "")
    if not haproxy_service_id:
        logger.info("Dockercloud haproxy is not running in a service in SwarmMode")
        return "", set()

    haproxy_nets = set([network.get("NetworkID", "") for name, network in
                        haproxy_container.get("NetworkSettings", {}).get("Networks", {}).iteritems()
                        if name != "ingress"])

    return haproxy_service_id, haproxy_nets


def get_swarm_mode_links(docker, haproxy_service_id, haproxy_nets):
    services = docker.services()
    tasks = docker.tasks(filters={"desired-state": "running"})
    return get_task_links(tasks, services, haproxy_service_id, haproxy_nets)


def get_task_links(tasks, services, haproxy_service_id, haproxy_nets):
    services_id_name = {s.get("ID"): s.get("Spec", {}).get("Name", "") for s in services}
    services_id_labels = {s.get("ID"): s.get("Spec", {}).get("Labels", {}) for s in services}
    links = {}
    linked_tasks = {}
    for task in tasks:
        task_nets = [network.get("Network", {}).get("ID", "") for network in task.get("NetworksAttachments", [])]
        task_service_id = task.get("ServiceID", "")
        task_nets_attached = haproxy_nets.intersection(set(task_nets))
        if task_service_id != haproxy_service_id and task_nets_attached:
            task_id = task.get("ID", "")
            task_slot = "%d" % task.get("Slot", 0)
            task_service_id = task.get("ServiceID", "")
            task_service_name = services_id_name.get(task_service_id, "")
            task_labels = services_id_labels.get(task_service_id, {})

            if task_labels.get(LABEL_SWARM_MODE_DEACTIVATE, "").lower() == "true":
                continue

            container_name = ".".join([task_service_name, task_slot, task_id])
            task_envvars = get_task_envvars(task.get("Spec", {}).get("ContainerSpec", {}).get("Env", []))

            service_ports = ""
            for task_envvar in task_envvars:
                if task_envvar["key"] == SERVICE_PORTS_ENVVAR_NAME:
                    service_ports = task_envvar["value"]
            task_ports = [x.strip() for x in service_ports.strip().split(",") if x.strip()]

            task_ips = []
            for network_attachment in task.get("NetworksAttachments", []):
                if network_attachment.get("Network", {}).get("ID", "") in task_nets_attached:
                    task_ips = network_attachment.get("Addresses", [])
                    break

            if task_ips:
                task_ip = task_ips[0].split("/")[0]
            else:
                task_ip = container_name

            task_endpoints = {"%s/tcp" % port: "tcp://%s:%s" % (task_ip, port) for port in task_ports}

            links[task_id] = {"endpoints": task_endpoints, "container_name": container_name,
                              "service_name": task_service_name, "container_envvars": task_envvars}
            linked_tasks[task_id] = task_labels
    return links, linked_tasks


def get_task_envvars(envvars):
    new_envvars = []
    for _envvar in envvars:
        terms = _envvar.split("=", 1)
        envvar = {"key": terms[0]}
        if len(terms) == 2:
            envvar["value"] = terms[1]
        else:
            envvar["value"] = ""
        new_envvars.append(envvar)
    return new_envvars


def get_service_links_str(links):
    return compose_mode_link_helper.get_service_links_str(links)


def get_container_links_str(links):
    return compose_mode_link_helper.get_container_links_str(links)
