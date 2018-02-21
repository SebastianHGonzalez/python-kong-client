import unittest
from unittest.mock import MagicMock

import faker

from src.kong.clients import PluginAdminClient


class PluginAdminTest(unittest.TestCase):

    def setUp(self):
        self.faker = faker.Faker()

        self.plugin_created_at = self.faker.random_int()
        self.plugin_id = self.faker.uuid4()
        self.plugin_name = self.faker.word()
        self.consumer_id = self.faker.uuid4()
        self.api_name_or_id = self.faker.uuid4()

        self.plugin_json = {"created_at": self.plugin_created_at,
                            "config": {"setting": "value"},
                            "id": self.plugin_id,
                            "enabled": True,
                            "name": self.plugin_name}

        self.kong_url = self.faker.url()
        self.plugins_endpoint = self.kong_url + 'plugins/'
        self.session_mock = MagicMock()
        self.plugin_admin_client = PluginAdminClient(self.kong_url, session=self.session_mock)

        self.session_mock.post.return_value.status_code = 201
        self.session_mock.get.return_value.status_code = 200
        self.session_mock.delete.return_value.status_code = 204
        self.session_mock.patch.return_value.status_code = 200

    def test_create_plugin_for_all_apis_and_consumers(self):

        # Exercise
        self.plugin_admin_client.create(self.plugin_name)

        # Verify
        expected_data = {'name': self.plugin_name}
        self.session_mock.post.assert_called_once_with(self.plugins_endpoint, data=expected_data)

    def test_create_plugin_for_all_apis_and_specific_consumer(self):

        # Exercise
        self.plugin_admin_client.create(self.plugin_name, self.consumer_id)

        # Verify
        expected_data = {'name': self.plugin_name,
                         'consumer_id': self.consumer_id}
        self.session_mock.post.assert_called_once_with(self.plugins_endpoint, data=expected_data)

    def test_create_plugin_for_specific_api_and_every_consumer(self):

        # Exercise
        self.plugin_admin_client.create(self.plugin_name, api_name_or_id=self.api_name_or_id)

        # Verify
        expected_url = self.kong_url + 'apis/' + self.api_name_or_id + '/plugins/'
        expected_data = {'name': self.plugin_name}
        self.session_mock.post.assert_called_once_with(expected_url, data=expected_data)

    def test_create_plugin_w_config(self):
        # Setup
        config = {'setting': 'value'}

        # Exercise
        self.plugin_admin_client.create(self.plugin_name, config=config)

        # Verify
        expected_data = {'name': self.plugin_name,
                         'config.setting': 'value'}
        self.session_mock.post.assert_called_once_with(self.plugins_endpoint, data=expected_data)

    def test_retrieve_existing_plugin(self):
        # Exercise
        self.plugin_admin_client.retrieve(self.plugin_id)

        # Verify
        self.session_mock.get.assert_called_once_with(self.plugins_endpoint + self.plugin_id)

    def test_retrieve_non_existing_plugin(self):
        # Setup
        self.session_mock.get.return_value.status_code = 404
        self.session_mock.get.return_value.content = {"message": "Not found"}

        # Verify
        self.assertRaisesRegex(NameError, 'Not found',
                               lambda: self.plugin_admin_client.retrieve(self.plugin_id))

    def test_list_plugins(self):
        # Setup
        self.session_mock.get.return_value.json.return_value = {'total': 1, 'data': [self.plugin_json]}

        # Exercise
        generator = self.plugin_admin_client.list()

        plugin_json = generator.__next__()

        # Verify
        self.assertEqual(plugin_json, self.plugin_json)
        self.session_mock.get.assert_called_once_with(self.plugins_endpoint,
                                                      data={'size': 10,
                                                            'offset': None})

    def test_list_plugins_w_parameters(self):
        # Setup
        self.session_mock.get.return_value.json = lambda: {'total': 1, 'data': [self.plugin_json]}

        # Exercise
        generator = self.plugin_admin_client.list(id=self.plugin_id,
                                                  name=self.plugin_name,
                                                  api_id=self.api_name_or_id,
                                                  consumer_id=self.consumer_id)

        plugin_json = generator.__next__()

        # Verify
        self.assertEqual(plugin_json, self.plugin_json)
        self.session_mock.get.assert_called_once_with(self.plugins_endpoint,
                                                      data={'size': 10,
                                                            'offset': None,
                                                            'id': self.plugin_id,
                                                            'name': self.plugin_name,
                                                            'api_id': self.api_name_or_id,
                                                            'consumer_id': self.consumer_id})

    def test_list_plugins_w_invalid_parameters(self):
        # Verify
        self.assertRaisesRegex(KeyError, 'invalid_field',
                               lambda: self.plugin_admin_client.list(invalid_field='invalid_value'))

    def test_detete_plugin(self):
        # Exercise
        self.plugin_admin_client.delete(self.plugin_id)

        # Verify
        expected_url = self.plugins_endpoint + self.plugin_id
        self.session_mock.delete.assert_called_once_with(expected_url)

    def test_delete_plugin_w_api_pk(self):
        # Exercise
        self.plugin_admin_client.delete(self.plugin_id, api_pk=self.api_name_or_id)

        # Verify
        expected_url = self.kong_url + 'apis/' + self.api_name_or_id + '/plugins/' + self.plugin_id
        self.session_mock.delete.assert_called_once_with(expected_url)

    def test_retrieve_enabled_plugins(self):
        # Setup
        self.session_mock.get.return_value.json.return_value = {"enabled_plugins": []}

        # Exercise
        retrieved = self.plugin_admin_client.retrieve_enabled()

        # Verify
        self.session_mock.get.assert_called_once_with(self.plugins_endpoint + 'enabled/')
        self.assertEqual(retrieved, [])

    def test_retrieve_schema(self):
        # Setup
        json = {"fields":
                {"hide_credentials":
                 {"default": False,
                  "type": "boolean"},
                 "key_names":
                 {"default": "function",
                  "required": True,
                  "type": "array"}}}
        self.session_mock.get.return_value.json.return_value = json

        # Exercise
        retrieved = self.plugin_admin_client.retrieve_schema(self.plugin_name)

        # Verify
        self.session_mock.get.assert_called_once_with(self.plugins_endpoint + 'schema/' + self.plugin_name)
        self.assertEquals(retrieved, json)

    def test_update_plugin(self):
        # Setup
        data = {'name': self.plugin_name,
                'consumer_id': self.consumer_id}

        config = {'setting': 'value'}

        # Exercise
        self.plugin_admin_client.update(self.plugin_id, api_pk=self.api_name_or_id, config=config, **data)

        # Verify
        expected_url = self.kong_url + 'apis/' + self.api_name_or_id + '/plugins/' + self.plugin_id
        expected_data = {'name': self.plugin_name,
                         'consumer_id': self.consumer_id,
                         'config.setting': 'value'}

        self.session_mock.patch.assert_called_once_with(expected_url, data=expected_data)

    def test_update_plugin_wo_api_pk(self):
        # Setup
        data = {'name': self.plugin_name,
                'consumer_id': self.consumer_id}

        config = {'setting': 'value'}

        # Exercise
        self.plugin_admin_client.update(self.plugin_id, config=config, **data)

        # Verify
        expected_url = self.plugins_endpoint + self.plugin_id
        expected_data = {'name': self.plugin_name,
                         'consumer_id': self.consumer_id,
                         'config.setting': 'value'}

        self.session_mock.patch.assert_called_once_with(expected_url, data=expected_data)

    def test_update_plugin_wo_config(self):
        # Setup
        data = {'name': self.plugin_name,
                'consumer_id': self.consumer_id}

        # Exercise
        self.plugin_admin_client.update(self.plugin_id, **data)

        # Verify
        expected_url = self.plugins_endpoint + self.plugin_id
        expected_data = data

        self.session_mock.patch.assert_called_once_with(expected_url, data=expected_data)
