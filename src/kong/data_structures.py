class ApiData(dict):

    @staticmethod
    def allowed_parameters():
        return 'hosts', 'uris', 'methods', 'strip_uri',\
               'preserve_host', 'retries', 'https_only',\
               'http_if_terminated', 'upstream_connect_timeout',\
               'upstream_send_timeout', 'upstream_read_timeout'

    @staticmethod
    def satisfy_semi_optional_parameters(**kwargs):
        return 'hosts' in kwargs\
               or 'uris' in kwargs\
               or 'methods' in kwargs

    def __init__(self, api_name, upstream_url, **kwargs):
        if not self.satisfy_semi_optional_parameters(**kwargs):
            raise ValueError('uris, methods or hosts must be provided to create')

        for k in kwargs:
            if k not in self.allowed_parameters():
                raise ValueError('invalid parameter: %s' % k)

        self['name'] = api_name
        self['upstream_url'] = upstream_url

        for k, v in kwargs.items():
            if k in self.allowed_parameters():
                self[k] = v
