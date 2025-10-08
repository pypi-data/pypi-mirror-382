# -*- coding: utf-8 -*-
# Authored by: Josh (joshzda@gmail.com)
from amazon_ad.api.base import ZADAuthAPI

class Token(ZADAuthAPI):

    def get_token(self, code, redirect_uri):
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': self._client.client_id,
            'client_secret': self._client.client_secret
        }

        return self.post('', data)

    def refresh_token(self, refresh_token):
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self._client.client_id,
            'client_secret': self._client.client_secret
        }

        return self.post('', data)