import unittest
from unittest.mock import MagicMock
import faker

from src.kong.clients import ConsumerAdminClient


class ApiAdminClientTest(unittest.TestCase):

    def setUp(self):
        self.faker = faker.Faker()

        self.consumer_username = self.faker.user_name()
        self.consumer_custom_id = self.faker.uuid4()
        self.consumer_id = self.faker.uuid4()

        self.session_mock = MagicMock()

        self.json = lambda: {'id': self.consumer_id,
                             'username': self.consumer_username,
                             'custom_id': self.consumer_custom_id}

        self.session_mock.post.return_value.status_code = 201
        self.session_mock.get.return_value.status_code = 200

        self.session_mock.post.return_value.json = self.json

        self.requests_mock = MagicMock()
        self.requests_mock.session.return_value = self.session_mock

        self.kong_admin_url = self.faker.url()
        self.consumer_admin_client = ConsumerAdminClient(self.kong_admin_url, session=self.requests_mock.session())

        self.consumer_endpoint = self.kong_admin_url + 'consumers/'

    def test_create_consumer_w_username(self):
        # Exercise
        self.consumer_admin_client.create(username=self.consumer_username)

        # Verify
        self.session_mock.post.assert_called_once_with(self.consumer_endpoint,
                                                       data={'username': self.consumer_username})

    def test_create_consumer_w_custom_id(self):
        # Exercise
        self.consumer_admin_client.create(custom_id=self.consumer_custom_id)

        # Verify
        self.session_mock.post.assert_called_once_with(self.consumer_endpoint,
                                                       data={'custom_id': self.consumer_custom_id})

    def test_create_consumer_w_custom_id_and_username(self):
        # Exercise
        self.consumer_admin_client.create(username=self.consumer_username,
                                          custom_id=self.consumer_custom_id)

        # Verify
        self.session_mock.post.assert_called_once_with(self.consumer_endpoint,
                                                       data={'username': self.consumer_username,
                                                             'custom_id': self.consumer_custom_id})

    def test_create_consumer_wo_parameters(self):
        # Verify
        self.assertRaisesRegex(ValueError, r'username',
                               self.consumer_admin_client.create)

    def test_create_conflict_username(self):
        # Setup
        self.session_mock.post.return_value.status_code = 409
        self.session_mock.post.return_value.content = {"username":
                                                       "already exists with value %s" % self.consumer_username}

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
        self.session_mock.get.asser_called_once_with(self.consumer_endpoint + self.consumer_username)
