import requests


class ApiData(dict):

    def __init__(self, api_name, upstream_url, api_uris):
        self['name'] = api_name
        self['upstream_url'] = upstream_url
        self['uris'] = api_uris


class RestClient:

    def __init__(self, url, requests_module=requests):
        self._requests = requests_module
        self.url = url


class ApiAdminClient(RestClient):

    def create(self, api_name, upstream_url, api_uris, **kwargs):
        api_data = ApiData(api_name, upstream_url, api_uris)
        self._requests.post(self.url, data=dict(api_data))
        return api_data
