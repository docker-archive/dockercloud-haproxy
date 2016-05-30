import unittest

from haproxy.helper.tcp_helper import *


class TcpHelperTestCase(unittest.TestCase):
    def test_get_tcp_port_list(self):
        details = {'web-a': {'tcp_ports': ['22']},
                   'web-b': {'tcp_ports': ['33', '44', '22']},
                   'web-c': {}}
        self.assertEqual(['22'], get_tcp_port_list(details, ['web-a']))
        self.assertEqual(['33', '44', '22'], get_tcp_port_list(details, ['web-b']))
        self.assertEqual(['33', '44', '22'], get_tcp_port_list(details, ['web-b', 'web-c']))
        self.assertEqual(['22', '33', '44', '22'], get_tcp_port_list(details, ['web-a', 'web-b', 'web-d']))
        self.assertEqual([], get_tcp_port_list(details, []))
        self.assertEqual([], get_tcp_port_list({}, ['web-a']))

    def test_parse_port_string(self):
        enable_ssl, port_num = parse_port_string("443", "ssl_string")
        self.assertFalse(enable_ssl)
        self.assertEqual('443', port_num)

        enable_ssl, port_num = parse_port_string("443", "")
        self.assertFalse(enable_ssl)
        self.assertEqual('443', port_num)

        enable_ssl, port_num = parse_port_string("443/ssl", "ssl_string")
        self.assertTrue(enable_ssl)
        self.assertEqual('443', port_num)

        enable_ssl, port_num = parse_port_string("443/ssl", "")
        self.assertFalse(enable_ssl)
        self.assertEqual('443', port_num)

        enable_ssl, port_num = parse_port_string("443/wrong", "ssl_string")
        self.assertFalse(enable_ssl)
        self.assertEqual('443/wrong', port_num)

    def test_get_tcp_routes(self):
        details = {'HW': {'tcp_ports': ['22', '22', '33', '44/ssl'], 'health_check': 'checked'}}
        routes = {'HW': [{'container_name': 'HW_1', 'proto': 'tcp', 'port': '22', 'addr': '10.7.0.2'},
                         {'container_name': 'HW_2', 'proto': 'tcp', 'port': '22', 'addr': '10.7.0.3'},
                         {'container_name': 'HW_1', 'proto': 'tcp', 'port': '33', 'addr': '10.7.0.2'},
                         {'container_name': 'HW_2', 'proto': 'tcp', 'port': '33', 'addr': '10.7.0.3'},
                         {'container_name': 'HW_1', 'proto': 'tcp', 'port': '44', 'addr': '10.7.0.2'},
                         {'container_name': 'HW_2', 'proto': 'tcp', 'port': '44', 'addr': '10.7.0.3'}]}

        self.assertEqual(([], []), get_tcp_routes(details, routes, '22', '33'))
        self.assertEqual(([], []), get_tcp_routes(details, routes, '44/ddl', '44'))
        self.assertEqual(([], []), get_tcp_routes(details, {}, '22', '22'))
        self.assertEqual(([], []), get_tcp_routes({}, routes, '22', '22'))

        tcp_routes, routes_added = get_tcp_routes(details, routes, '22', '22')
        self.assertEqual(['server HW_1 10.7.0.2:22 checked', 'server HW_2 10.7.0.3:22 checked'], tcp_routes)
        self.assertEqual([{'addr': '10.7.0.2', 'container_name': 'HW_1', 'port': '22', 'proto': 'tcp'},
                          {'addr': '10.7.0.3', 'container_name': 'HW_2', 'port': '22', 'proto': 'tcp'}], routes_added)

        tcp_routes, routes_added = get_tcp_routes(details, routes, '33', '33')
        self.assertEqual(['server HW_1 10.7.0.2:33 checked', 'server HW_2 10.7.0.3:33 checked'], tcp_routes)
        self.assertEqual([{'addr': '10.7.0.2', 'container_name': 'HW_1', 'port': '33', 'proto': 'tcp'},
                          {'addr': '10.7.0.3', 'container_name': 'HW_2', 'port': '33', 'proto': 'tcp'}], routes_added)

        tcp_routes, routes_added = get_tcp_routes(details, routes, '44/ssl', '44')
        self.assertEqual(['server HW_1 10.7.0.2:44 checked', 'server HW_2 10.7.0.3:44 checked'], tcp_routes)
        self.assertEqual([{'addr': '10.7.0.2', 'container_name': 'HW_1', 'port': '44', 'proto': 'tcp'},
                          {'addr': '10.7.0.3', 'container_name': 'HW_2', 'port': '44', 'proto': 'tcp'}], routes_added)

        tcp_routes, routes_added = get_tcp_routes({'HW': {'tcp_ports': ['44', '44/ssl'], 'health_check': 'checked'}},
                                                  routes, '44', '44')
        self.assertEqual(['server HW_1 10.7.0.2:44 checked', 'server HW_2 10.7.0.3:44 checked'], tcp_routes)
        self.assertEqual([{'addr': '10.7.0.2', 'container_name': 'HW_1', 'port': '44', 'proto': 'tcp'},
                          {'addr': '10.7.0.3', 'container_name': 'HW_2', 'port': '44', 'proto': 'tcp'}], routes_added)

        details = {'HW': {'tcp_ports': ['22']},
                   'WEB': {'tcp_ports': ['22'], 'health_check': 'checked'}}
        routes = {'HW': [{'container_name': 'HW_1', 'proto': 'tcp', 'port': '22', 'addr': '10.7.0.2'},
                         {'container_name': 'HW_2', 'proto': 'tcp', 'port': '22', 'addr': '10.7.0.3'}],
                  'WEB': [{'container_name': 'WEB_1', 'proto': 'tcp', 'port': '22', 'addr': '10.7.0.4'},
                          {'container_name': 'WEB_2', 'proto': 'tcp', 'port': '22', 'addr': '10.7.0.5'}]}
        tcp_routes, routes_added = get_tcp_routes(details, routes, '22', '22')
        self.assertEqual(['server WEB_1 10.7.0.4:22 checked',
                          'server WEB_2 10.7.0.5:22 checked',
                          'server HW_1 10.7.0.2:22 check inter 2000 rise 2 fall 3',
                          'server HW_2 10.7.0.3:22 check inter 2000 rise 2 fall 3'], tcp_routes)
        self.assertEqual([{'addr': '10.7.0.4', 'container_name': 'WEB_1', 'port': '22', 'proto': 'tcp'},
                          {'addr': '10.7.0.5', 'container_name': 'WEB_2', 'port': '22', 'proto': 'tcp'},
                          {'addr': '10.7.0.2', 'container_name': 'HW_1', 'port': '22', 'proto': 'tcp'},
                          {'addr': '10.7.0.3', 'container_name': 'HW_2', 'port': '22', 'proto': 'tcp'}], routes_added)

    def test_get_healthcheck_string(self):
        details = {'HW': {'tcp_ports': ['22']},
                   'WEB': {'tcp_ports': ['22'], 'health_check': 'checked'}}
        self.assertEqual(HEALTH_CHECK, get_healthcheck_string(details, "HW"))
        self.assertEqual("checked", get_healthcheck_string(details, "WEB"))
        self.assertEqual(HEALTH_CHECK, get_healthcheck_string(details, "NOT_EXIST"))
        self.assertEqual(HEALTH_CHECK, get_healthcheck_string({}, "NOT_EXIST"))

    def test_get_extra_route_settings_string(self):
        details = {'HW': {'tcp_ports': ['22']},
                   'WEB': {'tcp_ports': ['22'], 'extra_route_settings': 'extra settings'}}
        self.assertEqual(EXTRA_ROUTE_SETTINGS, get_extra_route_settings_string(details, "HW"))
        self.assertEqual("extra settings", get_extra_route_settings_string(details, "WEB"))
        self.assertEqual(EXTRA_ROUTE_SETTINGS, get_extra_route_settings_string(details, "NOT_EXIST"))
        self.assertEqual(EXTRA_ROUTE_SETTINGS, get_extra_route_settings_string({}, "NOT_EXIST"))

    def test_get_service_aliases_given_tcp_port(self):
        details = {'HW': {'tcp_ports': ['22', '33']},
                   'HELLO': {'tcp_ports': ['22']},
                   'WORLD': {'tcp_ports': ['33']}}
        self.assertEqual(['HW', 'HELLO'], get_service_aliases_given_tcp_port(details, ['HW', 'HELLO', 'WORLD'], '22'))
        self.assertEqual(['HW', 'WORLD'], get_service_aliases_given_tcp_port(details, ['HW', 'HELLO', 'WORLD'], '33'))

        self.assertEqual(['HELLO'], get_service_aliases_given_tcp_port(details, ['HELLO', 'WORLD'], '22'))
        self.assertEqual(['WORLD'], get_service_aliases_given_tcp_port(details, ['HELLO', 'WORLD'], '33'))

        self.assertEqual([], get_service_aliases_given_tcp_port(details, ['HELLO', 'WORLD'], '44'))
        self.assertEqual([], get_service_aliases_given_tcp_port(details, [], '33'))
        self.assertEqual([], get_service_aliases_given_tcp_port({}, ['HELLO', 'WORLD'], '33'))
        self.assertEqual([], get_service_aliases_given_tcp_port({}, [], '33'))

    def test_get_tcp_balance(self):
        details = {'HW': {'balance': "a"},
                   'HELLO': {'balance': "b"},
                   'WORLD': {'balance': ""}}
        self.assertEqual([], get_tcp_balance({}))
        self.assertEqual([], get_tcp_balance({'WORLD': {'balance': ""}}))
        self.assertTrue(get_tcp_balance(details) in [["balance a"], ["balance b"], []])

    def test_get_tcp_options(self):
        details = {'HW': {'option': ["opt1", 'opt2']},
                   'HELLO': {'option': ["opt3", "opt1"]},
                   'WORLD': {'option': ["opt4", "opt2"]}}
        self.assertEqual(["option opt1", "option opt2", "option opt3", "option opt4"],
                         get_tcp_options(details, ["HW", "HELLO", "WORLD"]))
        self.assertEqual(["option opt3", "option opt1", "option opt4", "option opt2"],
                         get_tcp_options(details, ["HELLO", "WORLD"]))
        self.assertEqual([], get_tcp_options(details, ["SOMETHING"]))
        self.assertEqual([], get_tcp_options({}, ["SOMETHING"]))

    def test_get_tcp_extra_settings(self):
        details = {"HELLO": {"extra_settings": "abc, def , ghi   "},
                   "WORLD": {"extra_settings": "abc, de\,f,abc"}}

        self.assertEqual(["abc", "de,f"], get_tcp_extra_settings(details, ["WORLD"]))
        self.assertEqual(["abc", "def", "ghi", "de,f"], get_tcp_extra_settings(details, ["HELLO", "WORLD"]))
        self.assertEqual([], get_tcp_extra_settings({}, ["HELLO", "WORLD"]))
        self.assertEqual([], get_tcp_extra_settings(details, []))
