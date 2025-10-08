# -*- coding: utf-8 -*-
# Authored by: Josh (joshzda@gmail.com)

try:
    # python2
    from urllib import urlencode
except ImportError:
    # python3
    from urllib.parse import urlencode

from amazon_ad.client.base import BaseClient
from amazon_ad.core.utils.amazon import get_country_endpoint, get_region_endpoint
from amazon_ad.api.auth import Token


class ZADAuthClient(BaseClient):
    API_BASE_URL = None

    token = Token()

    def __init__(self, client_id, client_secret, region="NA", prepare_mode=False, timeout=(10, 10), auto_retry=True, *args, **kwargs):
        super(ZADAuthClient, self).__init__(prepare_mode, timeout, auto_retry, *args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret
        self.region = region

    def get_api_base_url(self):
        return get_region_endpoint(self.region, 'TOKEN')

    def authorization_url(self, redirect_uri, state=''):
        base_url= get_region_endpoint(self.region, 'AUTHORIZATION')

        params = {
            'client_id': self.client_id,
            'scope': 'cpc_advertising:campaign_management',
            'response_type': 'code',
            'state': state,
            'redirect_uri': redirect_uri,
        }
        query_string = urlencode(params)

        return '%s?%s' % (base_url, query_string)