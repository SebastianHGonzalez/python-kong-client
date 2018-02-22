## Usage
#### Install
    $ python setup.py install
    
#### Import into your project
```python
from kong.KongAdminClient import KongAdminClient
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