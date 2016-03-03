import unittest

from haproxy.config import parse_extra_bind_settings


class ParseExtraBindSettings(unittest.TestCase):
    def test_parse_extra_bind_settings(self):
        self.assertEqual({}, parse_extra_bind_settings(""))
        self.assertEqual({"80": "name http"}, parse_extra_bind_settings("80:name http"))
        self.assertEqual({"80": "name  http"}, parse_extra_bind_settings(" 80 : name  http  "))
        self.assertEqual({"80": "name http", "443": "accept-proxy"},
                         parse_extra_bind_settings(" 443:accept-proxy  , 80:name http "))
        self.assertEqual({"80": "name, http", "443": "accept,-proxy"},
                         parse_extra_bind_settings(" 443:accept\,-proxy, 80:name\, http "))
