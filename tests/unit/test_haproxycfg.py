import unittest

import mock

from haproxy import haproxycfg
from haproxy.haproxycfg import *
from haproxy.parser.base_parser import Specs
from haproxy.parser.legacy_link_parser import LegacyLinkSpecs
from haproxy.parser.new_link_parser import NewLinkSpecs


class HaproxyInitTestCase(unittest.TestCase):
    @mock.patch.object(haproxycfg.Haproxy, '_init_cloud_links')
    @mock.patch.object(haproxycfg.Haproxy, '_init_new_links')
    def test_initialize(self, mock_init_new_links, mock_init_cloud_links):
        self.assertTrue(isinstance(Haproxy._initialize("new"), NewLinkSpecs))
        self.assertTrue(isinstance(Haproxy._initialize("cloud"), NewLinkSpecs))
        self.assertTrue(isinstance(Haproxy._initialize("legacy"), LegacyLinkSpecs))
        self.assertTrue(isinstance(Haproxy._initialize("other"), LegacyLinkSpecs))

    @mock.patch("haproxy.haproxycfg.docker_client")
    def test_init_new_links_regressiong(self, mock_client):
        mock_client.side_effect = Exception()
        self.assertIsNone(Haproxy._init_new_links())


class HaproxyUpdateTestCase(unittest.TestCase):
    @mock.patch("haproxy.helper.update_helper.run_reload")
    @mock.patch("haproxy.haproxycfg.save_to_file")
    @mock.patch.object(haproxycfg.Haproxy, '_initialize')
    def test_update_haproxy_cfg_updated_success(self, mock_init, mock_save, mock_run_reload):
        haproxy = Haproxy()
        haproxy.link_mode = "cloud"
        cfg = {"key": "value"}
        Haproxy.cls_cfg = {}
        mock_save.return_value = True

        haproxy._update_haproxy(cfg)
        mock_save.assert_called_with(HAPROXY_CONFIG_FILE, cfg)
        self.assertTrue(mock_run_reload.called)

    @mock.patch("haproxy.haproxycfg.UpdateHelper.run_reload")
    @mock.patch("haproxy.haproxycfg.save_to_file")
    @mock.patch.object(haproxycfg.Haproxy, '_initialize')
    def test_update_haproxy_cfg_updated_failed(self, mock_init, mock_save, mock_run_reload):
        haproxy = Haproxy()
        haproxy.link_mode = "cloud"
        cfg = {"key": "value"}
        Haproxy.cls_cfg = {}
        mock_save.return_value = False

        haproxy._update_haproxy(cfg)
        mock_save.assert_called_with(HAPROXY_CONFIG_FILE, cfg)
        self.assertFalse(mock_run_reload.called)

    @mock.patch("haproxy.haproxycfg.UpdateHelper.run_reload")
    @mock.patch("haproxy.haproxycfg.save_to_file")
    @mock.patch.object(haproxycfg.Haproxy, '_initialize')
    def test_update_haproxy_cfg_ssl_updated(self, mock_init, mock_save, mock_run_reload):
        haproxy = Haproxy()
        haproxy.link_mode = "cloud"
        cfg = {"key": "value"}
        Haproxy.cls_cfg = cfg
        haproxy.ssl_updated = True
        mock_save.return_value = False

        haproxy._update_haproxy(cfg)
        self.assertFalse(mock_save.called)
        self.assertTrue(mock_run_reload.called)

    @mock.patch("haproxy.haproxycfg.UpdateHelper.run_reload")
    @mock.patch("haproxy.haproxycfg.save_to_file")
    @mock.patch.object(haproxycfg.Haproxy, '_initialize')
    def test_update_haproxy_cfg_no_updates(self, mock_init, mock_save, mock_run_reload):
        haproxy = Haproxy()
        haproxy.link_mode = "cloud"
        cfg = {"key": "value"}
        Haproxy.cls_cfg = cfg
        haproxy.ssl_updated = False
        mock_save.return_value = False

        haproxy._update_haproxy(cfg)
        self.assertFalse(mock_save.called)
        self.assertFalse(mock_run_reload.called)

    @mock.patch("haproxy.haproxycfg.UpdateHelper.run_once")
    @mock.patch("haproxy.haproxycfg.UpdateHelper.run_reload")
    @mock.patch("haproxy.haproxycfg.save_to_file")
    @mock.patch.object(haproxycfg.Haproxy, '_initialize')
    def test_update_haproxy_cfg_only_once(self, mock_init, mock_save, mock_run_reload, mock_run_once):
        haproxy = Haproxy()
        haproxy.link_mode = "legacy"
        cfg = {"key": "value"}
        haproxy._update_haproxy(cfg)
        mock_save.assert_called_with(HAPROXY_CONFIG_FILE, cfg)
        self.assertFalse(mock_run_reload.called)
        self.assertTrue(mock_run_once)


