import unittest

from kong.kong_clients import RestClient


class RestClientTest(unittest.TestCase):

    def test_normalize_url_wo_trailing_slash(self):
        # Setup
        url = 'http://foo.bar'

        # Exercise
        normalized_url = RestClient.normalize_url(url)

        # Validate
        self.assertEqual('http://foo.bar/', normalized_url)

    def test_normalize_url_wo_scheme(self):
        # Setup
        url = 'foo.bar/'

        # Exercise
        normalized_url = RestClient.normalize_url(url)

        # Validate
        self.assertEqual('http://foo.bar/', normalized_url)

    def test_normalize_url_w_path_wo_trailing_slash(self):
        # Setup
        url = 'http://foo.bar/endpoint'

        # Exercise
        normalized_url = RestClient.normalize_url(url)

        # Validate
        self.assertEqual('http://foo.bar/endpoint/', normalized_url)

    def test_normalize_url_w_quey_params(self):
        # Setup
        url = 'http://foo.bar/?query=1'

        # Exercise
        normalized_url = RestClient.normalize_url(url)

        # Validate
        self.assertEqual('http://foo.bar/', normalized_url)
