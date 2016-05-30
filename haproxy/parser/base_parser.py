import urlparse


class Specs(object):
    def __init__(self):
        self.service_aliases = []
        self.details = {}
        self.routes = {}
        self.vhosts = []

    def _merge_services_with_same_vhost(self):
        services_with_same_vhost = {}
        unique_vhost = {}

        for service_alias, detail in self.details.iteritems():
            vhost_str = detail['virtual_host_str']
            if vhost_str:
                if vhost_str in unique_vhost:
                    services_with_same_vhost[service_alias] = unique_vhost[vhost_str]
                else:
                    unique_vhost[vhost_str] = service_alias

        for service_alias in services_with_same_vhost:
            self.service_aliases.remove(service_alias)
            del self.details[service_alias]

            if service_alias in self.routes:
                for route in self.routes[service_alias]:
                    if service_alias in services_with_same_vhost and \
                                    services_with_same_vhost[service_alias] in self.routes:
                        self.routes[services_with_same_vhost[service_alias]].append(route)
                del self.routes[service_alias]

            vhosts = []
            for vhost in self.vhosts:
                if vhost['service_alias'] != service_alias:
                    vhosts.append(vhost)
            self.vhosts = vhosts

    @staticmethod
    def _parse_vhosts(details):
        for service_alias, attr in details.iteritems():
            virtual_host_str = attr["virtual_host_str"] = attr["virtual_host"]

            parsed_virtual_host = []
            if virtual_host_str:
                for h in [h.strip() for h in virtual_host_str.strip().split(",")]:
                    pr = urlparse.urlparse(h)
                    if not pr.netloc:
                        pr = urlparse.urlparse("http://%s" % h)
                    port = '443' if pr.scheme.lower() in ['https', 'wss'] else "80"
                    host = pr.netloc
                    if ":" in pr.netloc:
                        host_port = pr.netloc.split(":")
                        host = host_port[0]
                        port = host_port[1]
                    parsed_virtual_host.append({"scheme": pr.scheme,
                                                "host": host,
                                                "port": port,
                                                "path": pr.path})
            details[service_alias]["virtual_host"] = parsed_virtual_host

        vhosts = []
        for service_alias, attr in details.iteritems():
            virtual_hosts = attr["virtual_host"]

            if virtual_hosts:
                for v in virtual_hosts:
                    vhost = dict(v)
                    vhost["service_alias"] = service_alias
                    vhosts.append(vhost)
        try:
            return sorted(vhosts, key=lambda vhost: details[vhost["service_alias"]]["virtual_host_weight"],
                          reverse=True)
        except:
            return

    def get_details(self):
        return self.details

    def get_routes(self):
        return self.routes

    def get_vhosts(self):
        return self.vhosts

    def get_service_aliases(self):
        return self.service_aliases

    def get_default_ssl_cert(self):
        if not hasattr(self, "default_ssl_cert"):
            self.default_ssl_cert = filter(lambda x: x,
                                           [attr["default_ssl_cert"] for attr in self.details.itervalues() if
                                            "default_ssl_cert" in attr])
        return self.default_ssl_cert

    def get_ssl_cert(self):
        if not hasattr(self, "ssl_cert"):
            self.ssl_cert = filter(lambda x: x, [attr["ssl_cert"] for attr in self.details.itervalues() if
                                                 "ssl_cert" in attr])
        return self.ssl_cert


class EnvParser(object):
    def __init__(self):
        self.details = {}

    def get_details(self):
        return self.details

    @staticmethod
    def parse_default_ssl_cert(value):
        if value:
            return value.replace(r'\n', '\n')
        return ""

    @staticmethod
    def parse_ssl_cert(value):
        return EnvParser.parse_default_ssl_cert(value)

    @staticmethod
    def parse_exclude_ports(value):
        # '3306, 8080' => ['3306', '8080']
        if value:
            return [x.strip() for x in value.strip().split(",") if x.strip()]
        return []

    @staticmethod
    def parse_virtual_host(value):
        return value

    @staticmethod
    def parse_force_ssl(value):
        return value

    @staticmethod
    def parse_appsession(value):
        return value

    @staticmethod
    def parse_balance(value):
        return value

    @staticmethod
    def parse_cookie(value):
        return value

    @staticmethod
    def parse_tcp_ports(value):
        # '9000, 22/ssl_bind_string' => ['9000', '22/ssl_bind_string']
        if value:
            return [x.strip() for x in value.strip().split(",") if x.strip()]
        return []

    @staticmethod
    def parse_health_check(value):
        return value

    @staticmethod
    def parse_http_check(value):
        return value

    @staticmethod
    def parse_virtual_host_weight(value):
        try:
            return int(value)
        except:
            return 0

    @staticmethod
    def parse_hsts_max_age(value):
        return value

    @staticmethod
    def parse_gzip_compression_type(value):
        return value

    @staticmethod
    def parse_option(value):
        if value:
            return [x.strip() for x in value.strip().split(",") if x.strip()]
        return []

    @staticmethod
    def parse_extra_settings(value):
        return value

    @staticmethod
    def parse_extra_route_settings(value):
        return value