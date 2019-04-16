from abc import abstractmethod

import re
from urllib3.util import parse_url, Url

from kong.exceptions import SchemaViolation


class ObjectData:

    def __init__(self, **kwargs):

        validated = self.validate_schema(**kwargs)

        for k, val in validated.items():
            self.validate_parameter(k, val)
            self.__setattr__(k, val)

    @abstractmethod
    def validate_obligatory_parameters(self, **kwargs):
        pass

    @abstractmethod
    def validate_semi_optional_parameters(self, **kwargs):  # pylint:disable=invalid-name
        pass

    def validate_schema(self, **kwargs):
        self.validate_obligatory_parameters(**kwargs)
        self.validate_semi_optional_parameters(**kwargs)
        return kwargs

    @property
    @abstractmethod
    def allowed_parameters(self):
        pass

    def validate_parameter(self, parameter, value):
        if parameter not in self.allowed_parameters:
            raise SchemaViolation('invalid parameter: %s' % parameter)

        if not isinstance(value, (str, int, bool, list, dict, None.__class__)):
            raise ValueError('invalid value: %s value must be str, int, '
                             'bool, _perform_list or dict' % parameter)

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

    def validate_obligatory_parameters(self, **kwargs):
        if 'upstream_url' not in kwargs:
            raise SchemaViolation('name and upstream_url must be provided to _perform_create')

    def validate_semi_optional_parameters(self, **kwargs):
        if not ('hosts' in kwargs
                or 'uris' in kwargs
                or 'methods' in kwargs):
            raise SchemaViolation('uris, methods or hosts must be provided to _perform_create')

        return kwargs

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
    pk_identifier = 'name'

    def validate_semi_optional_parameters(self, **kwargs):
        pass

    def validate_obligatory_parameters(self, **kwargs):
        pass

    def validate_schema(self, **kwargs):

        if 'url' not in kwargs:
            required_fields = ['host', 'protocol']
            for field in required_fields:
                if field not in kwargs:
                    raise SchemaViolation('%s: required field missing' % field)

            if 'port' not in kwargs:
                kwargs['port'] = 80
            if 'path' not in kwargs:
                kwargs['path'] = '/'

        else:
            overflowed_fields = ['host', 'protocol', 'port', 'path']
            for field in overflowed_fields:
                if field in kwargs:
                    raise SchemaViolation('%s: got multiple values' % field)

            url = parse_url(kwargs.pop('url'))
            kwargs['protocol'] = url.scheme
            kwargs['host'] = url.host
            kwargs['port'] = url.port or 80
            kwargs['path'] = url.path or '/'

        return kwargs

    @property
    def allowed_parameters(self):
        return 'name', 'protocol', 'host', 'port', 'path',\
               'retries', 'connect_timeout', 'send_timeout',\
               'read_timeout', 'url', 'id', \
               'created_at', 'updated_at', 'write_timeout', 'tags'

    @property
    def url(self):
        return Url(scheme=self.protocol, host=self.host, port=self.port, path=self.path).url


class PluginData(ObjectData):
    def validate_semi_optional_parameters(self, **kwargs):
        pass

    def validate_obligatory_parameters(self, **kwargs):
        if "name" not in kwargs:
            raise SchemaViolation('name must be provided to _perform_create')

    @property
    def allowed_parameters(self):
        return "id", "service_id", "consumer_id",\
               "name", "config", "enabled",\
               "created_at", "api_id", "route_id"


class ConsumerData(ObjectData):
    def validate_obligatory_parameters(self, **kwargs):
        pass

    @property
    def allowed_parameters(self):
        return "id", "username", "custom_id", "created_at", "tags"

    def validate_semi_optional_parameters(self, **kwargs):
        if ("username" not in kwargs) and ("custom_id" not in kwargs):
            raise SchemaViolation('at least one of username or '
                                  'custom_id must be provided '
                                  'to _perform_create')


class RouteData(ObjectData):
    pk_identifier = 'name'

    def validate_semi_optional_parameters(self, **kwargs):
        if not ('hosts' in kwargs
                or 'paths' in kwargs
                or 'methods' in kwargs):
            raise SchemaViolation('uris, methods or hosts must be provided to _perform_create')

    def validate_obligatory_parameters(self, **kwargs):
        pass

    @property
    def allowed_parameters(self):
        return "name", "id", "created_at", "updated_at", \
               "protocols", "methods", "hosts", \
               "paths", "regex_priority", "strip_path", \
               "preserve_host", "service", "snis", "sources", \
                "destinations", "tags"


class TargetData(ObjectData):
    def validate_semi_optional_parameters(self, **kwargs):
        pass

    def validate_obligatory_parameters(self, **kwargs):
        if "target" not in kwargs:
            raise SchemaViolation("target must be provided to _perform_create")

    @property
    def allowed_parameters(self):
        return "id", "target", "weight", \
               "upstream_id", "created_at"


class UpstreamData(ObjectData):
    @staticmethod
    def allowed_update_params():
        return [
            'name', 'slots', 'hash_on', 'hash_fallback', 'hash_on_header',
            'hash_fallback_header', 'healthchecks.active.timeout',
            'healthchecks.active.concurrency',
            'healthchecks.active.http_path',
            'healthchecks.active.healthy.interval',
            'healthchecks.active.healthy.http_statuses',
            'healthchecks.active.healthy.successes',
            'healthchecks.active.unhealthy.interval',
            'healthchecks.active.unhealthy.http_statuses',
            'healthchecks.active.unhealthy.tcp_failures',
            'healthchecks.active.unhealthy.timeouts',
            'healthchecks.active.unhealthy.http_failures',
            'healthchecks.passive.healthy.http_statuses',
            'healthchecks.passive.healthy.successes',
            'healthchecks.passive.unhealthy.http_statuses',
            'healthchecks.passive.unhealthy.tcp_failures',
            'healthchecks.passive.unhealthy.timeouts',
            'healthchecks.passive.unhealthy.http_failures',
        ]

    def validate_semi_optional_parameters(self, **kwargs):
        if ("hash_on" in kwargs) \
                and (kwargs['hash_on'].lower() == "header") \
                and ("hash_on_header" not in kwargs):
            raise SchemaViolation("hash_on_header required when "
                                  "hash_on is set to header")

        if("hash_fallback" in kwargs) \
                and (kwargs['hash_fallback'].lower() == 'header') \
                and ('hash_fallback_header' not in kwargs):
            raise SchemaViolation("hash_fallback_header required "
                                  "when hash_fallback is set to "
                                  "header")

    def validate_obligatory_parameters(self, **kwargs):
        if "name" not in kwargs:
            raise SchemaViolation("name must be provided to _perform_create")

    @property
    def allowed_parameters(self):
        return self.allowed_update_params()
