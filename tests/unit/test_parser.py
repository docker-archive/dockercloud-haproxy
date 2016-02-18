import copy
import unittest

from haproxy.parser import *


class ParseExtraBindSettings(unittest.TestCase):
    def test_parse_extra_bind_settings(self):
        self.assertEqual({}, parse_extra_bind_settings(""))
        self.assertEqual({"80": "name http"}, parse_extra_bind_settings("80:name http"))
        self.assertEqual({"80": "name  http"}, parse_extra_bind_settings(" 80 : name  http  "))
        self.assertEqual({"80": "name http", "443": "accept-proxy"},
                         parse_extra_bind_settings(" 443:accept-proxy  , 80:name http "))
        self.assertEqual({"80": "name, http", "443": "accept,-proxy"},
                         parse_extra_bind_settings(" 443:accept\,-proxy, 80:name\, http "))


class SpecsTestCase(unittest.TestCase):
    def setUp(self):
        self.links = {'/api/app/v1/container/418768e3-530c-4e8f-8ba9-9ae27f72768d/':
                          {'service_name': 'HELLO',
                           'container_uri': '/api/app/v1/container/418768e3-530c-4e8f-8ba9-9ae27f72768d/',
                           'container_envvars': {
                               'HELLO_1_ENV_VIRTUAL_HOST': 'b.com',
                               'HELLO_1_ENV_MODE': 'http',
                               'HELLO_1_PORT_80_TCP': "tcp://10.7.0.1:80"},
                           'service_uri': '/api/app/v1/service/bc091010-0054-4cc6-9038-73ea1efc5b99/',
                           'container_name': 'HELLO_1',
                           'endpoints': {
                               '80/tcp': 'tcp://10.7.0.1:80'}},
                      '/api/app/v1/container/af5cdd7b-9af8-49d2-a3b2-308dbc187dd8/':
                          {'service_name': 'WORLD',
                           'container_uri': '/api/app/v1/container/af5cdd7b-9af8-49d2-a3b2-308dbc187dd8/',
                           'container_envvars': {
                               'WORLD_1_ENV_MODE': 'http',
                               'WORLD_1_ENV_VIRTUAL_HOST': 'a.com',
                               'WORLD_1_PORT_80_TCP': "tcp://10.7.0.3:80"},
                           'service_uri': '/api/app/v1/service/0d12900d-2ae8-4244-a9c0-48466347c08a/',
                           'container_name': 'WORLD_1',
                           'endpoints': {
                               '80/tcp': 'tcp://10.7.0.3:80'}}}
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
                                  'option': []},
                        'HELLO': {'default_ssl_cert': '', 'ssl_cert': '', 'exclude_ports': [], 'hsts_max_age': None,
                                  'gzip_compression_type': None, 'http_check': None, 'virtual_host_weight': 0,
                                  'health_check': None, 'cookie': None, 'virtual_host': 'b.com', 'force_ssl': None,
                                  'tcp_ports': [], 'balance': None, 'extra_settings': None, 'appsession': None,
                                  'option': []}}
        self.routes = {'WORLD': [{'container_name': 'WORLD_1', 'proto': 'tcp', 'port': '80', 'addr': '10.7.0.3'}],
                       'HELLO': [{'container_name': 'HELLO_1', 'proto': 'tcp', 'port': '80', 'addr': '10.7.0.1'}]}
        self.vhosts = [{'path': '', 'host': 'a.com', 'scheme': 'http', 'port': '80', 'service_alias': 'WORLD'},
                       {'path': '', 'host': 'b.com', 'scheme': 'http', 'port': '80', 'service_alias': 'HELLO'}]
        self.updated_details = {
            'WORLD': {'default_ssl_cert': '', 'ssl_cert': '', 'virtual_host_weight': 0, 'hsts_max_age': None,
                      'gzip_compression_type': None, 'http_check': None, 'health_check': None, 'cookie': None,
                      'virtual_host': [{'path': '', 'host': 'a.com', 'scheme': 'http', 'port': '80'}],
                      'exclude_ports': [], 'force_ssl': None, 'tcp_ports': [], 'balance': None, 'extra_settings': None,
                      'appsession': None, 'virtual_host_str': 'a.com', 'option': []},
            'HELLO': {'default_ssl_cert': '', 'ssl_cert': '', 'virtual_host_weight': 0, 'hsts_max_age': None,
                      'gzip_compression_type': None, 'http_check': None, 'health_check': None, 'cookie': None,
                      'virtual_host': [{'path': '', 'host': 'b.com', 'scheme': 'http', 'port': '80'}],
                      'exclude_ports': [], 'force_ssl': None, 'tcp_ports': [], 'balance': None, 'extra_settings': None,
                      'appsession': None, 'virtual_host_str': 'b.com', 'option': []}}

    def test_merge_services_with_same_vhost(self):
        specs = Specs()
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

        specs.merge_services_with_same_vhost()
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

    def test_parse_envvars(self):
        self.assertEqual(os.environ, Specs()._parse_envvars(None))

        self.assertEqual(self.envvars, Specs()._parse_envvars(self.links))

    def test_parse_service_aliases(self):
        specs = Specs()
        self.assertEqual([], specs._parse_service_aliases(None))

        specs.envvars = self.envvars
        self.assertEqual(self.service_aliases, specs._parse_service_aliases(None))

        self.assertEqual(self.service_aliases, Specs()._parse_service_aliases(self.links))

    def test_parse_details(self):
        specs = Specs()
        self.assertEqual({}, specs._parse_details())

        specs.envvars = self.envvars
        specs.service_aliases = self.service_aliases
        self.assertEqual(self.details, specs._parse_details())

    def test_parse_routes(self):
        specs = Specs()
        self.assertEqual({}, specs._parse_routes(None))

        specs.details = self.details
        self.assertEqual(self.routes, specs._parse_routes(self.links))

    def test_parse_vhost(self):
        specs = Specs()
        self.assertEqual([], specs._parse_vhosts())

        specs.details = copy.deepcopy(self.details)
        self.assertEqual(self.vhosts, specs._parse_vhosts())
        self.assertEqual(self.updated_details, specs.details)

    def test_get_default_ssl_cert(self):
        specs = Specs()
        self.assertEqual([], specs.get_default_ssl_cert())

        specs = Specs()
        specs.default_ssl_cert = ["cert"]
        self.assertEqual(["cert"], specs.get_default_ssl_cert())

        specs = Specs()
        specs.details = {'A': {"default_ssl_cert": "certA"},
                         'B': {"default_ssl_cert": "certB"},
                         'C': {}}
        self.assertEqual(["certA", "certB"], specs.get_default_ssl_cert())

    def test_get_ssl_cert(self):
        specs = Specs()
        self.assertEqual([], specs.get_ssl_cert())

        specs = Specs()
        specs.ssl_cert = ["cert"]
        self.assertEqual(["cert"], specs.get_ssl_cert())

        specs = Specs()
        specs.details = {'A': {"ssl_cert": "certA"},
                         'B': {"ssl_cert": "certB"},
                         'C': {}}
        self.assertEqual(["certA", "certB"], specs.get_ssl_cert())


