import logging
import unittest

import mock

from haproxy import config
from haproxy.eventhandler import on_cloud_event
from haproxy.haproxycfg import Haproxy

logging.disable(logging.CRITICAL)


class OnCloudEventTestCase(unittest.TestCase):
    def setUp(self):
        self.linked_services = Haproxy.cls_linked_services
        Haproxy.cls_linked_services = set(["/svc/a/", "/svc/b/", "/svc/c/"])
        self.service_uri = config.HAPROXY_SERVICE_URI
        config.HAPROXY_SERVICE_URI = "/svc/uuid/"

    def tearDown(self):
        Haproxy.cls_linked_services = self.linked_services
        config.HAPROXY_SERVICE_URI = self.service_uri

    @mock.patch("haproxy.eventhandler.run_haproxy")
    def test_event_reload_in_service_opterations(self, mock_run_haproxy):
        not_triggered_event_01 = '{}'
        not_triggered_event_02 = '{"state": "In progress", "type": "container", "parents": ["/svc/a/"]}'
        not_triggered_event_03 = '{"state": "Pending", "type": "container", "parents": ["/svc/a/"]}'
        not_triggered_event_04 = '{"state": "Terminating", "type": "container", "parents": ["/svc/a/"]}'
        not_triggered_event_05 = '{"state": "Starting", "type": "container", "parents": ["/svc/a/"]}'
        not_triggered_event_06 = '{"state": "Scaling", "type": "container", "parents": ["/svc/a/"]}'
        not_triggered_event_07 = '{"state": "Stopping", "type": "container", "parents": ["/svc/a/"]}'
        not_triggered_event_08 = '{"state": "Running", "type": "node", "parents": ["/svc/a/"]}'
        not_triggered_event_09 = '{"state": "Running", "type": "container", "parents": ["/svc/d/"]}'

        on_cloud_event(not_triggered_event_01)
        on_cloud_event(not_triggered_event_02)
        on_cloud_event(not_triggered_event_03)
        on_cloud_event(not_triggered_event_04)
        on_cloud_event(not_triggered_event_05)
        on_cloud_event(not_triggered_event_06)
        on_cloud_event(not_triggered_event_07)
        on_cloud_event(not_triggered_event_08)
        on_cloud_event(not_triggered_event_09)

        self.assertEqual(0, mock_run_haproxy.call_count)

        triggered_event_01 = '{"state": "Stopped", "type": "container", "parents": ["/svc/a/"]}'
        triggered_event_02 = '{"state": "Started", "type": "container", "parents": ["/svc/a/"]}'
        triggered_event_03 = '{"state": "Running", "type": "container", "parents": ["/svc/a/"]}'
        triggered_event_04 = '{"state": "Running", "type": "service", "parents": ["/svc/a/"]}'
        triggered_event_05 = '{"state": "Running", "type": "container", "parents": ["/svc/b/"]}'
        triggered_event_06 = '{"state": "Running", "type": "container", "parents": ["/svc/b/", "/svc/b/"]}'
        triggered_event_07 = '{"state": "Running", "type": "container", "parents": ["/svc/a/", "/svc/b/", "/svc/c/"]}'

        on_cloud_event(triggered_event_01)
        on_cloud_event(triggered_event_02)
        on_cloud_event(triggered_event_03)
        on_cloud_event(triggered_event_04)
        on_cloud_event(triggered_event_05)
        on_cloud_event(triggered_event_06)
        on_cloud_event(triggered_event_07)

        self.assertEqual(7, mock_run_haproxy.call_count)

    @mock.patch("haproxy.eventhandler.run_haproxy")
    def test_event_reload_in_link_opterations(self, mock_run_haproxy):
        not_triggered_event_01 = '{}'
        not_triggered_event_02 = '{"state": "Failed", "parents": ["/svc/a/"]}'
        not_triggered_event_03 = '{"state": "Success", "parents": ["/svc/a/"]}'
        not_triggered_event_04 = '{"state": "Success", "parents": []}'

        on_cloud_event(not_triggered_event_01)
        on_cloud_event(not_triggered_event_02)
        on_cloud_event(not_triggered_event_03)
        on_cloud_event(not_triggered_event_04)
        self.assertEqual(0, mock_run_haproxy.call_count)

        triggered_event_01 = '{"state": "Success", "parents": ["/svc/uuid/"]}'
        triggered_event_02 = '{"state": "Success", "parents": ["/svc/a/", "/svc/uuid/"]}'

        on_cloud_event(triggered_event_01)
        on_cloud_event(triggered_event_02)
        self.assertEqual(2, mock_run_haproxy.call_count)
