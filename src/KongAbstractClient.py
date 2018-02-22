from abc import abstractmethod
from RestClient import RestClient


class KongAbstractClient(RestClient):

    @property
    def endpoint(self):
        return self.url + self.path

    @abstractmethod
    def path(self):
        pass

    @abstractmethod
    def _allowed_query_params(self):
        pass

    def _send_create(self, data, endpoint=None):

        endpoint = endpoint or self.endpoint

        response = self.session.post(endpoint, data=data)

        if response.status_code == 409:
            raise NameError(response.content)

        if response.status_code != 201:
            raise Exception(response.content)

        return response.json()

    def _send_delete(self, name_or_id, endpoint=None):
        url = (endpoint or self.endpoint) + name_or_id
        response = self.session.delete(url)

        if response.status_code == 404:
            raise NameError(response.content)

        if response.status_code != 204:
            raise Exception(response.content)

        return response.json()

    def _send_update(self, pk_or_id, data, endpoint=None):
        url = (endpoint or self.endpoint) + pk_or_id
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

    def _send_retrieve(self, name_or_id, endpoint=None):
        endpoint = endpoint or self.endpoint
        url = endpoint + name_or_id
        response = self.session.get(url)

        if response.status_code == 404:
            raise NameError(response.content)

        if response.status_code != 200:
            raise Exception(response.content)

        return response.json()

    @staticmethod
    def _validate_params(query_params, allowed_params):
        validated_params = {}
        for k, val in query_params.items():
            if k in allowed_params:
                validated_params[k] = val
            else:
                raise KeyError('invalid query parameter: %s' % k)
        return validated_params

    def _validate_query_params(self, params):
        return self._validate_params(params, self._allowed_query_params)

    def _validate_update_params(self, params):
        return self._validate_params(params, self._allowed_update_params)

    def retrieve(self, pk_or_id):
        if not isinstance(pk_or_id, str):
            raise TypeError("expected str but got %s" % type(pk_or_id))

        return self._send_retrieve(pk_or_id)

    def list(self, size=10, **kwargs):

        query_params = self._validate_query_params(kwargs)

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

    def update(self, pk_or_id, **kwargs):

        query_params = self._validate_update_params(kwargs)

        return self._send_update(pk_or_id, query_params)

    def delete(self, pk_or_id):
        if not isinstance(pk_or_id, str):
            raise TypeError("expected str but got: %s" % type(pk_or_id))

        return self._send_delete(pk_or_id)
