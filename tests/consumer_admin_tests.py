import unittest
from unittest.mock import MagicMock
import faker

from kong.kong_clients import ConsumerAdminClient


class ApiAdminClientTest(unittest.TestCase):

    def setUp(self):
        self.faker = faker.Faker()

        self.consumer_username = self.faker.user_name()
        self.consumer_custom_id = self.faker.uuid4()
        self.consumer_id = self.faker.uuid4()
        self.consumer_created_at = self.faker.random_int()

        self.consumer_data = {'id': self.consumer_id,
                              'username': self.consumer_username,
                              'custom_id': self.consumer_custom_id,
                              'created_at': self.consumer_created_at}

        self.session_mock = MagicMock()

        self.json = {'id': self.consumer_id,
                     'username': self.consumer_username,
                     'custom_id': self.consumer_custom_id}

        self.session_mock.post.return_value.status_code = 201
        self.session_mock.get.return_value.status_code = 200
        self.session_mock.patch.return_value.status_code = 200
        self.session_mock.delete.return_value.status_code = 204

        self.session_mock.post.return_value.json.return_value = self.json

        self.requests_mock = MagicMock()
        self.requests_mock.session.return_value = self.session_mock

        self.kong_admin_url = self.faker.url()
        self.consumer_admin_client = ConsumerAdminClient(self.kong_admin_url,
                                                         _session=self.requests_mock.session())

        self.consumer_endpoint = self.kong_admin_url + 'consumers/'

    def test_create_consumer_w_username(self):
        # Exercise
        self.consumer_admin_client.create(username=self.consumer_username)

        # Verify
        self.session_mock.post.assert_called_once_with(self.consumer_endpoint,
                                                       json={'username': self.consumer_username})

    def test_create_consumer_w_custom_id(self):
        # Exercise
        self.consumer_admin_client.create(custom_id=self.consumer_custom_id)

        # Verify
        self.session_mock.post.assert_called_once_with(self.consumer_endpoint,
                                                       json={'custom_id': self.consumer_custom_id})

    def test_create_consumer_w_custom_id_and_username(self):
        # Exercise
        self.consumer_admin_client.create(username=self.consumer_username,
                                          custom_id=self.consumer_custom_id)

        # Verify
        self.session_mock.post.assert_called_once_with(self.consumer_endpoint,
                                                       json={'username': self.consumer_username,
                                                             'custom_id': self.consumer_custom_id})

    def test_create_consumer_wo_parameters(self):
        # Verify
        self.assertRaisesRegex(ValueError, r'username',
                               self.consumer_admin_client.create)

    def test_create_conflict_username(self):
        # Setup
        self.session_mock.post.return_value.status_code = 409
        self.session_mock.post.return_value.content = {"username":
                                                       "already exists with value %s"
                                                       % self.consumer_username}

        # Verify
        self.assertRaisesRegex(NameError, r'already exists',
                               lambda: self.consumer_admin_client.create(self.consumer_username))

    def test_create_internal_server_error(self):
        # Setup
        self.session_mock.post.return_value.status_code = 500
        self.session_mock.post.return_value.content = "internal server error"

        # Verify
        self.assertRaisesRegex(Exception, r'server error',
                               lambda: self.consumer_admin_client.create(self.consumer_username))

    def test_retrieve(self):
        # Exercise
        self.consumer_admin_client.retrieve(self.consumer_username)

        # Verify
        self.session_mock.get\
            .asser_called_once_with(self.consumer_endpoint + self.consumer_username)

    def test_list_consumers(self):
        # Setup
        self.session_mock.get.return_value.json\
            .return_value = {'total': 1, 'data': [self.consumer_data]}
        generator = self.consumer_admin_client.list()

        # Exercise
        generator.__next__()

        # Verify
        expected_data = {'offset': None, 'size': 10}
        self.session_mock.get.asser_called_once_with(self.consumer_endpoint, data=expected_data)

    def test_list_consumers_w_params(self):
        # Setup
        self.session_mock.get.return_value.json\
            .return_value = {'total': 1, 'data': [self.consumer_data]}
        generator = self.consumer_admin_client.list(id=self.consumer_id,
                                                    username=self.consumer_username,
                                                    custom_id=self.consumer_custom_id)

        # Exercise
        generator.__next__()

        # Verify
        expected_data = {'offset': None,
                         'size': 10,
                         'id': self.consumer_id,
                         'username': self.consumer_username,
                         'custom_id': self.consumer_custom_id}
        self.session_mock.get.asser_called_once_with(self.consumer_endpoint, data=expected_data)

    def test_list_consumers_w_invalid_params(self):
        # Setup
        invalid_query = {'invalid_field': 'invalid_value'}

        # Verify
        self.assertRaisesRegex(KeyError, 'invalid_field',
                               lambda: self.consumer_admin_client.list(**invalid_query))

    def test_update_consumer(self):
        # Setup
        new_username = self.faker.user_name()
        new_custom_id = self.faker.uuid4()
        data = {'username': new_username,
                'custom_id': new_custom_id}

        # Exercise
        self.consumer_admin_client.update(self.consumer_username, **data)

        # Verify
        self.session_mock.patch\
            .assert_called_once_with(self.consumer_endpoint + self.consumer_username,
                                     json=data)

    def test_update_consumer_w_invalid_params(self):
        # Setup
        data = {'invalid_field': 'invalid_value'}

        # Verify
        self.assertRaisesRegex(KeyError, 'invalid_field',
                               lambda: self.consumer_admin_client
                               .update(self.consumer_username, **data))

    def test_delete_consumer(self):
        # Exercise
        self.consumer_admin_client.delete(self.consumer_username)

        # Verify
        self.session_mock.delete\
            .assert_called_once_with(self.consumer_endpoint + self.consumer_username)

    def test_delete_w_invalid_value(self):
        # Setup
        invalid_value = self.faker.random_int()

        # Verify
        self.assertRaisesRegex(TypeError, 'str',
                               lambda: self.consumer_admin_client.delete(invalid_value))
