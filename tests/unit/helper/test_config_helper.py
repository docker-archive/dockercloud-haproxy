import unittest

from haproxy.helper.config_helper import *


class ConfigHelperTestCase(unittest.TestCase):
    def test_config_ssl_bind_options(self):
        self.assertEqual([], config_ssl_bind_options(""))
        self.assertEqual(["ssl-default-bind-options ssl_bind_option"], config_ssl_bind_options("ssl_bind_option"))

    def test_config_ssl_bind_ciphers(self):
        self.assertEqual([], config_ssl_bind_ciphers(""))
        self.assertEqual(["ssl-default-bind-ciphers AES"], config_ssl_bind_ciphers("AES"))

    def test_extra_setting(self):
        self.assertEqual([], config_extra_settings(""))
        self.assertEqual(["abc"], config_extra_settings("abc"))
        self.assertEqual(["abc", "def", "abc"], config_extra_settings("abc, def  ,abc  "))
        self.assertEqual(["abc", "def", "abc"], config_extra_settings("abc, def  ,abc  "))
        self.assertEqual(["ab,c", "def", "abc"], config_extra_settings("ab\,c, def  ,abc  "))

    def test_config_option(self):
        self.assertEqual([], config_option(""))
        self.assertEqual(["option aa"], config_option("aa"))
        self.assertEqual(["option aa", "option bb", "option cc"], config_option("aa,  bb  ,cc "))

    def test_config_timeout(self):
        self.assertEqual([], config_timeout(""))
        self.assertEqual(["timeout aa"], config_timeout("aa"))
        self.assertEqual(["timeout aa", "timeout bb", "timeout cc"], config_timeout("aa,  bb  ,cc "))
