# -*- coding: utf-8 -*-

from amazon_ad.api.base import ZADOpenAPI

ALLOW_REPORT_TYPES = [
    "campaigns",
    "adGroups",
    "targets",
    "keywords",
]


DEFAULT_REPORT_METRICS = {
    "campaigns":  [
        "campaignName",
        "campaignId",
        "campaignStatus",
        "campaignBudget",
        "campaignBudgetType",

        # "campaignRuleBasedBudget",  # V2
        # "applicableBudgetRuleId",  # V2
        # "applicableBudgetRuleName",  # V2
        #
        # "adGroupName",
        # "adGroupId",
        # "keywordText",
        # "keywordBid",
        # "keywordStatus",
        # "targetId",
        #
        # "searchTermImpressionRank",
        # "searchTermImpressionShare"
        #
        # "targetingExpression",
        # "targetingText",
        # "targetingType",
        # "matchType",

        "impressions",
        "clicks",
        "cost",
        "attributedDetailPageViewsClicks14d",
        "attributedSales14d",
        "attributedSales14dSameSKU",
        "attributedConversions14d",
        "attributedConversions14dSameSKU",
        "attributedOrdersNewToBrand14d",
        "attributedOrdersNewToBrandPercentage14d",
        "attributedOrderRateNewToBrand14d",
        "attributedSalesNewToBrand14d",
        "attributedSalesNewToBrandPercentage14d",
        "attributedUnitsOrderedNewToBrand14d",
        "attributedUnitsOrderedNewToBrandPercentage14d",
        "unitsSold14d",
        "dpv14d",

        # "query",
        # "viewableImpressions",
        # "videoFirstQuartileViews",
        # "videoMidpointViews",
        # "videoThirdQuartileViews",
        # "videoCompleteViews",
        # "video5SecondViews",
        # "video5SecondViewRate",
        # "videoUnmutes",
        # "vtr",
        # "vctr",
    ],
    "adGroups": [
        "campaignName",
        "campaignId",
        "campaignStatus",
        "campaignBudget",
        "campaignBudgetType",

        # "campaignRuleBasedBudget",  # V2
        # "applicableBudgetRuleId",  # V2
        # "applicableBudgetRuleName",  # V2
        #
        "adGroupName",
        "adGroupId",
        # "keywordText",
        # "keywordBid",
        # "keywordStatus",
        # "targetId",
        #
        # "searchTermImpressionRank",
        # "searchTermImpressionShare"
        #
        # "targetingExpression",
        # "targetingText",
        # "targetingType",
        # "matchType",

        "impressions",
        "clicks",
        "cost",
        "attributedDetailPageViewsClicks14d",
        "attributedSales14d",
        "attributedSales14dSameSKU",
        "attributedConversions14d",
        "attributedConversions14dSameSKU",
        "attributedOrdersNewToBrand14d",
        "attributedOrdersNewToBrandPercentage14d",
        "attributedOrderRateNewToBrand14d",
        "attributedSalesNewToBrand14d",
        "attributedSalesNewToBrandPercentage14d",
        "attributedUnitsOrderedNewToBrand14d",
        "attributedUnitsOrderedNewToBrandPercentage14d",
        "unitsSold14d",
        "dpv14d",

        # "query",
        # "viewableImpressions",
        # "videoFirstQuartileViews",
        # "videoMidpointViews",
        # "videoThirdQuartileViews",
        # "videoCompleteViews",
        # "video5SecondViews",
        # "video5SecondViewRate",
        # "videoUnmutes",
        # "vtr",
        # "vctr",
    ],

    # Unsupported fields for targets report: keywordStatus,keywordText,keywordBid,matchType.
    # Unrecognized metric: query
    # Unsupported fields for targets report:
    # applicableBudgetRuleId,applicableBudgetRuleName,searchTermImpressionShare,campaignRuleBasedBudget,searchTermImpressionRank.
    # Metric vtr is not available for campaign type HEADLINE_SEARCH
    "targets": [
        "campaignName",
        "campaignId",
        "campaignStatus",
        "campaignBudget",
        "campaignBudgetType",

        # "campaignRuleBasedBudget",  # V2
        # "applicableBudgetRuleId",  # V2
        # "applicableBudgetRuleName",  # V2

        "adGroupName",
        "adGroupId",
        # "keywordText",
        # "keywordBid",
        # "keywordStatus",
        "targetId",

        # "searchTermImpressionRank",  # V2
        # "searchTermImpressionShare",  # V2

        "targetingExpression",
        "targetingText",
        "targetingType",
        # "matchType",
        "impressions",
        "clicks",
        "cost",
        "attributedDetailPageViewsClicks14d",
        "attributedSales14d",
        "attributedSales14dSameSKU",
        "attributedConversions14d",
        "attributedConversions14dSameSKU",
        "attributedOrdersNewToBrand14d",
        "attributedOrdersNewToBrandPercentage14d",
        "attributedOrderRateNewToBrand14d",
        "attributedSalesNewToBrand14d",
        "attributedSalesNewToBrandPercentage14d",
        "attributedUnitsOrderedNewToBrand14d",
        "attributedUnitsOrderedNewToBrandPercentage14d",
        "unitsSold14d",
        "dpv14d",

        # "query",  # V2
        # "viewableImpressions",  # V2
        # "videoFirstQuartileViews",  # V2
        # "videoMidpointViews",  # V2
        # "videoThirdQuartileViews",  # V2
        # "videoCompleteViews",  # V2
        # "video5SecondViews",  # V2
        # "video5SecondViewRate",  # V2
        # "videoUnmutes",  # V2
        # "vtr",  # V2
        # "vctr",  # V2
    ],
    "keywords": [
        "campaignName",
        "campaignId",
        "campaignStatus",
        "campaignBudget",
        "campaignBudgetType",

        # "campaignRuleBasedBudget",  # V2
        # "applicableBudgetRuleId",  # V2
        # "applicableBudgetRuleName",  # V2

        "adGroupName",
        "adGroupId",
        "keywordText",
        "keywordBid",
        "keywordStatus",
        "targetId",

        # "searchTermImpressionRank",
        # "searchTermImpressionShare"

        "targetingExpression",
        "targetingText",
        "targetingType",
        "matchType",
        "impressions",
        "clicks",
        "cost",
        "attributedDetailPageViewsClicks14d",
        "attributedSales14d",
        "attributedSales14dSameSKU",
        "attributedConversions14d",
        "attributedConversions14dSameSKU",
        "attributedOrdersNewToBrand14d",
        "attributedOrdersNewToBrandPercentage14d",
        "attributedOrderRateNewToBrand14d",
        "attributedSalesNewToBrand14d",
        "attributedSalesNewToBrandPercentage14d",
        "attributedUnitsOrderedNewToBrand14d",
        "attributedUnitsOrderedNewToBrandPercentage14d",
        "unitsSold14d",
        "dpv14d",

        # "query",
        # "viewableImpressions",
        # "videoFirstQuartileViews",
        # "videoMidpointViews",
        # "videoThirdQuartileViews",
        # "videoCompleteViews",
        # "video5SecondViews",
        # "video5SecondViewRate",
        # "videoUnmutes",
        # "vtr",
        # "vctr",
    ],
    # 貌似所有sb报表均可以导出这些字段（有的为空值），建议使用快照了导出全字段
    "all": [
        "campaignName",
        "campaignId",
        "campaignStatus",
        "campaignBudget",
        "campaignBudgetType",

        "campaignRuleBasedBudget",  # V2
        "applicableBudgetRuleId",  # V2
        "applicableBudgetRuleName",  # V2

        "adGroupName",
        "adGroupId",
        "keywordText",
        "keywordBid",
        "keywordStatus",
        "targetId",

        "searchTermImpressionRank",
        "searchTermImpressionShare"

        "targetingExpression",
        "targetingText",
        "targetingType",
        "matchType",
        "impressions",
        "clicks",
        "cost",
        "attributedDetailPageViewsClicks14d",
        "attributedSales14d",
        "attributedSales14dSameSKU",
        "attributedConversions14d",
        "attributedConversions14dSameSKU",
        "attributedOrdersNewToBrand14d",
        "attributedOrdersNewToBrandPercentage14d",
        "attributedOrderRateNewToBrand14d",
        "attributedSalesNewToBrand14d",
        "attributedSalesNewToBrandPercentage14d",
        "attributedUnitsOrderedNewToBrand14d",
        "attributedUnitsOrderedNewToBrandPercentage14d",
        "unitsSold14d",
        "dpv14d",

        "query",
        "viewableImpressions",
        "videoFirstQuartileViews",
        "videoMidpointViews",
        "videoThirdQuartileViews",
        "videoCompleteViews",
        "video5SecondViews",
        "video5SecondViewRate",
        "videoUnmutes",
        "vtr",
        "vctr",
    ],

}

