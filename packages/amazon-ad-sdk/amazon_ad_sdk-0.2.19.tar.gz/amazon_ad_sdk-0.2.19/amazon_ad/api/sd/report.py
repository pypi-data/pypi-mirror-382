# -*- coding: utf-8 -*-
# Authored by: Ryan

from amazon_ad.api.base import ZADOpenAPI

ALLOW_REPORT_TYPES = [
    "campaigns",
    "adGroups",
    "productAds",
    "targets",
    "asins",
]

# 所有的广告策略
ALL_TACTICS = ['T00001', 'T00020', 'T00030', 'remarketing']

REPORT_TYPE_METRIC_MAPPING = {
    'campaigns': {
        'T00020': ['campaignName',
                   'campaignId',

                   'campaignStatus',  # new
                   'campaignBudget',  # new
                   'attributedDetailPageView14d',  # new
                   'viewAttributedDetailPageView14d',  # new
                   
                   'impressions',
                   'clicks',
                   'cost',
                   'currency',
                   'attributedConversions1d',
                   'attributedConversions7d',
                   'attributedConversions14d',
                   'attributedConversions30d',
                   'attributedConversions1dSameSKU',
                   'attributedConversions7dSameSKU',
                   'attributedConversions14dSameSKU',
                   'attributedConversions30dSameSKU',
                   'attributedUnitsOrdered1d',
                   'attributedUnitsOrdered7d',
                   'attributedUnitsOrdered14d',
                   'attributedUnitsOrdered30d',
                   'attributedSales1d',
                   'attributedSales7d',
                   'attributedSales14d',
                   'attributedSales30d',
                   'attributedSales1dSameSKU',
                   'attributedSales7dSameSKU',
                   'attributedSales14dSameSKU',
                   'attributedSales30dSameSKU',
                   'attributedOrdersNewToBrand14d',
                   'attributedSalesNewToBrand14d',
                   'attributedUnitsOrderedNewToBrand14d',
                   'costType',
                   'viewImpressions',
                   'viewAttributedConversions14d',
                   'viewAttributedSales14d',
                   'viewAttributedUnitsOrdered14d'],
        'T00030': ['campaignName',
                   'campaignId',

                   'campaignStatus',  # new
                   'campaignBudget',  # new
                   'attributedDetailPageView14d',  # new
                   'viewAttributedDetailPageView14d',  # new

                   'impressions',
                   'clicks',
                   'cost',
                   'currency',
                   'attributedConversions1d',
                   'attributedConversions7d',
                   'attributedConversions14d',
                   'attributedConversions30d',
                   'attributedConversions1dSameSKU',
                   'attributedConversions7dSameSKU',
                   'attributedConversions14dSameSKU',
                   'attributedConversions30dSameSKU',
                   'attributedUnitsOrdered1d',
                   'attributedUnitsOrdered7d',
                   'attributedUnitsOrdered14d',
                   'attributedUnitsOrdered30d',
                   'attributedSales1d',
                   'attributedSales7d',
                   'attributedSales14d',
                   'attributedSales30d',
                   'attributedSales1dSameSKU',
                   'attributedSales7dSameSKU',
                   'attributedSales14dSameSKU',
                   'attributedSales30dSameSKU',
                   'attributedOrdersNewToBrand14d',
                   'attributedSalesNewToBrand14d',
                   'attributedUnitsOrderedNewToBrand14d',
                   'costType',
                   'viewImpressions',
                   'viewAttributedConversions14d',
                   'viewAttributedSales14d',
                   'viewAttributedUnitsOrdered14d'],
        'remarketing': ['campaignName',
                        'campaignId',
                        'impressions',
                        'clicks',
                        'cost',
                        'currency',
                        'attributedConversions1d',
                        'attributedConversions7d',
                        'attributedConversions14d',
                        'attributedConversions30d',
                        'attributedConversions1dSameSKU',
                        'attributedConversions7dSameSKU',
                        'attributedConversions14dSameSKU',
                        'attributedConversions30dSameSKU',
                        'attributedUnitsOrdered1d',
                        'attributedUnitsOrdered7d',
                        'attributedUnitsOrdered14d',
                        'attributedUnitsOrdered30d',
                        'attributedSales1d',
                        'attributedSales7d',
                        'attributedSales14d',
                        'attributedSales30d',
                        'attributedSales1dSameSKU',
                        'attributedSales7dSameSKU',
                        'attributedSales14dSameSKU',
                        'attributedSales30dSameSKU'],
        'T00001': ['campaignName',
                   'campaignId',
                   'campaignStatus',
                   'currency',
                   'impressions',
                   'clicks',
                   'cost',
                   'attributedDPV14d',
                   'attributedUnitsSold14d',
                   'attributedSales14d'],
        '_matched_target_': ['attributedConversions14d',
                             'attributedConversions14dSameSKU',
                             'attributedConversions1d',
                             'attributedConversions1dSameSKU',
                             'attributedConversions30d',
                             'attributedConversions30dSameSKU',
                             'attributedConversions7d',
                             'attributedConversions7dSameSKU',
                             'attributedDetailPageView14d',
                             'attributedOrdersNewToBrand14d',
                             'attributedSales14d',
                             'attributedSales14dSameSKU',
                             'attributedSales1d',
                             'attributedSales1dSameSKU',
                             'attributedSales30d',
                             'attributedSales30dSameSKU',
                             'attributedSales7d',
                             'attributedSales7dSameSKU',
                             'attributedSalesNewToBrand14d',
                             'attributedUnitsOrdered14d',
                             'attributedUnitsOrdered1d',
                             'attributedUnitsOrdered30d',
                             'attributedUnitsOrdered7d',
                             'attributedUnitsOrderedNewToBrand14d',
                             'campaignBudget',
                             'campaignId',
                             'campaignName',
                             'campaignStatus',
                             'clicks',
                             'cost',
                             'costType',
                             'currency',
                             'impressions',
                             'viewAttributedConversions14d',
                             'viewAttributedDetailPageView14d',
                             'viewAttributedSales14d',
                             'viewAttributedUnitsOrdered14d',
                             'viewImpressions',
                             'viewAttributedOrdersNewToBrand14d',
                             'viewAttributedSalesNewToBrand14d',
                             'viewAttributedUnitsOrderedNewToBrand14d',
                             'attributedBrandedSearches14d',
                             'viewAttributedBrandedSearches14d'],
    },
    'adGroups': {'T00020': ['campaignName',
                            'campaignId',
                            'adGroupName',
                            'adGroupId',

                            'attributedDetailPageView14d',  # new
                            'viewAttributedDetailPageView14d',  # new

                            'impressions',
                            'clicks',
                            'cost',
                            'currency',
                            'attributedConversions1d',
                            'attributedConversions7d',
                            'attributedConversions14d',
                            'attributedConversions30d',
                            'attributedConversions1dSameSKU',
                            'attributedConversions7dSameSKU',
                            'attributedConversions14dSameSKU',
                            'attributedConversions30dSameSKU',
                            'attributedUnitsOrdered1d',
                            'attributedUnitsOrdered7d',
                            'attributedUnitsOrdered14d',
                            'attributedUnitsOrdered30d',
                            'attributedSales1d',
                            'attributedSales7d',
                            'attributedSales14d',
                            'attributedSales30d',
                            'attributedSales1dSameSKU',
                            'attributedSales7dSameSKU',
                            'attributedSales14dSameSKU',
                            'attributedSales30dSameSKU',
                            'attributedOrdersNewToBrand14d',
                            'attributedSalesNewToBrand14d',
                            'attributedUnitsOrderedNewToBrand14d',
                            'bidOptimization',
                            'viewImpressions',
                            'viewAttributedConversions14d',
                            'viewAttributedSales14d',
                            'viewAttributedUnitsOrdered14d'],
                 'T00030': ['campaignName',
                            'campaignId',
                            'adGroupName',
                            'adGroupId',

                            'attributedDetailPageView14d',  # new
                            'viewAttributedDetailPageView14d',  # new

                            'impressions',
                            'clicks',
                            'cost',
                            'currency',
                            'attributedConversions1d',
                            'attributedConversions7d',
                            'attributedConversions14d',
                            'attributedConversions30d',
                            'attributedConversions1dSameSKU',
                            'attributedConversions7dSameSKU',
                            'attributedConversions14dSameSKU',
                            'attributedConversions30dSameSKU',
                            'attributedUnitsOrdered1d',
                            'attributedUnitsOrdered7d',
                            'attributedUnitsOrdered14d',
                            'attributedUnitsOrdered30d',
                            'attributedSales1d',
                            'attributedSales7d',
                            'attributedSales14d',
                            'attributedSales30d',
                            'attributedSales1dSameSKU',
                            'attributedSales7dSameSKU',
                            'attributedSales14dSameSKU',
                            'attributedSales30dSameSKU',
                            'attributedOrdersNewToBrand14d',
                            'attributedSalesNewToBrand14d',
                            'attributedUnitsOrderedNewToBrand14d',
                            'bidOptimization',
                            'viewImpressions',
                            'viewAttributedConversions14d',
                            'viewAttributedSales14d',
                            'viewAttributedUnitsOrdered14d'],
                 'remarketing': ['campaignName',
                                 'campaignId',
                                 'adGroupName',
                                 'adGroupId',
                                 'impressions',
                                 'clicks',
                                 'cost',
                                 'currency',
                                 'attributedConversions1d',
                                 'attributedConversions7d',
                                 'attributedConversions14d',
                                 'attributedConversions30d',
                                 'attributedConversions1dSameSKU',
                                 'attributedConversions7dSameSKU',
                                 'attributedConversions14dSameSKU',
                                 'attributedConversions30dSameSKU',
                                 'attributedUnitsOrdered1d',
                                 'attributedUnitsOrdered7d',
                                 'attributedUnitsOrdered14d',
                                 'attributedUnitsOrdered30d',
                                 'attributedSales1d',
                                 'attributedSales7d',
                                 'attributedSales14d',
                                 'attributedSales30d',
                                 'attributedSales1dSameSKU',
                                 'attributedSales7dSameSKU',
                                 'attributedSales14dSameSKU',
                                 'attributedSales30dSameSKU'],
                 '_matched_target_': ['adGroupId',
                                      'adGroupName',
                                      'attributedConversions14d',
                                      'attributedConversions14dSameSKU',
                                      'attributedConversions1d',
                                      'attributedConversions1dSameSKU',
                                      'attributedConversions30d',
                                      'attributedConversions30dSameSKU',
                                      'attributedConversions7d',
                                      'attributedConversions7dSameSKU',
                                      'attributedDetailPageView14d',
                                      'attributedOrdersNewToBrand14d',
                                      'attributedSales14d',
                                      'attributedSales14dSameSKU',
                                      'attributedSales1d',
                                      'attributedSales1dSameSKU',
                                      'attributedSales30d',
                                      'attributedSales30dSameSKU',
                                      'attributedSales7dSameSKU',
                                      'attributedUnitsOrdered14d',
                                      'attributedUnitsOrdered1d',
                                      'attributedUnitsOrdered30d',
                                      'attributedUnitsOrdered7d',
                                      'attributedUnitsOrderedNewToBrand14d',
                                      'bidOptimization',
                                      'campaignId',
                                      'campaignName',
                                      'clicks',
                                      'cost',
                                      'currency',
                                      'impressions',
                                      'viewAttributedConversions14d',
                                      'viewAttributedDetailPageView14d',
                                      'viewAttributedSales14d',
                                      'viewAttributedUnitsOrdered14d',
                                      'viewImpressions',
                                      'viewAttributedOrdersNewToBrand14d',
                                      'viewAttributedSalesNewToBrand14d',
                                      'viewAttributedUnitsOrderedNewToBrand14d',
                                      'attributedBrandedSearches14d',
                                      'viewAttributedBrandedSearches14d',
                                      'attributedSales7d',  # 2022-10-11发现接口实际支持而文档缺没有描述
                                      'attributedSalesNewToBrand14d',  # 2022-10-11发现接口实际支持而文档缺没有描述
                                      ],
                 },
    'productAds': {'T00020': ['campaignName',
                              'campaignId',
                              'adGroupName',
                              'adGroupId',

                              'attributedDetailPageView14d',  # new
                              'viewAttributedDetailPageView14d',  # new

                              'asin',
                              'sku',
                              'adId',
                              'impressions',
                              'clicks',
                              'cost',
                              'currency',
                              'attributedConversions1d',
                              'attributedConversions7d',
                              'attributedConversions14d',
                              'attributedConversions30d',
                              'attributedConversions1dSameSKU',
                              'attributedConversions7dSameSKU',
                              'attributedConversions14dSameSKU',
                              'attributedConversions30dSameSKU',
                              'attributedUnitsOrdered1d',
                              'attributedUnitsOrdered7d',
                              'attributedUnitsOrdered14d',
                              'attributedUnitsOrdered30d',
                              'attributedSales1d',
                              'attributedSales7d',
                              'attributedSales14d',
                              'attributedSales30d',
                              'attributedSales1dSameSKU',
                              'attributedSales7dSameSKU',
                              'attributedSales14dSameSKU',
                              'attributedSales30dSameSKU',
                              'attributedOrdersNewToBrand14d',
                              'attributedSalesNewToBrand14d',
                              'attributedUnitsOrderedNewToBrand14d',
                              'viewImpressions',
                              'viewAttributedConversions14d',
                              'viewAttributedSales14d',
                              'viewAttributedUnitsOrdered14d'],
                   'T00030': ['campaignName',
                              'campaignId',
                              'adGroupName',
                              'adGroupId',

                              'attributedDetailPageView14d',  # new
                              'viewAttributedDetailPageView14d',  # new

                              'asin',
                              'sku',
                              'adId',
                              'impressions',
                              'clicks',
                              'cost',
                              'currency',
                              'attributedConversions1d',
                              'attributedConversions7d',
                              'attributedConversions14d',
                              'attributedConversions30d',
                              'attributedConversions1dSameSKU',
                              'attributedConversions7dSameSKU',
                              'attributedConversions14dSameSKU',
                              'attributedConversions30dSameSKU',
                              'attributedUnitsOrdered1d',
                              'attributedUnitsOrdered7d',
                              'attributedUnitsOrdered14d',
                              'attributedUnitsOrdered30d',
                              'attributedSales1d',
                              'attributedSales7d',
                              'attributedSales14d',
                              'attributedSales30d',
                              'attributedSales1dSameSKU',
                              'attributedSales7dSameSKU',
                              'attributedSales14dSameSKU',
                              'attributedSales30dSameSKU',
                              'attributedOrdersNewToBrand14d',
                              'attributedSalesNewToBrand14d',
                              'attributedUnitsOrderedNewToBrand14d',
                              'viewImpressions',
                              'viewAttributedConversions14d',
                              'viewAttributedSales14d',
                              'viewAttributedUnitsOrdered14d'],
                   'remarketing': ['campaignName',
                                   'campaignId',
                                   'adGroupName',
                                   'adGroupId',
                                   'asin',
                                   'sku',
                                   'adId',
                                   'impressions',
                                   'clicks',
                                   'cost',
                                   'currency',
                                   'attributedConversions1d',
                                   'attributedConversions7d',
                                   'attributedConversions14d',
                                   'attributedConversions30d',
                                   'attributedConversions1dSameSKU',
                                   'attributedConversions7dSameSKU',
                                   'attributedConversions14dSameSKU',
                                   'attributedConversions30dSameSKU',
                                   'attributedUnitsOrdered1d',
                                   'attributedUnitsOrdered7d',
                                   'attributedUnitsOrdered14d',
                                   'attributedUnitsOrdered30d',
                                   'attributedSales1d',
                                   'attributedSales7d',
                                   'attributedSales14d',
                                   'attributedSales30d',
                                   'attributedSales1dSameSKU',
                                   'attributedSales7dSameSKU',
                                   'attributedSales14dSameSKU',
                                   'attributedSales30dSameSKU']},
    'targets': {'T00020': ['campaignName',
                           'campaignId',
                           'adGroupName',
                           'adGroupId',
                           'targetId',
                           'targetingExpression',
                           'targetingText',
                           'targetingType',

                           'attributedDetailPageView14d',  # new
                           'viewAttributedDetailPageView14d',  # new

                           'impressions',
                           'clicks',
                           'cost',
                           'currency',
                           'attributedConversions1d',
                           'attributedConversions7d',
                           'attributedConversions14d',
                           'attributedConversions30d',
                           'attributedConversions1dSameSKU',
                           'attributedConversions7dSameSKU',
                           'attributedConversions14dSameSKU',
                           'attributedConversions30dSameSKU',
                           'attributedUnitsOrdered1d',
                           'attributedUnitsOrdered7d',
                           'attributedUnitsOrdered14d',
                           'attributedUnitsOrdered30d',
                           'attributedSales1d',
                           'attributedSales7d',
                           'attributedSales14d',
                           'attributedSales30d',
                           'attributedSales1dSameSKU',
                           'attributedSales7dSameSKU',
                           'attributedSales14dSameSKU',
                           'attributedSales30dSameSKU',
                           'attributedOrdersNewToBrand14d',
                           'attributedSalesNewToBrand14d',
                           'attributedUnitsOrderedNewToBrand14d',
                           'viewImpressions',
                           'viewAttributedConversions14d',
                           'viewAttributedSales14d',
                           'viewAttributedUnitsOrdered14d'],
                'T00030': ['campaignName',
                           'campaignId',
                           'adGroupName',
                           'adGroupId',
                           'targetId',
                           'targetingExpression',
                           'targetingText',
                           'targetingType',

                           'attributedDetailPageView14d',  # new
                           'viewAttributedDetailPageView14d',  # new

                           'impressions',
                           'clicks',
                           'cost',
                           'currency',
                           'attributedConversions1d',
                           'attributedConversions7d',
                           'attributedConversions14d',
                           'attributedConversions30d',
                           'attributedConversions1dSameSKU',
                           'attributedConversions7dSameSKU',
                           'attributedConversions14dSameSKU',
                           'attributedConversions30dSameSKU',
                           'attributedUnitsOrdered1d',
                           'attributedUnitsOrdered7d',
                           'attributedUnitsOrdered14d',
                           'attributedUnitsOrdered30d',
                           'attributedSales1d',
                           'attributedSales7d',
                           'attributedSales14d',
                           'attributedSales30d',
                           'attributedSales1dSameSKU',
                           'attributedSales7dSameSKU',
                           'attributedSales14dSameSKU',
                           'attributedSales30dSameSKU',
                           'attributedOrdersNewToBrand14d',
                           'attributedSalesNewToBrand14d',
                           'attributedUnitsOrderedNewToBrand14d',
                           'viewImpressions',
                           'viewAttributedConversions14d',
                           'viewAttributedSales14d',
                           'viewAttributedUnitsOrdered14d'],
                '_matched_target_': ['adGroupId',
                                     'adGroupName',
                                     'attributedConversions14d',
                                     'attributedConversions14dSameSKU',
                                     'attributedConversions1d',
                                     'attributedConversions1dSameSKU',
                                     'attributedConversions30d',
                                     'attributedConversions30dSameSKU',
                                     'attributedConversions7d',
                                     'attributedConversions7dSameSKU',
                                     'attributedDetailPageView14d',
                                     'attributedOrdersNewToBrand14d',
                                     'attributedSales14d',
                                     'attributedSales14dSameSKU',
                                     'attributedSales1d',
                                     'attributedSales1dSameSKU',
                                     'attributedSales30d',
                                     'attributedSales30dSameSKU',
                                     'attributedSales7d',
                                     'attributedSales7dSameSKU',
                                     'attributedSalesNewToBrand14d',
                                     'attributedUnitsOrdered14d',
                                     'attributedUnitsOrdered1d',
                                     'attributedUnitsOrdered30d',
                                     'attributedUnitsOrdered7d',
                                     'attributedUnitsOrderedNewToBrand14d',
                                     'campaignId',
                                     'campaignName',
                                     'clicks',
                                     'cost',
                                     'currency',
                                     'impressions',
                                     'targetId',
                                     'targetingExpression',
                                     'targetingText',
                                     'targetingType',
                                     'viewAttributedConversions14d',
                                     'viewAttributedDetailPageView14d',
                                     'viewAttributedSales14d',
                                     'viewAttributedUnitsOrdered14d',
                                     'viewAttributedOrdersNewToBrand14d',
                                     'viewAttributedSalesNewToBrand14d',
                                     'viewAttributedUnitsOrderedNewToBrand14d',
                                     'attributedBrandedSearches14d',
                                     'viewAttributedBrandedSearches14d',
                                     'viewImpressions',  # 2022-10-11发现接口实际支持而文档缺没有描述
                                     ],
                },

    # Unsupported fields for asin report: attributedDetailPageView14d,viewAttributedDetailPageView14d,costType.
    'asins': {'T00020': ['campaignName',
                         'campaignId',
                         'adGroupName',
                         'adGroupId',

                         # 'attributedDetailPageView14d',  # new
                         # 'viewAttributedDetailPageView14d',  # new
                         # 'costType',  # new
                         'attributedOrdersNewToBrand14d',  # new
                         'attributedSalesNewToBrand14d',  # new
                         'attributedUnitsOrderedNewToBrand14d',  # new

                         'asin',
                         'otherAsin',
                         'sku',
                         'currency',
                         'attributedUnitsOrdered1dOtherSKU',
                         'attributedUnitsOrdered7dOtherSKU',
                         'attributedUnitsOrdered14dOtherSKU',
                         'attributedUnitsOrdered30dOtherSKU',
                         'attributedSales1dOtherSKU',
                         'attributedSales7dOtherSKU',
                         'attributedSales14dOtherSKU',
                         'attributedSales30dOtherSKU'],
              'T00030': ['campaignName',
                         'campaignId',
                         'adGroupName',
                         'adGroupId',

                         # 'attributedDetailPageView14d',  # new
                         # 'viewAttributedDetailPageView14d',  # new
                         # 'costType',  # new
                         'attributedOrdersNewToBrand14d',  # new
                         'attributedSalesNewToBrand14d',  # new
                         'attributedUnitsOrderedNewToBrand14d',  # new

                         'asin',
                         'otherAsin',
                         'sku',
                         'currency',
                         'attributedUnitsOrdered1dOtherSKU',
                         'attributedUnitsOrdered7dOtherSKU',
                         'attributedUnitsOrdered14dOtherSKU',
                         'attributedUnitsOrdered30dOtherSKU',
                         'attributedSales1dOtherSKU',
                         'attributedSales7dOtherSKU',
                         'attributedSales14dOtherSKU',
                         'attributedSales30dOtherSKU']}}