class HaproxyConfigSSLTestCase(unittest.TestCase):
    @mock.patch.object(haproxycfg.Haproxy, '_config_ssl_cacerts')
    @mock.patch.object(haproxycfg.Haproxy, '_config_ssl_certs')
    @mock.patch.object(haproxycfg.Haproxy, '_initialize')
    def test_config_ssl(self, mock_init, mock_certs, mock_cacerts):
        mock_certs.return_value = 'ssl certs'
        mock_cacerts.return_value = ' ssl cacerts'
        haproxy = Haproxy()
        haproxy.ssl_bind_string = ""
        haproxy._config_ssl()
        self.assertEquals("ssl certs ssl cacerts", haproxy.ssl_bind_string)

        mock_certs.return_value = ""
        mock_cacerts.return_value = ""
        haproxy = Haproxy()
        haproxy.ssl_bind_string = ""
        haproxy._config_ssl()
        self.assertEquals("", haproxy.ssl_bind_string)

    @mock.patch("haproxy.haproxycfg.SslHelper.save_certs")
    @mock.patch("haproxy.haproxycfg.SslHelper.get_extra_ssl_certs")
    @mock.patch.object(haproxycfg.Haproxy, '_initialize')
    def test_config_ssl_certs(self, mock_init, mock_get_extra_ssl_certs, mock_save):
        haproxy = Haproxy()
        haproxy.specs = Specs()
        self.assertEqual("", haproxy._config_ssl_certs())

        haproxy = Haproxy()
        haproxy.specs = Specs()
        mock_get_extra_ssl_certs.return_value = ["cert"]
        Haproxy.cls_certs = []
        self.assertEqual("ssl crt /certs/", haproxy._config_ssl_certs())
        self.assertEqual(["cert"], Haproxy.cls_certs)
        self.assertTrue(haproxy.ssl_updated)

        haproxy = Haproxy()
        haproxy.specs = Specs()
        mock_get_extra_ssl_certs.return_value = ["cert"]
        Haproxy.cls_certs = ["cert"]
        self.assertEqual("ssl crt /certs/", haproxy._config_ssl_certs())
        self.assertFalse(haproxy.ssl_updated)

    @mock.patch("haproxy.haproxycfg.SslHelper.save_certs")
    @mock.patch.object(haproxycfg.Haproxy, '_initialize')
    def test_config_ssl_certs(self, mock_init, mock_save):
        haproxy = Haproxy()
        haproxy.specs = Specs()
        self.assertEqual("", haproxy._config_ssl_cacerts())

        haproxy = Haproxy()
        haproxy.specs = Specs()
        haproxycfg.DEFAULT_CA_CERT = "cacert"
        Haproxy.cls_certs = []
        self.assertEqual(" ca-file /cacerts/cert0.pem verify required", haproxy._config_ssl_cacerts())
        self.assertEqual(["cacert"], Haproxy.cls_ca_certs)
        self.assertTrue(haproxy.ssl_updated)

        haproxy = Haproxy()
        haproxy.specs = Specs()
        haproxycfg.DEFAULT_CA_CERT = "cacert"
        Haproxy.cls_certs = ["cacert"]
        self.assertEqual(" ca-file /cacerts/cert0.pem verify required", haproxy._config_ssl_cacerts())
        self.assertFalse(haproxy.ssl_updated)

        haproxycfg.DEFAULT_CA_CERT = config.DEFAULT_CA_CERT


