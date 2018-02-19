import requests
from abc import abstractmethod

from .structures import ApiData


class RestClient:

    def __init__(self, url, requests_module=requests):
        self._session = requests_module.session()

        # TODO: validate url
        self.url = url

    @property
    def session(self):
        # TODO: research sessions inner workings
        return self._session

    @property
    def endpoint(self):
        return self.url + self.path

    @abstractmethod
    def path(self):
        pass


class ApiAdminClient(RestClient):

    @property
    def path(self):
        return 'apis/'

    def api_create(self, api_name_or_data, upstream_url=None, **kwargs):

        if isinstance(api_name_or_data, ApiData):
            api_data = api_name_or_data

        elif upstream_url is None:
            raise ValueError("must provide a upstream_url")

        elif isinstance(api_name_or_data, str):
            api_name = api_name_or_data
            api_data = ApiData(name=api_name, upstream_url=upstream_url, **kwargs)
        else:
            raise ValueError("must provide ApiData instance or name to create a api")

        return self.__send_create(api_data)

    def __send_create(self, api_data):
        response = self.session.post(self.endpoint, data=api_data.raw())

        if response.status_code == 409:
            raise NameError(response.content)

        if response.status_code != 201:
            raise Exception(response.content)

        data = response.json()
        return self.__api_data_from_response(data)

    @staticmethod
    def __api_data_from_response(data):
        d = {}
        for k, v in data.items():
            if k in ApiData.allowed_parameters():
                d[k] = v
        return ApiData(**d)

    def api_delete(self, data):
        if isinstance(data, ApiData):
            name_or_id = data['name']
        elif isinstance(data, str):
            name_or_id = data
        else:
            raise TypeError("must provide ApiData instance or str")

        return self.__send_delete(name_or_id)

    def __send_delete(self, name_or_id):
        url = self.endpoint + name_or_id
        response = self.session.delete(url)

        if response.status_code == 404:
            raise NameError(response.content)

        if response.status_code != 204:
            raise Exception(response.content)

        return response.json()

    def api_update(self, api_data):
        if isinstance(api_data, ApiData):
            data = api_data.raw()
        elif isinstance(api_data, dict):
            data = ApiData(**api_data).raw()
        else:
            raise TypeError('expected ApiData or dict instance')

        return self.__send_update(data)

    def __send_update(self, data):
        url = self.endpoint + data['name']
        response = self.session.patch(url, data=data)

        if response.status_code == 400:
            raise KeyError(response.content)

        if response.status_code == 404:
            raise NameError(response.content)

        if response.status_code != 200:
            raise Exception(response.content)

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

    def __send_list(self, size=10, offset=None):
        url = self.endpoint
        response = self.session.get(url, data={'offset': offset,
                                               'size': size})

        if response.status_code != 200:
            raise Exception(response.content)

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
        return self.__send_list(0)[2]

    def api_retrieve(self, name_or_id):
        if not isinstance(name_or_id, str):
            raise TypeError("expected str but got %s" % type(name_or_id))

        data = self.__send_retrieve(name_or_id)

        return self.__api_data_from_response(data)

    def __send_retrieve(self, name_or_id):
        url = self.endpoint + name_or_id
        response = self.session.get(url)

        if response.status_code == 404:
            raise NameError(response.content)

        if response.status_code != 200:
            raise Exception(response.content)

        return response.json()

    def api_update_or_create(self, api_data):
        if not isinstance(api_data, ApiData):
            raise TypeError('expected ApiData instance but got: %s' % type(api_data))

        data = self.__send_update_or_create(api_data)

        return self.__api_data_from_response(data)

    def __send_update_or_create(self, api_data):
        response = self.session.put(self.endpoint, data=api_data.raw())

        if response.status_code not in [200, 201]:
            raise Exception(response.content)

        return response.json()


class ConsumerAdminClient(RestClient):

    @property
    def path(self):
        return 'consumers/'

    def consumer_create(self, username=None, custom_id=None):
        if not username and not custom_id:
            raise ValueError('username or custom_id must be provided to create consumer')

        consumer_data = {}
        if username:
            consumer_data['username'] = username
        if custom_id:
            consumer_data['custom_id'] = custom_id

        self.__send_create(consumer_data)

    def __send_create(self, consumer_data):
        response = self.session.post(self.endpoint, data=consumer_data)

        if response.status_code == 409:
            raise NameError(response.content)

        if response.status_code != 201:
            raise Exception(response.content)

        return response.json()