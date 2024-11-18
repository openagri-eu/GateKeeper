#!/usr/bin/env python
from uuid import uuid4
import os
import jwt
from datetime import datetime, timedelta
import json
import requests
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_calendar.settings')

from django.conf import settings

import ipdb; ipdb.set_trace()

gatekeeper_url = 'http://localhost:8001'

url = f"{gatekeeper_url}/api/login/"

# User credentials in test database
data = {
    "username": "admin2",
    "password": "admin2"
}

# Send POST request to get the token
response = requests.post(url, data=data)
print(response.json())

if response.status_code == 200:
    # Extract tokens from the JSON response
    tokens = response.json()
    token = tokens.get("access")

register_service = False
if register_service:

    reg_url = f'{gatekeeper_url}/api/register_service/'

    data = {
        'service_name': 'FarmCalendar',
        'api_root_url': 'http://localhost:8002/api/v1/'
    }

    headers = {
        'Authorization': f'Bearer {token}',

    }

    request_kwargs = {
        'headers': headers,
        'data': data
    }

    response = requests.post(reg_url, **request_kwargs)
    print(f"Response Status Code: {response.status_code}\n\n")
    print(f"Response Content: {json.dumps(response.json(), indent=4)}\n\n")


# ask for a farm, for now the service name can be passed
# in the future it would be best to provide a OCSM class/attributes mapping to service endpoints,
# based on their OpenAPI (swagger) schema. But I'm not sure this is much viable,
# since it would requires the services to have a standardized endpoint definition (i.e., use REST API for example).
# so for now this is a standard reverse proxy behaviour,
#
# but in the future it would be interesting to provide
# and endpoint that someone can access based only on the OCSM ontology to post/udpate/retrieve/filter out specifc resources

farm_url = f'{gatekeeper_url}/api/proxy/FarmCalendar/Farm/1/'

headers = {
    'Authorization': f'Bearer {token}',

}
request_kwargs = {
    'headers': headers,
}
response = requests.get(farm_url, **request_kwargs)
print(f"Response Status Code: {response.status_code}\n\n")
print(f"Response Content: {json.dumps(response.json(), indent=4)}\n\n")