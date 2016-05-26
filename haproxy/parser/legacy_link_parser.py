import os

import haproxy.config
from haproxy.parser.base_parser import EnvParser, Specs


class LegacyLinkSpecs(Specs):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.envvars = os.environ
        self.service_aliases = self._parse_service_aliases(self.envvars)
        self.details = self._parse_details(self.service_aliases, self.envvars)
        self.routes = self._parse_routes(self.details, self.envvars)
        self.vhosts = self._parse_vhosts(self.details)
        self._merge_services_with_same_vhost()

    @staticmethod
    def _parse_service_aliases(envvars):
        service_aliases = []
        for key, value in envvars.iteritems():
            match = haproxy.config.SERVICE_ALIAS_MATCH.search(key)
            if match:
                detailed_match = haproxy.config.DETAILED_SERVICE_ALIAS_MATCH.search(key)
                if detailed_match:
                    alias = key[:detailed_match.start()]
                else:
                    alias = key[:match.start()]

                if alias not in service_aliases:
                    service_aliases.append(alias)
        return service_aliases

    @staticmethod
    def _parse_details(service_aliases, envvars):
        env_parser = LegacyLinkEnvParser(service_aliases)
        for key, value in envvars.iteritems():
            env_parser.parse(key, value)
        details = env_parser.get_details()

        # generate empty details if there is no environment variables set in the application services
        for service_alias in set(service_aliases) - set(details.iterkeys()):
            env_parser.parse(service_alias + "_ENV_", "")

        return env_parser.get_details()

    @staticmethod
    def _parse_routes(details, envvars):
        routes = {}
        for key, value in envvars.iteritems():
            if not key or not value:
                continue
            match = haproxy.config.SERVICE_ALIAS_MATCH.search(key)
            if match:
                detailed_match = haproxy.config.DETAILED_SERVICE_ALIAS_MATCH.search(key)
                if detailed_match:
                    service_alias = key[:detailed_match.start()]
                else:
                    service_alias = key[:match.start()]

                container_name = key[:match.start()]

                be_match = haproxy.config.BACKEND_MATCH.match(value)
                if be_match:
                    route = haproxy.config.BACKEND_MATCH.match(value).groupdict()

                    route.update({"container_name": container_name})
                    exclude_ports = details.get(service_alias, {}).get("exclude_ports")
                    if not exclude_ports or (exclude_ports and route["port"] not in exclude_ports):
                        if service_alias in routes:
                            routes[service_alias].append(route)
                        else:
                            routes[service_alias] = [route]
        return routes


class LegacyLinkEnvParser(EnvParser):
    def __init__(self, service_aliases):
        super(self.__class__, self).__init__()
        self.service_aliases = service_aliases

    def parse(self, key, value):
        for method in self.__class__.__base__.__dict__:
            if method.startswith("parse_"):
                match = haproxy.config.ENV_SERVICE_ALIAS_MATCH.search(key)
                if match:
                    detailed_match = haproxy.config.ENV_DETAILED_SERVICE_ALIAS_MATCH.search(key)
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