class TestRouteParser(unittest.TestCase):
    def setUp(self):
        self.links = {'/api/app/v1/container/418768e3-530c-4e8f-8ba9-9ae27f72768d/':
                          {'service_name': 'HELLO',
                           'container_uri': '/api/app/v1/container/418768e3-530c-4e8f-8ba9-9ae27f72768d/',
                           'container_envvars': {
                               'HELLO_1_ENV_VIRTUAL_HOST': 'b.com',
                               'HELLO_1_ENV_MODE': 'http',
                               'HELLO_1_PORT_80_TCP': "tcp://10.7.0.1:80"},
                           'service_uri': '/api/app/v1/service/bc091010-0054-4cc6-9038-73ea1efc5b99/',
                           'container_name': 'HELLO_1',
                           'endpoints': {
                               '80/tcp': 'tcp://10.7.0.1:80'}},
                      '/api/app/v1/container/af5cdd7b-9af8-49d2-a3b2-308dbc187dd8/':
                          {'service_name': 'WORLD',
                           'container_uri': '/api/app/v1/container/af5cdd7b-9af8-49d2-a3b2-308dbc187dd8/',
                           'container_envvars': {
                               'WORLD_1_ENV_MODE': 'http',
                               'WORLD_1_ENV_VIRTUAL_HOST': 'a.com',
                               'WORLD_1_PORT_80_TCP': "tcp://10.7.0.3:80"},
                           'service_uri': '/api/app/v1/service/0d12900d-2ae8-4244-a9c0-48466347c08a/',
                           'container_name': 'WORLD_1',
                           'endpoints': {
                               '80/tcp': 'tcp://10.7.0.3:80'}}}
        self.envvars = {'WORLD_1_ENV_MODE': 'http',
                        'HELLO_1_ENV_MODE': 'http',
                        'HELLO_1_ENV_VIRTUAL_HOST': 'b.com',
                        'WORLD_1_PORT_80_TCP': 'tcp://10.7.0.3:80',
                        'WORLD_1_ENV_VIRTUAL_HOST': 'a.com',
                        'HELLO_1_PORT_80_TCP': 'tcp://10.7.0.1:80'}
        self.details = {
            'WORLD': {'default_ssl_cert': '', 'ssl_cert': '', 'virtual_host_weight': 0, 'hsts_max_age': None,
                      'gzip_compression_type': None, 'http_check': None, 'health_check': None, 'cookie': None,
                      'virtual_host': [{'path': '', 'host': 'a.com', 'scheme': 'http', 'port': '80'}],
                      'exclude_ports': [], 'force_ssl': None, 'tcp_ports': [], 'balance': None, 'extra_settings': None,
                      'appsession': None, 'virtual_host_str': 'a.com', 'option': []},
            'HELLO': {'default_ssl_cert': '', 'ssl_cert': '', 'virtual_host_weight': 0, 'hsts_max_age': None,
                      'gzip_compression_type': None, 'http_check': None, 'health_check': None, 'cookie': None,
                      'virtual_host': [{'path': '', 'host': 'b.com', 'scheme': 'http', 'port': '80'}],
                      'exclude_ports': [], 'force_ssl': None, 'tcp_ports': [], 'balance': None, 'extra_settings': None,
                      'appsession': None, 'virtual_host_str': 'b.com', 'option': []}}
        self.routes = {'WORLD': [{'container_name': 'WORLD_1', 'proto': 'tcp', 'port': '80', 'addr': '10.7.0.3'}],
                       'HELLO': [{'container_name': 'HELLO_1', 'proto': 'tcp', 'port': '80', 'addr': '10.7.0.1'}]}

    def test_parse_remote_routes(self):
        self.assertEqual(self.routes, RouteParser.parse_remote_routes(self.details, self.links))

    def test_parse_local_routes(self):
        self.assertEqual(self.routes, RouteParser.parse_local_routes(self.details, self.envvars))


class EnvParserTestCase(unittest.TestCase):
    def test_parse(self):
        env = EnvParser(["HELLO", "WORLD"])

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