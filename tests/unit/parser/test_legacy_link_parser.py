import unittest

from haproxy.parser.legacy_link_parser import *


class SpecsTestCase(unittest.TestCase):

    def setUp(self):
        self.envvars = {'WORLD_1_ENV_MODE': 'http',
                        'HELLO_1_ENV_MODE': 'http',
                        'HELLO_1_ENV_VIRTUAL_HOST': 'b.com',
                        'WORLD_1_PORT_80_TCP': 'tcp://10.7.0.3:80',
                        'WORLD_1_ENV_VIRTUAL_HOST': 'a.com',
                        'HELLO_1_PORT_80_TCP': 'tcp://10.7.0.1:80'}
        self.service_aliases = ['HELLO', 'WORLD']
        self.details = {'WORLD': {'default_ssl_cert': '', 'ssl_cert': '', 'exclude_ports': [], 'hsts_max_age': None,
                                  'gzip_compression_type': None, 'http_check': None, 'virtual_host_weight': 0,
                                  'health_check': None, 'cookie': None, 'virtual_host': 'a.com', 'force_ssl': None,
                                  'tcp_ports': [], 'balance': None, 'extra_settings': None, 'appsession': None,
                                  'option': [], "extra_route_settings": None},
                        'HELLO': {'default_ssl_cert': '', 'ssl_cert': '', 'exclude_ports': [], 'hsts_max_age': None,
                                  'gzip_compression_type': None, 'http_check': None, 'virtual_host_weight': 0,
                                  'health_check': None, 'cookie': None, 'virtual_host': 'b.com', 'force_ssl': None,
                                  'tcp_ports': [], 'balance': None, 'extra_settings': None, 'appsession': None,
                                  'option': [], "extra_route_settings": None}}
        self.routes = {'WORLD': [{'container_name': 'WORLD_1', 'proto': 'tcp', 'port': '80', 'addr': '10.7.0.3'}],
                       'HELLO': [{'container_name': 'HELLO_1', 'proto': 'tcp', 'port': '80', 'addr': '10.7.0.1'}]}
        self.vhosts = [{'path': '', 'host': 'a.com', 'scheme': 'http', 'port': '80', 'service_alias': 'WORLD'},
                       {'path': '', 'host': 'b.com', 'scheme': 'http', 'port': '80', 'service_alias': 'HELLO'}]

    def test_merge_services_with_same_vhost(self):
        specs = LegacyLinkSpecs()
        specs.details = {"HELLO": {"virtual_host_str": "a.com"},
                         "WORLD": {"virtual_host_str": "a.com"},
                         "HW": {"virtual_host_str": "b.com"}}
        specs.service_aliases = ["HELLO", "WORLD", "HW"]
        specs.routes = {'HW': [{'container_name': 'HW_1', 'proto': 'http', 'port': '80', 'addr': '10.7.0.2'},
                               {'container_name': 'HW_2', 'proto': 'http', 'port': '80', 'addr': '10.7.0.3'}],
                        'HELLO': [{'container_name': 'HELLO_1', 'proto': 'http', 'port': '80', 'addr': '10.7.0.4'},
                                  {'container_name': 'HELLO_2', 'proto': 'http', 'port': '80', 'addr': '10.7.0.5'}],
                        'WORLD': [{'container_name': 'WORLD_1', 'proto': 'http', 'port': '80', 'addr': '10.7.0.6'},
                                  {'container_name': 'WORLD_2', 'proto': 'http', 'port': '80', 'addr': '10.7.0.7'}]}
        specs.vhosts = [{'service_alias': 'HELLO', 'path': '', 'host': 'a.com', 'scheme': 'http', 'port': '80'},
                        {'service_alias': 'WORLD', 'path': '', 'host': 'a.com', 'scheme': 'http', 'port': '80'},
                        {'service_alias': 'HW', 'path': '', 'host': 'b.com', 'scheme': 'http', 'port': '80'}]

        specs._merge_services_with_same_vhost()
        self.assertEqual({'WORLD': {'virtual_host_str': 'a.com'}, 'HW': {'virtual_host_str': 'b.com'}}, specs.details)
        self.assertEqual(["WORLD", "HW"], specs.service_aliases)
        self.assertEqual({'WORLD': [{'addr': '10.7.0.6', 'proto': 'http', 'port': '80', 'container_name': 'WORLD_1'},
                                    {'addr': '10.7.0.7', 'proto': 'http', 'port': '80', 'container_name': 'WORLD_2'},
                                    {'addr': '10.7.0.4', 'proto': 'http', 'port': '80', 'container_name': 'HELLO_1'},
                                    {'addr': '10.7.0.5', 'proto': 'http', 'port': '80', 'container_name': 'HELLO_2'}],
                          'HW': [{'addr': '10.7.0.2', 'proto': 'http', 'port': '80', 'container_name': 'HW_1'},
                                 {'addr': '10.7.0.3', 'proto': 'http', 'port': '80', 'container_name': 'HW_2'}]},
                         specs.routes)
        self.assertEqual([{'path': '', 'host': 'a.com', 'scheme': 'http', 'service_alias': 'WORLD', 'port': '80'},
                          {'path': '', 'host': 'b.com', 'scheme': 'http', 'service_alias': 'HW', 'port': '80'}],
                         specs.vhosts)

    def test_parse_service_aliases(self):
        specs = LegacyLinkSpecs()
        self.assertEqual([], specs._parse_service_aliases({}))

        specs.envvars = self.envvars
        self.assertEqual(self.service_aliases, specs._parse_service_aliases(self.envvars))

    def test_parse_details(self):
        specs = LegacyLinkSpecs()
        empty_details = {'WORLD': {'default_ssl_cert': '', 'ssl_cert': '', 'exclude_ports': [], 'hsts_max_age': None,
                                   'gzip_compression_type': None, 'http_check': None, 'virtual_host_weight': 0,
                                   'health_check': None, 'cookie': None, 'virtual_host': None, 'force_ssl': None,
                                   'tcp_ports': [], 'balance': None, 'extra_settings': None, 'appsession': None,
                                   'option': [], "extra_route_settings": None},
                         'HELLO': {'default_ssl_cert': '', 'ssl_cert': '', 'exclude_ports': [], 'hsts_max_age': None,
                                   'gzip_compression_type': None, 'http_check': None, 'virtual_host_weight': 0,
                                   'health_check': None, 'cookie': None, 'virtual_host': None, 'force_ssl': None,
                                   'tcp_ports': [], 'balance': None, 'extra_settings': None, 'appsession': None,
                                   'option': [], "extra_route_settings": None}}
        self.assertEqual({}, specs._parse_details([], {}))
        self.assertEqual(empty_details, specs._parse_details(self.service_aliases, {}))
        self.assertEqual({}, specs._parse_details([], self.envvars))

        specs.envvars = self.envvars
        specs.service_aliases = self.service_aliases
        self.assertEqual(self.details, specs._parse_details(self.service_aliases, self.envvars))

    def test_parse_routes(self):
        specs = LegacyLinkSpecs()
        self.assertEqual({}, specs._parse_routes({}, {}))

        specs.details = self.details
        self.assertEqual(self.routes, specs._parse_routes(self.details, self.envvars))

        envvars = {'WORLD_1_ENV_MODE': 'http',
                   'HELLO_1_ENV_MODE': 'http',
                   'HELLO_1_ENV_VIRTUAL_HOST': 'b.com',
                   'WORLD_1_PORT_80_TCP': 'tcp://10.7.0.3:80',
                   'WORLD_1_ENV_VIRTUAL_HOST': 'a.com',
                   'HELLO_1_PORT_80_TCP': 'tcp://10.7.0.1:80',
                   'DUPLICATED_PORT_80_TCP': 'tcp://10.7.0.1:80'}
        details = {'WORLD': {'default_ssl_cert': '', 'ssl_cert': '', 'exclude_ports': [], 'hsts_max_age': None,
                             'gzip_compression_type': None, 'http_check': None, 'virtual_host_weight': 0,
                             'health_check': None, 'cookie': None, 'virtual_host': 'a.com', 'force_ssl': None,
                             'tcp_ports': [], 'balance': None, 'extra_settings': None, 'appsession': None,
                             'option': [], "extra_route_settings": None},
                   'HELLO': {'default_ssl_cert': '', 'ssl_cert': '', 'exclude_ports': [], 'hsts_max_age': None,
                             'gzip_compression_type': None, 'http_check': None, 'virtual_host_weight': 0,
                             'health_check': None, 'cookie': None, 'virtual_host': 'b.com', 'force_ssl': None,
                             'tcp_ports': [], 'balance': None, 'extra_settings': None, 'appsession': None,
                             'option': [], "extra_route_settings": None},
                   'DUPLICATED': {'default_ssl_cert': '', 'ssl_cert': '', 'exclude_ports': [], 'hsts_max_age': None,
                                  'gzip_compression_type': None, 'http_check': None, 'virtual_host_weight': 0,
                                  'health_check': None, 'cookie': None, 'virtual_host': 'b.com', 'force_ssl': None,
                                  'tcp_ports': [], 'balance': None, 'extra_settings': None, 'appsession': None,
                                  'option': [], "extra_route_settings": None}
                   }

        routes = {'WORLD': [{'container_name': 'WORLD_1', 'proto': 'tcp', 'port': '80', 'addr': '10.7.0.3'}],
                  'HELLO': [{'container_name': 'HELLO_1', 'proto': 'tcp', 'port': '80', 'addr': '10.7.0.1',}],
                  'DUPLICATED': [{'container_name': 'DUPLICATED', 'proto': 'tcp', 'port': '80', 'addr': '10.7.0.1'}]}
        self.assertEqual(routes, specs._parse_routes(details, envvars))


