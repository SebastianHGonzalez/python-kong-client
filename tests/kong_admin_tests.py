import unittest
from unittest.mock import MagicMock

from kong.kong_clients import KongAdminClient


class KongAdminClientTest(unittest.TestCase):

    def setUp(self):

        self.node_status = {"server": {
            "total_requests": 3,
            "connections_active": 1,
            "connections_accepted": 1,
            "connections_handled": 1,
            "connections_reading": 0,
            "connections_writing": 1,
            "connections_waiting": 0
        },
            "database": {
                "reachable": True
            }
        }

        self.kong_admin_url = 'http://kongadminurl:8001/'
        self.session_mock = MagicMock()

        self.session_mock.get.return_value.json.return_value = self.node_status

        self.client = KongAdminClient(self.kong_admin_url, self.session_mock)

    def test_retrieve_node_status(self):

        # Exercise
        response = self.client.node_status()

        # Verify
        self.session_mock.get.assert_called_once_with(self.kong_admin_url + 'status/')
        self.assertEqual(response, self.node_status,
                         "KongAdminClient.node_status() did not return node status")
