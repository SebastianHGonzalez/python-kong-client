import unittest
from faker import Faker

from src.kong.providers import ApiDataProvider

from src.kong.clients import ApiAdminClient


class ApiAdminClientTest(unittest.TestCase):

    def setUp(self):
        self.faker = Faker()
        self.faker.add_provider(ApiDataProvider)
        self.api_name = self.faker.api_name()
        self.api_upstream_url = self.faker.url()
        self.api_uris = self.faker.api_uris()

        self.api_admin_client = ApiAdminClient()

    def test_api_admin_create(self):
        """
            Test: ApiAdminClient.crete() creates a ApiData instance with
                api's data
        """

        # Exercise
        api_data = self.api_admin_client.create(self.api_name, self.api_upstream_url, self.api_uris)

        # Verify
        self.assertEqual(api_data['name'], self.api_name)
        self.assertEqual(api_data['upstream_url'], self.api_upstream_url)
        self.assertEqual(api_data['uris'], self.api_uris)


if __name__ == '__main__':
    unittest.main()
