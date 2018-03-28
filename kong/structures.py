from abc import abstractmethod

import re
from urllib3.util import parse_url

from kong.exceptions import SchemaViolation


class ObjectData:

    def __init__(self, name, **kwargs):

        self.validate_schema(**kwargs)

        self.validate_parameter('name', name)
        self.name = name

        for k, val in kwargs.items():
            self.validate_parameter(k, val)
            self.__setattr__(k, val)

    @abstractmethod
    def validate_schema(self, **kwargs):
        pass

    @property
    @abstractmethod
    def allowed_parameters(self):
        pass

    def validate_parameter(self, parameter, value):
        if parameter not in self.allowed_parameters:
            raise SchemaViolation('invalid parameter: %s' % parameter)

        if not isinstance(value, (str, int, bool, list, dict)):
            raise ValueError('invalid value: %s value must be str, int, bool, list or dict' % parameter)

    def as_dict(self):
        return self.__dict__.copy()

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


class ApiData(ObjectData):

    @property
    def allowed_parameters(self):
        return 'id', 'name', 'upstream_url',\
               'hosts', 'uris', 'methods', 'strip_uri',\
               'preserve_host', 'retries', 'https_only',\
               'http_if_terminated', 'upstream_connect_timeout',\
               'upstream_send_timeout', 'upstream_read_timeout',\
               'created_at'

    @staticmethod
    def satisfy_semi_optional_parameters(**kwargs):  # pylint: disable=invalid-name
        return 'hosts' in kwargs\
               or 'uris' in kwargs\
               or 'methods' in kwargs

    @staticmethod
    def satisfy_obligatory_parameters(**kwargs):
        return 'upstream_url' in kwargs

    def validate_schema(self, **kwargs):
        if not self.satisfy_obligatory_parameters(**kwargs):
            raise SchemaViolation('name and upstream_url must be provided to create')
        if not self.satisfy_semi_optional_parameters(**kwargs):
            raise SchemaViolation('uris, methods or hosts must be provided to create')

    def add_uri(self, uri):
        self.uris.append(self.__normalize_uri(uri))
        return ", ".join(self.uris)

    @staticmethod
    def __normalize_uri(uri):
        normalized = uri.strip()
        if re.match(pattern=r'([/]{1}[\w\d]+)+\/?',
                    string=uri) is None:
            raise ValueError("invalid uri: %s" % normalized)
        return normalized


class ServiceData(ObjectData):

    @property
    def allowed_parameters(self):
        return 'name', 'protocol', 'host', 'port', 'path',\
               'retries', 'connect_timeout', 'send_timeout',\
               'read_timeout', 'url'