class HaproxyConfigUserListTestCase(unittest.TestCase):
    def test_config_userlist_section(self):
        self.assertEqual({}, Haproxy._config_userlist_section(""))
        self.assertEqual({'userlist haproxy_userlist': ['user user insecure-password pass']},
                         Haproxy._config_userlist_section("user:pass"))
        self.assertEqual(OrderedDict([('userlist haproxy_userlist', ['user user1 insecure-password pass1',
                                                                     'user user2 insecure-password pass2',
                                                                     'user user3 insecure-password pass3'])]),
                         Haproxy._config_userlist_section("user1:pass1, user2:pass2  ,user3:pass3"))

        self.assertEqual(OrderedDict([('userlist haproxy_userlist', ['user us,er1 insecure-password pass,1',
                                                                     'user user2 insecure-password ',
                                                                     'user  insecure-password pass3'])]),
                         Haproxy._config_userlist_section("us\,er1:pass\,1, user2:, :pass3"))

    @mock.patch.object(Specs, 'get_routes')
    @mock.patch.object(Specs, 'get_service_aliases')
    @mock.patch.object(Specs, 'get_details')
    @mock.patch.object(haproxycfg.Haproxy, '_initialize')
    def test_config_tcp_sections(self, mock_init, mock_details, mock_services, mock_routes):
        haproxy = Haproxy()
        haproxy.specs = Specs()
        mock_details.return_value = {}
        mock_services.return_value = []
        mock_routes.return_value = {}
        self.assertEqual({}, haproxy._config_tcp_sections())

        haproxy = Haproxy()
        haproxy.specs = Specs()
        mock_details.return_value = {'HW': {'tcp_ports': ['22'], 'health_check': 'check'}}
        mock_services.return_value = ["HW"]
        mock_routes.return_value = {
            'HW': [{'container_name': 'HW_1', 'proto': 'tcp', 'port': '22', 'addr': '10.7.0.2'},
                   {'container_name': 'HW_2', 'proto': 'tcp', 'port': '22', 'addr': '10.7.0.3'},
                   {'container_name': 'HW_1', 'proto': 'tcp', 'port': '33', 'addr': '10.7.0.2'},
                   {'container_name': 'HW_2', 'proto': 'tcp', 'port': '33', 'addr': '10.7.0.3'}]}
        self.assertEqual(OrderedDict([('listen port_22', ['bind :22',
                                                          'mode tcp',
                                                          'server HW_1 10.7.0.2:22 check',
                                                          'server HW_2 10.7.0.3:22 check'])]),
                         haproxy._config_tcp_sections())

        haproxy = Haproxy()
        haproxy.specs = Specs()
        mock_details.return_value = {'HW': {'tcp_ports': ['22', '33'], 'health_check': 'check'}}
        mock_services.return_value = ["HW"]
        mock_routes.return_value = {
            'HW': [{'container_name': 'HW_1', 'proto': 'tcp', 'port': '22', 'addr': '10.7.0.2'},
                   {'container_name': 'HW_2', 'proto': 'tcp', 'port': '22', 'addr': '10.7.0.3'},
                   {'container_name': 'HW_1', 'proto': 'tcp', 'port': '33', 'addr': '10.7.0.2'},
                   {'container_name': 'HW_2', 'proto': 'tcp', 'port': '33', 'addr': '10.7.0.3'}]}
        self.assertEqual(OrderedDict([('listen port_33', ['bind :33',
                                                          'mode tcp',
                                                          'server HW_1 10.7.0.2:33 check',
                                                          'server HW_2 10.7.0.3:33 check']),
                                      ('listen port_22', ['bind :22', 'mode tcp',
                                                          'server HW_1 10.7.0.2:22 check',
                                                          'server HW_2 10.7.0.3:22 check'])]),
                         haproxy._config_tcp_sections())

        haproxy = Haproxy()
        haproxy.specs = Specs()
        mock_details.return_value = {'HW': {'tcp_ports': ['22', '33'], 'health_check': 'check'},
                                     'WEB': {'tcp_ports': ['22', '44']}}
        mock_services.return_value = ["HW", "WEB"]
        mock_routes.return_value = {
            'HW': [{'container_name': 'HW_1', 'proto': 'tcp', 'port': '22', 'addr': '10.7.0.2'},
                   {'container_name': 'HW_2', 'proto': 'tcp', 'port': '22', 'addr': '10.7.0.3'},
                   {'container_name': 'HW_1', 'proto': 'tcp', 'port': '33', 'addr': '10.7.0.2'},
                   {'container_name': 'HW_2', 'proto': 'tcp', 'port': '33', 'addr': '10.7.0.3'}],
            'WEB': [{'container_name': 'WEB_1', 'proto': 'tcp', 'port': '22', 'addr': '10.7.0.4'},
                    {'container_name': 'WEB_2', 'proto': 'tcp', 'port': '22', 'addr': '10.7.0.5'},
                    {'container_name': 'WEB_1', 'proto': 'tcp', 'port': '44', 'addr': '10.7.0.4'},
                    {'container_name': 'WEB_2', 'proto': 'tcp', 'port': '44', 'addr': '10.7.0.5'}]}

        self.assertEqual(OrderedDict([('listen port_33', ['bind :33',
                                                          'mode tcp',
                                                          'server HW_1 10.7.0.2:33 check',
                                                          'server HW_2 10.7.0.3:33 check']),
                                      ('listen port_44', ['bind :44',
                                                          'mode tcp',
                                                          'server WEB_1 10.7.0.4:44 check inter 2000 rise 2 fall 3',
                                                          'server WEB_2 10.7.0.5:44 check inter 2000 rise 2 fall 3']),
                                      ('listen port_22', ['bind :22',
                                                          'mode tcp',
                                                          'server WEB_1 10.7.0.4:22 check inter 2000 rise 2 fall 3',
                                                          'server WEB_2 10.7.0.5:22 check inter 2000 rise 2 fall 3',
                                                          'server HW_1 10.7.0.2:22 check',
                                                          'server HW_2 10.7.0.3:22 check'])]),
                         haproxy._config_tcp_sections())


