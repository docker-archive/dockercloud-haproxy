import unittest

import mock

from haproxy.helper.update_helper import *


class UpdateHelperTestCase(unittest.TestCase):
    class blockingObject(object):
        terminated = False
        timeout = None

        def __init__(self, timeout):
            self.timeout = timeout

        def wait(self):
            startTime = time.time()
            # block until waiting == true or we've hit the timeout
            while self.terminated == False and time.time() < startTime + self.timeout:
                time.sleep(0.5)

        def poll(self):
            return None

        def terminate(self):
            self.terminated = True
            
        def communicate(self):
            return ("", "")

        pass

    class Object(object):
      returncode = 0
      
      def communicate(self):
        return ("", "")
      
      pass

    @mock.patch("haproxy.helper.update_helper.subprocess.Popen")
    def test_run_graceful_reload_within_timeout(self, mock_popen):
        old_process = UpdateHelperTestCase.blockingObject(2)
        old_process.pid = "old_pid"
        new_process = UpdateHelperTestCase.Object()
        new_process.pid = "new_pid"
        mock_popen.return_value = new_process
        run_reload(old_process, 5)
        self.assertFalse(old_process.terminated)

    @mock.patch("haproxy.helper.update_helper.subprocess.Popen")
    def test_run_graceful_reload_exceeding_timeout(self, mock_popen):
        old_process = UpdateHelperTestCase.blockingObject(10)
        old_process.pid = "old_pid"
        new_process = UpdateHelperTestCase.Object()
        new_process.pid = "new_pid"
        mock_popen.return_value = new_process
        run_reload(old_process, 5)
        self.assertTrue(old_process.terminated)

    @mock.patch("haproxy.helper.update_helper.threading.Thread")
    @mock.patch("haproxy.helper.update_helper.subprocess.Popen")
    def test_run_graceful_reload_with_old_process(self, mock_popen, mock_new_thread):
        old_process = UpdateHelperTestCase.Object()
        old_process.pid = "old_pid"
        new_process = UpdateHelperTestCase.Object()
        new_process.pid = "new_pid"
        mock_popen.return_value = new_process
        run_reload(old_process, 0)
        mock_popen.assert_called_with(HAPROXY_RUN_COMMAND + ['-sf', 'old_pid'])
        mock_new_thread.assert_called_with(target=wait_pid, args=[old_process, 0])

    @mock.patch("haproxy.helper.update_helper.threading.Thread")
    @mock.patch("haproxy.helper.update_helper.subprocess.Popen")
    def test_run_brutal_reload_with_old_process(self, mock_popen, mock_new_thread):
        old_process = UpdateHelperTestCase.Object()
        old_process.pid = "old_pid"
        new_process = UpdateHelperTestCase.Object()
        new_process.pid = "new_pid"
        mock_popen.return_value = new_process
        run_reload(old_process, -1)
        mock_popen.assert_called_with(HAPROXY_RUN_COMMAND + ['-st', 'old_pid'])
        mock_new_thread.assert_called_with(target=wait_pid, args=[old_process, -1])

    @mock.patch("haproxy.helper.update_helper.threading.Thread")
    @mock.patch("haproxy.helper.update_helper.subprocess.Popen")
    def test_run_reload_with_empty_old_process(self, mock_popen, mock_new_thread):
        new_process = UpdateHelperTestCase.Object()
        new_process.pid = "new_pid"
        mock_popen.return_value = new_process
        run_reload(None)
        mock_popen.assert_called_with(HAPROXY_RUN_COMMAND)
