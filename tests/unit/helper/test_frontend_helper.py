import unittest

import mock

from haproxy.helper import frontend_helper
from haproxy.helper.frontend_helper import *


class FrontendHelperTestCase(unittest.TestCase):
    def setUp(self):
        self.monitor_port = frontend_helper.MONITOR_PORT
        self.monitor_uri = frontend_helper.MONITOR_URI
        self.extra_bind_settings = frontend_helper.EXTRA_BIND_SETTINGS
        self.maxconn = frontend_helper.MAXCONN
        frontend_helper.MONITOR_PORT = "9999"
        frontend_helper.MONITOR_URI = "/ping"
        frontend_helper.EXTRA_BIND_SETTINGS = {"8888": "name http", "4443": "accept-proxy"}
        frontend_helper.MAXCONN = "55555"
        frontend_helper.EXTRA_FRONTEND_SETTINGS = {}
        frontend_helper.SKIP_FORWARDED_PROTO = None

    def tearDown(self):
        frontend_helper.MONITOR_PORT = self.monitor_port
        frontend_helper.MONITOR_URI = self.monitor_uri
        frontend_helper.EXTRA_BIND_SETTINGS = self.extra_bind_settings
        frontend_helper.MAXCONN = self.maxconn
        frontend_helper.EXTRA_FRONTEND_SETTINGS = {}
        frontend_helper.SKIP_FORWARDED_PROTO = None

    def test_config_frontend_with_virtual_host_without_monitoring_uri_added(self):
        vhosts = [{'service_alias': 'web-a', 'path': '', 'host': 'a.com', 'scheme': 'http', 'port': '80'}]
        cfg, monitor_uri_configured = config_frontend_with_virtual_host(vhosts, "ssl crt /certs/")
        result = OrderedDict([('frontend port_80', ['bind :80',
                                                    'reqadd X-Forwarded-Proto:\\ http',
                                                    'maxconn 55555',
                                                    'acl is_websocket hdr(Upgrade) -i WebSocket',
                                                    'acl host_rule_1 hdr(host) -i a.com',
                                                    'acl host_rule_1_port hdr(host) -i a.com:80',
                                                    'use_backend SERVICE_web-a if host_rule_1 or host_rule_1_port'])])
        self.assertEqual(result, cfg)
        self.assertFalse(monitor_uri_configured)

    def test_config_frontend_with_virtual_host_with_path_rules(self):
        vhosts = [{'service_alias': 'web-a', 'path': '/path/*', 'host': '*', 'scheme': 'http', 'port': '80'}]
        cfg, monitor_uri_configured = config_frontend_with_virtual_host(vhosts, "ssl crt /certs/")
        result = OrderedDict([('frontend port_80', ['bind :80',
                                                    'reqadd X-Forwarded-Proto:\\ http',
                                                    'maxconn 55555',
                                                    'acl is_websocket hdr(Upgrade) -i WebSocket',
                                                    'acl host_rule_1 hdr_reg(host) -i ^.*$',
                                                    'acl host_rule_1_port hdr_reg(host) -i ^.*:80$',
                                                    'acl path_rule_1 path_reg -i ^/path/.*$',
                                                    'use_backend SERVICE_web-a if path_rule_1 host_rule_1 or '
                                                    'path_rule_1 host_rule_1_port'])])
        self.assertEqual(result, cfg)
        self.assertFalse(monitor_uri_configured)

    def test_config_frontend_with_virtual_host_with_monitoring_uri_added(self):
        vhosts = [{'service_alias': 'web-a', 'path': '', 'host': 'a.com', 'scheme': 'http', 'port': '9999'}]
        cfg, monitor_uri_configured = config_frontend_with_virtual_host(vhosts, "ssl crt /certs/")
        result = OrderedDict([('frontend port_9999',
                               ['bind :9999',
                                'reqadd X-Forwarded-Proto:\\ http',
                                'maxconn 55555',
                                'monitor-uri /ping',
                                'acl is_websocket hdr(Upgrade) -i WebSocket',
                                'acl host_rule_1 hdr(host) -i a.com',
                                'acl host_rule_1_port hdr(host) -i a.com:9999',
                                'use_backend SERVICE_web-a if host_rule_1 or host_rule_1_port'])])
        self.assertEqual(result, cfg)
        self.assertTrue(monitor_uri_configured)

    def test_check_require_default_route(self):
        routes = {'HW': [{'container_name': 'HW_1', 'proto': 'tcp', 'port': '80', 'addr': '10.7.0.3'},
                         {'container_name': 'HW_2', 'proto': 'tcp', 'port': '80', 'addr': '10.7.0.2'}],
                  'WEB': [{'container_name': 'WEB_2', 'proto': 'tcp', 'port': '8080', 'addr': '10.7.0.4'},
                          {'container_name': 'WEB_1', 'proto': 'tcp', 'port': '8080', 'addr': '10.7.0.5'}]}
        routes_added_1 = [{'container_name': 'HW_1', 'proto': 'tcp', 'port': '80', 'addr': '10.7.0.3'},
                          {'container_name': 'HW_2', 'proto': 'tcp', 'port': '80', 'addr': '10.7.0.2'}]
        routes_added_2 = [{'container_name': 'HW_1', 'proto': 'tcp', 'port': '80', 'addr': '10.7.0.3'},
                          {'container_name': 'HW_2', 'proto': 'tcp', 'port': '80', 'addr': '10.7.0.2'},
                          {'container_name': 'WEB_2', 'proto': 'tcp', 'port': '8080', 'addr': '10.7.0.4'},
                          {'container_name': 'WEB_1', 'proto': 'tcp', 'port': '8080', 'addr': '10.7.0.5'}]

        self.assertTrue(check_require_default_route(routes, routes_added_1))
        self.assertFalse(check_require_default_route(routes, routes_added_2))
        self.assertFalse(check_require_default_route({}, routes_added_1))
        self.assertTrue(check_require_default_route(routes, []))

    def test_acl_condition(self):
        host_rules = ['acl host_rule_1 hdr(host) -i a.com']
        path_rules = ['acl path_rule_1 path_reg -i ^/path/.*$']
        rule_counter = 3
        vhost = {'service_alias': 'web-a', 'path': '', 'host': 'a.com', 'scheme': 'http', 'port': '8080'}

        self.assertEqual("path_rule_3 host_rule_3 or path_rule_3 host_rule_3_port",
                         calculate_acl_condition(host_rules, path_rules, rule_counter, vhost))
        self.assertEqual("host_rule_3 or host_rule_3_port",
                         calculate_acl_condition(host_rules, [], rule_counter, vhost))
        self.assertEqual("path_rule_3",
                         calculate_acl_condition([], path_rules, rule_counter, vhost))

        vhost2 = {'service_alias': 'web-a', 'path': '', 'host': 'a.com', 'scheme': 'ws', 'port': '8080'}
        self.assertEqual("is_websocket path_rule_3 host_rule_3 or is_websocket path_rule_3 host_rule_3_port",
                         calculate_acl_condition(host_rules, path_rules, rule_counter, vhost2))
        self.assertEqual("is_websocket host_rule_3 or is_websocket host_rule_3_port",
                         calculate_acl_condition(host_rules, [], rule_counter, vhost2))
        self.assertEqual("is_websocket path_rule_3",
                         calculate_acl_condition([], path_rules, rule_counter, vhost2))

        vhost3 = {'service_alias': 'web-a', 'path': '', 'host': 'a.com', 'scheme': 'wss', 'port': '8080'}
        self.assertEqual("is_websocket path_rule_3 host_rule_3 or is_websocket path_rule_3 host_rule_3_port",
                         calculate_acl_condition(host_rules, path_rules, rule_counter, vhost3))
        self.assertEqual("is_websocket host_rule_3 or is_websocket host_rule_3_port",
                         calculate_acl_condition(host_rules, [], rule_counter, vhost3))
        self.assertEqual("is_websocket path_rule_3",
                         calculate_acl_condition([], path_rules, rule_counter, vhost3))

    def test_calculate_host_rules(self):
        self.assertEqual(["acl host_rule_3 hdr(host) -i a.com", "acl host_rule_3_port hdr(host) -i a.com:80"],
                         calculate_host_rules("80", 3, "a.com"))
        self.assertEqual(["acl host_rule_3 hdr_reg(host) -i ^a.*\\.com$",
                          "acl host_rule_3_port hdr_reg(host) -i ^a.*\\.com:80$"],
                         calculate_host_rules("80", 3, "a*.com"))
        self.assertEqual(["acl host_rule_3 hdr_reg(host) -i ^.*$",
                          "acl host_rule_3_port hdr_reg(host) -i ^.*:8080$"],
                         calculate_host_rules("8080", 3, "*"))

    def test_calculate_path_rules(self):
        self.assertEqual(["acl path_rule_3 path -i /path/"], calculate_path_rules("/path/", 3))
        self.assertEqual(["acl path_rule_3 path_reg -i ^/pa\\.th/.*/$"], calculate_path_rules("/pa.th/*/", 3))

    @mock.patch("haproxy.helper.frontend_helper.get_bind_string")
    def test_config_common_part_with_ssl(self, mock_get_bind_string):
        mock_get_bind_string.return_value = ("443 ssl crt /certs/", True)
        frontend_section, monitor_uri_configured = config_common_part("443", "ssl crt /certs/", [])
        self.assertEqual(
            ["bind :443 ssl crt /certs/", "reqadd X-Forwarded-Proto:\ https",
             "acl is_websocket hdr(Upgrade) -i WebSocket"],
            frontend_section)
        self.assertFalse(monitor_uri_configured)

    @mock.patch("haproxy.helper.frontend_helper.get_bind_string")
    def test_config_common_part_without_ssl(self, mock_get_bind_string):
        mock_get_bind_string.return_value = ("80", False)
        frontend_section, monitor_uri_configured = config_common_part("80", "ssl crt /certs/", [])
        self.assertEqual(["bind :80",
                          'reqadd X-Forwarded-Proto:\\ http',
                          "maxconn 55555",
                          "acl is_websocket hdr(Upgrade) -i WebSocket"],
                         frontend_section)
        self.assertFalse(monitor_uri_configured)

    @mock.patch("haproxy.helper.frontend_helper.get_bind_string")
    def test_config_common_part_with_ssl(self, mock_get_bind_string):
        mock_get_bind_string.return_value = ("9999 ssl crt /certs/", True)
        frontend_section, monitor_uri_configured = config_common_part("9999", "ssl crt /certs/", [])
        self.assertEqual(["bind :9999 ssl crt /certs/",
                          "reqadd X-Forwarded-Proto:\ https",
                          'maxconn 55555',
                          "monitor-uri %s" % frontend_helper.MONITOR_URI,
                          "acl is_websocket hdr(Upgrade) -i WebSocket"],
                         frontend_section)
        self.assertTrue(monitor_uri_configured)

    @mock.patch("haproxy.helper.frontend_helper.get_bind_string")
    def test_config_common_part_with_monitor_uri(self, mock_get_bind_string):
        mock_get_bind_string.return_value = ("9999", False)
        frontend_section, monitor_uri_configured = config_common_part("9999", "ssl crt /certs/", [])
        self.assertEqual(
            ["bind :9999", 'reqadd X-Forwarded-Proto:\\ http', "acl is_websocket hdr(Upgrade) -i WebSocket",
             "monitor-uri %s" % frontend_helper.MONITOR_URI],
            frontend_section)
        self.assertTrue(monitor_uri_configured)

    @mock.patch("haproxy.helper.frontend_helper.get_bind_string")
    def test_config_common_part_with_extra_frontend_sttings(self, mock_get_bind_string):
        mock_get_bind_string.return_value = ("80", False)
        frontend_helper.EXTRA_FRONTEND_SETTINGS = {'80': ["reqadd header1 value1", "reqadd header2 value2"]}
        frontend_section, monitor_uri_configured = config_common_part("80", "ssl crt /certs/", [])
        self.assertEqual(["bind :80", 'reqadd X-Forwarded-Proto:\\ http',
                          'maxconn 55555',
                          'reqadd header1 value1',
                          'reqadd header2 value2',
                          "acl is_websocket hdr(Upgrade) -i WebSocket"],
                         frontend_section)
        self.assertFalse(monitor_uri_configured)
        frontend_helper.EXTRA_FRONTEND_SETTINGS = {}

    @mock.patch("haproxy.helper.frontend_helper.get_bind_string")
    def test_config_common_part_without_forwarded_headers(self, mock_get_bind_string):
        mock_get_bind_string.return_value = ("80", False)
        frontend_helper.SKIP_FORWARDED_PROTO = 'true'
        frontend_section, monitor_uri_configured = config_common_part("80", "ssl crt /certs/", [])
        self.assertEqual(["bind :80",
                          "maxconn 55555",
                          "acl is_websocket hdr(Upgrade) -i WebSocket"],
                         frontend_section)

    @mock.patch("haproxy.helper.frontend_helper.get_bind_string")
    def test_config_common_part_without_forwarded_headers_with_ssl(self, mock_get_bind_string):
        mock_get_bind_string.return_value = ("9999 ssl crt /certs/", True)
        frontend_helper.SKIP_FORWARDED_PROTO = 'true'
        frontend_section, monitor_uri_configured = config_common_part("9999", "ssl crt /certs/", [])
        self.assertEqual(["bind :9999 ssl crt /certs/",
                          'maxconn 55555',
                          "monitor-uri %s" % frontend_helper.MONITOR_URI,
                          "acl is_websocket hdr(Upgrade) -i WebSocket"],
                         frontend_section)

    def test_get_bind_string(self):
        vhosts = [{'service_alias': 'web-a', 'path': '', 'host': 'a.com', 'scheme': 'http', 'port': '80'},
                  {'service_alias': 'web-b', 'path': '', 'host': 'a.com', 'scheme': 'http', 'port': '8888'},
                  {'service_alias': 'web-a', 'path': '', 'host': 'a.com', 'scheme': 'https', 'port': '443'},
                  {'service_alias': 'web-a', 'path': '', 'host': 'a.com', 'scheme': 'ws', 'port': '5000'},
                  {'service_alias': 'web-a', 'path': '', 'host': 'a.com', 'scheme': 'wss', 'port': '4443'}]
        bind, ssl = get_bind_string("80", "ssl crt /certs/", vhosts)
        self.assertEqual("80", bind)
        self.assertFalse(ssl)

        bind, ssl = get_bind_string("8888", "ssl crt /certs/", vhosts)
        self.assertEqual("8888 name http", bind)
        self.assertFalse(ssl)

        bind, ssl = get_bind_string("443", "ssl crt /certs/", vhosts)
        self.assertEqual("443 ssl crt /certs/", bind)
        self.assertTrue(ssl)

        bind, ssl = get_bind_string("5000", "ssl crt /certs/", vhosts)
        self.assertEqual("5000", bind)
        self.assertFalse(ssl)

        bind, ssl = get_bind_string("4443", "ssl crt /certs/", vhosts)
        self.assertEqual("4443 accept-proxy ssl crt /certs/", bind)
        self.assertTrue(ssl)

    def test_config_default_front(self):
        cfg, monitor_uri_configured = config_default_frontend("ssl crt /certs/")
        self.assertEqual(OrderedDict([('frontend default_port_80',
                                       ['bind :80',
                                        'reqadd X-Forwarded-Proto:\\ http',
                                        'maxconn 55555',
                                        'default_backend default_service']),
                                      ('frontend default_port_443',
                                       ['bind :443 ssl crt /certs/',
                                        'reqadd X-Forwarded-Proto:\\ https',
                                        'maxconn 55555',
                                        'default_backend default_service'])]), cfg)
        self.assertFalse(monitor_uri_configured)

        cfg, monitor_uri_configured = config_default_frontend("")
        self.assertEqual(OrderedDict([('frontend default_port_80',
                                       ['bind :80',
                                        'reqadd X-Forwarded-Proto:\\ http',
                                        'maxconn 55555',
                                        'default_backend default_service'])
                                      ]), cfg)
        self.assertFalse(monitor_uri_configured)

        frontend_helper.MONITOR_PORT = "80"
        cfg, monitor_uri_configured = config_default_frontend("")
        self.assertEqual(OrderedDict([('frontend default_port_80',
                                       ['bind :80',
                                        'reqadd X-Forwarded-Proto:\\ http',
                                        'maxconn 55555',
                                        'monitor-uri /ping',
                                        'default_backend default_service'])]), cfg)
        self.assertTrue(monitor_uri_configured)

        frontend_helper.MONITOR_PORT = "443"
        frontend_helper.EXTRA_BIND_SETTINGS = {"443": "accept-proxy"}
        cfg, monitor_uri_configured = config_default_frontend("ssl crt /certs/")
        self.assertEqual(OrderedDict([('frontend default_port_80',
                                       ['bind :80',
                                        'reqadd X-Forwarded-Proto:\\ http',
                                        'maxconn 55555',
                                        'default_backend default_service']),
                                      ('frontend default_port_443',
                                       ['bind :443 ssl crt /certs/ accept-proxy',
                                        'reqadd X-Forwarded-Proto:\\ https',
                                        'maxconn 55555',
                                        'monitor-uri /ping',
                                        'default_backend default_service'])]), cfg)
        self.assertTrue(monitor_uri_configured)

        frontend_helper.EXTRA_FRONTEND_SETTINGS = {'80': ["reqadd header1 value1"], '443': ["reqadd header2 value2"]}
        cfg, monitor_uri_configured = config_default_frontend("ssl crt /certs/")
        self.assertEqual(OrderedDict([('frontend default_port_80',
                                       ['bind :80',
                                        'reqadd X-Forwarded-Proto:\\ http',
                                        'maxconn 55555',
                                        'reqadd header1 value1',
                                        'default_backend default_service']),
                                      ('frontend default_port_443',
                                       ['bind :443 ssl crt /certs/ accept-proxy',
                                        'reqadd X-Forwarded-Proto:\\ https',
                                        'maxconn 55555',
                                        'monitor-uri /ping',
                                        'reqadd header2 value2',
                                        'default_backend default_service'])]), cfg)
        self.assertTrue(monitor_uri_configured)

        frontend_helper.SKIP_FORWARDED_PROTO = 'true'
        cfg, monitor_uri_configured = config_default_frontend("ssl crt /certs/")
        self.assertEqual(OrderedDict([('frontend default_port_80',
                                       ['bind :80',
                                        'maxconn 55555',
                                        'reqadd header1 value1',
                                        'default_backend default_service']),
                                      ('frontend default_port_443',
                                       ['bind :443 ssl crt /certs/ accept-proxy',
                                        'maxconn 55555',
                                        'monitor-uri /ping',
                                        'reqadd header2 value2',
                                        'default_backend default_service'])]), cfg)
        self.assertTrue(monitor_uri_configured)

    def test_config_common_part_with_monitor_uri(self):
        self.assertEqual(OrderedDict(), config_monitor_frontend(True))
        self.assertEqual(OrderedDict([('frontend monitor', ['bind :9999', 'monitor-uri /ping'])]),
                         config_monitor_frontend(False))

        frontend_helper.MONITOR_PORT = ""
        self.assertEqual(OrderedDict(), config_monitor_frontend(False))

        frontend_helper.MONITOR_PORT = "3333"
        self.assertEqual(OrderedDict([('frontend monitor', ['bind :3333', 'monitor-uri /ping'])]),
                         config_monitor_frontend(False))
