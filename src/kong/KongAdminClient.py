from requests import session as requests_session
from kong.ApiAdminClient import ApiAdminClient
from kong.ConsumerAdminClient import ConsumerAdminClient
from kong.PluginAdminClient import PluginAdminClient


class KongAdminClient:

    def __init__(self, kong_admin_url, session=requests_session()):
        self.apis = ApiAdminClient(kong_admin_url, session)
        self.consumers = ConsumerAdminClient(kong_admin_url, session)
        self.plugins = PluginAdminClient(kong_admin_url, session)
