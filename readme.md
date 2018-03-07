# Python Kong Client
[![Build Status](https://travis-ci.org/SebastianHGonzalez/python-kong-client.svg?branch=master)](https://travis-ci.org/SebastianHGonzalez/python-kong-client) 

## Description
This is a small library to provide [kong](http://getkong.org/) server administration functionality inside your python application

This library is currently in version 0.1.4 and it was built around [kong 0.12.x specifications](https://getkong.org/docs/0.12.x/admin-api/)

## Features
Supported operations for Apis, Consumers and Plugins
- create
- delete
- retrieve
- update
- list
- count

Supported additional operations for Plugins
- retrieve_enabled
- retrieve_schema

Not supported
- update_or_create
- Information routes (yet)
- Certificates object routes (yet)
- SNI object routes (yet)
- Upstream object routes (yet)
- Target object routes (yet)

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
for more info checkout [kong documentation](https://getkong.org/docs/0.12.x/admin-api/)

## Development
#### setup
    $ npm install
    $ git hooks install
    $ pip install -r requirements.txt
    
#### testing
    $ pytest