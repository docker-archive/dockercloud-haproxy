import haproxy.config
from haproxy.parser.base_parser import Specs, EnvParser


class NewLinkSpecs(Specs):
    def __init__(self, links):
        super(self.__class__, self).__init__()
        self.service_aliases = self._parse_service_aliases(links)
        self.details = self._parse_details(self.service_aliases, links)
        self.routes = self._parse_routes(self.details, links)
        self.vhosts = self._parse_vhosts(self.details)
        self._merge_services_with_same_vhost()

    @staticmethod
    def _parse_service_aliases(links):
        service_aliases = []
        for link in links.itervalues():
            if link["service_name"] not in service_aliases:
                service_aliases.append(link["service_name"])
        return service_aliases

    @staticmethod
    def _parse_details(service_aliases, links):
        env_parser = NewLinkEnvParser(service_aliases)
        for link in links.itervalues():
            for envvar in link['container_envvars']:
                env_parser.parse(link['service_name'], envvar['key'], envvar['value'])
        details = env_parser.get_details()
        return details

    @staticmethod
    def _parse_routes(details, links):
        routes = {}
        for link in links.itervalues():
            container_name = link["container_name"]
            service_alias = link["service_name"]
            if service_alias not in routes:
                routes[service_alias] = []
            for endpoint in link["endpoints"].itervalues():
                route = haproxy.config.BACKEND_MATCH.match(endpoint).groupdict()
                route.update({"container_name": container_name})
                exclude_ports = details.get(service_alias, {}).get("exclude_ports", [])
                if not exclude_ports or (exclude_ports and route["port"] not in exclude_ports):
                    if route not in routes[service_alias]:
                        routes[service_alias].append(route)
        return routes


class NewLinkEnvParser(EnvParser):
    def __init__(self, service_aliases):
        super(self.__class__, self).__init__()
        self.attrs = [method[6:] for method in self.__class__.__base__.__dict__ if method.startswith("parse_")]
        for service_aliase in service_aliases:
            self.details[service_aliase] = {}
            for attr in self.attrs:
                self.details[service_aliase][attr] = self.__getattribute__("parse_%s" % attr)("")
        self.service_aliases = service_aliases

    def parse(self, service, key, value):
        key = key.lower()
        if service in self.service_aliases:
            for attr in self.attrs:
                if key == attr and not self.details[service][key]:
                    self.details[service][key] = getattr(self, "parse_%s" % key)(value)
