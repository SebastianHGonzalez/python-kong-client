import unittest

from kong.structures import ServiceData


class ServiceDataTest(unittest.TestCase):

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
        self.service_retries = 5
        self.service_connect_timeout = 60000
        self.service_read_timeout = 60000
        self.service_send_timeout = 60000

        self.service_dict = {
            "id": "4e13f54a-bbf1-47a8-8777-255fed7116f2",
            "created_at": 1488869076800,
            "updated_at": 1488869076800,
            "connect_timeout": self.service_connect_timeout,
            "protocol": self.service_protocol,
            "host": self.service_host,
            "port": self.service_port,
            "path": self.service_path,
            "name": self.service_name,
            "retries": self.service_retries,
            "read_timeout": self.service_read_timeout,
            "send_timeout": self.service_send_timeout
        }

    def setUp(self):
        self.setup_service_vars()

    def test_create_service(self):

        created = ServiceData(self.service_name, protocol=self.service_protocol, host=self.service_host)

        self.assertEqual(self.service_name, created.name)
        self.assertEqual(self.service_protocol, created.protocol)
        self.assertEqual(self.service_host, created.host)

    def test_service_data_as_dict(self):

        created = ServiceData(self.service_name,
                              protocol=self.service_protocol,
                              host=self.service_host,
                              connect_timeout=self.service_connect_timeout,
                              port=self.service_port,
                              path=self.service_path,
                              retries=self.service_retries,
                              read_timeout=self.service_read_timeout,
                              send_timeout=self.service_send_timeout)

        expected = {
            "connect_timeout": self.service_connect_timeout,
            "protocol": self.service_protocol,
            "host": self.service_host,
            "port": self.service_port,
            "path": self.service_path,
            "name": self.service_name,
            "retries": self.service_retries,
            "read_timeout": self.service_read_timeout,
            "send_timeout": self.service_send_timeout
        }

        self.assertEqual(expected, created.as_dict())

    def test_create_service_using_url(self):

        created = ServiceData(self.service_name, url=self.service_url)
        print(created)
        self.assertEqual(self.service_protocol, created.protocol)
        self.assertEqual(self.service_host, created.host)
        self.assertEqual(self.service_port, created.port)
        self.assertEqual(self.service_path, created.path)
        self.assertEqual(self.service_url, created.url)
