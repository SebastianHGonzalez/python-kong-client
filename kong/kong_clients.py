from abc import abstractmethod
from urllib3.util.url import Url, parse_url
from requests import session
from kong.structures import ApiData, ConsumerData


class RestClient:

    def __init__(self, url, _session=session()):
        self._session = _session

        self.url = self.normalize_url(url)

    @property
    def session(self):
        return self._session

    @staticmethod
    def normalize_url(url):
        url = parse_url(url)

        path = url.path or ''
        if not path.endswith('/'):
            path += '/'

        url = Url(scheme=url.scheme or 'http',
                  auth=url.auth,
                  host=url.host,
                  port=url.port,
                  path=path,
                  fragment=url.fragment)

        return url.url


class KongAdminClient(RestClient):

    def __init__(self, *args, **kwargs):
        super(KongAdminClient, self).__init__(*args, **kwargs)

        self.apis = ApiAdminClient(self.url, self.session)
        self.consumers = ConsumerAdminClient(self.url, self.session)
        self.plugins = PluginAdminClient(self.url, self.session)
        self.services = ServiceAdminClient(self.url, self.session)

    def node_status(self):
        return self.session.get(self.url + 'status/').json()

    def node_information(self):
        return self.session.get(self.url).json()


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

    @abstractmethod
    def _allowed_update_params(self):
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

    def _validate_params(self, query_params, allowed_params):
        validated_params = {}
        for k, val in query_params.items():
            if k in allowed_params:
                validated_params[k] = self._stringify_if_list(val)
            else:
                raise KeyError('invalid query parameter: %s' % k)
        return validated_params

    def _validate_query_params(self, params):
        return self._validate_params(params, self._allowed_query_params)

    def _validate_update_params(self, params):
        return self._validate_params(params, self._allowed_update_params)

    def create(self, name, **kwargs):
        return self._send_create(dict(**kwargs, name=name))

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

    @staticmethod
    def _stringify_if_list(str_or_list):
        if isinstance(str_or_list, (list, dict, tuple)):
            val = ", ".join(str_or_list)
        else:
            val = str_or_list
        return val

    def delete(self, pk_or_id):
        if not isinstance(pk_or_id, str):
            raise TypeError("expected str but got: %s" % type(pk_or_id))

        return self._send_delete(pk_or_id)


class ConsumerAdminClient(KongAbstractClient):

    @property
    def path(self):
        return 'consumers/'

    @property
    def _allowed_query_params(self):
        return ['id'] + self._allowed_update_params

    @property
    def _allowed_update_params(self):
        return ['custom_id', 'username']

    def create(self, username=None, custom_id=None):  # pylint: disable=arguments-differ
        if not username and not custom_id:
            raise ValueError('username or custom_id must be provided to create consumer')

        consumer_data = {}
        if username:
            consumer_data['username'] = username
        if custom_id:
            consumer_data['custom_id'] = custom_id

        return self._send_create(consumer_data)


class PluginAdminClient(KongAbstractClient):

    @property
    def path(self):
        return 'plugins/'

    @property
    def _allowed_query_params(self):
        return 'id', 'name', 'api_id', 'consumer_id'

    @property
    def _allowed_update_params(self):
        return 'name', 'consumer_id'

    def _make_api_plugin_endpoint(self, api_pk):
        return self.url + 'apis/' + api_pk + '/' + self.path

    @staticmethod
    def _add_config_to_data(data, config):
        if config is not None:
            for k, val in config.items():
                data['config.' + k] = val
        return data

    def _resolve_endpoint(self, api_pk):
        endpoint = None
        if api_pk is not None:
            endpoint = self._make_api_plugin_endpoint(api_pk)
        return endpoint

    # pylint: disable=arguments-differ
    def create(self, plugin_name, consumer_id=None, api_name_or_id=None, config=None):
        data = {'name': plugin_name}

        if consumer_id is not None:
            data['consumer_id'] = consumer_id

        endpoint = self._resolve_endpoint(api_name_or_id)

        data = self._add_config_to_data(data, config)

        return self._send_create(data, endpoint=endpoint)

    def delete(self, plugin_id, api_pk=None):  # pylint: disable=arguments-differ
        endpoint = self._resolve_endpoint(api_pk)

        return self._send_delete(plugin_id, endpoint=endpoint)

    def retrieve_enabled(self):
        return self.retrieve('enabled/')["enabled_plugins"]

    def retrieve_schema(self, plugin_name):
        return self.retrieve('schema/' + plugin_name)

    # pylint: disable=arguments-differ
    def update(self, pk_or_id, api_pk=None, config=None, **kwargs):

        query_params = self._validate_update_params(kwargs)

        endpoint = self._resolve_endpoint(api_pk)

        query_params = self._add_config_to_data(query_params, config)

        return self._send_update(pk_or_id, query_params, endpoint=endpoint)


class ApiAdminClient(KongAbstractClient):

    @property
    def _allowed_query_params(self):
        return ['id', 'name', 'upstream_url', 'retries']

    @property
    def _allowed_update_params(self):
        return self._allowed_query_params + ['hosts', 'uris',
                                             'methods', 'strip_uri',
                                             'preserve_host', 'https_only',
                                             'http_if_terminated',
                                             'upstream_connect_timeout',
                                             'upstream_send_timeout',
                                             'upstream_read_timeout',
                                             'created_at']

    @property
    def path(self):
        return 'apis/'

    @staticmethod
    def __api_data_from_response(data):
        validated_data = {}
        for k, val in data.items():
            if k in ApiData.allowed_parameters():
                validated_data[k] = val
        return ApiData(**validated_data)

    # pylint: disable=arguments-differ
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

        data = self._send_create(api_data)
        return self.__api_data_from_response(data)

    def retrieve(self, pk_or_id):
        response = super(ApiAdminClient, self).retrieve(pk_or_id)
        return self.__api_data_from_response(response)

    def list(self, size=10, **kwargs):
        return map(self.__api_data_from_response,
                   super(ApiAdminClient, self).list(size, **kwargs))

    def update(self, pk_or_id, **kwargs):
        response = super(ApiAdminClient, self).update(pk_or_id, **kwargs)
        return self.__api_data_from_response(response)


class ServiceAdminClient(KongAbstractClient):

    @property
    def path(self):
        return 'services/'

    def create(self, name, **kwargs):
        consumer = ConsumerData(name=name, **kwargs)

        return self._send_create(consumer)
