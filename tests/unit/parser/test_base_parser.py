import unittest

from haproxy.parser.legacy_link_parser import *


class SpecsTestCase(unittest.TestCase):
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

    def test_parse_vhost(self):
        details = {'WORLD': {'default_ssl_cert': '', 'ssl_cert': '', 'exclude_ports': [], 'hsts_max_age': None,
                             'gzip_compression_type': None, 'http_check': None, 'virtual_host_weight': 0,
                             'health_check': None, 'cookie': None, 'virtual_host': 'a.com', 'force_ssl': None,
                             'tcp_ports': [], 'balance': None, 'extra_settings': None, 'appsession': None,
                             'option': []},
                   'HELLO': {'default_ssl_cert': '', 'ssl_cert': '', 'exclude_ports': [], 'hsts_max_age': None,
                             'gzip_compression_type': None, 'http_check': None, 'virtual_host_weight': 0,
                             'health_check': None, 'cookie': None, 'virtual_host': 'b.com', 'force_ssl': None,
                             'tcp_ports': [], 'balance': None, 'extra_settings': None, 'appsession': None,
                             'option': []}}
        vhosts = [{'path': '', 'host': 'a.com', 'scheme': 'http', 'port': '80', 'service_alias': 'WORLD'},
                  {'path': '', 'host': 'b.com', 'scheme': 'http', 'port': '80', 'service_alias': 'HELLO'}]
        updated_details = {
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

        specs = Specs()
        self.assertEqual([], specs._parse_vhosts({}))

        specs = Specs()
        specs.details = details
        self.assertEqual(vhosts, specs._parse_vhosts(specs.details))
        self.assertEqual(updated_details, specs.details)

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


class EnvParserTestCase(unittest.TestCase):
    def test_parse_default_ssl_cert(self):
        self.assertEqual("", EnvParser.parse_default_ssl_cert(""))
        self.assertEqual("abc", EnvParser.parse_default_ssl_cert("abc"))
        self.assertEqual("abc\ndef", EnvParser.parse_default_ssl_cert("abc\ndef"))
        self.assertEqual("abc\ndef", EnvParser.parse_default_ssl_cert("abc\\ndef"))

    def test_parse_ssl_cert(self):
        self.assertEqual("", EnvParser.parse_ssl_cert(""))
        self.assertEqual("abc", EnvParser.parse_ssl_cert("abc"))
        self.assertEqual("abc\ndef", EnvParser.parse_ssl_cert("abc\ndef"))
        self.assertEqual("abc\ndef", EnvParser.parse_ssl_cert("abc\\ndef"))

    def test_parse_parse_exclude_ports(self):
        self.assertEqual([], EnvParser.parse_exclude_ports(""))
        self.assertEqual(['3306', '3307', '3308'], EnvParser.parse_exclude_ports("3306, 3307 , 3308 , "))

    def test_parse_tcp_ports(self):
        self.assertEqual([], EnvParser.parse_tcp_ports(""))
        self.assertEqual(['9000', '22/ssl', '33/ssl'], EnvParser.parse_tcp_ports("9000, 22/ssl , 33/ssl , "))

    def test_parse_option(self):
        self.assertEqual([], EnvParser.parse_option(""))
        self.assertEqual(['opt1', 'opt2', 'opt3'], EnvParser.parse_tcp_ports("opt1, opt2 , opt3 , "))
