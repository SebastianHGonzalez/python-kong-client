from kong.KongAbstractClient import KongAbstractClient


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

    def create(self, username=None, custom_id=None):
        if not username and not custom_id:
            raise ValueError('username or custom_id must be provided to create consumer')

        consumer_data = {}
        if username:
            consumer_data['username'] = username
        if custom_id:
            consumer_data['custom_id'] = custom_id

        return self._send_create(consumer_data)