class HaproxyConfigFrontendTestCase(unittest.TestCase):
    @mock.patch.object(Specs, 'get_vhosts')
    @mock.patch.object(Specs, 'get_routes')
    @mock.patch.object(Specs, 'get_service_aliases')
    @mock.patch.object(Specs, 'get_details')
    @mock.patch.object(haproxycfg.Haproxy, '_initialize')
    def test_config_frontend_sections(self, mock_init, mock_details, mock_services, mock_routes, mock_vhosts):
        haproxy = Haproxy()
        haproxy.specs = Specs()
        mock_details.return_value = {}
        mock_services.return_value = []
        mock_routes.return_value = {}
        mock_vhosts.return_value = []
        self.assertEqual({}, haproxy._config_frontend_sections())

        haproxy = Haproxy()
        haproxy.specs = Specs()
        mock_details.return_value = {'HW': {'balance': "source",
                                            'virtual_host': "a.com",
                                            'health_check': "check"}}
        mock_services.return_value = ["HW"]
        mock_routes.return_value = {
            'HW': [{'container_name': 'HW_1', 'proto': 'http', 'port': '80', 'addr': '10.7.0.2'},
                   {'container_name': 'HW_2', 'proto': 'http', 'port': '80', 'addr': '10.7.0.3'}]}
        mock_vhosts.return_value = [
            {'service_alias': 'HW', 'path': '', 'host': 'a.com', 'scheme': 'http', 'port': '80'}]
        self.assertEqual(OrderedDict([('frontend port_80',
                                       ['bind :80',
                                        'reqadd X-Forwarded-Proto:\\ http',
                                        'maxconn 4096',
                                        'acl is_websocket hdr(Upgrade) -i WebSocket',
                                        'acl host_rule_1 hdr(host) -i a.com',
                                        'acl host_rule_1_port hdr(host) -i a.com:80',
                                        'use_backend SERVICE_HW if host_rule_1 or host_rule_1_port'])]),
                         haproxy._config_frontend_sections())

        haproxy = Haproxy()
        haproxy.specs = Specs()
        mock_details.return_value = {'HW': {'balance': "source",
                                            'health_check': "check"}}
        mock_services.return_value = ["HW"]
        mock_routes.return_value = {
            'HW': [{'container_name': 'HW_1', 'proto': 'http', 'port': '80', 'addr': '10.7.0.2'},
                   {'container_name': 'HW_2', 'proto': 'http', 'port': '80', 'addr': '10.7.0.3'}]}
        mock_vhosts.return_value = []
        self.assertEqual(OrderedDict([('frontend default_port_80',
                                       ['bind :80',
                                        'reqadd X-Forwarded-Proto:\\ http',
                                        'maxconn 4096',
                                        'default_backend default_service'])]),
                         haproxy._config_frontend_sections())


