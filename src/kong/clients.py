import requests

from .structures import ApiData


class RestClient:

    def __init__(self, url, requests_module=requests):
        self._session = requests_module.session()
        self.url = url

    @property
    def session(self):
        return self._session


class ApiAdminClient(RestClient):

    def api_create(self, api_name_or_data, upstream_url=None, **kwargs):

        if isinstance(api_name_or_data, ApiData):
            api_data = api_name_or_data

        elif upstream_url is None:
            raise ValueError("must provide a upstream_url")

        elif isinstance(api_name_or_data, str):
            api_name = api_name_or_data
            api_data = ApiData(name=api_name, upstream_url=upstream_url, **kwargs)

        return self.__send_create(api_data)

    def __send_create(self, api_data):
        response = self.session.post(self.url + 'apis/', data=dict(api_data))

        # TODO: handle response codes
        if response.status_code == 409:
            raise NameError(response.content)

        data = response.json()
        return self.__api_data_from_response(data)

    @staticmethod
    def __api_data_from_response(data):
        d = {}
        for k in ApiData.allowed_parameters():
            if k in data:
                d[k] = data[k]
        return ApiData(**d)

    def api_delete(self, data):
        if isinstance(data, ApiData):
            name_or_id = data['name']
        else:
            name_or_id = data

        return self.__send_delete(name_or_id)

    def __send_delete(self, name_or_id):
        url = self.url + 'apis/' + name_or_id
        response = self.session.delete(url)

        # TODO: handle response codes

        return response.json()

    def api_update(self, api_data):
        if isinstance(api_data, ApiData):
            data = dict(api_data)
        elif isinstance(api_data, dict):
            data = api_data
        else:
            raise TypeError('expected ApiData or dict instance')

        return self.__send_update(data)

    def __send_update(self, data):
        url = self.url + 'apis/' + data['name']
        response = self.session.patch(url, data=data)

        # TODO: handle response codes

        return response.json()

    def api_list(self, size=10):
        def generator():
            offset = None
            while True:
                offset, cached, _ = self.__send_list(size, offset)

                while cached:
                    yield cached.pop()

                if offset is None:
                    break

        return generator()

    def __send_list(self, size=10, offset=0):
        url = self.url + 'apis/'
        response = self.session.get(url, data={'offset': offset,
                                               'size': size})

        # TODO: handle response codes

        response = response.json()

        if 'data' in response:
            apis = response['data']
        else:
            apis = []

        if 'offset' in response:
            offset = response['offset']
        else:
            offset = None

        return offset, apis, response['total']

    def api_count(self):
        return self.__send_list()[2]
