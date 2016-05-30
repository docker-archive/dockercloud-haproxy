import re

from haproxy.config import HEALTH_CHECK, EXTRA_ROUTE_SETTINGS
from haproxy.utils import get_service_attribute


def get_tcp_port_list(details, service_aliases):
    ports = []
    for service_alias in service_aliases:
        tcp_ports = get_service_attribute(details, "tcp_ports", service_alias)
        if tcp_ports and isinstance(tcp_ports, list):
            ports.extend(tcp_ports)
    return ports


def parse_port_string(port, ssl_bind_string):
    enable_ssl = False
    port_num = port
    if port.lower().endswith("/ssl"):
        port_num = port[:-4]
        if ssl_bind_string:
            enable_ssl = True

    return enable_ssl, port_num


def get_tcp_routes(details, routes, port, port_num):
    tcp_routes = []
    routes_added = []
    addresses_added = []
    if port != port_num and port != port_num + "/ssl":
        return tcp_routes, routes_added

    for _service_alias, routes in routes.iteritems():
        tcp_ports = get_service_attribute(details, "tcp_ports", _service_alias)
        if tcp_ports and port in tcp_ports:
            for route in routes:
                if route["port"] == port_num:
                    address = "%s:%s" % (route["addr"], route["port"])
                    if address not in addresses_added:
                        addresses_added.append(address)
                        tcp_route = ["server %s %s" % (route["container_name"], address)]
                        health_check = get_healthcheck_string(details, _service_alias)
                        extra_route_settings = get_extra_route_settings_string(details, _service_alias)
                        route_setting = " ".join([health_check, extra_route_settings]).strip()
                        tcp_route.append(route_setting)
                        tcp_routes.append(" ".join(tcp_route))
                    routes_added.append(route)

    return tcp_routes, routes_added


def get_healthcheck_string(details, service_alias):
    health_check = get_service_attribute(details, "health_check", service_alias)
    health_check = health_check if health_check else HEALTH_CHECK
    return health_check


def get_extra_route_settings_string(details, service_alias):
    extra_route_settings = get_service_attribute(details, "extra_route_settings", service_alias)
    extra_route_settings = extra_route_settings if extra_route_settings else EXTRA_ROUTE_SETTINGS
    return extra_route_settings


def get_service_aliases_given_tcp_port(details, service_aliases, tcp_port):
    services = []
    for service_alias in service_aliases:
        tcp_ports = get_service_attribute(details, "tcp_ports", service_alias)
        if tcp_ports and tcp_port in tcp_ports:
            services.append(service_alias)
    return services


def get_tcp_balance(details):
    balance = get_service_attribute(details, 'balance')
    if balance:
        return ["balance %s" % balance]
    else:
        return []


def get_tcp_options(details, services):
    option_list = []
    for service in services:
        options = get_service_attribute(details, 'option', service)
        if options and type(options) is list:
            for option in options:
                if option not in option_list:
                    option_list.append(option)
    return ["option %s" % option for option in option_list]


def get_tcp_extra_settings(details, services):
    setting_list = []
    for service in services:
        extra_settings = get_service_attribute(details, 'extra_settings', service)
        if extra_settings:
            settings = re.split(r'(?<!\\),', extra_settings)
            for s in settings:
                setting = s.strip().replace("\,", ",")
                if setting and setting not in setting_list:
                    setting_list.append(setting)
    return setting_list
