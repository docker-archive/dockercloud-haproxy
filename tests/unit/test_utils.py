import logging
import os
import tempfile
import unittest
import uuid

import dockercloud
import mock

from haproxy.config import API_RETRY
from haproxy.utils import fetch_remote_obj, get_uuid_from_resource_uri, save_to_file, get_service_attribute, prettify, \
    get_bind_string

logging.disable(logging.CRITICAL)


class FetchRemoteObjTestCase(unittest.TestCase):
    def setUp(self):
        self.container = dockercloud.Container.create()

    @mock.patch("haproxy.utils.dockercloud.Utils.fetch_by_resource_uri")
    def test_fetch_remote_object(self, mock_fetch_by_resource_uri):
        self.assertIsNone(fetch_remote_obj(""))
        mock_fetch_by_resource_uri.return_value = self.container
        self.assertEqual(self.container, fetch_remote_obj("uri"))

    @mock.patch("haproxy.utils.time.sleep")
    @mock.patch("haproxy.utils.dockercloud.Utils.fetch_by_resource_uri")
    def test_fetch_remote_object_with_exception(self, mock_fetch_by_resource_uri, mock_sleep):
        mock_fetch_by_resource_uri.side_effect = [dockercloud.ObjectNotFound("This is an error"), self.container]
        self.assertEqual(self.container, fetch_remote_obj("uri"))
        mock_sleep.assert_called_once_with(API_RETRY)


class GetUuidFromResourceUriTestCase(unittest.TestCase):
    def test_get_uuid_from_resource_uri(self):
        self.assertEqual("uuid", get_uuid_from_resource_uri("/api/app/v1/container/uuid/"))
        self.assertEqual("uuid", get_uuid_from_resource_uri("/api/app/v1/container/uuid"))
        self.assertEqual("", get_uuid_from_resource_uri("uuid"))


class SaveToFileTestCase(unittest.TestCase):
    def setUp(self):
        self.f = tempfile.TemporaryFile()

    def tearDown(self):
        self.f.close()
        try:
            os.remove(self.f.name)
        except:
            pass

    def test_save_to_file(self):
        content = str(uuid.uuid4())
        self.assertTrue(save_to_file(self.f.name, content))
        txt = open(self.f.name).read()
        self.assertEqual(content, txt)

    def test_save_to_file_with_error(self):
        self.assertFalse(save_to_file("/", "something"))


class PrettifyTestCase(unittest.TestCase):
    def test_prettify(self):
        input = {"frontend port_80": ["listen 80", "timeout 80000"], "backend port_80": ["server 0.0.0.0:80"]}
        output1 = """frontend port_80
  listen 80
  timeout 80000
backend port_80
  server 0.0.0.0:80"""
        output2 = """frontend port_80
##listen 80
##timeout 80000
backend port_80
##server 0.0.0.0:80"""
        self.assertEqual(output1, prettify(input))
        self.assertEqual(output1, prettify(input, indent="  "))
        self.assertEqual(output2, prettify(input, indent="##"))


class GetServiceAttributeTestCase(unittest.TestCase):
    def setUp(self):
        self.details = {'web-a': {'attrA': 'valueA', 'attrB': 'valueB'},
                        'web-b': {'attrA': 'valueC', 'attrD': 'valueD'}}

    def test_get_service_attribute_with_service_aliase(self):
        self.assertEqual("valueA", get_service_attribute(self.details, 'attrA', 'web-a'))
        self.assertEqual("valueB", get_service_attribute(self.details, 'attrB', 'web-a'))
        self.assertEqual(None, get_service_attribute(self.details, 'attrC', 'web-a'))
        self.assertEqual("valueC", get_service_attribute(self.details, 'attrA', 'web-b'))
        self.assertEqual("valueB", get_service_attribute(self.details, 'attrB', 'web-a'))
        self.assertEqual(None, get_service_attribute(self.details, 'attrC', 'web-a'))
        self.assertEqual(None, get_service_attribute(self.details, 'attrA', 'web-c'))
        self.assertEqual(None, get_service_attribute(None, 'attrA', 'web-a'))

    def test_get_servide_attribute_without_service_aliase(self):
        self.assertIn(get_service_attribute(self.details, 'attrA'), ['valueA', 'valueC'])
        self.assertEqual(get_service_attribute(self.details, 'attrB'), "valueB")
        self.assertEqual(get_service_attribute(self.details, 'attrD'), "valueD")
        self.assertIsNone(get_service_attribute(self.details, 'attrE'))


class GetBindStringTestCase(unittest.TestCase):
    def setUp(self):
        self.bind_settings = {'80': "name http", "443": "accept-proxy"}

    def test_get_bind_string(self):
        self.assertEqual("80 name http ssl crt /certs/",
                         get_bind_string(enable_ssl=True, port_num="80", ssl_bind_string="ssl crt /certs/",
                                         bind_settings=self.bind_settings))
        self.assertEqual("80 name http",
                         get_bind_string(enable_ssl=False, port_num="80", ssl_bind_string="ssl crt /certs/",
                                         bind_settings=self.bind_settings))
        self.assertEqual("3306 ssl crt /certs/",
                         get_bind_string(enable_ssl=True, port_num="3306", ssl_bind_string="ssl crt /certs/",
                                         bind_settings=self.bind_settings))
        self.assertEqual("3306",
                         get_bind_string(enable_ssl=False, port_num="3306", ssl_bind_string="ssl crt /certs/",
                                         bind_settings=self.bind_settings))
        self.assertEqual("443 accept-proxy ssl crt /certs/",
                         get_bind_string(enable_ssl=True, port_num="443", ssl_bind_string="ssl crt /certs/",
                                         bind_settings=self.bind_settings))
        self.assertEqual("443 ssl crt /certs/",
                         get_bind_string(enable_ssl=True, port_num="443", ssl_bind_string="ssl crt /certs/",
                                         bind_settings={}))
        self.assertEqual("443",
                         get_bind_string(enable_ssl=False, port_num="443", ssl_bind_string="ssl crt /certs/",
                                         bind_settings={}))
        self.assertEqual("443 accept-proxy", get_bind_string(enable_ssl=True, port_num="443", ssl_bind_string="",
                                                             bind_settings=self.bind_settings))
        self.assertEqual("443", get_bind_string(enable_ssl=True, port_num="443", ssl_bind_string="", bind_settings={}))
