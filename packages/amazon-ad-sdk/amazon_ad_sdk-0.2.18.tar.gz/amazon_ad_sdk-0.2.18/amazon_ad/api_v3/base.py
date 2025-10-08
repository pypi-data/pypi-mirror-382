# -*- coding: utf-8 -*-

from amazon_ad.api.base import ZADAPI


class ZADOpenAPIV3(ZADAPI):
    """
    Version 3

    https://advertising.amazon.com/API/docs/en-us/reporting/v3/get-started
    """

    def get_header(self):
        _headers = {
            'Amazon-Advertising-API-ClientId': self._client.client_id,
            'Authorization': 'Bearer %s' % self._client.access_token,
            'Content-Type': 'application/vnd.createasyncreportrequest.v3+json',
            'Connection': 'close',
        }

        if self._client.profile_id is not None:
            _headers.update(
                {
                    "Amazon-Advertising-API-Scope": self._client.profile_id
                }
            )

        return _headers
