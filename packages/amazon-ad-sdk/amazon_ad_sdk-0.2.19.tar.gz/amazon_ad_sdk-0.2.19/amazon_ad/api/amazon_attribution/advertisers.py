# -*- coding: utf-8 -*-
"""
https://advertising.amazon.com/API/docs/en-us/amazon-attribution-prod-3p/#/Advertisers
"""

from amazon_ad.api.base import ZADOpenAPI


class AttributionAdvertisers(ZADOpenAPI):

    def get_advertisers(self, params=None):
        path = '/attribution/advertisers'
        return self.get(path, params=params)
