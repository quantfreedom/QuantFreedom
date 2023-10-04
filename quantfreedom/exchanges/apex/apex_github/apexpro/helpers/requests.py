import json

import requests

from apexpro.errors import  ApexproApiError
from apexpro.helpers.request_helpers import remove_nones

# TODO: Use a separate session per client instance.
session = requests.session()
session.headers.update({
    'User-Agent': 'apexpro-python-sdk-1.0.0' ,
    'Content-Type': 'application/x-www-urlencoded',
    'Accept': 'application/json',
})


class Response(object):
    def __init__(self, data={}, headers=None):
        self.data = data
        self.headers = headers


def request(uri, method, headers=None, data_values={}):
    response = send_request(
        uri,
        method,
        headers,
        data=json.dumps(
            remove_nones(data_values)
        )
    )
    if not str(response.status_code).startswith('2'):
        raise ApexproApiError(response)

    if response.content:
        return Response(response.json(), response.headers)
    else:
        return Response('{}', response.headers)


def send_request(uri, method, headers=None, **kwargs):
    return getattr(session, method)(uri, headers=headers, **kwargs)
