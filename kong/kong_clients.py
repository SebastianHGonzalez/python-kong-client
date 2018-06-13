from abc import abstractmethod
from urllib3.util.url import Url, parse_url
from requests import session
from kong.structures import ApiData, ServiceData, ConsumerData, \
    PluginData, RouteData, TargetData, UpstreamData
from kong.exceptions import SchemaViolation


class RestClient:  # pylint:disable=too-few-public-methods

    def __init__(self, url, _session=session()):
        self._session = _session

        self.url = self._normalize_url(url)

    @property
    def session(self):
        return self._session

    @staticmethod
    def _normalize_url(url):
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
        self.routes = RouteAdminClient(self.url, self.session)
        self.upstreams = UpstreamAdminClient(self.url, self.session)
        self.targets = TargetAdminClient(self.url, self.session)

    def node_status(self):
        return self.session.get(self.url + 'status/').json()

    def node_information(self):
        return self.session.get(self.url).json()


class KongAbstractClient(RestClient):

    @property
    @abstractmethod
    def _object_data_class(self):
        return lambda x: x

    def _to_object_data(self, data_dict):
        return self._object_data_class(**data_dict)

    def _to_list_object_data(self, list_data_dict):
        return map(self._to_object_data, list_data_dict)

    def create(self, **kwargs):
        data_dict = self._perform_create(**kwargs)
        return self._to_object_data(data_dict)

    def delete(self, pk_or_id):
        self._perform_delete(pk_or_id)

    def list(self, size=10, **kwargs):
        data_dict = self._perform_list(size, **kwargs)
        return self._to_list_object_data(data_dict)

    def retrieve(self, pk_or_id):
        data_dict = self._perform_retrieve(pk_or_id)
        return self._to_object_data(data_dict)

    def update(self, pk_or_id, **kwargs):
        data_dict = self._perform_update(pk_or_id, **kwargs)
        return self._to_object_data(data_dict)

    @property
    def _endpoint(self):
        return self.url + self._path

    @abstractmethod
    def _path(self):
        pass

    @abstractmethod
    def _allowed_query_params(self):
        pass

    @abstractmethod
    def _allowed_update_params(self):
        pass

    def _send_create(self, data, endpoint=None):

        endpoint = endpoint or self._endpoint

        response = self.session.post(endpoint, json=data)

        if response.status_code == 409:
            raise NameError(response.content)

        if response.status_code != 201:
            raise Exception(response.content)

        return response.json()

    def _send_delete(self, name_or_id, endpoint=None):
        url = (endpoint or self._endpoint) + name_or_id
        response = self.session.delete(url)

        if response.status_code == 404:
            raise NameError(response.content)

        if response.status_code != 204:
            raise Exception(response.content)

    def _send_update(self, pk_or_id, data, endpoint=None):
        url = (endpoint or self._endpoint) + pk_or_id

        response = self.session.patch(url, json=data)

        if response.status_code == 400:
            raise KeyError(response.content)

        if response.status_code == 404:
            raise NameError(response.content)

        if response.status_code != 200:
            raise Exception(response.content)

        return response.json()

    def _send_list(self, size=10, offset=None, **kwargs):
        data = {**{'offset': offset, 'size': size}, **kwargs}

        response = self.session.get(self._endpoint,
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
        #  pylint: disable=pointless-string-statement
        """
        total is deprecated since kong 0.13.0

        return offset, elements, response['total']
        """
        return offset, elements

    def _send_retrieve(self, name_or_id, endpoint=None):
        endpoint = endpoint or self._endpoint
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

    def _perform_create(self, **kwargs):
        return self._send_create(kwargs)

    def _perform_retrieve(self, pk_or_id):
        if not isinstance(pk_or_id, str):
            raise TypeError("expected str but got %s" % type(pk_or_id))

        return self._send_retrieve(pk_or_id)

    def _perform_list(self, size=10, **kwargs):

        query_params = self._validate_query_params(kwargs)

        def generator():
            offset = None
            while True:
                offset, cached = self._send_list(size, offset, **query_params)

                while cached:
                    yield cached.pop()

                if offset is None:
                    break

        return generator()

    #  pylint: disable=pointless-string-statement
    """
    Deprecated since kong 0.13.0

    def count(self):
        return self._send_list(0)[2]
    """

    def _perform_update(self, pk_or_id, **kwargs):

        query_params = self._validate_update_params(kwargs)

        return self._send_update(pk_or_id, query_params)

    @staticmethod
    def _stringify_if_list(str_or_list):
        if isinstance(str_or_list, (list, dict, tuple)):
            val = ", ".join(str_or_list)
        else:
            val = str_or_list
        return val

    def _perform_delete(self, pk_or_id):
        if not isinstance(pk_or_id, str):
            raise TypeError("expected str but got: %s" % type(pk_or_id))

        return self._send_delete(pk_or_id)


class ConsumerAdminClient(KongAbstractClient):

    @property
    def _object_data_class(self):
        return ConsumerData

    @property
    def _path(self):
        return 'consumers/'

    @property
    def _allowed_query_params(self):
        return ['id'] + self._allowed_update_params

    @property
    def _allowed_update_params(self):
        return ['custom_id', 'username']

    def _perform_create(self, username=None, custom_id=None):  # pylint: disable=arguments-differ
        if not username and not custom_id:
            raise ValueError('username or custom_id must be provided to _perform_create consumer')

        consumer_data = {}
        if username:
            consumer_data['username'] = username
        if custom_id:
            consumer_data['custom_id'] = custom_id

        return self._send_create(consumer_data)


class PluginAdminClient(KongAbstractClient):

    @property
    def _object_data_class(self):
        return PluginData

    @property
    def _path(self):
        return 'plugins/'

    @property
    def _allowed_query_params(self):
        return 'id', 'name', 'api_id', 'consumer_id'

    @property
    def _allowed_update_params(self):
        return 'name', 'consumer_id'

    def _make_api_plugin_endpoint(self, api_pk):
        return self.url + 'apis/' + api_pk + '/' + self._path

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
    def _perform_create(self, plugin_name, consumer_id=None, api_name_or_id=None, config=None):
        data = {'name': plugin_name}

        if consumer_id is not None:
            data['consumer_id'] = consumer_id

        endpoint = self._resolve_endpoint(api_name_or_id)

        data = self._add_config_to_data(data, config)

        return self._send_create(data, endpoint=endpoint)

    def _perform_delete(self, plugin_id, api_pk=None):  # pylint: disable=arguments-differ
        endpoint = self._resolve_endpoint(api_pk)

        return self._send_delete(plugin_id, endpoint=endpoint)

    def retrieve_enabled(self):
        list_data_dict = self._perform_retrieve('enabled/')["enabled_plugins"]
        return self._to_list_object_data(list_data_dict)

    def retrieve_schema(self, plugin_name):
        return self._perform_retrieve('schema/' + plugin_name)

    # pylint: disable=arguments-differ
    def _perform_update(self, pk_or_id, api_pk=None, config=None, **kwargs):

        query_params = self._validate_update_params(kwargs)

        endpoint = self._resolve_endpoint(api_pk)

        query_params = self._add_config_to_data(query_params, config)

        return self._send_update(pk_or_id, query_params, endpoint=endpoint)


class ApiAdminClient(KongAbstractClient):

    @property
    def _object_data_class(self):
        return ApiData

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
    def _path(self):
        return 'apis/'

    # pylint: disable=arguments-differ
    def _perform_create(self, name=None, api_data=None, upstream_url=None, **kwargs):

        if isinstance(name, str):
            api_data = ApiData(name=name, upstream_url=upstream_url, **kwargs)

        elif isinstance(api_data, ApiData):
            pass

        elif upstream_url is None:
            raise ValueError("must provide a upstream_url")

        else:
            raise ValueError("must provide ApiData instance or name to _perform_create a api")

        return self._send_create(api_data.as_dict())


class ServiceAdminClient(KongAbstractClient):

    @property
    def _object_data_class(self):
        return ServiceData

    @property
    def _allowed_update_params(self):
        return 'name', 'protocol', 'host', 'port', 'path', \
               'retries', 'connect_timeout', 'send_timeout', \
               'read_timeout', 'url'

    @property
    def _allowed_query_params(self):
        return []

    @property
    def _path(self):
        return 'services/'

    def _perform_create(self, name, **kwargs):
        service = ServiceData(name=name, **kwargs)
        return self._send_create(service.as_dict())


class RouteAdminClient(KongAbstractClient):

    @property
    def _object_data_class(self):
        return RouteData

    @property
    def _allowed_update_params(self):
        return 'protocols', 'methods', 'hosts',\
               'paths', 'strip_path', 'preserve_host',\
               'service',

    @property
    def _allowed_query_params(self):
        return []

    @property
    def _path(self):
        return 'routes/'

    #  pylint: disable=arguments-differ
    def _perform_create(self, service, **kwargs):

        service_id = self.get_service_id(service)

        return self._send_create(dict(**kwargs, service={'id': service_id}))

    def list_associated_to_service(self, service_or_pk, size=10, **kwargs):

        manager = KongAbstractClient(self.url, _session=self.session)
        manager._path = 'services/%s/routes/' % self.get_service_id(service_or_pk)

        list_data_dict = manager._perform_list(size, **kwargs)
        return self._to_list_object_data(list_data_dict)

    @staticmethod
    def get_service_id(service):
        service_id = service

        if not isinstance(service, str):
            try:
                service_id = service.id
            except AttributeError:
                try:
                    service_id = service.name
                except AttributeError:
                    raise SchemaViolation('must provide service or service_id')

        return service_id


class UpstreamAdminClient(KongAbstractClient):

    @property
    def _object_data_class(self):
        return UpstreamData

    @property
    def _allowed_update_params(self):
        return self._object_data_class.allowed_update_params()

    @property
    def _allowed_query_params(self):
        return 'id', 'name', 'hash_on', 'hash_fallback',\
               'hash_on_header', 'hash_fallback_header', 'slots'

    @property
    def _path(self):
        return 'upstreams/'

    def health_status(self, name_or_id):
        url = self._endpoint + name_or_id + '/health/'
        response = self.session.get(url)

        if response.status_code == 404:
            raise NameError(response.content)

        if response.status_code != 200:
            raise Exception(response.content)

        return response.json()


class TargetAdminClient(KongAbstractClient):

    @property
    def _object_data_class(self):
        return TargetData

    def _allowed_update_params(self):
        raise NotImplementedError

    @property
    def _allowed_query_params(self):
        return 'id', 'target', 'weight'

    @property
    def _path(self):
        return 'upstreams/%s/targets/'

    @property
    def _endpoint(self):
        return self.__endpoint

    @_endpoint.setter
    def endpoint(self, val):
        self.__endpoint = val  # pylint: disable=attribute-defined-outside-init

    #  pylint: disable=arguments-differ
    def _perform_create(self, upstream_name_or_id, **kwargs):

        if 'target' not in kwargs:
            raise SchemaViolation('must provide target url to _perform_create a target object')

        self.configure_endpoint(upstream_name_or_id)

        return self._send_create(kwargs)

    def configure_endpoint(self, upstream_name_or_id):
        self.endpoint = self.url + (self._path % upstream_name_or_id)

    #  pylint: disable=arguments-differ
    def _perform_list(self, upstream_name_or_id, size=10, **kwargs):
        self.configure_endpoint(upstream_name_or_id)

        return super(TargetAdminClient, self)._perform_list(size, **kwargs)

    def list_all(self, upstream_name_or_id, size=10, **kwargs):
        self.configure_endpoint(upstream_name_or_id)

        self._endpoint += 'all/'

        list_data_dict = super(TargetAdminClient, self)._perform_list(size, **kwargs)
        return self._to_list_object_data(list_data_dict)

    #  pylint: disable=arguments-differ
    def _perform_delete(self, upstream_name_or_id, target_or_id):
        self.configure_endpoint(upstream_name_or_id)

        return super(TargetAdminClient, self)._perform_delete(target_or_id)

    def set_healthy(self, upstream_name_or_id, target_or_id, is_healthy):
        url = self.url + (self._path % upstream_name_or_id) \
              + target_or_id \
              + ('/healthy/' if is_healthy else '/unhealthy/')
        response = self.session.post(url)

        if response.status_code != 204:
            raise Exception(response.content)

    def _perform_update(self, pk_or_id, **kwargs):
        raise NotImplementedError

    def _perform_retrieve(self, pk_or_id):
        raise NotImplementedError
