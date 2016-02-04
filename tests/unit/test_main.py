import os
import unittest

import mock

from haproxy.main import create_pid_file, set_autoreload


class CreatePidFileTestCase(unittest.TestCase):
    @mock.patch("haproxy.utils.save_to_file")
    def test_create_pid_file(self, mock_save_to_file):
        pid = str(os.getpid())
        mock_save_to_file.asser_called()
        self.assertEqual(pid, create_pid_file())


class AutoReloadTestCase(unittest.TestCase):
    def test_set_autoreload(self):
        self.assertTrue(set_autoreload("container_uri", "service_uri", "api_auth"))
        self.assertFalse(set_autoreload(None, "service_uri", "api_auth"))
        self.assertFalse(set_autoreload("container_uri", None, "api_auth"))
        self.assertFalse(set_autoreload("container_uri", "service_uri", None))
        self.assertFalse(set_autoreload(None, None, None))
