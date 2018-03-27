from abc import abstractmethod
import requests

import unittest
from unittest.mock import MagicMock


from kong.kong_clients import ServiceAdminClient


class ServiceAdminClientAbstractTest:

    @abstractmethod
    def kong_url(self):
        pass

    @abstractmethod
    def new_service_admin_client(self):
        pass

    def setUp(self):
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

        self.service_admin_client = self.new_service_admin_client()

    def create_a_service_w_url(self):
        return self.service_admin_client.create(name=self.service_name,
                                                url=self.service_url)

    def test_create_a_service_w_url(self):
        created = self.create_a_service_w_url()

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


class ServiceAdminClientMockedTest(ServiceAdminClientAbstractTest, unittest.TestCase):

    @property
    def kong_url(self):
        return 'http://kong.url/'

    def new_service_admin_client(self):
        return ServiceAdminClient(self.kong_url, _session=self.session)

    def test_create_a_service_w_url(self):
        super(ServiceAdminClientMockedTest, self).test_create_a_service_w_url()

        expected_data = {'url': self.service_url, 'name': self.service_name}
        endpoint = self.kong_url + 'services/'
        self.session.post.assert_called_once_with(endpoint, data=expected_data)


class ServiceAdminClientServerTest(ServiceAdminClientAbstractTest, unittest.TestCase):

    @property
    def kong_url(self):
        return 'http://localhost:8001/'

    def new_service_admin_client(self):
        return ServiceAdminClient(self.kong_url, _session=requests.session())

    def tearDown(self):
        self.service_admin_client.delete(self.service_name)