class SdReport(ZADOpenAPI):
    def request(self, record_type, report_date, tactic, metrics, segment=None):
        """
        POST    /sd/{recordType}/report
        """

        path = '/sd/{record_type}/report'.format(record_type=record_type)

        if isinstance(metrics, (list, tuple)):
            metrics = ','.join(metrics)

        data = {
            'reportDate': report_date,
            'tactic': tactic,
            'metrics': metrics
        }
        if segment:
            data['segment'] = segment

        return self.post(path, data)

    def _get_metrics(self, metrics, default):
        if not metrics:
            metrics = default

        return metrics

    def campaigns(self, report_date, tactic, metrics=None, **kwargs):

        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('campaigns').get(tactic))

        return self.request('campaigns', report_date, tactic, metrics)

    def campaigns_t00001(self, report_date, metrics=None, **kwargs):
        tactic = 'T00001'
        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('campaigns').get(tactic))
        return self.request('campaigns', report_date, tactic, metrics)

    def campaigns_t00020(self, report_date, metrics=None, **kwargs):
        tactic = 'T00020'
        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('campaigns').get(tactic))
        return self.request('campaigns', report_date, tactic, metrics)

    def campaigns_t00020_matched_target(self, report_date, metrics=None, **kwargs):
        tactic = 'T00020'
        if not metrics:
            metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('campaigns').get('_matched_target_'))
        return self.request('campaigns', report_date, tactic, metrics, segment='matchedTarget')

    def campaigns_t00030(self, report_date, metrics=None, **kwargs):
        tactic = 'T00030'
        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('campaigns').get(tactic))
        return self.request('campaigns', report_date, tactic, metrics)

    def campaigns_t00030_matched_target(self, report_date, metrics=None, **kwargs):
        tactic = 'T00030'
        if not metrics:
            metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('campaigns').get('_matched_target_'))
        return self.request('campaigns', report_date, tactic, metrics, segment='matchedTarget')

    def campaigns_remarketing(self, report_date, metrics=None, **kwargs):
        tactic = 'remarketing'
        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('campaigns').get(tactic))
        return self.request('campaigns', report_date, tactic, metrics)

    def ad_groups(self, report_date, tactic, metrics=None, **kwargs):

        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('adGroups').get(tactic))

        return self.request('adGroups', report_date, tactic, metrics)

    def ad_groups_t00020(self, report_date, metrics=None, **kwargs):
        tactic = 'T00020'
        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('adGroups').get(tactic))
        return self.request('adGroups', report_date, tactic, metrics)

    def ad_groups_t00020_matched_target(self, report_date, metrics=None, **kwargs):
        tactic = 'T00020'
        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('adGroups').get('_matched_target_'))
        return self.request('adGroups', report_date, tactic, metrics, segment='matchedTarget')

    def ad_groups_t00030(self, report_date, metrics=None, **kwargs):
        tactic = 'T00030'
        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('adGroups').get(tactic))
        return self.request('adGroups', report_date, tactic, metrics)

    def ad_groups_t00030_matched_target(self, report_date, metrics=None, **kwargs):
        tactic = 'T00030'
        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('adGroups').get('_matched_target_'))
        return self.request('adGroups', report_date, tactic, metrics, segment='matchedTarget')

    def ad_groups_remarketing(self, report_date, metrics=None, **kwargs):
        tactic = 'remarketing'
        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('adGroups').get(tactic))
        return self.request('adGroups', report_date, tactic, metrics)

    def product_ads(self, report_date, tactic, metrics=None, **kwargs):

        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('productAds').get(tactic))

        return self.request('productAds', report_date, tactic, metrics)

    def product_ads_t00020(self, report_date, metrics=None, **kwargs):
        tactic = 'T00020'
        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('productAds').get(tactic))
        return self.request('productAds', report_date, tactic, metrics)

    def product_ads_t00030(self, report_date, metrics=None, **kwargs):
        tactic = 'T00030'
        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('productAds').get(tactic))
        return self.request('productAds', report_date, tactic, metrics)

    def product_ads_remarketing(self, report_date, metrics=None, **kwargs):
        tactic = 'remarketing'
        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('productAds').get(tactic))
        return self.request('productAds', report_date, tactic, metrics)

    def targets(self, report_date, tactic, metrics=None, **kwargs):

        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('targets').get(tactic))

        return self.request('targets', report_date, tactic, metrics)

    def targets_t00020(self, report_date, metrics=None, **kwargs):
        tactic = 'T00020'
        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('targets').get(tactic))
        return self.request('targets', report_date, tactic, metrics)

    def targets_t00020_matched_target(self, report_date, metrics=None, **kwargs):
        tactic = 'T00020'
        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('targets').get('_matched_target_'))
        return self.request('targets', report_date, tactic, metrics, segment='matchedTarget')

    def targets_t00030(self, report_date, metrics=None, **kwargs):
        tactic = 'T00030'
        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('targets').get(tactic))
        return self.request('targets', report_date, tactic, metrics)

    def targets_t00030_matched_target(self, report_date, metrics=None, **kwargs):
        tactic = 'T00030'
        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('targets').get('_matched_target_'))
        return self.request('targets', report_date, tactic, metrics, segment='matchedTarget')

    def asins(self, report_date, tactic, metrics=None, **kwargs):

        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('asins').get(tactic))

        return self.request('asins', report_date, tactic, metrics)

    def asins_t00020(self, report_date, metrics=None, **kwargs):
        tactic = 'T00020'
        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('asins').get(tactic))
        return self.request('asins', report_date, tactic, metrics)

    def asins_t00030(self, report_date, metrics=None, **kwargs):
        tactic = 'T00030'
        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('asins').get(tactic))
        return self.request('asins', report_date, tactic, metrics)

    def local_test(self, **kwargs):
        """
        测试用的接口
        """
        path = kwargs.get('path')
        data = kwargs.get('data')
        print(path)
        return self.post(path, data)
