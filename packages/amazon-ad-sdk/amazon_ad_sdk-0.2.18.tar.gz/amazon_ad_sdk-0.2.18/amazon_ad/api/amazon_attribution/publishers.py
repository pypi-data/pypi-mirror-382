# -*- coding: utf-8 -*-
"""
https://advertising.amazon.com/API/docs/en-us/amazon-attribution-prod-3p/#/Publishers
"""

from amazon_ad.api.base import ZADOpenAPI


class AttributionPublishers(ZADOpenAPI):

    def get_publishers(self, params=None):
        path = '/attribution/publishers'
        return self.get(path, params=params)
