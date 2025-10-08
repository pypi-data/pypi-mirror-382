# -*- coding: utf-8 -*-
# https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi#/Campaigns

from amazon_ad.api.base import ZADOpenAPI


class SbCampaigns(ZADOpenAPI):

    def get_campaigns(self, params=None):
        path = '/sb/campaigns'
        if not params:
            params = {
                'startIndex': 0,  # TODO 翻页
                'count': 5000,
                'stateFilter': 'enabled,paused,archived'
            }
        return self.get(path, params=params)
