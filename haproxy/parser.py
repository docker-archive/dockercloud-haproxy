import os
import re
import urlparse

import config


def parse_extra_bind_settings(extra_bind_settings):
    bind_dict = {}
    if extra_bind_settings:
        settings = re.split(r'(?<!\\),', extra_bind_settings)
        for setting in settings:
            term = setting.split(":", 1)
            if len(term) == 2:
                bind_dict[term[0].strip().replace("\,", ",")] = term[1].strip().replace("\,", ",")
    return bind_dict


class Specs(object):
    def __init__(self, links=None):
        self.envvars = self._parse_envvars(links)
        self.service_aliases = self._parse_service_aliases(links)
        self.details = self._parse_details()
        self.routes = self._parse_routes(links)
        self.vhosts = self._parse_vhosts()
        self.merge_services_with_same_vhost()

    def merge_services_with_same_vhost(self):
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

            for route in self.routes[service_alias]:
                self.routes[services_with_same_vhost[service_alias]].append(route)
            del self.routes[service_alias]

            vhosts = []
            for vhost in self.vhosts:
                if vhost['service_alias'] != service_alias:
                    vhosts.append(vhost)
            self.vhosts = vhosts

    @staticmethod
    def _parse_envvars(links):
        envvars = {}
        if links:
            for link in links.itervalues():
                envvars.update(link["container_envvars"])
        else:
            envvars = os.environ
        return envvars

    def _parse_service_aliases(self, links):
        service_aliases = []
        if links:
            for link in links.itervalues():
                if link["service_name"] not in service_aliases:
                    service_aliases.append(link["service_name"])
        else:

            for key, value in self.envvars.iteritems():
                match = config.SERVICE_ALIAS_MATCH.search(key)
                if match:
                    detailed_match = config.DETAILED_SERVICE_ALIAS_MATCH.search(key)
                    if detailed_match:
                        alias = key[:detailed_match.start()]
                    else:
                        alias = key[:match.start()]

                    if alias not in service_aliases:
                        service_aliases.append(alias)
        return service_aliases

    def _parse_details(self):
        env_parser = EnvParser(self.service_aliases)
        for key, value in self.envvars.iteritems():
            env_parser.parse(key, value)
        details = env_parser.get_details()

        # generate empty details if there is no environment variables set in the application services
        for service_alias in set(self.service_aliases) - set(details.iterkeys()):
            env_parser.parse(service_alias + "_ENV_", "")

        return env_parser.get_details()

    def _parse_routes(self, links):
        return RouteParser.parse(self.details, links)

    def _parse_vhosts(self):
        for service_alias, attr in self.details.iteritems():
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
            self.details[service_alias]["virtual_host"] = parsed_virtual_host

        vhosts = []
        for service_alias, attr in self.details.iteritems():
            virtual_hosts = attr["virtual_host"]

            if virtual_hosts:
                for v in virtual_hosts:
                    vhost = dict(v)
                    vhost["service_alias"] = service_alias
                    vhosts.append(vhost)
        try:
            return sorted(vhosts, key=lambda vhost: self.details[vhost["service_alias"]]["virtual_host_weight"],
                          reverse=True)
        except:
            return vhosts

    def get_details(self):
        return self.details

    def get_routes(self):
        return self.routes

    def get_vhosts(self):
        return self.vhosts

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

    def get_service_aliases(self):
        return self.service_aliases


class RouteParser(object):
    @staticmethod
    def parse(details, links=None):
        if links:
            return RouteParser.parse_remote_routes(details, links)
        else:
            return RouteParser.parse_local_routes(details, os.environ)

    @staticmethod
    def parse_remote_routes(details, links):
        routes = {}
        for link in links.itervalues():
            container_name = link["container_name"]
            service_alias = link["service_name"]
            for endpoint in link["endpoints"].itervalues():
                route = config.BACKEND_MATCH.match(endpoint).groupdict()
                route.update({"container_name": container_name})
                exclude_ports = details.get(service_alias, {}).get("exclude_ports")
                if not exclude_ports or (exclude_ports and route["port"] not in exclude_ports):
                    if service_alias in routes:
                        routes[service_alias].append(route)
                    else:
                        routes[service_alias] = [route]
        return routes

    @staticmethod
    def parse_local_routes(details, envvars):
        routes = {}
        for key, value in envvars.iteritems():
            if not key or not value:
                continue
            match = config.SERVICE_ALIAS_MATCH.search(key)
            if match:
                detailed_match = config.DETAILED_SERVICE_ALIAS_MATCH.search(key)
                if detailed_match:
                    service_alias = key[:detailed_match.start()]
                else:
                    service_alias = key[:match.start()]

                container_name = key[:match.start()]

                be_match = config.BACKEND_MATCH.match(value)
                if be_match:
                    route = config.BACKEND_MATCH.match(value).groupdict()

                    route.update({"container_name": container_name})
                    exclude_ports = details.get(service_alias, {}).get("exclude_ports")
                    if not exclude_ports or (exclude_ports and route["port"] not in exclude_ports):
                        if service_alias in routes:
                            # Avoid add the dulicated route twice(remove the first one, which is inject as the service name
                            for _route in routes[service_alias]:
                                if route['proto'] == _route['proto'] and \
                                                route['port'] == _route['port'] and \
                                                route['addr'] == _route['addr']:
                                    routes[service_alias].remove(_route)
                            routes[service_alias].append(route)
                        else:
                            routes[service_alias] = [route]
        return routes


class EnvParser(object):
    def __init__(self, service_aliases):
        self.service_aliases = service_aliases
        self.details = {}

    def parse(self, key, value):
        for method in self.__class__.__dict__:
            if method.startswith("parse_"):
                match = config.ENV_SERVICE_ALIAS_MATCH.search(key)
                if match:
                    detailed_match = config.ENV_DETAILED_SERVICE_ALIAS_MATCH.search(key)
                    if detailed_match:
                        service_alias = key[:detailed_match.start()]
                    else:
                        service_alias = key[:match.start()]

                    if service_alias in self.service_aliases:
                        attr_name = method[6:]
                        if key.endswith("_ENV_%s" % attr_name.upper()):
                            attr_value = getattr(self, method)(value)
                        else:
                            attr_value = getattr(self, method)(None)

                        if service_alias in self.details:
                            if attr_name in self.details[service_alias]:
                                if attr_value:
                                    self.details[service_alias][attr_name] = attr_value
                            else:
                                self.details[service_alias][attr_name] = attr_value
                        else:
                            self.details[service_alias] = {attr_name: attr_value}

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
            return [x.strip() for x in value.strip().split(",")]
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
            return [p.strip() for p in value.strip().split(",") if p.strip()]
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
            return [p.strip() for p in value.strip().split(",") if p.strip()]
        return []

    @staticmethod
    def parse_extra_settings(value):
        return value
