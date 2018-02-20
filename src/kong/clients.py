import requests
from abc import abstractmethod

from .structures import ApiData


class RestClient:

    def __init__(self, url, session=requests.session()):
        self._session = session

        # TODO: validate url
        self.url = url

    @property
    def session(self):
        # TODO: research sessions inner workings
        return self._session


class KongAbstractClient(RestClient):

    @property
    def endpoint(self):
        return self.url + self.path

    @abstractmethod
    def path(self):
        pass

    def _send_create(self, data):
        response = self.session.post(self.endpoint, data=data)

        if response.status_code == 409:
            raise NameError(response.content)

        if response.status_code != 201:
            raise Exception(response.content)

        return response.json()

    def _send_delete(self, name_or_id):
        url = self.endpoint + name_or_id
        response = self.session.delete(url)

        if response.status_code == 404:
            raise NameError(response.content)

        if response.status_code != 204:
            raise Exception(response.content)

        return response.json()

    def _send_update(self, name_or_id, data):
        url = self.endpoint + name_or_id
        response = self.session.patch(url, data=data)

        if response.status_code == 400:
            raise KeyError(response.content)

        if response.status_code == 404:
            raise NameError(response.content)

        if response.status_code != 200:
            raise Exception(response.content)

        return response.json()

    def _send_list(self, size=10, offset=None, **kwargs):
        data = {**{'offset': offset, 'size': size}, **kwargs}

        response = self.session.get(self.endpoint,
                                    data=data)

        if response.status_code != 200:
            raise Exception(response.content)

        response = response.json()

        if 'data' in response:
            elements = response['data']
        else:
            elements = []

        if 'offset' in response:
            offset = response['offset']
        else:
            offset = None

        return offset, elements, response['total']

    def _send_retrieve(self, name_or_id):
        url = self.endpoint + name_or_id
        response = self.session.get(url)

        if response.status_code == 404:
            raise NameError(response.content)

        if response.status_code != 200:
            raise Exception(response.content)

        return response.json()

    def _send_update_or_create(self, data):
        response = self.session.put(self.endpoint, data=data)

        if response.status_code not in [200, 201]:
            raise Exception(response.content)

        return response.json()

    def retrieve(self, name_or_id):
        if not isinstance(name_or_id, str):
            raise TypeError("expected str but got %s" % type(name_or_id))

        return self._send_retrieve(name_or_id)


class ApiAdminClient(KongAbstractClient):

    @property
    def _allowed_query_params(self):
        return ['id', 'name', 'upstream_url', 'retries']

    @property
    def path(self):
        return 'apis/'

    def create(self, api_name_or_data, upstream_url=None, **kwargs):

        if isinstance(api_name_or_data, ApiData):
            api_data = api_name_or_data

        elif upstream_url is None:
            raise ValueError("must provide a upstream_url")

        elif isinstance(api_name_or_data, str):
            api_name = api_name_or_data
            api_data = ApiData(name=api_name, upstream_url=upstream_url, **kwargs)
        else:
            raise ValueError("must provide ApiData instance or name to create a api")

        data = self._send_create(api_data.raw())
        return self.__api_data_from_response(data)

    @staticmethod
    def __api_data_from_response(data):
        d = {}
        for k, v in data.items():
            if k in ApiData.allowed_parameters():
                d[k] = v
        return ApiData(**d)

    def delete(self, data):
        if isinstance(data, ApiData):
            name_or_id = data['name']
        elif isinstance(data, str):
            name_or_id = data
        else:
            raise TypeError("must provide ApiData instance or str")

        return self._send_delete(name_or_id)

    def update(self, api_data):
        if isinstance(api_data, ApiData):
            data = api_data.raw()
        elif isinstance(api_data, dict):
            data = ApiData(**api_data).raw()
        else:
            raise TypeError('expected ApiData or dict instance')

        return self._send_update(data['name'], data)

    def list(self, size=10, **kwargs):

        query_params = {}
        for k, v in kwargs.items():
            if k in self._allowed_query_params:
                query_params[k] = v
            else:
                raise KeyError('invalid query parameter: %s' % k)

        def generator():
            offset = None
            while True:
                offset, cached, _ = self._send_list(size, offset, **query_params)

                while cached:
                    yield cached.pop()

                if offset is None:
                    break

        return generator()

    def count(self):
        return self._send_list(0)[2]

    def retrieve(self, name_or_id):

        data = super(ApiAdminClient, self).retrieve(name_or_id)

        return self.__api_data_from_response(data)

    def update_or_create(self, api_data):
        if not isinstance(api_data, ApiData):
            raise TypeError('expected ApiData instance but got: %s' % type(api_data))

        data = self._send_update_or_create(api_data.raw())

        return self.__api_data_from_response(data)


class ConsumerAdminClient(KongAbstractClient):

    @property
    def path(self):
        return 'consumers/'

    def create(self, username=None, custom_id=None):
        if not username and not custom_id:
            raise ValueError('username or custom_id must be provided to create consumer')

        consumer_data = {}
        if username:
            consumer_data['username'] = username
        if custom_id:
            consumer_data['custom_id'] = custom_id

        return self._send_create(consumer_data)

