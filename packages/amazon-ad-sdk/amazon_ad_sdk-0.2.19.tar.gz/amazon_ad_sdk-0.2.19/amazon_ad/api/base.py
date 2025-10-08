# -*- coding: utf-8 -*-
# Authored by: Josh (joshzda@gmail.com)


class ZADBaseAPI(object):
    API_BASE_URL = None

    def __init__(self, client=None):
        self._client = client

    def _get(self, url, **kwargs):
        if self.API_BASE_URL:
            kwargs['api_base_url'] = self.API_BASE_URL
        return self._client.get(url, **kwargs)

    def _post(self, url, **kwargs):
        if self.API_BASE_URL:
            kwargs['api_base_url'] = self.API_BASE_URL
        return self._client.post(url, **kwargs)

    def _put(self, url, **kwargs):
        if self.API_BASE_URL:
            kwargs['api_base_url'] = self.API_BASE_URL
        return self._client.put(url, **kwargs)


class ZADAPI(ZADBaseAPI):

    def get_header(self):
        return {}

    def _get(self, url, params=None, **kwargs):
        kwargs['params'] = params
        kwargs['headers'] = self.get_header()
        return super(ZADAPI, self)._get(url, **kwargs)

    def _post(self, url, params=None, data=None, **kwargs):
        kwargs['params'] = params
        kwargs['data'] = data
        kwargs['headers'] = self.get_header()
        return super(ZADAPI, self)._post(url, **kwargs)

    def _put(self, url, params=None, data=None, **kwargs):
        kwargs['params'] = params
        kwargs['data'] = data
        kwargs['headers'] = self.get_header()
        return super(ZADAPI, self)._put(url, **kwargs)

    def get(self, url, params=None, **kwargs):
        return self._get(url, params, **kwargs)

    def post(self, url, data=None, params=None, **kwargs):
        return self._post(url, params, data, **kwargs)

    def put(self, url, data=None, params=None, **kwargs):
        return self._put(url, params, data, **kwargs)

    def download(self, url, params=None, **kwargs):
        kwargs['stream'] = True
        return self._get(url, params, **kwargs)



class ZADAuthAPI(ZADAPI):

    def get_header(self):
        _headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "charset": "UTF-8",
            "Connection": "close"
        }

        return _headers


class ZADOpenAPI(ZADAPI):

    def get_header(self):
        _headers = {
            'Amazon-Advertising-API-ClientId': self._client.client_id,
            'Authorization': 'Bearer %s' % self._client.access_token,
            'Content-Type': 'application/json',
            'Connection': 'close',
        }

        if self._client.profile_id is not None:
            _headers.update(
                {
                    "Amazon-Advertising-API-Scope": self._client.profile_id
                }
            )

        return _headers
