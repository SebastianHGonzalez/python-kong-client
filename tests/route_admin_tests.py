from abc import abstractmethod
import pytest

import unittest
from unittest.mock import MagicMock

import requests

from kong.kong_clients import RouteAdminClient, ServiceAdminClient


class RouteAdminAbstractTests:

    def setUp(self):
        self.route_admin_client = RouteAdminClient(self.kong_url, _session=self.session)

    def test_create_route_w_service(self):
        self.create_and_assert(self.service)

    def test_create_route_w_service_id(self):
        self.create_and_assert(self.service.id)

    def test_retrieve_routes_associated_to_service(self):
        # Exercise
        generator = self.route_admin_client.list_associated_to_service(self.service.id)

        # Verify
        self.assert_retrieve_routes_associated_to_service(generator)

    @abstractmethod
    def assert_retrieve_routes_associated_to_service(self, result):
        pass


class RouteAdminMockedTests(RouteAdminAbstractTests, unittest.TestCase):

    def setUp(self):
        self.service_dict = {
            "id": "22108377-8f26-4c0e-bd9e-2962c1d6b0e6",
            "created_at": 14888869056483,
            "updated_at": 14888869056483,
            "protocols": ["http", "https"],
            "methods": None,
            "hosts": ["example.com"],
            "paths": None,
            "regex_priority": 0,
            "strip_path": True,
            "preserve_host": False,
            "service": {
                "id": "4e13f54a-bbf1-47a8-8777-255fed7116f2"
            }
        }

        self.mock_setup()
        super().setUp()

    def mock_setup(self):
        self.service = MagicMock()
        self.service.id = "4e13f54a-bbf1-47a8-8777-255fed7116f2"
        self.session = MagicMock()

        self.session.post.return_value.status_code = 201

        self.session.post.return_value.json.return_value = self.service_dict

        self.kong_url = 'http://kong.url/'
        self.routes_endpoint = self.kong_url + 'routes/'

    def create_and_assert(self, service_id):
        # Setup
        methods = ['GET']
        # Exercise
        self.route_admin_client.create(service=service_id, methods=methods)
        # Verify
        expected_data = {'service': {'id': self.service.id}, 'methods': methods}
        self.session.post.assert_called_once_with(self.routes_endpoint, json=expected_data)

    def assert_retrieve_routes_associated_to_service(self, result):
        self.session.get.return_value.status_code = 200
        try:
            result.__next__()
        except StopIteration:
            pass
        # Verify
        self.session.get\
            .assert_called_once_with('%sservices/%s/routes/' % (self.kong_url, self.service.id),
                                     data={'offset': None, 'size': 10})


@pytest.mark.slow
class RouteAdminServerTests(RouteAdminAbstractTests, unittest.TestCase):

    def setUp(self):
        self.kong_url = 'http://localhost:8001/'
        self.session = requests.session()

        self.service_admin_client = ServiceAdminClient(self.kong_url)

        self.service = self.service_admin_client.create(name='test-service',
                                                        url='http://test.service/path')
        super().setUp()

    def tearDown(self):
        self.route_admin_client.delete(self.created.id)
        self.created = None
        self.service_admin_client.delete(self.service.id)
        self.service = None

    def create_and_assert(self, service_or_id):
        # Setup
        methods = ['GET', 'POST']
        # Exercise
        self.created = self.route_admin_client.create(
            service=service_or_id, methods=methods)
        # Verify
        self.assertEqual(methods, self.created.methods)

    def assert_retrieve_routes_associated_to_service(self, result):
        routes_list = list(result)
        self.assertEqual(0, len(routes_list))

        self.created = self.route_admin_client.create(
            service=self.service.id, paths=['/test-path'])
        routes_list = list(self.route_admin_client.list_associated_to_service(self.service.id))
        self.assertEqual(1, len(routes_list))