class LegacyLinkEnvParserTestCase(unittest.TestCase):
    def test_parse(self):
        env = LegacyLinkEnvParser(["HELLO", "WORLD"])

        env.parse("HELLO_ENV_NOT_DEFINED", "n/a")
        self.assertTrue("not_defined" not in env.details["HELLO"])

        env.parse("HW_ENV_DEFAULT_SSL_CERT", "cert")
        self.assertTrue("HW" not in env.details)
        env.parse("HELLO_ENV_DEFAULT_SSL_CERT", "cert")
        self.assertEqual("cert", env.details["HELLO"]["default_ssl_cert"])
        env.parse("WORLD_ENV_DEFAULT_SSL_CERT", "cert\\ncert")
        self.assertEqual("cert\ncert", env.details["WORLD"]["default_ssl_cert"])

        env.parse("HW_ENV_SSL_CERT", "cert")
        self.assertTrue("HW" not in env.details)
        env.parse("HELLO_ENV_SSL_CERT", "cert")
        self.assertEqual("cert", env.details["HELLO"]["ssl_cert"])
        env.parse("WORLD_ENV_SSL_CERT", "cert\\ncert")
        self.assertEqual("cert\ncert", env.details["WORLD"]["ssl_cert"])

        env.parse("HELLO_ENV_EXCLUDE_PORTS", "80")
        self.assertEqual(["80"], env.details["HELLO"]["exclude_ports"])
        env.parse("WORLD_ENV_EXCLUDE_PORTS", "80, 88 ,8080")
        self.assertEqual(["80", "88", "8080"], env.details["WORLD"]["exclude_ports"])

        env.parse("HELLO_1_ENV_VIRTUAL_HOST", "a.com")
        self.assertEqual("a.com", env.details["HELLO"]["virtual_host"])

        env.parse("HELLO_2_ENV_FORCE_SSL", "True")
        self.assertEqual("True", env.details["HELLO"]["force_ssl"])

        env.parse("HELLO_2_ENV_APPSESSION", "session")
        self.assertEqual("session", env.details["HELLO"]["appsession"])

        env.parse("HELLO_2_ENV_BALANCE", "source")
        self.assertEqual("source", env.details["HELLO"]["balance"])

        env.parse("HELLO_2_ENV_COOKIE", "cookie")
        self.assertEqual("cookie", env.details["HELLO"]["cookie"])

        env.parse("HELLO_2_ENV_TCP_PORTS", "9000, 22/ssl , 80")
        self.assertEqual(["9000", "22/ssl", "80"], env.details["HELLO"]["tcp_ports"])

        env.parse("HELLO_2_ENV_HEALTH_CHECK", "check")
        self.assertEqual("check", env.details["HELLO"]["health_check"])

        env.parse("HELLO_2_ENV_HTTP_CHECK", "check")
        self.assertEqual("check", env.details["HELLO"]["http_check"])

        env.parse("HELLO_ENV_VIRTUAL_HOST_WEIGHT", "3")
        self.assertEqual(3, env.details["HELLO"]["virtual_host_weight"])
        env.parse("WORLD_ENV_VIRTUAL_HOST_WEIGHT", "a")
        self.assertEqual(0, env.details["WORLD"]["virtual_host_weight"])

        env.parse("HELLO_2_ENV_HSTS_MAX_AGE", "1m")
        self.assertEqual("1m", env.details["HELLO"]["hsts_max_age"])

        env.parse("HELLO_2_ENV_GZIP_COMPRESSION_TYPE", "gzip")
        self.assertEqual("gzip", env.details["HELLO"]["gzip_compression_type"])

        env.parse("HELLO_2_ENV_OPTION", "opt1, opt2 ,opt3")
        self.assertEqual(["opt1", "opt2", "opt3"], env.details["HELLO"]["option"])

        env.parse("HELLO_2_ENV_EXTRA_SETTINGS", "settings")
        self.assertEqual("settings", env.details["HELLO"]["extra_settings"])
