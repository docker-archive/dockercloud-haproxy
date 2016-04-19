from gevent.pool import Pool

from haproxy.config import SERVICE_NAME_MATCH
from haproxy.utils import get_uuid_from_resource_uri, fetch_remote_obj

LINKED_CONTAINER_CACHE = {}

pool = Pool(size=5)


def get_cloud_links(haproxy_container):
    links = _init_links(haproxy_container.linked_to_container)
    new_added_container_uris = _get_new_added_link_uri(LINKED_CONTAINER_CACHE, links)
    new_added_containers = _get_container_object_from_uri(new_added_container_uris)
    _update_container_cache(LINKED_CONTAINER_CACHE, new_added_container_uris, new_added_containers)
    linked_containers = _get_linked_containers(LINKED_CONTAINER_CACHE, haproxy_container.linked_to_container)
    _update_links(links, linked_containers)
    return links


def _init_links(container_links):
    links = {}
    for link in container_links:
        linked_container_uri = link["to_container"]
        linked_container_name = link["name"].upper().replace("-", "_")
        linked_container_service_name = linked_container_name

        match = SERVICE_NAME_MATCH.match(linked_container_name)
        if match:
            linked_container_service_name = match.group(1)

        links[linked_container_uri] = {
            "container_name": linked_container_name,
            "container_uri": linked_container_uri,
            "service_name": linked_container_service_name,
            "endpoints": link["endpoints"]
        }
    return links


def _get_new_added_link_uri(container_object_cache, links):
    return filter(lambda x: x not in container_object_cache, links)


def _get_container_object_from_uri(container_uris):
    global pool
    container_objects = pool.map(fetch_remote_obj, container_uris)
    return container_objects


def _update_container_cache(cache, new_container_object_uris, new_container_objects):
    for i, container_uri in enumerate(new_container_object_uris):
        cache[container_uri] = new_container_objects[i]


def _update_links(links, linked_containers):
    for linked_container in linked_containers:
        linked_container_uri = linked_container.resource_uri
        linked_container_service_uri = linked_container.service
        links[linked_container_uri]["service_uri"] = linked_container_service_uri
        links[linked_container_uri]["container_envvars"] = linked_container.container_envvars


def _get_linked_containers(cache, container_links):
    linked_containers = [cache[link["to_container"]] for link in container_links]
    return linked_containers


def get_linked_services(haproxy_links):
    linked_services = []
    for link in haproxy_links.itervalues():
        if link["service_uri"] not in linked_services:
            linked_services.append(link["service_uri"])
    return linked_services


def get_service_links_str(haproxy_links):
    return sorted(set(["%s(%s)" % (link.get("service_name"), get_uuid_from_resource_uri(link.get("service_uri", "")))
                       for link in haproxy_links.itervalues()]))


def get_container_links_str(haproxy_links):
    return sorted(
        set(["%s(%s)" % (link.get("container_name"), get_uuid_from_resource_uri(link.get("container_uri", "")))
             for link in haproxy_links.itervalues()]))
