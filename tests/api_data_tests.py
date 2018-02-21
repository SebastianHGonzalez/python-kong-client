import unittest
import faker
from tests.providers import ApiDataProvider
from structures import ApiData


class ApiDataTests(unittest.TestCase):

    def setUp(self):
        self.faker = faker.Faker()
        self.faker.add_provider(ApiDataProvider)

        self.api_name = self.faker.api_name()
        self.api_upstream_url = self.faker.url()
        self.api_uris = self.faker.api_uris()

    def test_create(self):
        # Setup
        hosts = [self.faker.domain_name() for _ in range(self.faker.random_int(0, 10))]
        methods = ["GET", "POST"]
        strip_uri = self.faker.boolean()
        preserve_host = self.faker.boolean()
        retries = self.faker.random_int()
        https_only = self.faker.boolean()
        http_if_terminated = self.faker.boolean()
        upstream_connect_timeout = self.faker.random_int()
        upstream_send_timeout = self.faker.random_int()
        upstream_read_timeout = self.faker.random_int()

        # Exercise
        self.api_data = ApiData(name=self.api_name,
                                upstream_url=self.api_upstream_url,
                                uris=self.api_uris,
                                hosts=hosts,
                                methods=methods,
                                strip_uri=strip_uri,
                                preserve_host=preserve_host,
                                retries=retries,
                                https_only=https_only,
                                http_if_terminated=http_if_terminated,
                                upstream_connect_timeout=upstream_connect_timeout,
                                upstream_send_timeout=upstream_send_timeout,
                                upstream_read_timeout=upstream_read_timeout)

        # Verify
        self.assertEqual(self.api_data['name'], self.api_name)
        self.assertEqual(self.api_data['upstream_url'], self.api_upstream_url)
        self.assertEqual(self.api_data['uris'], self.api_uris)

    def test_create_api_data_wo_uris_method_or_hosts_raises_exception(self):
        self.assertRaisesRegex(ValueError,
                               r'provided',
                               lambda: ApiData(name=self.api_name,
                                               upstream_url=self.api_upstream_url))

    def test_create_api_data_w_invalid_fields_raises_exception(self):
        # Setup
        invalid_value = ""

        # Verify
        self.assertRaisesRegex(KeyError,
                               r'invalid_field',
                               lambda: ApiData(name=self.api_name,
                                               upstream_url=self.api_upstream_url,
                                               uris=self.api_uris,
                                               invalid_field=invalid_value))

    def test_create_api_data_w_invalid_value_raises_exception(self):
        # Setup
        invalid_value = None

        # Verify
        self.assertRaisesRegex(ValueError,
                               r'invalid value',
                               lambda: ApiData(name=self.api_name,
                                               upstream_url=self.api_upstream_url,
                                               uris=self.api_uris,
                                               methods=invalid_value))

