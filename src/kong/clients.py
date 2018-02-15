import requests.structures

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

        return response.json()

    def delete(self, url=None, data={}):
        if url is None:
            url = self.url
        response = self._requests.delete(url, data=data)

        # TODO: handle response codes

        return response.json()

    def patch(self, url=None, data={}):
        if url is None:
            url = self.url
        response = self._requests.patch(url, data=data)

        # TODO: handle response codes

        return response.json()


class ApiAdminClient(RestClient):

    def create_api(self, api_name_or_data, upstream_url=None, **kwargs):

        if isinstance(api_name_or_data, ApiData):
            api_data = api_name_or_data

        elif upstream_url is None:
            raise ValueError("must provide a upstream_url")

        elif isinstance(api_name_or_data, str):
            api_name = api_name_or_data
            api_data = ApiData(name=api_name, upstream_url=upstream_url, **kwargs)

        return self.__send_create(api_data)

    def __send_create(self, api_data):
        data = self.post(self.url + 'apis/', data=dict(api_data))
        return self.__api_data_from_response(data)

    @staticmethod
    def __api_data_from_response(data):
        d = {}
        for k in ApiData.allowed_parameters():
            if k in data:
                d[k] = data[k]
        return ApiData(**d)

    def delete_api(self, data):
        if isinstance(data, ApiData):
            name_or_id = data['name']
        else:
            name_or_id = data

        return self.__send_delete(name_or_id)

    def __send_delete(self, name_or_id):
        url = self.url + 'apis/' + name_or_id
        return self.delete(url)

    def update_api(self, api_data):
        if isinstance(api_data, ApiData):
            data = dict(api_data)
        elif isinstance(api_data, dict):
            data = api_data
        else:
            raise TypeError('expected ApiData or dict instance')

        return self.__send_update(data)

    def __send_update(self, data):
        url = self.url + 'apis/' + data['name']
        return self.patch(url, data)