class HaproxyConfigBackendTestCase(unittest.TestCase):
    @mock.patch.object(Specs, 'get_vhosts')
    @mock.patch.object(Specs, 'get_routes')
    @mock.patch.object(Specs, 'get_service_aliases')
    @mock.patch.object(Specs, 'get_details')
    @mock.patch.object(haproxycfg.Haproxy, '_initialize')
    def test_config_backend_sections(self, mock_init, mock_details, mock_services, mock_routes, mock_vhosts):
        haproxy = Haproxy()
        haproxy.specs = Specs()
        mock_details.return_value = {}
        mock_services.return_value = []
        mock_routes.return_value = {}
        mock_vhosts.return_value = []
        self.assertEqual({}, haproxy._config_backend_sections())

        haproxy = Haproxy()
        haproxy.specs = Specs()
        mock_details.return_value = {'HW': {'balance': "source",
                                            'virtual_host': "a.com",
                                            'health_check': "check",
                                            'extra_route_settings': 'extra settings'}}
        mock_services.return_value = ["HW"]
        mock_routes.return_value = {
            'HW': [{'container_name': 'HW_1', 'proto': 'http', 'port': '80', 'addr': '10.7.0.2'},
                   {'container_name': 'HW_2', 'proto': 'http', 'port': '80', 'addr': '10.7.0.3'}]}
        mock_vhosts.return_value = [
            {'service_alias': 'HW', 'path': '', 'host': 'a.com', 'scheme': 'http', 'port': '80'}]
        self.assertEqual(OrderedDict([('backend SERVICE_HW', ['balance source',
                                                              'server HW_1 10.7.0.2:80 check extra settings',
                                                              'server HW_2 10.7.0.3:80 check extra settings'])]),
                         haproxy._config_backend_sections())

        haproxy = Haproxy()
        haproxy.specs = Specs()
        mock_details.return_value = {'HW': {'balance': "source",
                                            'health_check': "check"}}
        mock_services.return_value = ["HW"]
        mock_routes.return_value = {
            'HW': [{'container_name': 'HW_1', 'proto': 'http', 'port': '80', 'addr': '10.7.0.2'},
                   {'container_name': 'HW_2', 'proto': 'http', 'port': '80', 'addr': '10.7.0.3'}]}
        mock_vhosts.return_value = []
        self.assertEqual({}, haproxy._config_backend_sections())

        haproxy = Haproxy()
        haproxy.specs = Specs()
        haproxy.require_default_route = True
        mock_details.return_value = {'HW': {'balance': "source",
                                            'health_check': "check"}}
        mock_services.return_value = ["HW"]
        mock_routes.return_value = {
            'HW': [{'container_name': 'HW_1', 'proto': 'http', 'port': '80', 'addr': '10.7.0.2'},
                   {'container_name': 'HW_2', 'proto': 'http', 'port': '80', 'addr': '10.7.0.3'}]}
        mock_vhosts.return_value = []
        self.assertEqual(OrderedDict([('backend default_service', ['balance source',
                                                                   'server HW_1 10.7.0.2:80 check',
                                                                   'server HW_2 10.7.0.3:80 check'])]),
                         haproxy._config_backend_sections())
