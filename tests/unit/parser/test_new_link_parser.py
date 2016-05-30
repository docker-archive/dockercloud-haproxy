import unittest

from haproxy.parser.new_link_parser import *


class SpecsTestCase(unittest.TestCase):
    def setUp(self):
        self.links = {'8c64c58e2887877695e18972a263120262edc92a6fa2ab39b792a9606f565550':
                          {'service_name': 'tmp_world',
                           'container_name': 'tmp_world_1',
                           'container_envvars': [
                               {'value': 'ab.com',
                                'key': 'VIRTUAL_HOST'},
                               {'value': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
                                'key': 'PATH'}],
                           'compose_service': 'world',
                           'compose_project': 'tmp',
                           'endpoints': {
                               '80/tcp': 'tcp://tmp_world_1:80'}},
                      'a90c1c19288d0702712ca464f0df9216d00ba3e7267ae86505fd26c9f90c993b':
                          {'service_name': 'tmp_hello',
                           'container_name': 'tmp_hello_1',
                           'container_envvars': [
                               {'value': 'a.com',
                                'key': 'VIRTUAL_HOST'},
                               {'value': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
                                'key': 'PATH'}],
                           'compose_service': 'hello',
                           'compose_project': 'tmp',
                           'endpoints': {
                               '80/tcp': 'tcp://tmp_hello_1:80'}}}

        self.service_aliases = ['tmp_hello', 'tmp_world']
        self.details = {'tmp_world': {'default_ssl_cert': '', 'ssl_cert': '', 'exclude_ports': [], 'hsts_max_age': '',
                                      'gzip_compression_type': '', 'http_check': '', 'virtual_host_weight': 0,
                                      'health_check': '', 'cookie': '', 'virtual_host': 'ab.com', 'force_ssl': '',
                                      'tcp_ports': [], 'balance': '', 'extra_settings': '', 'appsession': '',
                                      'option': [], "extra_route_settings": ''},
                        'tmp_hello': {'default_ssl_cert': '', 'ssl_cert': '', 'exclude_ports': [], 'hsts_max_age': '',
                                      'gzip_compression_type': '', 'http_check': '', 'virtual_host_weight': 0,
                                      'health_check': '', 'cookie': '', 'virtual_host': 'a.com', 'force_ssl': '',
                                      'tcp_ports': [], 'balance': '', 'extra_settings': '', 'appsession': '',
                                      'option': [], "extra_route_settings": ''}}
        self.routes = {'tmp_hello': [{'addr': 'tmp_hello_1',
                                      'container_name': 'tmp_hello_1',
                                      'port': '80',
                                      'proto': 'tcp'}],
                       'tmp_world': [{'addr': 'tmp_world_1',
                                      'container_name': 'tmp_world_1',
                                      'port': '80',
                                      'proto': 'tcp'}]}
        self.links2 = {'id1': {'service_name': 'tmp_world',
                               'container_name': 'tmp_world_1',
                               'endpoints': {
                                   '80/tcp': 'tcp://tmp_world_1:80',
                                   '22/tcp': 'tcp://tmp_world_1:22'}
                               },
                       'id2': {'service_name': 'tmp_world',
                               'container_name': 'tmp_world_2',
                               'endpoints': {
                                   '80/tcp': 'tcp://tmp_world_2:80',
                                   '22/tcp': 'tcp://tmp_world_2:22'}
                               },
                       'id3': {'service_name': 'tmp_hello',
                               'container_name': 'tmp_world_1',
                               'endpoints': {
                                   '80/tcp': 'tcp://tmp_hello_1:80',
                                   '22/tcp': 'tcp://tmp_hello_1:22'},
                               },
                       }
        self.routes2 = {
            'tmp_world': [{'container_name': 'tmp_world_2', 'proto': 'tcp', 'port': '22', 'addr': 'tmp_world_2'},
                          {'container_name': 'tmp_world_2', 'proto': 'tcp', 'port': '80', 'addr': 'tmp_world_2'},
                          {'container_name': 'tmp_world_1', 'proto': 'tcp', 'port': '22', 'addr': 'tmp_world_1'},
                          {'container_name': 'tmp_world_1', 'proto': 'tcp', 'port': '80', 'addr': 'tmp_world_1'}],
            'tmp_hello': [{'container_name': 'tmp_world_1', 'proto': 'tcp', 'port': '22', 'addr': 'tmp_hello_1'},
                          {'container_name': 'tmp_world_1', 'proto': 'tcp', 'port': '80', 'addr': 'tmp_hello_1'}]}

    def test_parse_service_aliases(self):
        self.assertEqual([], NewLinkSpecs._parse_service_aliases({}))
        self.assertEqual(self.service_aliases, NewLinkSpecs._parse_service_aliases(self.links))

    def test_parse_details(self):
        empty_details = {'tmp_world': {'default_ssl_cert': '', 'ssl_cert': '', 'exclude_ports': [], 'hsts_max_age': '',
                                       'gzip_compression_type': '', 'http_check': '', 'virtual_host_weight': 0,
                                       'health_check': '', 'cookie': '', 'virtual_host': '', 'force_ssl': '',
                                       'tcp_ports': [], 'balance': '', 'extra_settings': '', 'appsession': '',
                                       'option': [], "extra_route_settings": ''},
                         'tmp_hello': {'default_ssl_cert': '', 'ssl_cert': '', 'exclude_ports': [], 'hsts_max_age': '',
                                       'gzip_compression_type': '', 'http_check': '', 'virtual_host_weight': 0,
                                       'health_check': '', 'cookie': '', 'virtual_host': '', 'force_ssl': '',
                                       'tcp_ports': [], 'balance': '', 'extra_settings': '', 'appsession': '',
                                       'option': [], "extra_route_settings": ''}}

        self.assertEqual({}, NewLinkSpecs._parse_details([], {}))
        self.assertEqual({}, NewLinkSpecs._parse_details([], self.links))
        self.assertEqual(empty_details, NewLinkSpecs._parse_details(self.service_aliases, {}))
        self.assertEqual(self.details, NewLinkSpecs._parse_details(self.service_aliases, self.links))

    def test_parse_routes(self):
        self.assertEqual({}, NewLinkSpecs._parse_routes({}, {}))
        self.assertEqual(self.routes, NewLinkSpecs._parse_routes({}, self.links))
        self.assertEqual({}, NewLinkSpecs._parse_routes(self.details, {}))
        self.assertEqual(self.routes, NewLinkSpecs._parse_routes(self.details, self.links))

    def test_parse_multi_routes(self):
        self.assertEqual(self.routes2, NewLinkSpecs._parse_routes({}, self.links2))

    def test_parse_routes_with_exclude_ports(self):
        details = {'tmp_hello': {'exclude_ports': ['20']}}
        self.assertEqual(self.routes2, NewLinkSpecs._parse_routes(details, self.links2))

        details = {'tmp_world': {'exclude_ports': ['80']}}
        routes = {'tmp_world': [{'container_name': 'tmp_world_2', 'proto': 'tcp', 'port': '22', 'addr': 'tmp_world_2'},
                                {'container_name': 'tmp_world_1', 'proto': 'tcp', 'port': '22', 'addr': 'tmp_world_1'}],
                  'tmp_hello': [{'container_name': 'tmp_world_1', 'proto': 'tcp', 'port': '22', 'addr': 'tmp_hello_1'},
                                {'container_name': 'tmp_world_1', 'proto': 'tcp', 'port': '80', 'addr': 'tmp_hello_1'}]}
        self.assertEqual(routes, NewLinkSpecs._parse_routes(details, self.links2))

        details = {'tmp_world': {'exclude_ports': ['80', '22']}}
        routes = {'tmp_world': [],
                  'tmp_hello': [{'container_name': 'tmp_world_1', 'proto': 'tcp', 'port': '22', 'addr': 'tmp_hello_1'},
                                {'container_name': 'tmp_world_1', 'proto': 'tcp', 'port': '80', 'addr': 'tmp_hello_1'}]}
        self.assertEqual(routes, NewLinkSpecs._parse_routes(details, self.links2))

        details = {'tmp_world': {'exclude_ports': ['80', '22']}, 'tmp_hello': {'exclude_ports': ['80']}}
        routes = {'tmp_world': [],
                  'tmp_hello': [{'container_name': 'tmp_world_1', 'proto': 'tcp', 'port': '22', 'addr': 'tmp_hello_1'}]}
        self.assertEqual(routes, NewLinkSpecs._parse_routes(details, self.links2))
