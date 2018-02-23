from kong.KongAbstractClient import KongAbstractClient
from kong.structures import ApiData


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
        d = {}
        for k, v in data.items():
            if k in ApiData.allowed_parameters():
                d[k] = v
        return ApiData(**d)

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
