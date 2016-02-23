from collections import OrderedDict

from haproxy.config import EXTRA_BIND_SETTINGS, MONITOR_URI, MONITOR_PORT, MAXCONN


def check_require_default_route(routes, routes_added):
    require_default_route = False
    all_routes = []
    for route_list in routes.itervalues():
        all_routes.extend(route_list)
    if len(routes_added) < len(all_routes):
        require_default_route = True

    return require_default_route


def config_frontend_with_virtual_host(vhosts, ssl_bind_string):
    monitor_uri_configured = False
    cfg = OrderedDict()
    frontend_dict = {}
    rule_counter = 0

    for vhost in vhosts:
        rule_counter += 1
        port = vhost["port"]

        # initialize bind clause for each port
        if port not in frontend_dict:
            frontend_section, _monitor_uri_configured = config_common_part(port, ssl_bind_string, vhosts)
            if _monitor_uri_configured:
                monitor_uri_configured = _monitor_uri_configured
        else:
            frontend_section = frontend_dict[port]

        acl_rule = []
        host_rules = calculate_host_rules(port, rule_counter, vhost["host"].strip("/"))
        path_rules = calculate_path_rules(vhost["path"].strip(), rule_counter)
        acl_rule.extend(host_rules)
        acl_rule.extend(path_rules)

        acl_condition = calculate_acl_condition(host_rules, path_rules, rule_counter, vhost)

        if acl_condition:
            use_backend = "use_backend SERVICE_%s if %s" % (vhost["service_alias"], acl_condition)
            acl_rule.append(use_backend)
            frontend_section.extend(acl_rule)

        frontend_dict[port] = frontend_section
    for port, frontend_section in frontend_dict.iteritems():
        cfg["frontend port_%s" % port] = frontend_section
    return cfg, monitor_uri_configured


def calculate_acl_condition(host_rules, path_rules, rule_counter, vhost):
    if vhost["scheme"].lower() in ["ws", "wss"]:
        acl_condition = "is_websocket"
    else:
        acl_condition = ""
    if path_rules:
        acl_condition = " ".join([acl_condition, "path_rule_%d" % rule_counter])
    if host_rules:
        acl_condition_1 = ("%s host_rule_%d" % (acl_condition, rule_counter)).strip()
        acl_condition_2 = ("%s host_rule_%d_port" % (acl_condition, rule_counter)).strip()
        acl_condition = " or ".join([acl_condition_1, acl_condition_2])
    return acl_condition.strip()


def calculate_host_rules(port, rule_counter, host):
    host_rules = []
    if "*" in host:
        host_rules.append("acl host_rule_%d hdr_reg(host) -i ^%s$" % (
            rule_counter, host.replace(".", "\.").replace("*", ".*")))
        host_rules.append("acl host_rule_%d_port hdr_reg(host) -i ^%s:%s$" % (
            rule_counter, host.replace(".", "\.").replace("*", ".*"), port))
    elif host:
        host_rules.append("acl host_rule_%d hdr(host) -i %s" % (rule_counter, host))
        host_rules.append("acl host_rule_%d_port hdr(host) -i %s:%s" % (rule_counter, host, port))
    return host_rules


def calculate_path_rules(path, rule_counter):
    path_rules = []
    if "*" in path:
        path_rules.append(
            "acl path_rule_%d path_reg -i ^%s$" % (
                rule_counter, path.replace(".", "\.").replace("*", ".*")))
    elif path:
        path_rules.append("acl path_rule_%d path -i %s" % (rule_counter, path))
    return path_rules


def config_common_part(port, ssl_bind_string, vhosts):
    monitor_uri_configured = False
    frontend_section = []
    bind_string, ssl = get_bind_string(port, ssl_bind_string, vhosts)
    frontend_section.append("bind :%s" % bind_string)
    if ssl:
        frontend_section.append("reqadd X-Forwarded-Proto:\ https")

    # add websocket acl rule
    frontend_section.append("acl is_websocket hdr(Upgrade) -i WebSocket")

    # add monitor uri
    if port == MONITOR_PORT and MONITOR_URI:
        frontend_section.append("monitor-uri %s" % MONITOR_URI)
        monitor_uri_configured = True
    return frontend_section, monitor_uri_configured


def get_bind_string(port, ssl_bind_string, vhosts):
    ssl = False
    for v in vhosts:
        if v["port"] == port:
            scheme = v["scheme"].lower()
            if scheme in ["https", "wss"] and ssl_bind_string:
                ssl = True
                break
    bind = " ".join([port, EXTRA_BIND_SETTINGS.get(port, "")])
    if ssl:
        bind = " ".join([bind.strip(), ssl_bind_string])
    return bind.strip(), ssl


def config_default_frontend(ssl_bind_string):
    cfg = OrderedDict()
    monitor_uri_configured = False
    frontend = [("bind :80 %s" % EXTRA_BIND_SETTINGS.get('80', "")).strip()]
    if ssl_bind_string:
        frontend.append(
            ("bind :443 %s %s" % (ssl_bind_string, EXTRA_BIND_SETTINGS.get('443', ""))).strip())
        frontend.append("reqadd X-Forwarded-Proto:\ https")

    if MONITOR_URI and (MONITOR_PORT == '80' or MONITOR_PORT == '443'):
        frontend.append("monitor-uri %s" % MONITOR_URI)
        monitor_uri_configured = True

    frontend.append("maxconn %s" % MAXCONN)
    frontend.append("default_backend default_service")
    cfg["frontend default_frontend"] = frontend

    return cfg, monitor_uri_configured


def config_monitor_frontend(monitor_uri_configured):
    cfg = OrderedDict()
    if not monitor_uri_configured and MONITOR_PORT and MONITOR_URI:
        cfg["frontend monitor"] = ["bind :%s" % MONITOR_PORT,
                                   "monitor-uri %s" % MONITOR_URI]
    return cfg
