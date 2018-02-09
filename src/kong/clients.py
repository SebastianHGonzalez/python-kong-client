class ApiData(dict):

    def __init__(self, api_name, upstream_url, api_uris):
        self['name'] = api_name
        self['upstream_url'] = upstream_url
        self['uris'] = api_uris


class ApiAdminClient:

    def create(self, api_name, upstream_url, api_uris, **kwargs):
        return ApiData(api_name, upstream_url, api_uris)
