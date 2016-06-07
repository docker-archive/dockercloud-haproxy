import unittest
from copy import copy

import dockercloud

from haproxy.helper.cloud_link_helper import _init_links, _get_new_added_link_uri, _get_linked_containers, \
    get_service_links_str, get_container_links_str, get_linked_services, _update_container_cache, _update_links


class CloudLinkHelperTestCase(unittest.TestCase):
    def setUp(self):
        self.container_links = [
            {"endpoints": {"80/tcp": "tcp://10.7.0.1:80"},
             "name": "hello-1",
             "from_container": "/api/app/v1/container/8e0cf8e4-3e51-433d-a0f8-df7f23ef38a5/",
             "to_container": "/api/app/v1/container/418768e3-530c-4e8f-8ba9-9ae27f72768d/"
             },
            {"endpoints": {"80/tcp": "tcp://10.7.0.3:80"},
             "name": "world-1",
             "from_container": "/api/app/v1/container/8e0cf8e4-3e51-433d-a0f8-df7f23ef38a5/",
             "to_container": "/api/app/v1/container/af5cdd7b-9af8-49d2-a3b2-308dbc187dd8/"
             }]
        self.links = {'/api/app/v1/container/af5cdd7b-9af8-49d2-a3b2-308dbc187dd8/':
                          {'service_name': 'WORLD',
                           'container_uri': '/api/app/v1/container/af5cdd7b-9af8-49d2-a3b2-308dbc187dd8/',
                           'endpoints': {'80/tcp': 'tcp://10.7.0.3:80'},
                           'container_name': 'WORLD_1'},
                      '/api/app/v1/container/418768e3-530c-4e8f-8ba9-9ae27f72768d/':
                          {'service_name': 'HELLO',
                           'container_uri': '/api/app/v1/container/418768e3-530c-4e8f-8ba9-9ae27f72768d/',
                           'endpoints': {'80/tcp': 'tcp://10.7.0.1:80'},
                           'container_name': 'HELLO_1'},
                      }

        self.new_links = {'/api/app/v1/container/418768e3-530c-4e8f-8ba9-9ae27f72768d/':
                              {'service_name': 'HELLO',
                               'container_uri': '/api/app/v1/container/418768e3-530c-4e8f-8ba9-9ae27f72768d/',
                               'container_envvars': [{'key': 'VIRTUAL_HOST', 'value': 'b.com'},
                                                     {'key': 'MODE', 'value': 'tcp'},
                                                     {'key': 'HELLO_1_ENV_NOT_SHOWN', 'value': 'not_shown'}],
                               'service_uri': '/api/app/v1/service/bc091010-0054-4cc6-9038-73ea1efc5b99/',
                               'container_name': 'HELLO_1',
                               'endpoints': {
                                   '80/tcp': 'tcp://10.7.0.1:80'}},
                          '/api/app/v1/container/af5cdd7b-9af8-49d2-a3b2-308dbc187dd8/':
                              {'service_name': 'WORLD',
                               'container_uri': '/api/app/v1/container/af5cdd7b-9af8-49d2-a3b2-308dbc187dd8/',
                               'container_envvars': [{'key': 'VIRTUAL_HOST', 'value': 'a.com'},
                                                     {'key': 'MODE', 'value': 'http'},
                                                     {'key': 'WORLD_1_ENV_NOT_SHOWN', 'value': 'a.com'}],
                               'service_uri': '/api/app/v1/service/0d12900d-2ae8-4244-a9c0-48466347c08a/',
                               'container_name': 'WORLD_1',
                               'endpoints': {
                                   '80/tcp': 'tcp://10.7.0.3:80'}}}
        container_a = dockercloud.Container.create()
        container_a.resource_uri = "/api/app/v1/container/af5cdd7b-9af8-49d2-a3b2-308dbc187dd8/"
        container_a.service = "/api/app/v1/service/0d12900d-2ae8-4244-a9c0-48466347c08a/"
        container_a.container_envvars = [{"value": "a.com", "key": "VIRTUAL_HOST"},
                                         {"value": "http", "key": "MODE"},
                                         {"value": "a.com", "key": "WORLD_1_ENV_NOT_SHOWN"}]
        self.container_a = container_a
        container_b = dockercloud.Container.create()
        container_b.resource_uri = "/api/app/v1/container/418768e3-530c-4e8f-8ba9-9ae27f72768d/"
        container_b.service = "/api/app/v1/service/bc091010-0054-4cc6-9038-73ea1efc5b99/"
        container_b.container_envvars = [{"value": "b.com", "key": "VIRTUAL_HOST"},
                                         {"value": "tcp", "key": "MODE"},
                                         {"value": "not_shown", "key": "HELLO_1_ENV_NOT_SHOWN"}]
        self.container_b = container_b

    def test_init_links(self):
        self.assertEqual(self.links, _init_links(self.container_links))
        self.assertEqual({}, _init_links([]))

    def test_get_new_added_links_uri(self):
        self.assertEqual([x for x in self.links], _get_new_added_link_uri({}, self.links))

        self.assertEqual([x for x in self.links if x != '/api/app/v1/container/184f7099-53a2-4223-a3df-a9ce73075625/'],
                         _get_new_added_link_uri({'/api/app/v1/container/184f7099-53a2-4223-a3df-a9ce73075625/': {}},
                                                 self.links))
        self.assertEqual([x for x in self.links if x != '/api/app/v1/container/184f7099-53a2-4223-a3df-a9ce73075625/'
                          and x != '/api/app/v1/container/1d84a62c-7fb2-42dc-b1e7-047bcc27e119/'],
                         _get_new_added_link_uri({'/api/app/v1/container/184f7099-53a2-4223-a3df-a9ce73075625/': {},
                                                  '/api/app/v1/container/1d84a62c-7fb2-42dc-b1e7-047bcc27e119/': {}},
                                                 self.links))

    def test_update_container_cache(self):
        cache = {}
        container_a = dockercloud.Container.create()
        container_a_uri = "uri_a"
        container_b = dockercloud.Container.create()
        container_b_uri = "uri_b"

        _update_container_cache(cache, [], {})
        self.assertEqual({}, cache)
        _update_container_cache(cache, [container_a_uri], [container_a])
        self.assertEqual({container_a_uri: container_a}, cache)
        _update_container_cache(cache, [container_a_uri], [container_b])
        self.assertEqual({container_a_uri: container_b}, cache)
        _update_container_cache(cache, [container_a_uri, container_b_uri], [container_a, container_b])
        self.assertEqual({container_a_uri: container_a, container_b_uri: container_b}, cache)

    def test_update_links(self):
        old_links = copy(self.links)
        _update_links(old_links, [self.container_a, self.container_b])
        self.assertEqual(self.new_links, old_links)

    def test_get_linked_containers(self):
        container_a = dockercloud.Container.create()
        container_b = dockercloud.Container.create()
        cache = {'/api/app/v1/container/af5cdd7b-9af8-49d2-a3b2-308dbc187dd8/': container_a,
                 '/api/app/v1/container/418768e3-530c-4e8f-8ba9-9ae27f72768d/': container_b}
        self.assertEqual([container_b, container_a], _get_linked_containers(cache, self.container_links))

    def test_get_linked_service(self):
        self.assertEqual(set(['/api/app/v1/service/bc091010-0054-4cc6-9038-73ea1efc5b99/',
                          '/api/app/v1/service/0d12900d-2ae8-4244-a9c0-48466347c08a/']),
                         get_linked_services(self.new_links))

    def test_get_service_Links_str(self):
        self.assertEqual(['HELLO(bc091010-0054-4cc6-9038-73ea1efc5b99)', 'WORLD(0d12900d-2ae8-4244-a9c0-48466347c08a)'],
                         get_service_links_str(self.new_links))

    def test_get_container_links_str(self):
        self.assertEqual(['HELLO_1(418768e3-530c-4e8f-8ba9-9ae27f72768d)',
                          'WORLD_1(af5cdd7b-9af8-49d2-a3b2-308dbc187dd8)'],
                         get_container_links_str(self.new_links))
