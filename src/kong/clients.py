import requests

from .data_structures import ApiData


class RestClient:

    def __init__(self, url, requests_module=requests):
        self._requests = requests_module
        self.url = url

    def post(self, url=None, data={}):
        if url is None:
            url = self.url
        response = self._requests.post(url, data=data)

        # TODO: handle response codes

        return response


class ApiAdminClient(RestClient):

    def create(self, api_name_or_data, upstream_url=None, **kwargs):

        if isinstance(api_name_or_data, ApiData):
            api_data = api_name_or_data

            return self.__send_create(api_data)
        elif upstream_url is None:
            raise ValueError("must provide a upstream_url")

        api_name = api_name_or_data
        api_data = ApiData(api_name, upstream_url, **kwargs)

        return self.__send_create(api_data)

    def __send_create(self, api_data):
        response = self.post(self.url + 'apis/', data=dict(api_data))

        return_value = {**api_data, **response['data']}
        if return_value != {**response['data'], **api_data}:
            raise ConnectionError('unexpected server response')

        return return_value
