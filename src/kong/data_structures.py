class ApiData(dict):

    @staticmethod
    def allowed_parameters():
        return 'id', 'name', 'upstream_url',\
               'hosts', 'uris', 'methods', 'strip_uri',\
               'preserve_host', 'retries', 'https_only',\
               'http_if_terminated', 'upstream_connect_timeout',\
               'upstream_send_timeout', 'upstream_read_timeout'

    @staticmethod
    def satisfy_semi_optional_parameters(**kwargs):
        return 'hosts' in kwargs\
               or 'uris' in kwargs\
               or 'methods' in kwargs

    @staticmethod
    def satisfy_obligatory_parameters(**kwargs):
        return 'name' in kwargs \
               and 'upstream_url' in kwargs

    def __init__(self, *args, **kwargs):
        if not self.satisfy_obligatory_parameters(**kwargs):
            raise ValueError('name and upstream_url must be provided to create')

        if not self.satisfy_semi_optional_parameters(**kwargs):
            raise ValueError('uris, methods or hosts must be provided to create')

        for k, v in kwargs.items():
            if k in self.allowed_parameters():
                self[k] = v
            else:
                raise ValueError('invalid parameter: %s' % k)
