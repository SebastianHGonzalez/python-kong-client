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
        self.api_kong_id = self.faker.kong_id()

        hosts = self.faker.domain_name()
        methods = ["GET", "POST"]
        strip_uri = self.faker.boolean()
        preserve_host = self.faker.boolean()
        retries = self.faker.random_int()
        https_only = self.faker.boolean()
        http_if_terminated = self.faker.boolean()
        upstream_connect_timeout = self.faker.random_int()
        upstream_send_timeout = self.faker.random_int()
        upstream_read_timeout = self.faker.random_int()

        self.api_data = ApiData(name=self.api_name,
                                upstream_url=self.api_upstream_url,
                                uris=self.api_uris,
                                hosts=hosts,
                                methods=methods,
                                strip_uri=strip_uri,
                                preserve_host=preserve_host,
                                retries=retries,
                                https_only=https_only,
                                http_if_terminated=http_if_terminated,
                                upstream_connect_timeout=upstream_connect_timeout,
                                upstream_send_timeout=upstream_send_timeout,
                                upstream_read_timeout=upstream_read_timeout)

        self.requests_mock = MagicMock()
        self.requests_mock.post = MagicMock()

        self.requests_mock.post.return_value.json = lambda: {**self.api_data, **{'id': self.api_kong_id}}

        self.kong_admin_url = self.faker.url()
        self.apis_endpoint = self.kong_admin_url + 'apis/'

        self.api_admin_client = ApiAdminClient(self.kong_admin_url, requests_module=self.requests_mock)
    #    self.api_admin_client = ApiAdminClient('http://localhost:8001/')

    def test_api_admin_create(self):
        """
            Test: ApiAdminClient.create() creates a api data dictionary
            instance with given api's data.
        """

        # Exercise
        api_data = self.api_admin_client.create_api(self.api_name, self.api_upstream_url, uris=self.api_uris)

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
        self.api_admin_client.create_api(self.api_name, self.api_upstream_url, uris=self.api_uris)

        # Verify
        expected_api_data = ApiData(name=self.api_name,
                                    upstream_url=self.api_upstream_url,
                                    uris=self.api_uris)
        self.requests_mock.post.assert_called_once_with(self.apis_endpoint,
                                                        data=dict(expected_api_data))

    def test_api_admin_create_using_api_data(self):
        """
            Test: passing a ApiData instance results in the same behaviour
            as normal create
        """
        # Setup
        orig_data = ApiData(name=self.api_name, upstream_url=self.api_upstream_url, uris=self.api_uris)

        # Exercise
        api_data = self.api_admin_client.create_api(orig_data)

        # Verify
        self.requests_mock.post.assert_called_once_with(self.apis_endpoint, data=dict(orig_data))

    def test_api_admin_delete_by_name(self):
        """
            Test: ApiAdmin.delete(api_name) deletes it from kong server
        """
        # Setup
        self.api_admin_client.create_api(self.api_name, self.api_upstream_url, uris=self.api_uris)

        # Exercise
        self.api_admin_client.delete_api(self.api_name)

        # Verify
        expected_data = {}
        api_endpoint = self.apis_endpoint + self.api_name
        self.requests_mock.delete.assert_called_once_with(api_endpoint, data=expected_data)

    def test_api_admin_delete_by_kong_id(self):
        """
            Test: ApiAdmin.delete(api_kong_id) deletes it from kong server
        """
        # Setup
        self.api_admin_client.create_api(self.api_name, self.api_upstream_url, uris=self.api_uris)

        # Exercise
        self.api_admin_client.delete_api(self.api_kong_id)

        # Verify
        expected_data = {}
        api_endpoint = self.apis_endpoint + self.api_kong_id
        self.requests_mock.delete.assert_called_once_with(api_endpoint, data=expected_data)

    def test_api_admin_delete_by_api_data(self):
        """
            Test: ApiAdmin.delete(api_data) deletes it from kong server
        """
        # Setup
        api_data = self.api_admin_client.create_api(self.api_name, self.api_upstream_url, uris=self.api_uris)

        # Exercise
        self.api_admin_client.delete_api(api_data)

        # Verify
        expected_data = {}
        api_endpoint = self.apis_endpoint + self.api_name
        self.requests_mock.delete.assert_called_once_with(api_endpoint, data=expected_data)

    def test_api_admin_update(self):
        """
            Test: ApiAdmin.update(api_data) updates it in kong server
        """
        # Setup
        api_data = self.api_admin_client.create_api(self.api_name, self.api_upstream_url, uris=self.api_uris)
        new_uri = self.faker.api_path()

        # Exercise
        api_data.add_uri(new_uri)
        self.api_admin_client.update_api(api_data)

        # Verify
        expected_data = dict(api_data)
        api_endpoint = self.apis_endpoint + self.api_name
        self.requests_mock.patch.assert_called_once_with(api_endpoint, data=expected_data)
