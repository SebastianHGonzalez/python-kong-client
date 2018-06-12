import unittest
from unittest.mock import MagicMock
from faker import Faker

from kong.providers import ApiDataProvider

from kong.kong_clients import ApiAdminClient
from kong.structures import ApiData


class ApiAdminClientTest(unittest.TestCase):

    def setUp(self):
        self.faker = Faker()
        self.faker.add_provider(ApiDataProvider)
        self.api_name = self.faker.api_name()
        self.api_upstream_url = self.faker.url()
        self.api_uris = self.faker.api_uris()
        self.api_kong_id = self.faker.kong_id()

        hosts = [self.faker.domain_name() for _ in range(self.faker.random_int(0, 10))]
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
        self.session_mock = MagicMock()
        self.requests_mock.session.return_value = self.session_mock

        data_w_id = {**self.api_data.as_dict(), **{'id': self.api_kong_id}}

        self.session_mock.post.return_value.json.return_value = data_w_id
        self.session_mock.put.return_value.json.return_value = data_w_id
        self.session_mock.patch.return_value.json.return_value = data_w_id

        self.session_mock.get.return_value.status_code = 200
        self.session_mock.post.return_value.status_code = 201
        self.session_mock.patch.return_value.status_code = 200
        self.session_mock.delete.return_value.status_code = 204

        self.kong_admin_url = self.faker.url()
        self.apis_endpoint = self.kong_admin_url + 'apis/'

        self.api_admin_client = ApiAdminClient(self.kong_admin_url,
                                               _session=self.requests_mock.session())

    def test_api_admin_create(self):
        """
            Test: ApiAdminClient._perform_create() creates a api data dictionary
            instance with given api's data.
        """

        # Exercise
        api_data = self.api_admin_client._perform_create(self.api_name,
                                                         self.api_upstream_url,
                                                         uris=self.api_uris)
        api_data = ApiData(**api_data)

        # Verify
        self.assertEqual(api_data.name, self.api_name)
        self.assertEqual(api_data.upstream_url, self.api_upstream_url)
        self.assertEqual(api_data.uris, self.api_uris)

    def test_api_admin_create_triggers_http_request_to_kong_server(self):
        """
            Test: ApiAdminClient._perform_create() triggers an http request
            to kong server to _perform_create the api in the server.
        """
        # Exercise
        self.api_admin_client._perform_create(
            self.api_name, self.api_upstream_url, uris=self.api_uris)

        # Verify
        expected_api_data = ApiData(name=self.api_name,
                                    upstream_url=self.api_upstream_url,
                                    uris=self.api_uris)
        self.session_mock.post.assert_called_once_with(self.apis_endpoint,
                                                       json=expected_api_data.as_dict())

    def test_api_admin_create_using_api_data(self):
        """
            Test: passing a ApiData instance results in the same behaviour
            as normal _perform_create
        """
        # Setup
        orig_data = ApiData(name=self.api_name,
                            upstream_url=self.api_upstream_url,
                            uris=self.api_uris)

        # Exercise
        self.api_admin_client._perform_create(orig_data)

        # Verify
        self.session_mock.post.assert_called_once_with(self.apis_endpoint, json=orig_data.as_dict())

    def test_api_admin_delete_by_name(self):
        """
            Test: ApiAdmin._perform_delete(api_name) deletes it from kong server
        """
        # Setup
        self.api_admin_client._perform_create(
            self.api_name, self.api_upstream_url, uris=self.api_uris)

        # Exercise
        self.api_admin_client._perform_delete(self.api_name)

        # Verify
        api_endpoint = self.apis_endpoint + self.api_name
        self.session_mock.delete.assert_called_once_with(api_endpoint)

    def test_api_admin_delete_by_kong_id(self):
        """
            Test: ApiAdmin._perform_delete(api_kong_id) deletes it from kong server
        """
        # Setup
        self.api_admin_client._perform_create(
            self.api_name, self.api_upstream_url, uris=self.api_uris)

        # Exercise
        self.api_admin_client._perform_delete(self.api_kong_id)

        # Verify
        api_endpoint = self.apis_endpoint + self.api_kong_id
        self.session_mock.delete.assert_called_once_with(api_endpoint)

    def test_api_admin_update(self):
        # Setup
        api_data = self.api_admin_client._perform_create(self.api_name,
                                                         self.api_upstream_url,
                                                         uris=self.api_uris)
        new_uri = self.faker.api_path()

        # Exercise
        api_data = ApiData(**api_data)
        api_data.add_uri(new_uri)
        response = self.api_admin_client._perform_update(api_data.name, **api_data.as_dict())

        # Verify
        self.assertEqual(response, api_data.as_dict())
        expected_data = {}
        for k, v in api_data.as_dict().items():
            value = self.api_admin_client._stringify_if_list(v)
            expected_data[k] = value
        api_endpoint = self.apis_endpoint + self.api_name
        self.session_mock.patch.assert_called_once_with(api_endpoint, json=expected_data)

    def test_api_admin_list(self):
        """
            Test: ApiAdmin._perform_list() returns
            a generator ApiData instances of all apis in kong server
        """
        # Setup
        amount = self.faker.random_int(1, 50)
        apis = []

        for _ in range(amount):
            api_data = self.api_admin_client._perform_create(self.faker.api_name(),
                                                             self.faker.url(),
                                                             uris=self.faker.api_uris())
            apis.append(api_data)

        self.session_mock.get.return_value.json.return_value = {'total': amount,
                                                                'data': apis}

        # Exercise
        apis_retrieved = list(self.api_admin_client._perform_list())
        actual_amount = len(apis_retrieved)

        # Verify
        self.assertEqual(amount, actual_amount)

    def test_api_admin_list_w_parameters(self):
        # Setup
        self.session_mock.get.return_value.json.return_value = {'data': [self.api_data], 'total': 1}

        # Exercise
        generator = self.api_admin_client._perform_list(id=self.api_kong_id,
                                                        name=self.api_name,
                                                        upstream_url=self.api_upstream_url)

        generator.__next__()

        # Verify
        expected_data = {'offset': None,
                         'size': 10,
                         'id': self.api_kong_id,
                         'name': self.api_name,
                         'upstream_url': self.api_upstream_url}
        self.session_mock.get.assert_called_once_with(self.apis_endpoint, data=expected_data)

    def test_api_admin_list_w_invalid_params(self):
        # Setup
        invalid_query = {'invalid_field': 'invalid_value'}

        # Verify
        self.assertRaisesRegex(KeyError, 'invalid_field',
                               lambda: self.api_admin_client._perform_list(**invalid_query))

    """
    count is deprecated since kong 0.13.0

    def test_api_admin_count(self):
        "Test: ApiAdmin.count() returns the number of created apis"
        # Setup
        amount = self.faker.random_int(1, 50)
        apis = []

        for _ in range(amount):
            api_data = self.api_admin_client._perform_create(self.faker.api_name(),
                                                    self.faker.url(),
                                                    uris=self.faker.api_uris())
            apis.append(api_data)

        self.session_mock.get.return_value.json.return_value = {'total': amount,
                                                                'data': apis}

        # Exercise
        actual_amount = self.api_admin_client.count()

        # Verify
        self.assertEqual(amount, actual_amount)
    """
    def test_create_bad_request(self):
        # Setup
        self.session_mock.post.return_value.status_code = 409
        self.session_mock.post.return_value.content = 'bad request'

        # Verify
        self.assertRaisesRegex(NameError, r'bad request',
                               lambda: self.api_admin_client._perform_create(self.api_name,
                                                                             self.api_upstream_url,
                                                                             uris=self.api_uris))

    def test_create_internal_server_error(self):
        # Setup
        self.session_mock.post.return_value.status_code = 500
        self.session_mock.post.return_value.content = 'internal server error'

        # Verify
        self.assertRaisesRegex(Exception, r'internal server error',
                               lambda: self.api_admin_client._perform_create(self.api_name,
                                                                             self.api_upstream_url,
                                                                             uris=self.api_uris))

    def test_delete_not_existing_api(self):
        # Setup
        self.session_mock.delete.return_value.status_code = 404
        self.session_mock.delete.return_value.content = {"message": "not found"}

        # Verify
        self.assertRaisesRegex(NameError, r"not found",
                               lambda: self.api_admin_client._perform_delete(self.api_name))

    def test_delete_internal_server_error(self):
        # Setup
        self.session_mock.delete.return_value.status_code = 500
        self.session_mock.delete.return_value.content = 'internal server error'

        # Verify
        self.assertRaisesRegex(Exception, r'internal server error',
                               lambda: self.api_admin_client._perform_delete(self.api_name))

    def test_update_w_invalid_parameters(self):
        # Setup
        self.session_mock.patch.return_value.status_code = 400
        self.session_mock.patch.return_value.content = {"strip": "strip is an unknown field"}

        # Verify
        self.assertRaisesRegex(KeyError, r"unknown field",
                               lambda: self.api_admin_client
                               ._perform_update(self.api_data.name, **self.api_data.as_dict()))

    def test_update_not_existing_api(self):
        # Setup
        self.session_mock.patch.return_value.status_code = 404
        self.session_mock.patch.return_value.content = {"message": "not found"}

        # Verify
        self.assertRaisesRegex(NameError, r"not found",
                               lambda: self.api_admin_client
                               ._perform_update(self.api_data.name, **self.api_data.as_dict()))

    def test_update_internal_server_error(self):
        # Setup
        self.session_mock.patch.return_value.status_code = 500
        self.session_mock.patch.return_value.content = 'internal server error'

        # Verify
        self.assertRaisesRegex(Exception, r'internal server error',
                               lambda: self.api_admin_client
                               ._perform_update(self.api_data.name, **self.api_data.as_dict()))

    def test_list_internal_server_error(self):
        # Setup
        self.session_mock.get.return_value.status_code = 500
        self.session_mock.get.return_value.content = 'internal server error'

        generator = self.api_admin_client._perform_list()

        def boom():
            for _ in generator:
                pass

        # Verify
        self.assertRaisesRegex(Exception, r'internal server error',
                               boom)

    def test_retrieve_api(self):
        # Setup
        self.session_mock.get.return_value.status_code = 200
        self.session_mock.get.return_value.json.return_value = self.api_data.as_dict()

        # Exercise
        retrieved = self.api_admin_client._perform_retrieve(self.api_name)

        # Verify
        self.assertEqual(self.api_data.as_dict(), retrieved)

    def test_retrieve_non_created_api(self):
        # Setup
        self.session_mock.get.return_value.status_code = 404
        self.session_mock.get.return_value.content = {"message": "Not found"}

        # Verify
        self.assertRaisesRegex(NameError, r'Not found',
                               lambda: self.api_admin_client._perform_retrieve(self.api_name))

    def test_update_api_w_multiple_hosts(self):
        # Exercise
        self.api_admin_client._perform_update(self.api_name, hosts=['host1', 'host2'])

        # Verify
        self.session_mock.patch.assert_called_once_with(self.apis_endpoint + self.api_name,
                                                        json={'hosts': 'host1, host2'})

    def test_update_api_removing_hosts(self):
        # Exercise
        self.api_admin_client._perform_update(self.api_name, hosts=[])

        # Verify
        self.session_mock.patch.assert_called_once_with(self.apis_endpoint + self.api_name,
                                                        json={'hosts': ''})

    def test_update_api_removing_uris(self):
        # Exercise
        self.api_admin_client._perform_update(self.api_name, uris=[])

        # Verify
        self.session_mock.patch.assert_called_once_with(self.apis_endpoint + self.api_name,
                                                        json={'uris': ''})