# 这些字段存在于 赞助品牌视频报告，即 creativeType=video
AVAILABLE_VIDEO_REPORT_METRICS = [
    "campaignName",
    "campaignId",
    "campaignStatus",
    "campaignBudget",
    "campaignBudgetType",
    "adGroupName",
    "adGroupId",
    "keywordText",
    "keywordBid",
    "keywordStatus",
    "targetId",
    "targetingExpression",
    "targetingText",
    "targetingType",
    "matchType",
    "impressions",
    "clicks",
    "cost",
    "attributedSales14d",
    "attributedSales14dSameSKU",
    "attributedConversions14d",
    "attributedConversions14dSameSKU",

    "query",  # V2
    "viewableImpressions",  # V2
    "videoFirstQuartileViews",  # V2
    "videoMidpointViews",  # V2
    "videoThirdQuartileViews",  # V2
    "videoCompleteViews",  # V2
    "video5SecondViews",  # V2
    "video5SecondViewRate",  # V2
    "videoUnmutes",  # V2
    "vtr",  # V2
    "vctr",  # V2
]


# 这些字段仅在video报表中存在
VIDEO_METRICS = [
    # "query",  # V2
    "viewableImpressions",  # V2
    "videoFirstQuartileViews",  # V2
    "videoMidpointViews",  # V2
    "videoThirdQuartileViews",  # V2
    "videoCompleteViews",  # V2
    "video5SecondViews",  # V2
    "video5SecondViewRate",  # V2
    "videoUnmutes",  # V2
    "vtr",  # V2
    "vctr",  # V2
]


# 这些类型的报表可以按相应的维度来细分出的报表
DEFAULT_REPORT_DIMENSIONAL = {
    "keywords": "query",  # search terms 搜索词
    "campaigns": "placement",  # placement location 展示位置
}

DEFAULT_CREATIVE_TYPE = [
    "video"
]


