from abc import abstractmethod
import requests

import unittest
from unittest.mock import MagicMock


from kong.kong_clients import ServiceAdminClient
from kong.exceptions import SchemaViolation


class ServiceAdminClientAbstractTest:

    @abstractmethod
    def kong_url(self):
        pass

    @abstractmethod
    def new_service_admin_client(self):
        pass

    def setup_client_var(self):
        self.service_admin_client = self.new_service_admin_client()

    def setup_service_vars(self):
        self.service_protocol = 'http'
        self.service_host = 'example.org'
        self.service_port = 8080
        self.service_path = '/api'
        self.service_name = 'example-service'
        self.service_url = '%s://%s:%s%s' % (self.service_protocol,
                                             self.service_host,
                                             self.service_port,
                                             self.service_path)
        self.service_retries = '5'

    def test_create_a_service_w_url(self):
        created = self.service_admin_client.create(name=self.service_name,
                                                   url=self.service_url)

        self.assert_correctly_created(created)

    def assert_correctly_created(self, created):
        self.assertEquals(12, len(created))
        self.assertRegex(created['id'], '^[\w\d]{8}-([\w\d]{4}-){3}[\w\d]{12}$')
        self.assertTrue(isinstance(created['created_at'], int))
        self.assertTrue(isinstance(created['updated_at'], int))
        self.assertTrue(isinstance(created['connect_timeout'], int))
        self.assertRegex(created['protocol'], self.service_protocol)
        self.assertRegex(created['host'], self.service_host)
        self.assertTrue(isinstance(created['port'], int))
        self.assertRegex(created['path'], self.service_path)
        self.assertRegex(created['name'], self.service_name)
        self.assertTrue(isinstance(created['retries'], int))
        self.assertTrue(isinstance(created['read_timeout'], int))
        self.assertTrue(isinstance(created['write_timeout'], int))

    def test_create_service(self):
        created = self.service_admin_client.create(name=self.service_name,
                                                   protocol=self.service_protocol,
                                                   host=self.service_host,
                                                   port=self.service_port,
                                                   path=self.service_path)
        self.assert_correctly_created(created)

    def test_create_w_invalid_params(self):
        self.assertRaises(SchemaViolation, lambda:
                          self.service_admin_client.create(name=self.service_name,
                                                           url=self.service_url,
                                                           invalid='invalid')
                          )


class ServiceAdminClientMockedTest(ServiceAdminClientAbstractTest, unittest.TestCase):

    @property
    def kong_url(self):
        return 'http://kong.url/'

    def setup_mock_vars(self):
        self.service_dict = {
            "id": "4e13f54a-bbf1-47a8-8777-255fed7116f2",
            "created_at": 1488869076800,
            "updated_at": 1488869076800,
            "connect_timeout": 60000,
            "protocol": self.service_protocol,
            "host": self.service_host,
            "port": self.service_port,
            "path": self.service_path,
            "name": self.service_name,
            "retries": 5,
            "read_timeout": 60000,
            "write_timeout": 60000
        }

        self.session = MagicMock()
        self.session.post.return_value.status_code = 201
        self.session.post.return_value.json.return_value = self.service_dict

    def new_service_admin_client(self):
        return ServiceAdminClient(self.kong_url, _session=self.session)

    def setUp(self):
        self.setup_service_vars()
        self.setup_mock_vars()
        self.setup_client_var()

    def test_create_a_service_w_url(self):
        super(ServiceAdminClientMockedTest, self).test_create_a_service_w_url()

        expected_data = dict(name=self.service_name, url=self.service_url)
        endpoint = self.kong_url + 'services/'
        self.session.post.assert_called_once_with(endpoint, data=expected_data)

    def test_create_service(self):
        super(ServiceAdminClientMockedTest, self).test_create_service()

        expected_data = dict(name=self.service_name,
                             protocol=self.service_protocol,
                             host=self.service_host,
                             port=self.service_port,
                             path=self.service_path)
        endpoint = self.kong_url + 'services/'
        self.session.post.assert_called_once_with(endpoint, data=expected_data)


class ServiceAdminClientServerTest(ServiceAdminClientAbstractTest, unittest.TestCase):

    @property
    def kong_url(self):
        return 'http://localhost:8001/'

    def setUp(self):
        self.setup_service_vars()
        self.setup_client_var()

    def new_service_admin_client(self):
        return ServiceAdminClient(self.kong_url, _session=requests.session())

    def tearDown(self):
        self.service_admin_client.delete(self.service_name)
