import string
import random

from faker.providers import BaseProvider


class ApiDataProvider(BaseProvider):

    def api_name(self):
        return self.generator.name().replace(' ', '')

    def api_path(self):
        path = self.generator.uri_path()
        if not path.startswith('/'):
            path = '/%s' % path
        return path

    def api_uris(self):
        uris = []
        for _ in range(self.random_int(1, 10)):
            uris.append(self.api_path())
        return uris

    def kong_id(self):
        """
            Generates a random kong_id
            Example: "14656344-9e38-4315-8ae2-c23551ea3b9d"
        :return:
        """
        return self.generator.uuid4()
