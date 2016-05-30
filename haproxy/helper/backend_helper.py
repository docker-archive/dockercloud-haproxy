import re

from haproxy.config import HEALTH_CHECK, HTTP_BASIC_AUTH, EXTRA_ROUTE_SETTINGS
from haproxy.utils import get_service_attribute


def get_backend_section(details, routes, vhosts, service_alias, routes_added):
    backend = []

    backend_websocket_setting = get_websocket_setting(vhosts, service_alias)
    backend.extend(backend_websocket_setting)

    backend_settings, is_sticky = get_backend_settings(details, service_alias, HTTP_BASIC_AUTH)
    backend.extend(backend_settings)

    route_health_check = get_route_health_check(details, service_alias, HEALTH_CHECK)
    extra_route_settings = get_extra_route_settings(details, service_alias, EXTRA_ROUTE_SETTINGS)
    route_setting = " ".join([route_health_check, extra_route_settings]).strip()
    backend_routes = get_backend_routes(route_setting, is_sticky, routes, routes_added, service_alias)
    backend.extend(backend_routes)
    return backend


def get_backend_routes(route_setting, is_sticky, routes, routes_added, service_alias):
    backend_routes = []
    for _service_alias, routes in routes.iteritems():
        if not service_alias or _service_alias == service_alias:
            addresses_added = []
            for route in routes:
                # avoid adding those tcp routes adding http backends
                if route in routes_added:
                    continue
                address = "%s:%s" % (route["addr"], route["port"])
                if address not in addresses_added:
                    addresses_added.append(address)
                    backend_route = ["server %s %s" % (route["container_name"], address)]
                    if is_sticky:
                        backend_route.append("cookie %s" % route["container_name"])

                    if route_setting:
                        backend_route.append(route_setting)

                    backend_routes.append(" ".join(backend_route))

    return sorted(backend_routes)


def get_route_health_check(details, service_alias, default_health_check):
    health_check = get_service_attribute(details, "health_check", service_alias)
    health_check = health_check if health_check else default_health_check
    return health_check


def get_extra_route_settings(details, service_alias, default_extra_route_settings):
    extra_route_settings = get_service_attribute(details, "extra_route_settings", service_alias)
    extra_route_settings = extra_route_settings if extra_route_settings else default_extra_route_settings
    return extra_route_settings


def get_websocket_setting(vhosts, service_alias):
    websocket_setting = []
    for v in vhosts:
        if service_alias == v["service_alias"]:
            if v["scheme"].lower() in ["ws", "wss"]:
                websocket_setting.append("option http-server-close")
                break
    return websocket_setting


def get_backend_settings(details, service_alias, basic_auth):
    backend_settings = []

    sticky_setting, is_sticky = get_sticky_setting(details, service_alias)
    backend_settings.extend(sticky_setting)
    backend_settings.extend(get_balance_setting(details, service_alias))
    backend_settings.extend(get_force_ssl_setting(details, service_alias))
    backend_settings.extend(get_http_check_setting(details, service_alias))
    backend_settings.extend(get_gzip_compression_setting(details, service_alias))
    backend_settings.extend(get_hsts_max_age_setting(details, service_alias))
    backend_settings.extend(get_options_setting(details, service_alias))
    backend_settings.extend(get_extra_settings_setting(details, service_alias))
    backend_settings.extend(get_basic_auth_setting(basic_auth))

    return backend_settings, is_sticky


def get_balance_setting(details, service_alias):
    setting = []
    balance = get_service_attribute(details, "balance", service_alias)
    if balance:
        setting.append("balance %s" % balance)
    return setting


def get_sticky_setting(details, service_alias):
    setting = []
    is_sticky = False

    appsession = get_service_attribute(details, "appsession", service_alias)
    if appsession:
        setting.append("appsession %s" % appsession)
        is_sticky = True

    cookie = get_service_attribute(details, "cookie", service_alias)
    if cookie:
        setting.append("cookie %s" % cookie)
        is_sticky = True

    return setting, is_sticky


def get_force_ssl_setting(details, service_alias):
    setting = []
    force_ssl = get_service_attribute(details, "force_ssl", service_alias)
    if force_ssl:
        setting.append("redirect scheme https code 301 if !{ ssl_fc }")
    return setting


def get_http_check_setting(details, service_alias):
    setting = []
    http_check = get_service_attribute(details, "http_check", service_alias)
    if http_check:
        setting.append("option httpchk %s" % http_check)
    return setting


def get_hsts_max_age_setting(details, service_alias):
    setting = []
    hsts_max_age = get_service_attribute(details, "hsts_max_age", service_alias)
    if hsts_max_age:
        setting.append("rspadd Strict-Transport-Security:\ max-age=%s;\ includeSubDomains" % hsts_max_age)
    return setting


def get_gzip_compression_setting(details, service_alias):
    setting = []
    gzip_compression_type = get_service_attribute(details, 'gzip_compression_type', service_alias)
    if gzip_compression_type:
        setting.append("compression algo gzip")
        setting.append("compression type %s" % gzip_compression_type)
    return setting


def get_options_setting(details, service_alias):
    setting = []
    options = get_service_attribute(details, 'option', service_alias)
    if options:
        for option in options:
            setting.append("option %s" % option)
    return setting


def get_extra_settings_setting(details, service_alias):
    setting = []
    extra_settings_str = get_service_attribute(details, 'extra_settings', service_alias)
    if extra_settings_str:
        extra_settings = re.split(r'(?<!\\),', extra_settings_str)
        for extra_setting in extra_settings:
            if extra_setting.strip():
                setting.append(extra_setting.strip().replace("\,", ","))
    return setting


def get_basic_auth_setting(basic_auth):
    setting = []
    if basic_auth:
        setting.append("acl need_auth http_auth(haproxy_userlist)")
        setting.append("http-request auth realm haproxy_basic_auth if !need_auth")
    return setting
