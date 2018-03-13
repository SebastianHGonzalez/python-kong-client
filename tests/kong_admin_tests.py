import unittest
from unittest.mock import MagicMock

from kong.kong_clients import KongAdminClient


class KongAdminClientTest(unittest.TestCase):

    def setUp(self):

        self.node_info = {
            "hostname": "",
            "node_id": "6a72192c-a3a1-4c8d-95c6-efabae9fb969",
            "lua_version": "LuaJIT 2.1.0-alpha",
            "plugins": {
                "available_on_server": ['http-log', 'rate-limiting'],
                "enabled_in_cluster": []
            },
            "configuration": {},
            "tagline": "Welcome to Kong",
            "version": "0.11.0"
        }

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

        self.client = KongAdminClient(self.kong_admin_url, self.session_mock)

    def test_retrieve_node_status(self):
        # Setup
        self.session_mock.get.return_value.json.return_value = self.node_status

        # Exercise
        response = self.client.node_status()

        # Verify
        self.session_mock.get.assert_called_once_with(self.kong_admin_url + 'status/')
        self.assertEqual(response, self.node_status,
                         "KongAdminClient.node_status() did not return node status")

    def test_retrueve_node_info(self):
        # Setup
        self.session_mock.get.return_value.json.return_value = self.node_info

        # Exercise
        response = self.client.node_information()

        # Verify
        self.session_mock.get.assert_called_once_with(self.kong_admin_url)
        self.assertEqual(response, self.node_info,
                         "KongAdminClient.node_information() did not return node info")