class SbReport(ZADOpenAPI):
    def request(self, record_type, report_date, metrics, segment=None, creative_type=None):
        """
        POST    /v2/hsa/{recordType}/report

        Request the creation of a performance report for all entities of a single type which have performance data to
        report. Record types can be: campaigns, adGroups, and keywords

        :param record_type: 枚举 ['campaigns', 'adGroups', 'keywords']
        :param report_date: 报表日期, 格式为: YYYYMMDD
        :param metrics: 列表对象，成员为报表指标，即导出字段；若 metrics=None, 则使用默认指标
        :param segment: [可选]
        :param creative_type: [可选]; 枚举 ['video']
        """

        path = '/v2/hsa/{record_type}/report'.format(record_type=record_type)

        if isinstance(metrics, (list, tuple)):
            metrics = ','.join(metrics)

        data = {
           'reportDate': report_date,
           'metrics': metrics
        }

        if segment:
            data['segment'] = segment

        if creative_type:
            data['creativeType'] = creative_type

        return self.post(path, data)

    def campaigns(self, report_date, metrics=None):
        """
        campaigns = set(json.loads(client.sb_report.campaigns(report_date=report_date)['kwargs']['data'].decode('utf-8'))['metrics'].split(','))

        In [19]: len(campaigns)
        Out[19]: 25
        """
        creative_type = None
        if not metrics:
            metrics = [
                'campaignName',
                'campaignId',
                'campaignStatus',
                'campaignBudget',
                'campaignBudgetType',
                'impressions',
                'clicks',
                'cost',
                'attributedDetailPageViewsClicks14d',
                'attributedSales14d',
                'attributedSales14dSameSKU',
                'attributedConversions14d',
                'attributedConversions14dSameSKU',
                'attributedOrdersNewToBrand14d',
                'attributedOrdersNewToBrandPercentage14d',
                'attributedOrderRateNewToBrand14d',
                'attributedSalesNewToBrand14d',
                'attributedSalesNewToBrandPercentage14d',
                'attributedUnitsOrderedNewToBrand14d',
                'attributedUnitsOrderedNewToBrandPercentage14d',
                'unitsSold14d',
                'dpv14d',
                'applicableBudgetRuleId',
                'applicableBudgetRuleName',
                'campaignRuleBasedBudget',
            ]
        return self.request('campaigns', report_date, metrics, creative_type=creative_type)

    def campaigns_video(self, report_date, metrics=None):
        """
        campaigns_video = set(json.loads(client.sb_report.campaigns_video(report_date=report_date)['kwargs']['data'].decode('utf-8'))['metrics'].split(','))

        In [21]: len(campaigns_video)
        Out[21]: 30

        In [43]: campaigns_video - campaigns
        Out[43]:
        {'vctr',
         'video5SecondViewRate',
         'video5SecondViews',
         'videoCompleteViews',
         'videoFirstQuartileViews',
         'videoMidpointViews',
         'videoThirdQuartileViews',
         'videoUnmutes',
         'viewableImpressions',
         'vtr'}

        In [44]: campaigns - campaigns_video
        Out[44]:
        {'applicableBudgetRuleId',
         'applicableBudgetRuleName',
         'campaignRuleBasedBudget',
         'dpv14d',
         'unitsSold14d'}
        """
        creative_type = 'video'
        if not metrics:
            metrics = [
                'attributedSales14d',
                'campaignStatus',
                'campaignBudget',
                'video5SecondViewRate',
                'cost',
                'videoUnmutes',
                'clicks',
                'attributedSales14dSameSKU',
                'campaignName',
                'attributedConversions14d',
                'videoThirdQuartileViews',
                'videoFirstQuartileViews',
                'videoCompleteViews',
                'vctr',
                'campaignId',
                'impressions',
                'viewableImpressions',
                'attributedConversions14dSameSKU',
                'videoMidpointViews',
                'video5SecondViews',
                'vtr',
                'campaignBudgetType',
                'attributedDetailPageViewsClicks14d',
                'attributedOrderRateNewToBrand14d',
                'attributedOrdersNewToBrand14d',
                'attributedOrdersNewToBrandPercentage14d',
                'attributedSalesNewToBrand14d',
                'attributedSalesNewToBrandPercentage14d',
                'attributedUnitsOrderedNewToBrand14d',
                'attributedUnitsOrderedNewToBrandPercentage14d',
            ]
        return self.request('campaigns', report_date, metrics, creative_type=creative_type)

    def campaigns_all(self, report_date, metrics=None):
        """
        campaigns_all = campaigns | campaigns_video

        In [26]: len(campaigns_all)
        Out[26]: 35

        In [28]: campaigns_all - campaigns
        Out[28]:
        {'vctr',
         'video5SecondViewRate',
         'video5SecondViews',
         'videoCompleteViews',
         'videoFirstQuartileViews',
         'videoMidpointViews',
         'videoThirdQuartileViews',
         'videoUnmutes',
         'viewableImpressions',
         'vtr'}

        In [29]: campaigns_all - campaigns_video
        Out[29]:
        {'applicableBudgetRuleId',
         'applicableBudgetRuleName',
         'campaignRuleBasedBudget',
         'dpv14d',
         'unitsSold14d'}
        """
        creative_type = 'all'
        if not metrics:
            metrics = [
                'applicableBudgetRuleId',
                'applicableBudgetRuleName',
                'attributedConversions14d',
                'attributedConversions14dSameSKU',
                'attributedDetailPageViewsClicks14d',
                'attributedOrderRateNewToBrand14d',
                'attributedOrdersNewToBrand14d',
                'attributedOrdersNewToBrandPercentage14d',
                'attributedSales14d',
                'attributedSales14dSameSKU',
                'attributedSalesNewToBrand14d',
                'attributedSalesNewToBrandPercentage14d',
                'attributedUnitsOrderedNewToBrand14d',
                'attributedUnitsOrderedNewToBrandPercentage14d',
                'campaignBudget',
                'campaignBudgetType',
                'campaignId',
                'campaignName',
                'campaignRuleBasedBudget',
                'campaignStatus',
                'clicks',
                'cost',
                'dpv14d',
                'impressions',
                'unitsSold14d',
                'vctr',
                'video5SecondViewRate',
                'video5SecondViews',
                'videoCompleteViews',
                'videoFirstQuartileViews',
                'videoMidpointViews',
                'videoThirdQuartileViews',
                'videoUnmutes',
                'viewableImpressions',
                'vtr',

                'attributedBrandedSearches14d',
                'currency',
                'topOfSearchImpressionShare',
            ]

        return self.request('campaigns', report_date, metrics, creative_type=creative_type)

    def placements(self, report_date, metrics=None):
        """
        placements = set(json.loads(client.sb_report.placements(report_date=report_date)['kwargs']['data'].decode('utf-8'))['metrics'].split(','))

        In [33]: placements - campaigns
        Out[33]: set()

        In [34]: campaigns - placements
        Out[34]:
        {'applicableBudgetRuleId',
         'applicableBudgetRuleName',
         'campaignRuleBasedBudget'}
        """
        segment = 'placement'
        creative_type = None
        if not metrics:
            metrics = [
                'campaignName',
                'campaignId',
                'campaignStatus',
                'campaignBudget',
                'campaignBudgetType',
                'impressions',
                'clicks',
                'cost',
                'attributedDetailPageViewsClicks14d',
                'attributedSales14d',
                'attributedSales14dSameSKU',
                'attributedConversions14d',
                'attributedConversions14dSameSKU',
                'attributedOrdersNewToBrand14d',
                'attributedOrdersNewToBrandPercentage14d',
                'attributedOrderRateNewToBrand14d',
                'attributedSalesNewToBrand14d',
                'attributedSalesNewToBrandPercentage14d',
                'attributedUnitsOrderedNewToBrand14d',
                'attributedUnitsOrderedNewToBrandPercentage14d',
                'unitsSold14d',
                'dpv14d',
            ]

        return self.request('campaigns', report_date, metrics, segment=segment, creative_type=creative_type)

    def placements_video(self, report_date, metrics=None):
        """
        placements_video = set(json.loads(client.sb_report.placements_video(report_date=report_date)['kwargs']['data'].decode('utf-8'))['metrics'].split(','))

        In [36]: len(placements_video)
        Out[36]: 30

        In [37]: placements_video - placements
        Out[37]:
        {'vctr',
         'video5SecondViewRate',
         'video5SecondViews',
         'videoCompleteViews',
         'videoFirstQuartileViews',
         'videoMidpointViews',
         'videoThirdQuartileViews',
         'videoUnmutes',
         'viewableImpressions',
         'vtr'}

        In [38]: placements - placements_video
        Out[38]: {'dpv14d', 'unitsSold14d'}

        """
        segment = 'placement'
        creative_type = 'video'
        if not metrics:
            metrics = [
                'attributedSales14d',
                'campaignStatus',
                'campaignBudget',
                'video5SecondViewRate',
                'cost',
                'videoUnmutes',
                'clicks',
                'attributedSales14dSameSKU',
                'campaignName',
                'attributedConversions14d',
                'videoThirdQuartileViews',
                'videoFirstQuartileViews',
                'videoCompleteViews',
                'vctr',
                'campaignId',
                'impressions',
                'viewableImpressions',
                'attributedConversions14dSameSKU',
                'videoMidpointViews',
                'video5SecondViews',
                'vtr',
                'campaignBudgetType',
                'attributedDetailPageViewsClicks14d',
                'attributedOrderRateNewToBrand14d',
                'attributedOrdersNewToBrand14d',
                'attributedOrdersNewToBrandPercentage14d',
                'attributedSalesNewToBrand14d',
                'attributedSalesNewToBrandPercentage14d',
                'attributedUnitsOrderedNewToBrand14d',
                'attributedUnitsOrderedNewToBrandPercentage14d',
            ]
        return self.request('campaigns', report_date, metrics, segment=segment, creative_type=creative_type)

    def placements_all(self, report_date, metrics=None):
        """
        placements_all = placements | placements_video

        In [47]: len(placements_all)
        Out[47]: 32

        In [48]: placements_all - placements
        Out[48]:
        {'vctr',
         'video5SecondViewRate',
         'video5SecondViews',
         'videoCompleteViews',
         'videoFirstQuartileViews',
         'videoMidpointViews',
         'videoThirdQuartileViews',
         'videoUnmutes',
         'viewableImpressions',
         'vtr'}

        In [49]: placements_all - placements_video
        Out[49]: {'dpv14d', 'unitsSold14d'}
        """

        segment = 'placement'
        creative_type = 'all'
        if not metrics:
            metrics = [
                'attributedConversions14d',
                'attributedConversions14dSameSKU',
                'attributedDetailPageViewsClicks14d',
                'attributedOrderRateNewToBrand14d',
                'attributedOrdersNewToBrand14d',
                'attributedOrdersNewToBrandPercentage14d',
                'attributedSales14d',
                'attributedSales14dSameSKU',
                'attributedSalesNewToBrand14d',
                'attributedSalesNewToBrandPercentage14d',
                'attributedUnitsOrderedNewToBrand14d',
                'attributedUnitsOrderedNewToBrandPercentage14d',
                'campaignBudget',
                'campaignBudgetType',
                'campaignId',
                'campaignName',
                'campaignStatus',
                'clicks',
                'cost',
                'dpv14d',
                'impressions',
                'unitsSold14d',
                'vctr',
                'video5SecondViewRate',
                'video5SecondViews',
                'videoCompleteViews',
                'videoFirstQuartileViews',
                'videoMidpointViews',
                'videoThirdQuartileViews',
                'videoUnmutes',
                'viewableImpressions',
                'vtr',

                'applicableBudgetRuleId',
                'applicableBudgetRuleName',
                'attributedBrandedSearches14d',
                'campaignRuleBasedBudget',
                'currency',
                'topOfSearchImpressionShare',
            ]
        return self.request('campaigns', report_date, metrics, segment=segment, creative_type=creative_type)

    def ad_groups(self, report_date, metrics=None):
        """
        ad_groups = set(json.loads(client.sb_report.ad_groups(report_date=report_date)['kwargs']['data'].decode('utf-8'))['metrics'].split(','))

        In [54]: len(ad_groups)
        Out[54]: 24
        """
        creative_type = None
        if not metrics:
            metrics = [
                'adGroupId',
                'adGroupName',
                'attributedConversions14d',
                'attributedConversions14dSameSKU',
                'attributedDetailPageViewsClicks14d',
                'attributedOrderRateNewToBrand14d',
                'attributedOrdersNewToBrand14d',
                'attributedOrdersNewToBrandPercentage14d',
                'attributedSales14d',
                'attributedSales14dSameSKU',
                'attributedSalesNewToBrand14d',
                'attributedSalesNewToBrandPercentage14d',
                'attributedUnitsOrderedNewToBrand14d',
                'attributedUnitsOrderedNewToBrandPercentage14d',
                'campaignBudget',
                'campaignBudgetType',
                'campaignId',
                'campaignName',
                'campaignStatus',
                'clicks',
                'cost',
                'dpv14d',
                'impressions',
                'unitsSold14d'
            ]
        return self.request('adGroups', report_date, metrics, creative_type=creative_type)

    def ad_groups_video(self, report_date, metrics=None):
        """
        ad_groups_video = set(json.loads(client.sb_report.ad_groups_video(report_date=report_date)['kwargs']['data'].decode('utf-8'))['metrics'].split(','))

        In [59]: len(ad_groups_video)
        Out[59]: 24

        In [60]: ad_groups_video - ad_groups
        Out[60]:
        {'vctr',
         'video5SecondViewRate',
         'video5SecondViews',
         'videoCompleteViews',
         'videoFirstQuartileViews',
         'videoMidpointViews',
         'videoThirdQuartileViews',
         'videoUnmutes',
         'viewableImpressions',
         'vtr'}

        In [61]: ad_groups - ad_groups_video
        Out[61]:
        {'attributedDetailPageViewsClicks14d',
         'attributedOrderRateNewToBrand14d',
         'attributedOrdersNewToBrand14d',
         'attributedOrdersNewToBrandPercentage14d',
         'attributedSalesNewToBrand14d',
         'attributedSalesNewToBrandPercentage14d',
         'attributedUnitsOrderedNewToBrand14d',
         'attributedUnitsOrderedNewToBrandPercentage14d',
         'dpv14d',
         'unitsSold14d'}
        """
        if not metrics:
            metrics = [
                'adGroupId',
                'adGroupName',
                'attributedConversions14d',
                'attributedConversions14dSameSKU',
                'attributedSales14d',
                'attributedSales14dSameSKU',
                'campaignBudget',
                'campaignBudgetType',
                'campaignId',
                'campaignName',
                'campaignStatus',
                'clicks',
                'cost',
                'impressions',
                'vctr',
                'video5SecondViewRate',
                'video5SecondViews',
                'videoCompleteViews',
                'videoFirstQuartileViews',
                'videoMidpointViews',
                'videoThirdQuartileViews',
                'videoUnmutes',
                'viewableImpressions',
                'vtr']

        creative_type = 'video'
        return self.request('adGroups', report_date, metrics, creative_type=creative_type)

    def ad_groups_all(self, report_date, metrics=None):
        """
        ad_groups_all = ad_groups | ad_groups_video

        In [64]: len(ad_groups_all)
        Out[64]: 34

        In [65]: ad_groups_all - ad_groups
        Out[65]:
        {'vctr',
         'video5SecondViewRate',
         'video5SecondViews',
         'videoCompleteViews',
         'videoFirstQuartileViews',
         'videoMidpointViews',
         'videoThirdQuartileViews',
         'videoUnmutes',
         'viewableImpressions',
         'vtr'}

        In [66]: ad_groups_all - ad_groups_video
        Out[66]:
        {'attributedDetailPageViewsClicks14d',
         'attributedOrderRateNewToBrand14d',
         'attributedOrdersNewToBrand14d',
         'attributedOrdersNewToBrandPercentage14d',
         'attributedSalesNewToBrand14d',
         'attributedSalesNewToBrandPercentage14d',
         'attributedUnitsOrderedNewToBrand14d',
         'attributedUnitsOrderedNewToBrandPercentage14d',
         'dpv14d',
         'unitsSold14d'}
        """
        creative_type = 'all'
        if not metrics:
            metrics = [
                'adGroupId',
                'adGroupName',
                'attributedConversions14d',
                'attributedConversions14dSameSKU',
                'attributedDetailPageViewsClicks14d',
                'attributedOrderRateNewToBrand14d',
                'attributedOrdersNewToBrand14d',
                'attributedOrdersNewToBrandPercentage14d',
                'attributedSales14d',
                'attributedSales14dSameSKU',
                'attributedSalesNewToBrand14d',
                'attributedSalesNewToBrandPercentage14d',
                'attributedUnitsOrderedNewToBrand14d',
                'attributedUnitsOrderedNewToBrandPercentage14d',
                'campaignBudget',
                'campaignBudgetType',
                'campaignId',
                'campaignName',
                'campaignStatus',
                'clicks',
                'cost',
                'dpv14d',
                'impressions',
                'unitsSold14d',
                'vctr',
                'video5SecondViewRate',
                'video5SecondViews',
                'videoCompleteViews',
                'videoFirstQuartileViews',
                'videoMidpointViews',
                'videoThirdQuartileViews',
                'videoUnmutes',
                'viewableImpressions',
                'vtr',

                'attributedBrandedSearches14d',
                'currency',
            ]
        return self.request('adGroups', report_date, metrics, creative_type=creative_type)

    def keywords(self, report_date, metrics=None):
        """
        keywords = set(json.loads(client.sb_report.keywords(report_date=report_date)['kwargs']['data'].decode('utf-8'))['metrics'].split(','))

        In [72]: len(keywords)
        Out[72]: 34
        """
        creative_type = None
        if not metrics:
            metrics = [
                'campaignName',
                'campaignId',
                'campaignStatus',
                'campaignBudget',
                'campaignBudgetType',
                'adGroupName',
                'adGroupId',
                'keywordText',
                'keywordBid',
                'keywordStatus',
                'targetId',
                'targetingExpression',
                'targetingText',
                'targetingType',
                'matchType',
                'impressions',
                'clicks',
                'cost',
                'attributedDetailPageViewsClicks14d',
                'attributedSales14d',
                'attributedSales14dSameSKU',
                'attributedConversions14d',
                'attributedConversions14dSameSKU',
                'attributedOrdersNewToBrand14d',
                'attributedOrdersNewToBrandPercentage14d',
                'attributedOrderRateNewToBrand14d',
                'attributedSalesNewToBrand14d',
                'attributedSalesNewToBrandPercentage14d',
                'attributedUnitsOrderedNewToBrand14d',
                'attributedUnitsOrderedNewToBrandPercentage14d',
                'unitsSold14d',
                'dpv14d',
                'searchTermImpressionRank',
                'searchTermImpressionShare',
            ]
        return self.request('keywords', report_date, metrics, creative_type=creative_type)

    def keywords_video(self, report_date, metrics=None):
        """
        keywords_video = set(json.loads(client.sb_report.keywords_video(report_date=report_date)['kwargs']['data'].decode('utf-8'))['metrics'].split(','))

        In [77]: len(keywords_video)
        Out[77]: 40

        In [78]: keywords_video - keywords
        Out[78]:
        {'vctr',
         'video5SecondViewRate',
         'video5SecondViews',
         'videoCompleteViews',
         'videoFirstQuartileViews',
         'videoMidpointViews',
         'videoThirdQuartileViews',
         'videoUnmutes',
         'viewableImpressions',
         'vtr'}

        In [84]: keywords - keywords_video
        Out[84]:
        {'dpv14d',
         'searchTermImpressionRank',
         'searchTermImpressionShare',
         'unitsSold14d'}

        """
        creative_type = 'video'
        if not metrics:
            metrics = [
                'attributedSales14d',
                'campaignStatus',
                'campaignBudget',
                'video5SecondViewRate',
                'cost',
                'targetingText',
                'videoUnmutes',
                'clicks',
                'attributedSales14dSameSKU',
                'campaignName',
                'attributedConversions14d',
                'videoThirdQuartileViews',
                'videoFirstQuartileViews',
                'keywordBid',
                'matchType',
                'adGroupName',
                'keywordText',
                'videoCompleteViews',
                'vctr',
                'campaignId',
                'keywordStatus',
                'impressions',
                'targetId',
                'targetingType',
                'viewableImpressions',
                'adGroupId',
                'attributedConversions14dSameSKU',
                'targetingExpression',
                'videoMidpointViews',
                'video5SecondViews',
                'vtr',
                'campaignBudgetType',
                'attributedDetailPageViewsClicks14d',
                'attributedOrderRateNewToBrand14d',
                'attributedOrdersNewToBrand14d',
                'attributedOrdersNewToBrandPercentage14d',
                'attributedSalesNewToBrand14d',
                'attributedSalesNewToBrandPercentage14d',
                'attributedUnitsOrderedNewToBrand14d',
                'attributedUnitsOrderedNewToBrandPercentage14d',
            ]

        return self.request('keywords', report_date, metrics, creative_type=creative_type)

    def keywords_all(self, report_date, metrics=None):
        """
        keywords_all = keywords | keywords_video

        In [81]: len(keywords_all)
        Out[81]: 44

        In [82]: keywords_all - keywords
        Out[82]:
        {'vctr',
         'video5SecondViewRate',
         'video5SecondViews',
         'videoCompleteViews',
         'videoFirstQuartileViews',
         'videoMidpointViews',
         'videoThirdQuartileViews',
         'videoUnmutes',
         'viewableImpressions',
         'vtr'}

        In [83]: keywords_all - keywords_video
        Out[83]:
        {'dpv14d',
         'searchTermImpressionRank',
         'searchTermImpressionShare',
         'unitsSold14d'}
        """

        creative_type = 'all'
        if not metrics:
            metrics = [
                'adGroupId',
                'adGroupName',
                'attributedConversions14d',
                'attributedConversions14dSameSKU',
                'attributedDetailPageViewsClicks14d',
                'attributedOrderRateNewToBrand14d',
                'attributedOrdersNewToBrand14d',
                'attributedOrdersNewToBrandPercentage14d',
                'attributedSales14d',
                'attributedSales14dSameSKU',
                'attributedSalesNewToBrand14d',
                'attributedSalesNewToBrandPercentage14d',
                'attributedUnitsOrderedNewToBrand14d',
                'attributedUnitsOrderedNewToBrandPercentage14d',
                'campaignBudget',
                'campaignBudgetType',
                'campaignId',
                'campaignName',
                'campaignStatus',
                'clicks',
                'cost',
                'dpv14d',
                'impressions',
                'keywordBid',
                'keywordStatus',
                'keywordText',
                'matchType',
                'searchTermImpressionRank',
                'searchTermImpressionShare',
                'targetId',
                'targetingExpression',
                'targetingText',
                'targetingType',
                'unitsSold14d',
                'vctr',
                'video5SecondViewRate',
                'video5SecondViews',
                'videoCompleteViews',
                'videoFirstQuartileViews',
                'videoMidpointViews',
                'videoThirdQuartileViews',
                'videoUnmutes',
                'viewableImpressions',
                'vtr',

                'applicableBudgetRuleId',
                'applicableBudgetRuleName',
                'attributedBrandedSearches14d',
                'campaignRuleBasedBudget',
                'currency',
                'keywordId',
                'topOfSearchImpressionShare',
            ]
        return self.request('keywords', report_date, metrics, creative_type=creative_type)

    def keywords_query(self, report_date, metrics=None):
        """
        keywords_query = set(json.loads(client.sb_report.keywords_query(report_date=report_date)['kwargs']['data'].decode('utf-8'))['metrics'].split(','))

        In [87]: len(keywords_query)
        Out[87]: 16
        """

        segment = 'query'
        creative_type = None
        if not metrics:
            metrics = [
                'adGroupId',
                'adGroupName',
                'attributedConversions14d',
                'attributedSales14d',
                'campaignBudget',
                'campaignBudgetType',
                'campaignId',
                'campaignName',
                'campaignStatus',
                'clicks',
                'cost',
                'impressions',
                'keywordBid',
                'keywordStatus',
                'keywordText',
                'matchType',
            ]
        return self.request('keywords', report_date, metrics, segment=segment, creative_type=creative_type)

    def keywords_query_video(self, report_date, metrics=None):
        """
        keywords_query_video = set(json.loads(client.sb_report.keywords_query_video(report_date=report_date)['kwargs']['data'].decode('utf-8'))['metrics'].split(','))

        In [90]: len(keywords_query_video)
        Out[90]: 26

        In [91]: keywords_query_video - keywords_query
        Out[91]:
        {'vctr',
         'video5SecondViewRate',
         'video5SecondViews',
         'videoCompleteViews',
         'videoFirstQuartileViews',
         'videoMidpointViews',
         'videoThirdQuartileViews',
         'videoUnmutes',
         'viewableImpressions',
         'vtr'}

        In [92]: keywords_query - keywords_query_video
        Out[92]: set()

        """
        segment = 'query'
        creative_type = 'video'
        if not metrics:
            metrics = [
                'adGroupId',
                'adGroupName',
                'attributedConversions14d',
                'attributedSales14d',
                'campaignBudget',
                'campaignBudgetType',
                'campaignId',
                'campaignName',
                'campaignStatus',
                'clicks',
                'cost',
                'impressions',
                'keywordBid',
                'keywordStatus',
                'keywordText',
                'matchType',
                'vctr',
                'video5SecondViewRate',
                'video5SecondViews',
                'videoCompleteViews',
                'videoFirstQuartileViews',
                'videoMidpointViews',
                'videoThirdQuartileViews',
                'videoUnmutes',
                'viewableImpressions',
                'vtr',
            ]
        return self.request('keywords', report_date, metrics, segment=segment, creative_type=creative_type)

    def keywords_query_all(self, report_date, metrics=None):
        """
        keywords_query_all = keywords_query | keywords_query_video

        In [95]: len(keywords_query_all)
        Out[95]: 26

        In [96]: keywords_query_all - keywords_query_video
        Out[96]: set()

        In [97]: keywords_query_all - keywords_query
        Out[97]:
        {'vctr',
         'video5SecondViewRate',
         'video5SecondViews',
         'videoCompleteViews',
         'videoFirstQuartileViews',
         'videoMidpointViews',
         'videoThirdQuartileViews',
         'videoUnmutes',
         'viewableImpressions',
         'vtr'}
        """
        segment = 'query'
        creative_type = 'all'
        if not metrics:
            metrics = [
                'adGroupId',
                'adGroupName',
                'attributedConversions14d',
                'attributedSales14d',
                'campaignBudget',
                'campaignBudgetType',
                'campaignId',
                'campaignName',
                'campaignStatus',
                'clicks',
                'cost',
                'impressions',
                'keywordBid',
                'keywordStatus',
                'keywordText',
                'matchType',
                'vctr',
                'video5SecondViewRate',
                'video5SecondViews',
                'videoCompleteViews',
                'videoFirstQuartileViews',
                'videoMidpointViews',
                'videoThirdQuartileViews',
                'videoUnmutes',
                'viewableImpressions',
                'vtr',

                'keywordId',
                # 'query',
                'searchTermImpressionRank',
                'searchTermImpressionShare',
            ]
        return self.request('keywords', report_date, metrics, segment=segment, creative_type=creative_type)

    def keywords_placement(self, report_date, metrics=None):
        """
        keywords_placement = set(json.loads(client.sb_report.keywords_placement(report_date=report_date)['kwargs']['data'].decode('utf-8'))['metrics'].split(','))

        In [100]: len(keywords_placement)
        Out[100]: 32

        In [102]: keywords_placement - keywords
        Out[102]: set()

        In [103]: keywords - keywords_placement
        Out[103]: {'searchTermImpressionRank', 'searchTermImpressionShare'}
        """

        segment = 'placement'
        creative_type = None
        if not metrics:
            metrics = [
                'adGroupId',
                'adGroupName',
                'attributedConversions14d',
                'attributedConversions14dSameSKU',
                'attributedDetailPageViewsClicks14d',
                'attributedOrderRateNewToBrand14d',
                'attributedOrdersNewToBrand14d',
                'attributedOrdersNewToBrandPercentage14d',
                'attributedSales14d',
                'attributedSales14dSameSKU',
                'attributedSalesNewToBrand14d',
                'attributedSalesNewToBrandPercentage14d',
                'attributedUnitsOrderedNewToBrand14d',
                'attributedUnitsOrderedNewToBrandPercentage14d',
                'campaignBudget',
                'campaignBudgetType',
                'campaignId',
                'campaignName',
                'campaignStatus',
                'clicks',
                'cost',
                'dpv14d',
                'impressions',
                'keywordBid',
                'keywordStatus',
                'keywordText',
                'matchType',
                'targetId',  # 实际上拿不到
                'targetingExpression',  # 实际上拿不到
                'targetingText',  # 实际上拿不到
                'targetingType',  # 实际上拿不到
                'unitsSold14d',
                # 'keywordId',  # 不加，默认也能得到
                # 'placement',  # 不能加，实际上就能拿到，但存在为NULL的情况
            ]
        return self.request('keywords', report_date, metrics, segment=segment, creative_type=creative_type)

    def keywords_placement_video(self, report_date, metrics=None):
        """
        keywords_placement_video = set(json.loads(client.sb_report.keywords_placement_video(report_date=report_date)['kwargs']['data'].decode('utf-8'))['metrics'].split(','))

        In [105]: len(keywords_placement_video)
        Out[105]: 32

        In [106]: keywords_placement_video - keywords_placement
        Out[106]:
        {'vctr',
         'video5SecondViewRate',
         'video5SecondViews',
         'videoCompleteViews',
         'videoFirstQuartileViews',
         'videoMidpointViews',
         'videoThirdQuartileViews',
         'videoUnmutes',
         'viewableImpressions',
         'vtr'}

        In [107]: keywords_placement - keywords_placement_video
        Out[107]:
        {'attributedDetailPageViewsClicks14d',
         'attributedOrderRateNewToBrand14d',
         'attributedOrdersNewToBrand14d',
         'attributedOrdersNewToBrandPercentage14d',
         'attributedSalesNewToBrand14d',
         'attributedSalesNewToBrandPercentage14d',
         'attributedUnitsOrderedNewToBrand14d',
         'attributedUnitsOrderedNewToBrandPercentage14d',
         'dpv14d',
         'unitsSold14d'}
        """

        segment = 'placement'
        creative_type = 'video'
        if not metrics:
            metrics = [
                'adGroupId',
                'adGroupName',
                'attributedConversions14d',
                'attributedConversions14dSameSKU',
                'attributedSales14d',
                'attributedSales14dSameSKU',
                'campaignBudget',
                'campaignBudgetType',
                'campaignId',
                'campaignName',
                'campaignStatus',
                'clicks',
                'cost',
                'impressions',
                'keywordBid',
                'keywordStatus',
                'keywordText',
                'matchType',
                'targetId',
                'targetingExpression',
                'targetingText',
                'targetingType',
                'vctr',
                'video5SecondViewRate',
                'video5SecondViews',
                'videoCompleteViews',
                'videoFirstQuartileViews',
                'videoMidpointViews',
                'videoThirdQuartileViews',
                'videoUnmutes',
                'viewableImpressions',
                'vtr',
            ]
        return self.request('keywords', report_date, metrics, segment=segment, creative_type=creative_type)

    def keywords_placement_all(self, report_date, metrics=None):
        """
        keywords_placement_all = keywords_placement_video | keywords_placement

        In [111]: len(keywords_placement_all)
        Out[111]: 42

        In [112]: keywords_placement_all - keywords_placement
        Out[112]:
        {'vctr',
         'video5SecondViewRate',
         'video5SecondViews',
         'videoCompleteViews',
         'videoFirstQuartileViews',
         'videoMidpointViews',
         'videoThirdQuartileViews',
         'videoUnmutes',
         'viewableImpressions',
         'vtr'}

        In [113]: keywords_placement_all - keywords_placement_video
        Out[113]:
        {'attributedDetailPageViewsClicks14d',
         'attributedOrderRateNewToBrand14d',
         'attributedOrdersNewToBrand14d',
         'attributedOrdersNewToBrandPercentage14d',
         'attributedSalesNewToBrand14d',
         'attributedSalesNewToBrandPercentage14d',
         'attributedUnitsOrderedNewToBrand14d',
         'attributedUnitsOrderedNewToBrandPercentage14d',
         'dpv14d',
         'unitsSold14d'}
        """
        segment = 'placement'
        creative_type = 'all'
        if not metrics:
            metrics = [
                'adGroupId',
                'adGroupName',
                'attributedConversions14d',
                'attributedConversions14dSameSKU',
                'attributedDetailPageViewsClicks14d',
                'attributedOrderRateNewToBrand14d',
                'attributedOrdersNewToBrand14d',
                'attributedOrdersNewToBrandPercentage14d',
                'attributedSales14d',
                'attributedSales14dSameSKU',
                'attributedSalesNewToBrand14d',
                'attributedSalesNewToBrandPercentage14d',
                'attributedUnitsOrderedNewToBrand14d',
                'attributedUnitsOrderedNewToBrandPercentage14d',
                'campaignBudget',
                'campaignBudgetType',
                'campaignId',
                'campaignName',
                'campaignStatus',
                'clicks',
                'cost',
                'dpv14d',
                'impressions',
                'keywordBid',
                'keywordStatus',
                'keywordText',
                'matchType',
                'targetId',
                'targetingExpression',
                'targetingText',
                'targetingType',
                'unitsSold14d',
                'vctr',
                'video5SecondViewRate',
                'video5SecondViews',
                'videoCompleteViews',
                'videoFirstQuartileViews',
                'videoMidpointViews',
                'videoThirdQuartileViews',
                'videoUnmutes',
                'viewableImpressions',
                'vtr',
            ]
        return self.request('keywords', report_date, metrics, segment=segment, creative_type=creative_type)

    def targets(self, report_date, metrics=None):
        """
        targets = set(json.loads(client.sb_report.targets(report_date=report_date)['kwargs']['data'].decode('utf-8'))['metrics'].split(','))

        In [116]: len(targets)
        Out[116]: 28
        """
        creative_type = None
        if not metrics:
            metrics = [
                'adGroupId',
                'adGroupName',
                'attributedConversions14d',
                'attributedConversions14dSameSKU',
                'attributedDetailPageViewsClicks14d',
                'attributedOrderRateNewToBrand14d',
                'attributedOrdersNewToBrand14d',
                'attributedOrdersNewToBrandPercentage14d',
                'attributedSales14d',
                'attributedSales14dSameSKU',
                'attributedSalesNewToBrand14d',
                'attributedSalesNewToBrandPercentage14d',
                'attributedUnitsOrderedNewToBrand14d',
                'attributedUnitsOrderedNewToBrandPercentage14d',
                'campaignBudget',
                'campaignBudgetType',
                'campaignId',
                'campaignName',
                'campaignStatus',
                'clicks',
                'cost',
                'dpv14d',
                'impressions',
                'targetId',
                'targetingExpression',
                'targetingText',
                'targetingType',
                'unitsSold14d',
            ]
        return self.request('targets', report_date, metrics, creative_type=creative_type)

    def targets_video(self, report_date, metrics=None):
        """
        targets_video = set(json.loads(client.sb_report.targets_video(report_date=report_date)['kwargs']['data'].decode('utf-8'))['metrics'].split(','))

        In [120]: len(targets_video)
        Out[120]: 36

        In [121]: targets_video - targets
        Out[121]:
        {'vctr',
         'video5SecondViewRate',
         'video5SecondViews',
         'videoCompleteViews',
         'videoFirstQuartileViews',
         'videoMidpointViews',
         'videoThirdQuartileViews',
         'videoUnmutes',
         'viewableImpressions',
         'vtr'}

        In [122]: targets - targets_video
        Out[122]: {'dpv14d', 'unitsSold14d'}
        """

        creative_type = 'video'
        if not metrics:
            metrics = [
                'adGroupId',
                'adGroupName',
                'attributedConversions14d',
                'attributedConversions14dSameSKU',
                'attributedDetailPageViewsClicks14d',
                'attributedOrderRateNewToBrand14d',
                'attributedOrdersNewToBrand14d',
                'attributedOrdersNewToBrandPercentage14d',
                'attributedSales14d',
                'attributedSales14dSameSKU',
                'attributedSalesNewToBrand14d',
                'attributedSalesNewToBrandPercentage14d',
                'attributedUnitsOrderedNewToBrand14d',
                'attributedUnitsOrderedNewToBrandPercentage14d',
                'campaignBudget',
                'campaignBudgetType',
                'campaignId',
                'campaignName',
                'campaignStatus',
                'clicks',
                'cost',
                'impressions',
                'targetId',
                'targetingExpression',
                'targetingText',
                'targetingType',
                'vctr',
                'video5SecondViewRate',
                'video5SecondViews',
                'videoCompleteViews',
                'videoFirstQuartileViews',
                'videoMidpointViews',
                'videoThirdQuartileViews',
                'videoUnmutes',
                'viewableImpressions',
                'vtr',
            ]

        return self.request('targets', report_date, metrics, creative_type=creative_type)

    def targets_all(self, report_date, metrics=None):
        """
        targets_all = targets | targets_video

        In [127]: len(targets_all)
        Out[127]: 38

        In [128]: targets_all - targets
        Out[128]:
        {'vctr',
         'video5SecondViewRate',
         'video5SecondViews',
         'videoCompleteViews',
         'videoFirstQuartileViews',
         'videoMidpointViews',
         'videoThirdQuartileViews',
         'videoUnmutes',
         'viewableImpressions',
         'vtr'}

        In [129]: targets_all - targets_video
        Out[129]: {'dpv14d', 'unitsSold14d'}
        """
        creative_type = 'all'
        if not metrics:
            metrics = [
                'adGroupId',
                'adGroupName',
                'attributedConversions14d',
                'attributedConversions14dSameSKU',
                'attributedDetailPageViewsClicks14d',
                'attributedOrderRateNewToBrand14d',
                'attributedOrdersNewToBrand14d',
                'attributedOrdersNewToBrandPercentage14d',
                'attributedSales14d',
                'attributedSales14dSameSKU',
                'attributedSalesNewToBrand14d',
                'attributedSalesNewToBrandPercentage14d',
                'attributedUnitsOrderedNewToBrand14d',
                'attributedUnitsOrderedNewToBrandPercentage14d',
                'campaignBudget',
                'campaignBudgetType',
                'campaignId',
                'campaignName',
                'campaignStatus',
                'clicks',
                'cost',
                'dpv14d',
                'impressions',
                'targetId',
                'targetingExpression',
                'targetingText',
                'targetingType',
                'unitsSold14d',
                'vctr',
                'video5SecondViewRate',
                'video5SecondViews',
                'videoCompleteViews',
                'videoFirstQuartileViews',
                'videoMidpointViews',
                'videoThirdQuartileViews',
                'videoUnmutes',
                'viewableImpressions',
                'vtr',

                'attributedBrandedSearches14d',
                'currency',
                'topOfSearchImpressionShare',
            ]
        return self.request('targets', report_date, metrics, creative_type=creative_type)

    def ads_all(self, report_date, metrics=None):
        """
        ads_all = set(json.loads(client.sb_report.ads_all(report_date=report_date)['kwargs']['data'].decode('utf-8'))['metrics'].split(','))

        In [140]: len(ads_all)
        Out[140]: 39
        """
        creative_type = 'all'
        if not metrics:
            metrics = [
                'adGroupId',
                'adGroupName',
                'adId',
                'applicableBudgetRuleId',
                'applicableBudgetRuleName',
                'attributedBrandedSearches14d',
                'attributedConversions14d',
                'attributedConversions14dSameSKU',
                'attributedDetailPageViewsClicks14d',
                'attributedOrderRateNewToBrand14d',
                'attributedOrdersNewToBrand14d',
                'attributedOrdersNewToBrandPercentage14d',
                'attributedSales14d',
                'attributedSales14dSameSKU',
                'attributedSalesNewToBrand14d',
                'attributedSalesNewToBrandPercentage14d',
                'attributedUnitsOrderedNewToBrand14d',
                'attributedUnitsOrderedNewToBrandPercentage14d',
                'campaignBudget',
                'campaignBudgetType',
                'campaignId',
                'campaignName',
                'campaignRuleBasedBudget',
                'campaignStatus',
                'clicks',
                'cost',
                'dpv14d',
                'impressions',
                'unitsSold14d',
                'vctr',
                'video5SecondViewRate',
                'video5SecondViews',
                'videoCompleteViews',
                'videoFirstQuartileViews',
                'videoMidpointViews',
                'videoThirdQuartileViews',
                'videoUnmutes',
                'viewableImpressions',
                'vtr',

                'currency',
            ]
        return self.request('ads', report_date, metrics, creative_type=creative_type)

    def local_test(self, **kwargs):
        """
        测试用的接口
        """
        path = kwargs.get('path')
        data = kwargs.get('data')
        return self.post(path, data)
