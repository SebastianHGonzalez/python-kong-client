# Python Kong Client
[![Build Status](https://travis-ci.org/devartis/python-kong-client.svg?branch=master)](https://travis-ci.org/devartis/python-kong-client) 

## Description
This is a small library to provide [kong](http://getkong.org/) server administration functionality inside your python application

This library is currently in version 0.1.7 and it was built around [kong 0.13.x specifications](https://getkong.org/docs/0.13.x/admin-api/)

## Features
Supported Information Routes
- node_status
- node_information

Supported operations for Services, Routes, Apis, Consumers, Plugins and Upstreams
- create
- delete
- retrieve
- update
- list

Additional supported operations for Routes
- list_associated_to_service

Additional supported operations for Plugins
- retrieve_enabled
- retrieve_schema

Additional supported operations for Upstreams
- health_status

Additional supported operations for Targets
- list_all
- set_healthy

Not supported
- update_or_create
- count (dropped in 0.16/kong 0.13.0)
- Certificates object routes (yet)
- SNI object routes (yet)

## Usage
#### Install
    $ python setup.py install
    
#### Import into your project
```python
from kong.kong_clients import KongAdminClient
```
#### Creating a kong api
```python
KONG_ADMIN_URL = 'http://localhost:8001/'
kong_client = KongAdminClient(KONG_ADMIN_URL)

kong_client.apis.create(api_name,  # Any string
                        api_upstream_url,  # Url string 'http://foo.bar/something"
                        uris=api_uris) # List of uri strings
```
for more info checkout [kong documentation](https://getkong.org/docs/0.13.x/admin-api/)

## Development
#### setup
    $ npm install
    $ git hooks install
    $ pip install -r requirements.txt
    
#### testing
    $ pytest
