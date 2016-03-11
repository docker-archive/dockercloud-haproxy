import os
import unittest

import mock

from haproxy.main import create_pid_file


class CreatePidFileTestCase(unittest.TestCase):
    @mock.patch("haproxy.utils.save_to_file")
    def test_create_pid_file(self, mock_save_to_file):
        pid = str(os.getpid())
        mock_save_to_file.asser_called()
        self.assertEqual(pid, create_pid_file())
