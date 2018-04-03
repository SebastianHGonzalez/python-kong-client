import unittest
from unittest.mock import MagicMock

from kong.kong_clients import RouteAdminClient


class RouteAdminTest(unittest.TestCase):

    def setUp(self):
        self.service = MagicMock()
        self.service.id = "4e13f54a-bbf1-47a8-8777-255fed7116f2"

        self.session = MagicMock()
        self.session.post.return_value.status_code = 201

        self.kong_url = 'http://kog.url/'
        self.routes_endpoint = self.kong_url + 'routes/'

        self.route_admin_client = RouteAdminClient(self.kong_url, _session=self.session)

    def test_create_route_w_service(self):
        self.create_and_assert(self.service)

    def test_create_route_w_service_id(self):
        self.create_and_assert(self.service.id)

    def create_and_assert(self, service_id):
        # Setup
        methods = ['GET', 'POST']
        # Exercise
        self.route_admin_client.create(service=service_id, methods=methods)
        # Verify
        expected_data = {'service': {'id': self.service.id}, 'methods': methods}
        self.session.post.assert_called_once_with(self.routes_endpoint, data=expected_data)
