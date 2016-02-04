import unittest

import mock

from haproxy.helper.ssl_helper import *


class SslHelperTestCase(unittest.TestCase):
    def test_get_extra_ssl_certs(self):
        os.environ["TEST_CERT1"] = "CERT1"
        os.environ["TEST_CERT2"] = "CERT2"
        os.environ["TEST_CERT3"] = "CERT3"
        self.assertEqual([], get_extra_ssl_certs(""))
        self.assertEqual(["CERT1"], get_extra_ssl_certs("TEST_CERT1"))
        self.assertEqual(["CERT1", "CERT2", "CERT3"], get_extra_ssl_certs("TEST_CERT1, TEST_CERT2  ,   TEST_CERT3  "))
        self.assertEqual([], get_extra_ssl_certs("NOT_EXIST_TEST_CERT"))
        self.assertEqual(["CERT1"], get_extra_ssl_certs("TEST_CERT1, TEST_CERT4"))

    @mock.patch("haproxy.helper.ssl_helper.save_to_file")
    @mock.patch("haproxy.helper.ssl_helper.os.makedirs")
    @mock.patch("haproxy.helper.ssl_helper.os.path.exists")
    def test_save_certs_path_exist(self, mock_exists, mock_make_dirs, mock_save_to_file):
        mock_exists.return_value = True
        save_certs("/test/path/", ["cert1"])
        self.assertFalse(mock_make_dirs.called)
        mock_save_to_file.assert_called_with("/test/path/cert0.pem", 'cert1')

    @mock.patch("haproxy.helper.ssl_helper.save_to_file")
    @mock.patch("haproxy.helper.ssl_helper.os.makedirs")
    @mock.patch("haproxy.helper.ssl_helper.os.path.exists")
    def test_save_certs_path_not_exist(self, mock_exists, mock_make_dirs, mock_save_to_file):
        mock_exists.return_value = False
        save_certs("/test/path", ["cert\\n1"])
        mock_make_dirs.assert_called_with("/test/path")
        mock_save_to_file.assert_called_with("/test/path/cert0.pem", 'cert\n1')

    @mock.patch("haproxy.helper.ssl_helper.save_to_file")
    @mock.patch("haproxy.helper.ssl_helper.os.makedirs")
    @mock.patch("haproxy.helper.ssl_helper.os.path.exists")
    def test_save_certs_multiple_certs(self, mock_exists, mock_make_dirs, mock_save_to_file):
        mock_exists.return_value = False
        save_certs("/test/path", ["cert\\n1", "cert2"])
        mock_make_dirs.assert_called_with("/test/path")
        mock_save_to_file.assert_any_call("/test/path/cert0.pem", 'cert\n1')
        mock_save_to_file.assert_any_call("/test/path/cert1.pem", 'cert2')
