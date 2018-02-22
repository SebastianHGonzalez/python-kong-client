from KongAbstractClient import KongAbstractClient


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

    def create(self, plugin_name, consumer_id=None, api_name_or_id=None, config=None):
        data = {'name': plugin_name}

        if consumer_id is not None:
            data['consumer_id'] = consumer_id

        endpoint = self._resolve_endpoint(api_name_or_id)

        data = self._add_config_to_data(data, config)

        return self._send_create(data, endpoint=endpoint)

    def delete(self, plugin_id, api_pk=None):
        endpoint = self._resolve_endpoint(api_pk)

        return self._send_delete(plugin_id, endpoint=endpoint)

    def retrieve_enabled(self):
        return self.retrieve('enabled/')["enabled_plugins"]

    def retrieve_schema(self, plugin_name):
        return self.retrieve('schema/' + plugin_name)

    def update(self, pk_or_id, api_pk=None, config=None, **kwargs):

        query_params = self._validate_update_params(kwargs)

        endpoint = self._resolve_endpoint(api_pk)

        query_params = self._add_config_to_data(query_params, config)

        return self._send_update(pk_or_id, query_params, endpoint=endpoint)
