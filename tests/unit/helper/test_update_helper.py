import unittest

import mock

from haproxy.helper.update_helper import *


class UpdateHelperTestCase(unittest.TestCase):
    class Object(object):
        pass

    @mock.patch("haproxy.helper.update_helper.thread.start_new_thread")
    @mock.patch("haproxy.helper.update_helper.subprocess.Popen")
    def test_run_reload_with_old_process(self, mock_popen, mock_new_thread):
        old_process = UpdateHelperTestCase.Object()
        old_process.pid = "pid"
        new_process = UpdateHelperTestCase.Object()
        new_process.pid = "new_pid"
        mock_popen.return_value = new_process
        mock_popen.return_value = old_process
        run_reload(old_process)
        mock_popen.assert_called_with(HAPROXY_RUN_COMMAND + ['-sf', 'pid'])
        mock_new_thread.caslled_with(wait_pid, (old_process,))

    @mock.patch("haproxy.helper.update_helper.thread.start_new_thread")
    @mock.patch("haproxy.helper.update_helper.subprocess.Popen")
    def test_run_reload_with_empty_old_process(self, mock_popen, mock_new_thread):
        new_process = UpdateHelperTestCase.Object()
        new_process.pid = "new_pid"
        mock_popen.return_value = new_process
        run_reload(None)
        mock_popen.assert_called_with(HAPROXY_RUN_COMMAND)
