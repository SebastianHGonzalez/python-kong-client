import unittest
from unittest.mock import MagicMock
from faker import Faker

from src.kong.providers import ApiDataProvider

from src.kong.clients import ApiAdminClient
from src.kong.data_structures import ApiData


class ApiAdminClientTest(unittest.TestCase):



    def setUp(self):
        self.faker = Faker()
        self.faker.add_provider(ApiDataProvider)
        self.api_name = self.faker.api_name()
        self.api_upstream_url = self.faker.url()
        self.api_uris = self.faker.api_uris()

        self.requests_mock = MagicMock()
        self.requests_mock.post = MagicMock()
        self.requests_mock.post.return_value = {'data': {'id': self.faker.kong_id()}}

        self.kong_admin_url = self.faker.url()
        self.apis_endpoint = self.kong_admin_url + 'apis/'

        self.api_admin_client = ApiAdminClient(self.kong_admin_url, requests_module=self.requests_mock)

    def test_api_admin_create(self):
        """
            Test: ApiAdminClient.create() creates a api data dictionary
            instance with given api's data.
        """

        # Exercise
        api_data = self.api_admin_client.create(self.api_name, self.api_upstream_url, uris=self.api_uris)

        # Verify
        self.assertEqual(api_data['name'], self.api_name)
        self.assertEqual(api_data['upstream_url'], self.api_upstream_url)
        self.assertEqual(api_data['uris'], self.api_uris)

    def test_api_admin_create_triggers_http_request_to_kong_server(self):
        """
            Test: ApiAdminClient.create() triggers an http request
            to kong server to create the api in the server.
        """
        # Exercise
        self.api_admin_client.create(self.api_name, self.api_upstream_url, uris=self.api_uris)

        # Verify
        expected_api_data = ApiData(self.api_name, self.api_upstream_url, uris=self.api_uris)
        self.requests_mock.post.assert_called_once_with(self.apis_endpoint, data=dict(expected_api_data))

    def test_api_admin_create_using_api_data(self):
        """
            Test: passing a ApiData instance results in the same behaviour
            as normal create
        """
        # Setup
        orig_data = ApiData(self.api_name, self.api_upstream_url, uris=self.api_uris)

        # Exercise
        api_data = self.api_admin_client.create(orig_data)

        # Verify
        expected_data = {**orig_data, **{'id': api_data['id']}}

        self.assertEqual(api_data, expected_data)
        self.requests_mock.post.assert_called_once_with(self.apis_endpoint, data=dict(orig_data))
