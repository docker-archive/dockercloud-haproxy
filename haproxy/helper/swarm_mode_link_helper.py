import logging
import compose_mode_link_helper

logger = logging.getLogger("haproxy")


def get_swarm_mode_links(docker, haproxy_container_short_id):
    try:
        haproxy_container = docker.inspect_container(haproxy_container_short_id)
    except Exception as e:
        logger.info("Docker API error, regressing to legacy links mode: %s" % e)
        return {}, set()
    labels = haproxy_container.get("Config", {}).get("Labels", {})
    service_id = labels.get("com.docker.swarm.node.id", "")
    service_name = labels.get("com.docker.swarm.service.name", "")
    task_id = labels.get("com.docker.swarm.task.id", "")
    task_name = labels.get("com.docker.swarm.task.name", "")
    if not (service_id and service_name and task_id and task_name):
        logger.info("Dockercloud haproxy is not running in a service in SwarmMode")
        return {}, set()

    nets = haproxy_container.get("NetworkSettings", {}).get("Networks", {})
    net_ids = [network.get("NetworkID", "") for network in nets.values()]

    linked_containers_ids = []
    for net_id in net_ids:
        network_inspect = docker.inspect_network(net_id)
        linked_containers_ids.extend(network_inspect.get("Containers", {}).keys())

    linked_containers = {}
    for linked_containers_id in linked_containers_ids:
        try:
            linked_container = docker.inspect_container(linked_containers_id)
        except Exception as e:
            logger.info("Docker API error: %s" % e)
            continue
        if linked_container.get("Config", {}).get("Labels", {}).get("com.docker.swarm.service.name",
                                                                    "") != service_name:
            linked_containers[linked_containers_id] = linked_container

    links, services = _calc_links(linked_containers)
    return links, services, net_ids


def _calc_links(containers):
    links = {}
    services = set()
    for container_id, container in containers.items():
        container_name = container.get("Name").lstrip("/")
        service_name = container.get("Config", {}).get("Labels", {}).get("com.docker.swarm.service.name", "")
        container_evvvars = get_container_envvars(container)
        endpoints = get_container_endpoints(container, container_name)
        links[container_id] = {"service_name": service_name,
                               "container_envvars": container_evvvars,
                               "container_name": container_name,
                               "endpoints": endpoints,
                               }
        services.add(service_name)
    return links, services


def get_container_endpoints(container, container_name):
    return compose_mode_link_helper.get_container_endpoints(container, container_name)


def get_container_envvars(container):
    return compose_mode_link_helper.get_container_envvars(container)


def get_service_links_str(links):
    return compose_mode_link_helper.get_service_links_str(links)


def get_container_links_str(links):
    return compose_mode_link_helper.get_container_links_str(links)
