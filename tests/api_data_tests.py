import unittest
import faker

from src.kong.providers import ApiDataProvider
from src.kong.data_structures import ApiData


class ApiDataTests(unittest.TestCase):

    def setUp(self):
        self.faker = faker.Faker()
        self.faker.add_provider(ApiDataProvider)

        self.api_name = self.faker.api_name()
        self.api_upstream_url = self.faker.url()
        self.api_uris = self.faker.api_uris()

    def test_create_api_data_wo_uris_method_or_hosts_raises_exception(self):
        self.assertRaisesRegex(ValueError,
                               r'provided',
                               lambda: ApiData(api_name=self.api_name,
                                               upstream_url=self.api_upstream_url))

    def test_create_api_data_w_invalid_fields_raises_exception(self):
        # Setup
        invalid_value = ""

        # Verify
        self.assertRaisesRegex(ValueError,
                               r'invalid_field',
                               lambda: ApiData(api_name=self.api_name,
                                               upstream_url=self.api_upstream_url,
                                               uris=self.api_uris,
                                               invalid_field=invalid_value))
