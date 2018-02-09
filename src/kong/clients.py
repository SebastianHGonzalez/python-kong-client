import requests

from .data_structures import ApiData


class RestClient:

    def __init__(self, url, requests_module=requests):
        self._requests = requests_module
        self.url = url


class ApiAdminClient(RestClient):

    def create(self, api_name_or_data, upstream_url=None, **kwargs):

        if isinstance(api_name_or_data, ApiData):
            api_data = api_name_or_data
            self._requests.post(self.url, data=dict(api_data))
            return api_data
        elif upstream_url is None:
            raise ValueError("must provide a upstream_url")

        api_name = api_name_or_data
        api_data = ApiData(api_name, upstream_url, **kwargs)
        self._requests.post(self.url, data=dict(api_data))
        return api_data
