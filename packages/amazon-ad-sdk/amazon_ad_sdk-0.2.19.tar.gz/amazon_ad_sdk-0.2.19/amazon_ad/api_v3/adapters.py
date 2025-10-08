# -*- coding: utf-8 -*-

import copy
import arrow
from pprint import pprint
from enum import Enum


class TimeUnit(Enum):
    """
    请求报告参数、必填、"timeUnit"

    timeUnit can be set to "DAILY" or "SUMMARY".
    If you set timeUnit to "DAILY", you should include "date" in your column list.
    If you set timeUnit to "SUMMARY" you can include "startDate" and "endDate" in your column list.

    https://advertising.amazon.com/API/docs/en-us/reporting/v3/get-started#timeunit-and-supported-columns

    Records:
    1) DAILY = ["date", "startDate", "endDate"]
    {"code":"400","detail":"configuration startDate and endDate are not supported columns for DAILY time unit. Please use date instead."}

    2) SUMMARY = ["startDate", "endDate", "date"]
    {"code":"400","detail":"configuration date is not a supported column for SUMMARY time unit. Please use startDate and/or endDate instead."}
    """
    DAILY = ["date"]
    SUMMARY = ["startDate", "endDate"]

    def __init__(self, columns):
        """Easy dot access like: TimeUnit.SUMMARY.columns"""
        self.columns = columns


class GroupBy(Enum):
    """
    请求报告参数、必填、"groupBy"

    所有报告请求都需要报告配置中的参数。确定报告的粒度级别。如果报告类型支持，您可以在请求中使用多个值。

    https://advertising.amazon.com/API/docs/en-us/reporting/v3/get-started#groupby
    https://advertising.amazon.com/API/docs/en-us/reporting/v3/report-types
    """
    pass


class AdsV3ReportsAdapter(object):

    _report_type_id: str = None
    _ad_product: str = None  # SPONSORED_PRODUCTS | SPONSORED_BRANDS | SPONSORED_DISPLAY
    _maximum_date_range: int = None  # days
    _data_retention: int = None  # days
    _time_unit_choices: tuple = ("SUMMARY", "DAILY")
    _group_by_choices: tuple = None
    _base_metrics: list = None
    _format: str = "GZIP_JSON"

    class GroupBy(Enum):
        def __init__(self, columns):
            self.columns = columns

    def __init__(self,
                 group_by: list,
                 time_unit: str,
                 start_date: str,
                 end_date: str,
                 name: str = None):
        assert set(group_by) in self._group_by_choices
        group_by.sort()
        self.group_by = group_by

        assert time_unit in self._time_unit_choices
        self.time_unit = time_unit

        assert arrow.get(end_date) > arrow.get(start_date), ":::ERROR: end_date < start_date !!!"
        # assert (arrow.get(end_date) - arrow.get(start_date)).days <= self._maximum_date_range, \
        #     "The maximum time range is exceeded"
        self.start_date = start_date  # "2022-07-01"
        self.end_date = end_date  # "2022-07-10"

        if not name:
            name = "%s_%s_%s_%s_%s_%s" % (self._report_type_id, self.start_date, self.end_date, '_'.join(self.group_by),
                                          self.time_unit, arrow.utcnow().isoformat())
        self.name = name

    def get_columns(self):
        columns = copy.deepcopy(self._base_metrics)
        for _gb in self.group_by:
            columns += self.GroupBy[_gb].columns
        columns += TimeUnit[self.time_unit].columns
        return columns

    def get_data_raw(self):
        data = {
            "name": self.name,
            "startDate": self.start_date,
            "endDate": self.end_date,
            "configuration": {
                "adProduct": self._ad_product,
                "groupBy": self.group_by,
                "columns": self.get_columns(),
                "reportTypeId": self._report_type_id,
                "timeUnit": self.time_unit,
                "format": self._format
            }
        }
        return data


class SPCampaignReportsAdapter(AdsV3ReportsAdapter):
    """
    Campaign reports contain performance data broken down at the campaign level.
    Campaign reports include all campaigns of the requested sponsored ad type that have performance activity for the requested days.
    For example, a Sponsored Products campaign report returns performance data for all Sponsored Products campaigns that received impressions on the chosen dates.
    Campaign reports can also be grouped by ad group and placement for more granular data.

    https://advertising.amazon.com/API/docs/en-us/reporting/v3/report-types#campaign-reports
    """

    _report_type_id = "spCampaigns"
    _ad_product = "SPONSORED_PRODUCTS"
    _maximum_date_range = 31
    _data_retention = 95
    _group_by_choices = (
        {"campaign"},
        {"adGroup"},
        {"campaignPlacement"},
        {"campaign", "adGroup"},
        {"campaign", "campaignPlacement"},
        # {"adGroup", "campaignPlacement"},  # FAILED
        # {"campaign", "adGroup", "campaignPlacement"},  # FAILED
    )

    _base_metrics = [
        "impressions",
        "clicks",
        "cost",
        "purchases1d",
        "purchases7d",
        "purchases14d",
        "purchases30d",
        "purchasesSameSku1d",
        "purchasesSameSku7d",
        "purchasesSameSku14d",
        "purchasesSameSku30d",
        "unitsSoldClicks1d",
        "unitsSoldClicks7d",
        "unitsSoldClicks14d",
        "unitsSoldClicks30d",
        "sales1d",
        "sales7d",
        "sales14d",
        "sales30d",
        "attributedSalesSameSku1d",
        "attributedSalesSameSku7d",
        "attributedSalesSameSku14d",
        "attributedSalesSameSku30d",
        "unitsSoldSameSku1d",
        "unitsSoldSameSku7d",
        "unitsSoldSameSku14d",
        "unitsSoldSameSku30d",
        "kindleEditionNormalizedPagesRead14d",
        "kindleEditionNormalizedPagesRoyalties14d",
        # "date",
        # "startDate",
        # "endDate",
        "campaignBiddingStrategy",
        "costPerClick",
        "clickThroughRate",
        "spend",
    ]

    class GroupBy(Enum):

        campaign = [
            "campaignName",
            "campaignId",
            "campaignStatus",
            "campaignBudgetAmount",
            "campaignBudgetType",
            "campaignRuleBasedBudgetAmount",
            "campaignApplicableBudgetRuleId",
            "campaignApplicableBudgetRuleName",
            "campaignBudgetCurrencyCode",
            # "topOfSearchImpressionShare",  # 特殊处理下；仅单独 groupBy campaign 时才会有这个字段
        ]

        adGroup = [
            "adGroupName",
            "adGroupId",
            "adStatus",
        ]

        campaignPlacement = [
            "placementClassification",
        ]

        def __init__(self, columns):
            """Easy dot access like: GroupBy.campaign.columns"""
            self.columns = columns

    def get_data_raw(self):
        columns = self.get_columns()
        if len(self.group_by) == 1 and self.group_by[0] == "campaign":
            columns.append("topOfSearchImpressionShare")

        data = {
            "name": self.name,
            "startDate": self.start_date,
            "endDate": self.end_date,
            "configuration": {
                "adProduct": self._ad_product,
                "groupBy": self.group_by,
                "columns": columns,
                "reportTypeId": self._report_type_id,
                "timeUnit": self.time_unit,
                "format": self._format
            }
        }
        return data


class SPTargetingReportsAdapter(AdsV3ReportsAdapter):
    """
    Targeting reports contain performance metrics broken down by both targeting expressions and keywords.
    To see only targeting expressions, set the keywordType filter to TARGETING_EXPRESSION and TARGETING_EXPRESSION_PREDEFINED.
    To see only keywords, set the keywordType filter to BROAD, PHRASE, and EXACT.

    https://advertising.amazon.com/API/docs/en-us/reporting/v3/report-types#targeting-reports
    """

    _report_type_id = "spTargeting"
    _ad_product = "SPONSORED_PRODUCTS"
    _maximum_date_range = 31
    _data_retention = 95
    _group_by_choices = (
        {"targeting"},
    )

    _base_metrics = [
        'impressions',
        'clicks',
        'costPerClick',
        'clickThroughRate',
        'cost',
        'purchases1d',
        'purchases7d',
        'purchases14d',
        'purchases30d',
        'purchasesSameSku1d',
        'purchasesSameSku7d',
        'purchasesSameSku14d',
        'purchasesSameSku30d',
        'unitsSoldClicks1d',
        'unitsSoldClicks7d',
        'unitsSoldClicks14d',
        'unitsSoldClicks30d',
        'sales1d',
        'sales7d',
        'sales14d',
        'sales30d',
        'attributedSalesSameSku1d',
        'attributedSalesSameSku7d',
        'attributedSalesSameSku14d',
        'attributedSalesSameSku30d',
        'unitsSoldSameSku1d',
        'unitsSoldSameSku7d',
        'unitsSoldSameSku14d',
        'unitsSoldSameSku30d',
        'kindleEditionNormalizedPagesRead14d',
        'kindleEditionNormalizedPagesRoyalties14d',
        'salesOtherSku7d',
        'unitsSoldOtherSku7d',
        'acosClicks7d',
        'acosClicks14d',
        'roasClicks7d',
        'roasClicks14d',
        'keywordId',
        'keyword',
        'campaignBudgetCurrencyCode',
        # 'date',
        # 'startDate',
        # 'endDate',
        'portfolioId',
        'campaignName',
        'campaignId',
        'campaignBudgetType',
        'campaignBudgetAmount',
        'campaignStatus',
        'keywordBid',
        'adGroupName',
        'adGroupId',
        'keywordType',
        'matchType',
        'targeting',

        "topOfSearchImpressionShare",
    ]

    class GroupBy(Enum):

        targeting = [
            "adKeywordStatus",
        ]

        def __init__(self, columns):
            """Easy dot access like: GroupBy.targeting.columns"""
            self.columns = columns


class SPSearchTermReportsAdapter(AdsV3ReportsAdapter):
    """
    Search term reports contain search term performance metrics broken down by targeting expressions and keywords.
    Use the keywordType filter to include either targeting expressions or keywords in your report.

    https://advertising.amazon.com/API/docs/en-us/reporting/v3/report-types#search-term-reports
    """

    _report_type_id = "spSearchTerm"
    _ad_product = "SPONSORED_PRODUCTS"
    _maximum_date_range = 31
    _data_retention = 95
    _group_by_choices = (
        {"searchTerm"},
    )

    _base_metrics = [
        'impressions',
        'clicks',
        'costPerClick',
        'clickThroughRate',
        'cost',
        'purchases1d',
        'purchases7d',
        'purchases14d',
        'purchases30d',
        'purchasesSameSku1d',
        'purchasesSameSku7d',
        'purchasesSameSku14d',
        'purchasesSameSku30d',
        'unitsSoldClicks1d',
        'unitsSoldClicks7d',
        'unitsSoldClicks14d',
        'unitsSoldClicks30d',
        'sales1d',
        'sales7d',
        'sales14d',
        'sales30d',
        'attributedSalesSameSku1d',
        'attributedSalesSameSku7d',
        'attributedSalesSameSku14d',
        'attributedSalesSameSku30d',
        'unitsSoldSameSku1d',
        'unitsSoldSameSku7d',
        'unitsSoldSameSku14d',
        'unitsSoldSameSku30d',
        'kindleEditionNormalizedPagesRead14d',
        'kindleEditionNormalizedPagesRoyalties14d',
        'salesOtherSku7d',
        'unitsSoldOtherSku7d',
        'acosClicks7d',
        'acosClicks14d',
        'roasClicks7d',
        'roasClicks14d',
        'keywordId',
        'keyword',
        'campaignBudgetCurrencyCode',
        # 'date',
        # 'startDate',
        # 'endDate',
        'portfolioId',
        'searchTerm',
        'campaignName',
        'campaignId',
        'campaignBudgetType',
        'campaignBudgetAmount',
        'campaignStatus',
        'keywordBid',
        'adGroupName',
        'adGroupId',
        'keywordType',
        'matchType',
        'targeting',
        # 'adKeywordStatus',
    ]

    class GroupBy(Enum):

        searchTerm = [
            "adKeywordStatus",
        ]

        def __init__(self, columns):
            """Easy dot access like: GroupBy.searchTerm.columns"""
            self.columns = columns


class SPAdvertisedProductReportsAdapter(AdsV3ReportsAdapter):
    """
    Advertised product reports contain performance data for products that are advertised as part of your campaigns.

    https://advertising.amazon.com/API/docs/en-us/reporting/v3/report-types#advertised-product-reports
    """

    _report_type_id = "spAdvertisedProduct"
    _ad_product = "SPONSORED_PRODUCTS"
    _maximum_date_range = 31
    _data_retention = 95
    _group_by_choices = (
        {"advertiser"},
    )

    _base_metrics = [
        # 'date',
        # 'startDate',
        # 'endDate',
        'campaignName',
        'campaignId',
        'adGroupName',
        'adGroupId',
        'adId',
        'portfolioId',
        'impressions',
        'clicks',
        'costPerClick',
        'clickThroughRate',
        'cost',
        'spend',
        'campaignBudgetCurrencyCode',
        'campaignBudgetAmount',
        'campaignBudgetType',
        'campaignStatus',
        'advertisedAsin',
        'advertisedSku',
        'purchases1d',
        'purchases7d',
        'purchases14d',
        'purchases30d',
        'purchasesSameSku1d',
        'purchasesSameSku7d',
        'purchasesSameSku14d',
        'purchasesSameSku30d',
        'unitsSoldClicks1d',
        'unitsSoldClicks7d',
        'unitsSoldClicks14d',
        'unitsSoldClicks30d',
        'sales1d',
        'sales7d',
        'sales14d',
        'sales30d',
        'attributedSalesSameSku1d',
        'attributedSalesSameSku7d',
        'attributedSalesSameSku14d',
        'attributedSalesSameSku30d',
        'salesOtherSku7d',
        'unitsSoldSameSku1d',
        'unitsSoldSameSku7d',
        'unitsSoldSameSku14d',
        'unitsSoldSameSku30d',
        'unitsSoldOtherSku7d',
        'kindleEditionNormalizedPagesRead14d',
        'kindleEditionNormalizedPagesRoyalties14d',
        'acosClicks7d',
        'acosClicks14d',
        'roasClicks7d',
        'roasClicks14d',
    ]

    class GroupBy(Enum):

        advertiser = []

        def __init__(self, columns):
            """Easy dot access like: GroupBy.advertiser.columns"""
            self.columns = columns


class SPPurchasedProductReportsAdapter(AdsV3ReportsAdapter):
    """
    Sponsored Products purchased product reports contain performance data for products that were purchased,
    but were not advertised as part of a campaign.
    The purchased product report contains both targeting expressions and keyword IDs.
    After you have received your report,
    you can filter on keywordType to distinguish between targeting expressions and keywords.

    https://advertising.amazon.com/API/docs/en-us/reporting/v3/report-types#purchased-product-reports
    """

    _report_type_id = "spPurchasedProduct"
    _ad_product = "SPONSORED_PRODUCTS"
    _maximum_date_range = 31
    _data_retention = 95
    _group_by_choices = (
        {"asin"},
    )

    _base_metrics = [
        # 'date',
        # 'startDate',
        # 'endDate',
        'portfolioId',
        'campaignName',
        'campaignId',
        'adGroupName',
        'adGroupId',
        'keywordId',
        'keyword',
        'keywordType',
        'advertisedAsin',
        'purchasedAsin',
        'advertisedSku',
        'campaignBudgetCurrencyCode',
        'matchType',
        'unitsSoldClicks1d',
        'unitsSoldClicks7d',
        'unitsSoldClicks14d',
        'unitsSoldClicks30d',
        'sales1d',
        'sales7d',
        'sales14d',
        'sales30d',
        'purchases1d',
        'purchases7d',
        'purchases14d',
        'purchases30d',
        'unitsSoldOtherSku1d',
        'unitsSoldOtherSku7d',
        'unitsSoldOtherSku14d',
        'unitsSoldOtherSku30d',
        'salesOtherSku1d',
        'salesOtherSku7d',
        'salesOtherSku14d',
        'salesOtherSku30d',
        'purchasesOtherSku1d',
        'purchasesOtherSku7d',
        'purchasesOtherSku14d',
        'purchasesOtherSku30d',
        'kindleEditionNormalizedPagesRead14d',
        'kindleEditionNormalizedPagesRoyalties14d',
    ]

    class GroupBy(Enum):

        asin = []

        def __init__(self, columns):
            """Easy dot access like: GroupBy.asin.columns"""
            self.columns = columns


class SPGrossAndInvalidTrafficReportsAdapter(AdsV3ReportsAdapter):
    _report_type_id = "spGrossAndInvalids"
    _ad_product = "SPONSORED_PRODUCTS"
    _maximum_date_range = 365
    _data_retention = 365
    _group_by_choices = (
        {"campaign"},
    )
    _format: str = "GZIP_JSON"  # GZIP_JSON or CSV

    _base_metrics = [
        # 'campaignId',  # 不支持
        'campaignName',
        'campaignStatus',
        # 'date',  # 从 timeUnit 里取
        # 'startDate',
        # 'endDate',
        'clicks',
        'impressions',
        'grossClickThroughs',
        'grossImpressions',
        'invalidClickThroughs',
        'invalidClickThroughRate',
        'invalidImpressions',
        'invalidImpressionRate',
    ]

    class GroupBy(Enum):

        campaign = []

        def __init__(self, columns):
            """Easy dot access like: GroupBy.campaign.columns"""
            self.columns = columns


class SBCampaignReportsAdapter(AdsV3ReportsAdapter):
    _report_type_id = "sbCampaigns"
    _ad_product = "SPONSORED_BRANDS"
    _maximum_date_range = 31
    _data_retention = 60
    _group_by_choices = (
        {"campaign"},
    )

    _base_metrics = [
        'addToCart',
        'addToCartClicks',
        'addToCartRate',
        'brandedSearches',
        'brandedSearchesClicks',
        'campaignBudgetAmount',
        'campaignBudgetCurrencyCode',
        'campaignBudgetType',
        'campaignId',
        'campaignName',
        'campaignStatus',
        'clicks',
        'cost',
        'costType',
        # 'date',
        'detailPageViews',
        'detailPageViewsClicks',
        'eCPAddToCart',
        # 'endDate',
        'impressions',
        'newToBrandDetailPageViewRate',
        'newToBrandDetailPageViews',
        'newToBrandDetailPageViewsClicks',
        'newToBrandECPDetailPageView',
        'newToBrandPurchases',
        'newToBrandPurchasesClicks',
        'newToBrandPurchasesPercentage',
        'newToBrandPurchasesRate',
        'newToBrandSales',
        'newToBrandSalesClicks',
        'newToBrandSalesPercentage',
        'newToBrandUnitsSold',
        'newToBrandUnitsSoldClicks',
        'newToBrandUnitsSoldPercentage',
        'purchases',
        'purchasesClicks',
        'purchasesPromoted',
        'sales',
        'salesClicks',
        'salesPromoted',
        # 'startDate',
        'topOfSearchImpressionShare',
        'unitsSold',
        'unitsSoldClicks',
        'video5SecondViewRate',
        'video5SecondViews',
        'videoCompleteViews',
        'videoFirstQuartileViews',
        'videoMidpointViews',
        'videoThirdQuartileViews',
        'videoUnmutes',
        'viewabilityRate',
        'viewableImpressions',
        'viewClickThroughRate',
    ]

    class GroupBy(Enum):

        # 重复了
        campaign = [
            # "campaignBudgetAmount",
            # "campaignBudgetCurrencyCode",
            # "campaignBudgetType",
            # "topOfSearchImpressionShare",
        ]

        def __init__(self, columns):
            """Easy dot access like: GroupBy.campaign.columns"""
            self.columns = columns


class SBAdGroupReportsAdapter(AdsV3ReportsAdapter):
    _report_type_id = "sbAdGroup"
    _ad_product = "SPONSORED_BRANDS"
    _maximum_date_range = 31
    _data_retention = 60
    _group_by_choices = (
        {"adGroup"},
        {"campaign"},
    )

    _base_metrics = [
        'addToCart',
        'addToCartClicks',
        'addToCartRate',
        'adGroupId',
        'adGroupName',
        'adStatus',
        'brandedSearches',
        'brandedSearchesClicks',
        'campaignBudgetAmount',
        'campaignBudgetCurrencyCode',
        'campaignBudgetType',
        'campaignId',
        'campaignName',
        'campaignStatus',
        'clicks',
        'cost',
        'costType',
        # 'date',
        'detailPageViews',
        'detailPageViewsClicks',
        'eCPAddToCart',
        # 'endDate',
        'impressions',
        'newToBrandDetailPageViewRate',
        'newToBrandDetailPageViews',
        'newToBrandDetailPageViewsClicks',
        'newToBrandECPDetailPageView',
        'newToBrandPurchases',
        'newToBrandPurchasesClicks',
        'newToBrandPurchasesPercentage',
        'newToBrandPurchasesRate',
        'newToBrandSales',
        'newToBrandSalesClicks',
        'newToBrandSalesPercentage',
        'newToBrandUnitsSold',
        'newToBrandUnitsSoldClicks',
        'newToBrandUnitsSoldPercentage',
        'purchases',
        'purchasesClicks',
        'purchasesPromoted',
        'sales',
        'salesClicks',
        'salesPromoted',
        # 'startDate',
        'unitsSold',
        'unitsSoldClicks',
        'video5SecondViewRate',
        'video5SecondViews',
        'videoCompleteViews',
        'videoFirstQuartileViews',
        'videoMidpointViews',
        'videoThirdQuartileViews',
        'videoUnmutes',
        'viewabilityRate',
        'viewableImpressions',
    ]

    class GroupBy(Enum):

        adGroup = []
        campaign = []

        def __init__(self, columns):
            """Easy dot access like: GroupBy.adGroup.columns"""
            self.columns = columns


class SBPlacementReportsAdapter(AdsV3ReportsAdapter):
    _report_type_id = "sbCampaignPlacement"
    _ad_product = "SPONSORED_BRANDS"
    _maximum_date_range = 31
    _data_retention = 60
    _group_by_choices = (
        {"campaignPlacement"},
        {"campaign"},
    )

    _base_metrics = [
        'addToCart',
        'addToCartClicks',
        'addToCartRate',
        'brandedSearches',
        'brandedSearchesClicks',
        'campaignBudgetAmount',
        'campaignBudgetCurrencyCode',
        'campaignBudgetType',
        'campaignId',
        'campaignName',
        'campaignStatus',
        'clicks',
        'cost',
        'costType',
        # 'date',
        'detailPageViews',
        'detailPageViewsClicks',
        'eCPAddToCart',
        # 'endDate',
        'impressions',
        'newToBrandDetailPageViewRate',
        'newToBrandDetailPageViews',
        'newToBrandDetailPageViewsClicks',
        'newToBrandECPDetailPageView',
        'newToBrandPurchases',
        'newToBrandPurchasesClicks',
        'newToBrandPurchasesPercentage',
        'newToBrandPurchasesRate',
        'newToBrandSales',
        'newToBrandSalesClicks',
        'newToBrandSalesPercentage',
        'newToBrandUnitsSold',
        'newToBrandUnitsSoldClicks',
        'newToBrandUnitsSoldPercentage',
        'purchases',
        'purchasesClicks',
        'purchasesPromoted',
        'sales',
        'salesClicks',
        'salesPromoted',
        # 'startDate',
        'unitsSold',
        'unitsSoldClicks',
        'video5SecondViewRate',
        'video5SecondViews',
        'videoCompleteViews',
        'videoFirstQuartileViews',
        'videoMidpointViews',
        'videoThirdQuartileViews',
        'videoUnmutes',
        'viewabilityRate',
        'viewableImpressions',
        'viewClickThroughRate'
    ]

    class GroupBy(Enum):

        campaignPlacement = [
            'placementClassification'
        ]
        campaign = []

        def __init__(self, columns):
            """Easy dot access like: GroupBy.campaignPlacement.columns"""
            self.columns = columns


class SBTargetingReportsAdapter(AdsV3ReportsAdapter):
    _report_type_id = "sbTargeting"
    _ad_product = "SPONSORED_BRANDS"
    _maximum_date_range = 31
    _data_retention = 60
    _group_by_choices = (
        {"targeting"},
    )

    _base_metrics = [
        'addToCart',
        'addToCartClicks',
        'addToCartRate',
        'adGroupId',
        'adGroupName',
        'brandedSearches',
        'brandedSearchesClicks',
        'campaignBudgetAmount',
        'campaignBudgetCurrencyCode',
        'campaignBudgetType',
        'campaignId',
        'campaignName',
        'campaignStatus',
        'clicks',
        'cost',
        'costType',
        # 'date',
        'detailPageViews',
        'detailPageViewsClicks',
        'eCPAddToCart',
        # 'endDate',
        'impressions',
        'keywordBid',
        'keywordId',
        'adKeywordStatus',
        'keywordText',
        'keywordType',
        'matchType',
        'newToBrandDetailPageViewRate',
        'newToBrandDetailPageViews',
        'newToBrandDetailPageViewsClicks',
        'newToBrandECPDetailPageView',
        'newToBrandPurchases',
        'newToBrandPurchasesClicks',
        'newToBrandPurchasesPercentage',
        'newToBrandPurchasesRate',
        'newToBrandSales',
        'newToBrandSalesClicks',
        'newToBrandSalesPercentage',
        'newToBrandUnitsSold',
        'newToBrandUnitsSoldClicks',
        'newToBrandUnitsSoldPercentage',
        'purchases',
        'purchasesClicks',
        'purchasesPromoted',
        'sales',
        'salesClicks',
        'salesPromoted',
        # 'startDate',
        'targetingExpression',
        'targetingId',
        'targetingText',
        'targetingType',
        'topOfSearchImpressionShare',

        'unitsSold',
        'viewableImpressions',
    ]

    class GroupBy(Enum):

        targeting = []

        def __init__(self, columns):
            """Easy dot access like: GroupBy.targeting.columns"""
            self.columns = columns


class SBSearchTermReportsAdapter(AdsV3ReportsAdapter):
    _report_type_id = "sbSearchTerm"
    _ad_product = "SPONSORED_BRANDS"
    _maximum_date_range = 31
    _data_retention = 60
    _group_by_choices = (
        {"searchTerm"},
    )

    _base_metrics = [
        'adGroupId',
        'adGroupName',
        'campaignBudgetAmount',
        'campaignBudgetCurrencyCode',
        'campaignBudgetType',
        'campaignId',
        'campaignName',
        'campaignStatus',
        'clicks',
        'cost',
        'costType',
        # 'date',
        # 'endDate',
        'impressions',
        'keywordBid',
        'keywordId',
        'keywordText',
        'matchType',
        'purchases',
        'purchasesClicks',
        'sales',
        'salesClicks',
        'searchTerm',
        # 'startDate',
        'unitsSold',
        'video5SecondViewRate',
        'video5SecondViews',
        'videoCompleteViews',
        'videoFirstQuartileViews',
        'videoMidpointViews',
        'videoThirdQuartileViews',
        'videoUnmutes',
        'viewabilityRate',
        'viewableImpressions',
        'viewClickThroughRate'
    ]

    class GroupBy(Enum):

        searchTerm = [
            'adKeywordStatus'
        ]

        def __init__(self, columns):
            """Easy dot access like: GroupBy.searchTerm.columns"""
            self.columns = columns


class SBAdReportsAdapter(AdsV3ReportsAdapter):
    _report_type_id = "sbAds"
    _ad_product = "SPONSORED_BRANDS"
    _maximum_date_range = 31
    _data_retention = 60
    _group_by_choices = (
        {"ads"},
    )

    _base_metrics = [
        'addToCart',
        'addToCartClicks',
        'addToCartRate',
        'adGroupId',
        'adGroupName',
        'adId',
        'brandedSearches',
        'brandedSearchesClicks',
        'campaignBudgetAmount',
        'campaignBudgetCurrencyCode',
        'campaignBudgetType',
        'campaignId',
        'campaignName',
        'campaignStatus',
        'clicks',
        'cost',
        'costType',
        # 'date',
        'detailPageViews',
        'detailPageViewsClicks',
        'eCPAddToCart',
        # 'endDate',
        'impressions',
        'newToBrandDetailPageViewRate',
        'newToBrandDetailPageViews',
        'newToBrandDetailPageViewsClicks',
        'newToBrandECPDetailPageView',
        'newToBrandPurchases',
        'newToBrandPurchasesClicks',
        'newToBrandPurchasesPercentage',
        'newToBrandPurchasesRate',
        'newToBrandSales',
        'newToBrandSalesClicks',
        'newToBrandSalesPercentage',
        'newToBrandUnitsSold',
        'newToBrandUnitsSoldClicks',
        'newToBrandUnitsSoldPercentage',
        'purchases',
        'purchasesClicks',
        'purchasesPromoted',
        'sales',
        'salesClicks',
        'salesPromoted',
        # 'startDate',
        'unitsSold',
        'unitsSoldClicks',
        'video5SecondViewRate',
        'video5SecondViews',
        'videoCompleteViews',
        'videoFirstQuartileViews',
        'videoMidpointViews',
        'videoThirdQuartileViews',
        'videoUnmutes',
        'viewabilityRate',
        'viewableImpressions'
    ]

    class GroupBy(Enum):

        ads = []

        def __init__(self, columns):
            """Easy dot access like: GroupBy.ads.columns"""
            self.columns = columns


class SBPurchasedProductReportsAdapter(AdsV3ReportsAdapter):
    """
    Sponsored Brands purchased product reports contain performance data for products that were purchased as a result of your campaign.

    https://advertising.amazon.com/API/docs/en-us/reporting/v3/report-types#sponsored-brands
    """

    _report_type_id = "sbPurchasedProduct"
    _ad_product = "SPONSORED_BRANDS"
    _maximum_date_range = 731
    _data_retention = 731
    _group_by_choices = (
        {"purchasedAsin"},
    )

    _base_metrics = [
        # 'date',
        # 'startDate',
        # 'endDate',

        'campaignId',
        'adGroupId',

        'budgetCurrency',
        'campaignBudgetCurrencyCode',
        'campaignName',
        'adGroupName',
        'attributionType',
        'purchasedAsin',
        'productName',
        'productCategory',
        'sales14d',
        'orders14d',
        'unitsSold14d',
        'newToBrandSales14d',
        'newToBrandOrders14d',
        'newToBrandPurchases14d',
        'newToBrandUnitsSold14d',
        'newToBrandSalesPercentage14d',
        'newToBrandOrdersPercentage14d',
        'newToBrandPurchasesPercentage14d',
        'newToBrandUnitsSoldPercentage14d',

        'campaignPriceTypeCode',
        'ordersClicks14d',
        'salesClicks14d',
        'unitsSoldClicks14d',

        # 'viewableImpressions',
    ]

    class GroupBy(Enum):

        purchasedAsin = []

        def __init__(self, columns):
            """Easy dot access like: GroupBy.purchasedAsin.columns"""
            self.columns = columns


class SBGrossAndInvalidTrafficReportsAdapter(SPGrossAndInvalidTrafficReportsAdapter):
    _report_type_id = "sbGrossAndInvalids"
    _ad_product = "SPONSORED_BRANDS"


class SDCampaignReportsAdapter(AdsV3ReportsAdapter):
    _report_type_id = "sdCampaigns"
    _ad_product = "SPONSORED_DISPLAY"
    _maximum_date_range = 31
    _data_retention = 65
    _group_by_choices = (
        {"campaign"},
        {"matchedTarget"},
        {"campaign", "matchedTarget"},
    )

    _errors_info = {
        'group by campaign & matchedTarget': {
            'code': '400',
            'detail': 'configuration columns include invalid value: (cumulativeReach, impressionsFrequencyAverage, '
                      'newToBrandDetailPageViewClicks, newToBrandDetailPageViewRate, newToBrandDetailPageViews, '
                      'newToBrandDetailPageViewViews, newToBrandECPDetailPageView). '
                      'When matchedTarget is included under groupBy, the following column value cannot be included: ('
                      'impressionsFrequencyAverage, newToBrandDetailPageViews, newToBrandDetailPageViewViews, '
                      'newToBrandDetailPageViewRate, newToBrandDetailPageViewClicks, newToBrandECPDetailPageView, '
                      'cumulativeReach)'
        }
    }

    _base_metrics = [
        'addToCart',
        'addToCartClicks',
        'addToCartRate',
        'addToCartViews',
        'brandedSearches',
        'brandedSearchesClicks',
        'brandedSearchesViews',
        'brandedSearchRate',
        'campaignBudgetCurrencyCode',
        'campaignId',
        'campaignName',
        'clicks',
        'cost',
        # 'date',
        'detailPageViews',
        'detailPageViewsClicks',
        'eCPAddToCart',
        'eCPBrandSearch',
        # 'endDate',
        'impressions',
        'impressionsViews',
        'newToBrandPurchases',
        'newToBrandPurchasesClicks',
        'newToBrandSalesClicks',
        'newToBrandUnitsSold',
        'newToBrandUnitsSoldClicks',
        'purchases',
        'purchasesClicks',
        'purchasesPromotedClicks',
        'sales',
        'salesClicks',
        'salesPromotedClicks',
        # 'startDate',
        'unitsSold',
        'unitsSoldClicks',
        'videoCompleteViews',
        'videoFirstQuartileViews',
        'videoMidpointViews',
        'videoThirdQuartileViews',
        'videoUnmutes',
        'viewabilityRate',
        'viewClickThroughRate',

        'leadFormOpens',
        'leads',
        'linkOuts',
    ]

    class GroupBy(Enum):

        campaign = [
            'campaignBudgetAmount',
            'campaignStatus',
            'costType',
            'cumulativeReach',
            'impressionsFrequencyAverage',
            'newToBrandDetailPageViewClicks',
            'newToBrandDetailPageViewRate',
            'newToBrandDetailPageViews',
            'newToBrandDetailPageViewViews',
            'newToBrandECPDetailPageView',
            'newToBrandSales'
        ]

        matchedTarget = [
            'matchedTargetAsin'
        ]

        def __init__(self, columns):
            """Easy dot access like: GroupBy.campaign.columns"""
            self.columns = columns

    def get_data_raw(self):
        data = super(SDCampaignReportsAdapter, self).get_data_raw()
        if set(self.group_by) == {"campaign", "matchedTarget"}:
            columns = copy.deepcopy(data['configuration']['columns'])
            columns = set(columns) - {
                'cumulativeReach',
                'impressionsFrequencyAverage',
                'newToBrandDetailPageViewClicks',
                'newToBrandDetailPageViewRate',
                'newToBrandDetailPageViews',
                'newToBrandDetailPageViewViews',
                'newToBrandECPDetailPageView'
            }
            data['configuration']['columns'] = list(columns)
        return data


class SDAdGroupReportsAdapter(AdsV3ReportsAdapter):
    _report_type_id = "sdAdGroup"
    _ad_product = "SPONSORED_DISPLAY"
    _maximum_date_range = 31
    _data_retention = 65
    _group_by_choices = (
        {"adGroup"},
        {"matchedTarget"},
        {"adGroup", "matchedTarget"},
    )

    _errors_info = {
        'group by adGroup and matchedTarget': {
            "code":"400",
            "detail":"configuration columns include invalid value: (cumulativeReach, impressionsFrequencyAverage, "
                     "newToBrandDetailPageViewClicks, newToBrandDetailPageViewRate, newToBrandDetailPageViews, "
                     "newToBrandDetailPageViewViews, newToBrandECPDetailPageView). When matchedTarget is included under "
                     "groupBy, the following column value cannot be included: (impressionsFrequencyAverage, "
                     "newToBrandDetailPageViews, newToBrandDetailPageViewViews, newToBrandDetailPageViewRate, "
                     "newToBrandDetailPageViewClicks, newToBrandECPDetailPageView, cumulativeReach)"
        }
    }

    _base_metrics = [
        'addToCart',
        'addToCartClicks',
        'addToCartRate',
        'addToCartViews',
        'adGroupId',
        'adGroupName',
        'bidOptimization',
        'brandedSearches',
        'brandedSearchesClicks',
        'brandedSearchesViews',
        'brandedSearchRate',
        'campaignBudgetCurrencyCode',
        'campaignId',
        'campaignName',
        'clicks',
        'cost',
        # 'date',
        'detailPageViews',
        'detailPageViewsClicks',
        'eCPAddToCart',
        'eCPBrandSearch',
        # 'endDate',
        'impressions',
        'impressionsViews',
        'newToBrandPurchases',
        'newToBrandPurchasesClicks',
        'newToBrandSales',
        'newToBrandSalesClicks',
        'newToBrandUnitsSold',
        'newToBrandUnitsSoldClicks',
        'purchases',
        'purchasesClicks',
        'purchasesPromotedClicks',
        'sales',
        'salesClicks',
        'salesPromotedClicks',
        # 'startDate',
        'unitsSold',
        'unitsSoldClicks',
        'videoCompleteViews',
        'videoFirstQuartileViews',
        'videoMidpointViews',
        'videoThirdQuartileViews',
        'videoUnmutes',
        'viewabilityRate',
        'viewClickThroughRate',

        'leadFormOpens',
        'leads',
        'linkOuts',
    ]

    class GroupBy(Enum):

        adGroup = [
            'cumulativeReach',
            'impressionsFrequencyAverage',
            'newToBrandDetailPageViewClicks',
            'newToBrandDetailPageViewRate',
            'newToBrandDetailPageViews',
            'newToBrandDetailPageViewViews',
            'newToBrandECPDetailPageView'
        ]

        matchedTarget = [
            'matchedTargetAsin'
        ]

        def __init__(self, columns):
            """Easy dot access like: GroupBy.adGroup.columns"""
            self.columns = columns

    def get_data_raw(self):
        data = super(SDAdGroupReportsAdapter, self).get_data_raw()
        if set(self.group_by) == {"adGroup", "matchedTarget"}:
            columns = copy.deepcopy(data['configuration']['columns'])
            columns = set(columns) - {
                'cumulativeReach',
                'impressionsFrequencyAverage',
                'newToBrandDetailPageViewClicks',
                'newToBrandDetailPageViewRate',
                'newToBrandDetailPageViews',
                'newToBrandDetailPageViewViews',
                'newToBrandECPDetailPageView'
            }
            data['configuration']['columns'] = list(columns)
        return data


class SDTargetingReportsAdapter(AdsV3ReportsAdapter):
    _report_type_id = "sdTargeting"
    _ad_product = "SPONSORED_DISPLAY"
    _maximum_date_range = 31
    _data_retention = 65
    _group_by_choices = (
        {"targeting"},
        {"matchedTarget"},
        {"targeting", "matchedTarget"},
    )

    _errors_info = {
        'group by adGroup and matchedTarget': {
            "code":"400",
            "detail":"configuration columns include invalid value: (newToBrandDetailPageViewClicks, "
                     "newToBrandDetailPageViewRate, newToBrandDetailPageViews, newToBrandDetailPageViewViews, "
                     "newToBrandECPDetailPageView). When matchedTarget is included under groupBy, the following column "
                     "value cannot be included: (newToBrandDetailPageViews, newToBrandDetailPageViewViews, "
                     "newToBrandDetailPageViewRate, newToBrandDetailPageViewClicks, newToBrandECPDetailPageView)"
        }
    }

    _base_metrics = [
        'addToCart',
        'addToCartClicks',
        'addToCartRate',
        'addToCartViews',
        'adGroupId',
        'adGroupName',
        'brandedSearches',
        'brandedSearchesClicks',
        'brandedSearchesViews',
        'brandedSearchRate',
        'campaignBudgetCurrencyCode',
        'campaignId',
        'campaignName',
        'clicks',
        'cost',
        # 'date',
        'detailPageViews',
        'detailPageViewsClicks',
        'eCPAddToCart',
        'eCPBrandSearch',
        # 'endDate',
        'impressions',
        'impressionsViews',
        'newToBrandPurchases',
        'newToBrandPurchasesClicks',
        'newToBrandSales',
        'newToBrandSalesClicks',
        'newToBrandUnitsSold',
        'newToBrandUnitsSoldClicks',
        'purchases',
        'purchasesClicks',
        'purchasesPromotedClicks',
        'sales',
        'salesClicks',
        'salesPromotedClicks',
        # 'startDate',
        'targetingExpression',
        'targetingId',
        'targetingText',
        'unitsSold',
        'unitsSoldClicks',
        'videoCompleteViews',

        'leadFormOpens',
        'leads',
        'linkOuts',
        'videoFirstQuartileViews',
        'videoMidpointViews',
        'videoThirdQuartileViews',
        'videoUnmutes',
        'viewClickThroughRate',
        'viewabilityRate',
    ]

    class GroupBy(Enum):

        targeting = [
            'adKeywordStatus',
            'newToBrandDetailPageViewClicks',
            'newToBrandDetailPageViewRate',
            'newToBrandDetailPageViews',
            'newToBrandDetailPageViewViews',
            'newToBrandECPDetailPageView'
        ]

        matchedTarget = [
            'matchedTargetAsin'
        ]

        def __init__(self, columns):
            """Easy dot access like: GroupBy.targeting.columns"""
            self.columns = columns

    def get_data_raw(self):
        data = super(SDTargetingReportsAdapter, self).get_data_raw()
        if set(self.group_by) == {"targeting", "matchedTarget"}:
            columns = copy.deepcopy(data['configuration']['columns'])
            columns = set(columns) - {
                'newToBrandDetailPageViewClicks',
                'newToBrandDetailPageViewRate',
                'newToBrandDetailPageViews',
                'newToBrandDetailPageViewViews',
                'newToBrandECPDetailPageView'
            }
            data['configuration']['columns'] = list(columns)
        return data


class SDAdvertisedProductReportsAdapter(AdsV3ReportsAdapter):
    _report_type_id = "sdAdvertisedProduct"
    _ad_product = "SPONSORED_DISPLAY"
    _maximum_date_range = 31
    _data_retention = 65
    _group_by_choices = (
        {"advertiser"},
    )

    _base_metrics = [
        'addToCart',
        'addToCartClicks',
        'addToCartRate',
        'addToCartViews',
        'adGroupId',
        'adGroupName',
        'adId',
        'bidOptimization',
        'brandedSearches',
        'brandedSearchesClicks',
        'brandedSearchesViews',
        'brandedSearchRate',
        'campaignBudgetCurrencyCode',
        'campaignId',
        'campaignName',
        'clicks',
        'cost',
        'cumulativeReach',
        # 'date',
        'detailPageViews',
        'detailPageViewsClicks',
        'eCPAddToCart',
        'eCPBrandSearch',
        # 'endDate',
        'impressions',
        'impressionsFrequencyAverage',
        'impressionsViews',
        'newToBrandDetailPageViewClicks',
        'newToBrandDetailPageViewRate',
        'newToBrandDetailPageViews',
        'newToBrandDetailPageViewViews',
        'newToBrandECPDetailPageView',
        'newToBrandPurchases',
        'newToBrandPurchasesClicks',
        'newToBrandSales',
        'newToBrandSalesClicks',
        'newToBrandUnitsSold',
        'newToBrandUnitsSoldClicks',
        'promotedAsin',
        'promotedSku',
        'purchases',
        'purchasesClicks',
        'purchasesPromotedClicks',
        'sales',
        'salesClicks',
        'salesPromotedClicks',
        # 'startDate',
        'unitsSold',
        'unitsSoldClicks',
        'videoCompleteViews',
        'videoFirstQuartileViews',
        'videoMidpointViews',
        'videoThirdQuartileViews',
        'videoUnmutes',
        'viewabilityRate',
        'viewClickThroughRate',

        'leadFormOpens',
        'leads',
        'linkOuts',
    ]

    class GroupBy(Enum):

        advertiser = []

        def __init__(self, columns):
            """Easy dot access like: GroupBy.advertiser.columns"""
            self.columns = columns


class SDPurchasedProductReportsAdapter(AdsV3ReportsAdapter):
    _report_type_id = "sdPurchasedProduct"
    _ad_product = "SPONSORED_DISPLAY"
    _maximum_date_range = 31
    _data_retention = 65
    _group_by_choices = (
        {"asin"},
    )

    _base_metrics = [
        'adGroupId',
        'adGroupName',
        'asinBrandHalo',
        'campaignBudgetCurrencyCode',
        'campaignId',
        'campaignName',
        'conversionsBrandHalo',
        'conversionsBrandHaloClicks',
        # 'date',
        # 'endDate',
        'promotedAsin',
        'promotedSku',
        'salesBrandHalo',
        'salesBrandHaloClicks',
        # 'startDate',
        'unitsSoldBrandHalo',
        'unitsSoldBrandHaloClicks'
    ]

    class GroupBy(Enum):

        asin = []

        def __init__(self, columns):
            """Easy dot access like: GroupBy.asin.columns"""
            self.columns = columns


class SDGrossAndInvalidTrafficReportsAdapter(SPGrossAndInvalidTrafficReportsAdapter):
    _report_type_id = "sdGrossAndInvalids"
    _ad_product = "SPONSORED_DISPLAY"


if __name__ == '__main__':

    # pprint(SPCampaignReportsAdapter(group_by=["campaign"], time_unit="DAILY", start_date="2022-07-01", end_date="2022-07-31").get_data_raw())
    # pprint(SPCampaignReportsAdapter(group_by=["campaign"], time_unit="SUMMARY", start_date="2022-07-01", end_date="2022-07-31").get_data_raw())
    # pprint(SPCampaignReportsAdapter(group_by=["adGroup"], time_unit="DAILY", start_date="2022-07-01", end_date="2022-07-31").get_data_raw())
    # pprint(SPCampaignReportsAdapter(group_by=["adGroup"], time_unit="SUMMARY", start_date="2022-07-01", end_date="2022-07-31").get_data_raw())
    # pprint(SPCampaignReportsAdapter(group_by=["campaignPlacement"], time_unit="DAILY", start_date="2022-07-01", end_date="2022-07-31").get_data_raw())
    # pprint(SPCampaignReportsAdapter(group_by=["campaignPlacement"], time_unit="SUMMARY", start_date="2022-07-01", end_date="2022-07-31").get_data_raw())
    # pprint(SPCampaignReportsAdapter(group_by=["campaign", "adGroup"], time_unit="DAILY", start_date="2022-07-01", end_date="2022-07-31").get_data_raw())
    # pprint(SPCampaignReportsAdapter(group_by=["campaign", "adGroup"], time_unit="SUMMARY", start_date="2022-07-01", end_date="2022-07-31").get_data_raw())
    # pprint(SPCampaignReportsAdapter(group_by=["campaign", "campaignPlacement"], time_unit="DAILY", start_date="2022-07-01", end_date="2022-07-31").get_data_raw())
    # pprint(SPCampaignReportsAdapter(group_by=["campaign", "campaignPlacement"], time_unit="SUMMARY", start_date="2022-07-01", end_date="2022-07-31").get_data_raw())
    #
    # TODO FAILED !!! failureReason: Report generation failed due to an internal error. Please retry
    # pprint(SPCampaignReportsAdapter(group_by=["adGroup", "campaignPlacement"], time_unit="DAILY", start_date="2022-07-01", end_date="2022-07-31").get_data_raw())
    # pprint(SPCampaignReportsAdapter(group_by=["adGroup", "campaignPlacement"], time_unit="SUMMARY", start_date="2022-07-01", end_date="2022-07-31").get_data_raw())
    # pprint(SPCampaignReportsAdapter(group_by=["campaign", "adGroup", "campaignPlacement"], time_unit="DAILY", start_date="2022-07-01", end_date="2022-07-31").get_data_raw())
    # pprint(SPCampaignReportsAdapter(group_by=["campaign", "adGroup", "campaignPlacement"], time_unit="SUMMARY", start_date="2022-07-01", end_date="2022-07-31").get_data_raw())
    #
    # pprint(SPTargetingReportsAdapter(group_by=["targeting"], time_unit="DAILY", start_date="2022-07-01", end_date="2022-07-31").get_data_raw())
    # pprint(SPTargetingReportsAdapter(group_by=["targeting"], time_unit="SUMMARY", start_date="2022-07-01", end_date="2022-07-31").get_data_raw())
    #
    # pprint(SPSearchTermReportsAdapter(group_by=["searchTerm"], time_unit="DAILY", start_date="2022-07-01", end_date="2022-07-31").get_data_raw())
    # pprint(SPSearchTermReportsAdapter(group_by=["searchTerm"], time_unit="SUMMARY", start_date="2022-07-01", end_date="2022-07-31").get_data_raw())
    #
    # pprint(SPAdvertisedProductReportsAdapter(group_by=["advertiser"], time_unit="DAILY", start_date="2022-07-01", end_date="2022-07-31").get_data_raw())
    # pprint(SPAdvertisedProductReportsAdapter(group_by=["advertiser"], time_unit="SUMMARY", start_date="2022-07-01", end_date="2022-07-31").get_data_raw())
    #
    # pprint(SPPurchasedProductReportsAdapter(group_by=["asin"], time_unit="DAILY", start_date="2022-07-01", end_date="2022-07-31").get_data_raw())
    # pprint(SPPurchasedProductReportsAdapter(group_by=["asin"], time_unit="SUMMARY", start_date="2022-07-01", end_date="2022-07-31").get_data_raw())
    #
    # pprint(SPGrossAndInvalidTrafficReportsAdapter(group_by=["campaign"], time_unit="DAILY", start_date="2023-01-01", end_date="2023-10-01").get_data_raw())
    # pprint(SPGrossAndInvalidTrafficReportsAdapter(group_by=["campaign"], time_unit="SUMMARY", start_date="2023-01-01", end_date="2023-10-01").get_data_raw())
    #
    #
    # pprint(SBCampaignReportsAdapter(group_by=["campaign"], time_unit="DAILY", start_date="2023-11-01", end_date="2023-11-30").get_data_raw())
    # pprint(SBCampaignReportsAdapter(group_by=["campaign"], time_unit="SUMMARY", start_date="2023-11-01", end_date="2023-11-30").get_data_raw())
    #
    # pprint(SBPurchasedProductReportsAdapter(group_by=["purchasedAsin"], time_unit="DAILY", start_date="2024-07-01", end_date="2024-07-10").get_data_raw())
    # pprint(SBPurchasedProductReportsAdapter(group_by=["purchasedAsin"], time_unit="SUMMARY", start_date="2021-07-01", end_date="2022-07-01").get_data_raw())
    #
    # pprint(SBGrossAndInvalidTrafficReportsAdapter(group_by=["campaign"], time_unit="DAILY", start_date="2023-01-01", end_date="2023-10-01").get_data_raw())
    # pprint(SBGrossAndInvalidTrafficReportsAdapter(group_by=["campaign"], time_unit="SUMMARY", start_date="2023-01-01", end_date="2023-10-01").get_data_raw())
    #
    #
    # pprint(SDCampaignReportsAdapter(group_by=["campaign"], time_unit="DAILY", start_date="2023-11-01", end_date="2023-11-30").get_data_raw())
    # pprint(SDCampaignReportsAdapter(group_by=["campaign"], time_unit="SUMMARY", start_date="2023-11-01", end_date="2023-11-30").get_data_raw())
    # pprint(SDCampaignReportsAdapter(group_by=["matchedTarget"], time_unit="DAILY", start_date="2023-11-01", end_date="2023-11-30").get_data_raw())
    # pprint(SDCampaignReportsAdapter(group_by=["matchedTarget"], time_unit="SUMMARY", start_date="2023-11-01", end_date="2023-11-30").get_data_raw())
    # pprint(SDCampaignReportsAdapter(group_by=["campaign", "matchedTarget"], time_unit="DAILY", start_date="2023-11-01", end_date="2023-11-30").get_data_raw())
    # pprint(SDCampaignReportsAdapter(group_by=["campaign", "matchedTarget"], time_unit="SUMMARY", start_date="2023-11-01", end_date="2023-11-30").get_data_raw())

    # pprint(SDAdGroupReportsAdapter(group_by=["adGroup"], time_unit="DAILY", start_date="2023-11-01", end_date="2023-11-30").get_data_raw())
    # pprint(SDAdGroupReportsAdapter(group_by=["adGroup"], time_unit="SUMMARY", start_date="2023-11-01", end_date="2023-11-30").get_data_raw())
    # pprint(SDAdGroupReportsAdapter(group_by=["matchedTarget"], time_unit="DAILY", start_date="2023-11-01", end_date="2023-11-30").get_data_raw())
    # pprint(SDAdGroupReportsAdapter(group_by=["matchedTarget"], time_unit="SUMMARY", start_date="2023-11-01", end_date="2023-11-30").get_data_raw())
    # pprint(SDAdGroupReportsAdapter(group_by=["adGroup", "matchedTarget"], time_unit="DAILY", start_date="2023-11-01", end_date="2023-11-30").get_data_raw())
    # pprint(SDAdGroupReportsAdapter(group_by=["adGroup", "matchedTarget"], time_unit="SUMMARY", start_date="2023-11-01", end_date="2023-11-30").get_data_raw())

    # pprint(SDTargetingReportsAdapter(group_by=["targeting"], time_unit="DAILY", start_date="2023-11-01", end_date="2023-11-30").get_data_raw())
    # pprint(SDTargetingReportsAdapter(group_by=["targeting"], time_unit="SUMMARY", start_date="2023-11-01", end_date="2023-11-30").get_data_raw())
    # pprint(SDTargetingReportsAdapter(group_by=["matchedTarget"], time_unit="DAILY", start_date="2023-11-01", end_date="2023-11-30").get_data_raw())
    # pprint(SDTargetingReportsAdapter(group_by=["matchedTarget"], time_unit="SUMMARY", start_date="2023-11-01", end_date="2023-11-30").get_data_raw())
    # pprint(SDTargetingReportsAdapter(group_by=["targeting", "matchedTarget"], time_unit="DAILY", start_date="2023-11-01", end_date="2023-11-30").get_data_raw())
    # pprint(SDTargetingReportsAdapter(group_by=["targeting", "matchedTarget"], time_unit="SUMMARY", start_date="2023-11-01", end_date="2023-11-30").get_data_raw())

    # pprint(SDAdvertisedProductReportsAdapter(group_by=["advertiser"], time_unit="DAILY", start_date="2023-11-01", end_date="2023-11-30").get_data_raw())
    # pprint(SDAdvertisedProductReportsAdapter(group_by=["advertiser"], time_unit="SUMMARY", start_date="2023-11-01", end_date="2023-11-30").get_data_raw())

    # pprint(SDPurchasedProductReportsAdapter(group_by=["asin"], time_unit="DAILY", start_date="2023-11-01", end_date="2023-11-30").get_data_raw())
    # pprint(SDPurchasedProductReportsAdapter(group_by=["asin"], time_unit="SUMMARY", start_date="2023-11-01", end_date="2023-11-30").get_data_raw())

    # pprint(SDGrossAndInvalidTrafficReportsAdapter(group_by=["campaign"], time_unit="DAILY", start_date="2023-01-01", end_date="2023-10-01").get_data_raw())
    # pprint(SDGrossAndInvalidTrafficReportsAdapter(group_by=["campaign"], time_unit="SUMMARY", start_date="2023-01-01", end_date="2023-10-01").get_data_raw())

    # pprint(SBTargetingReportsAdapter(group_by=["targeting"], time_unit="DAILY", start_date="2024-07-01", end_date="2024-07-10").get_data_raw())
    # pprint(SBAdGroupReportsAdapter(group_by=["adGroup"], time_unit="DAILY", start_date="2024-07-01", end_date="2024-07-02").get_data_raw())
    pprint(SBPurchasedProductReportsAdapter(group_by=["purchasedAsin"], time_unit="DAILY", start_date="2024-07-01", end_date="2024-07-02").get_data_raw())

    # response = ads_request_report(payload, ad_type='sb', record_type='c_campaign_daily', start_date='2024-06-16', end_date='2024-07-17')
    # response = ads_request_report(payload, ad_type='sb', record_type='c_campaign_summary', start_date='2024-06-16', end_date='2024-07-17')
    #
    # response = ads_request_report(payload, ad_type='sb', record_type='cp_campaign_placement_daily', start_date='2024-06-16', end_date='2024-07-17')
    # response = ads_request_report(payload, ad_type='sb', record_type='cp_campaign_placement_summary', start_date='2024-06-16', end_date='2024-07-17')
    #
    # response = ads_request_report(payload, ad_type='sb', record_type='ag_ad_group_daily', start_date='2024-06-16', end_date='2024-07-17')
    # response = ads_request_report(payload, ad_type='sb', record_type='ag_ad_group_summary', start_date='2024-06-16', end_date='2024-07-17')
    #
    # response = ads_request_report(payload, ad_type='sb', record_type='a_ads_daily', start_date='2024-06-16', end_date='2024-07-17')
    # response = ads_request_report(payload, ad_type='sb', record_type='a_ads_summary', start_date='2024-06-16', end_date='2024-07-17')
    #
    # response = ads_request_report(payload, ad_type='sb', record_type='t_targeting_daily', start_date='2024-06-16', end_date='2024-07-17')
    # response = ads_request_report(payload, ad_type='sb', record_type='t_targeting_summary', start_date='2024-06-16', end_date='2024-07-17')
    #
    # response = ads_request_report(payload, ad_type='sb', record_type='st_search_term_daily', start_date='2024-06-16', end_date='2024-07-17')
    # response = ads_request_report(payload, ad_type='sb', record_type='st_search_term_summary', start_date='2024-06-16', end_date='2024-07-17')
    #
    #
    # response = ads_request_report(payload, ad_type='sd', record_type='c_campaign_matched_target_daily', start_date='2024-06-16', end_date='2024-07-17')
    # response = ads_request_report(payload, ad_type='sd', record_type='c_campaign_matched_target_summary', start_date='2024-06-16', end_date='2024-07-17')
    #
    # response = ads_request_report(payload, ad_type='sd', record_type='ag_ad_group_matched_target_daily', start_date='2024-06-16', end_date='2024-07-17')
    # response = ads_request_report(payload, ad_type='sd', record_type='ag_ad_group_matched_target_summary', start_date='2024-06-16', end_date='2024-07-17')
    #
    # response = ads_request_report(payload, ad_type='sd', record_type='t_targeting_matched_target_daily', start_date='2024-06-16', end_date='2024-07-17')
    # response = ads_request_report(payload, ad_type='sd', record_type='t_targeting_matched_target_summary', start_date='2024-06-16', end_date='2024-07-17')
    #
    # response = ads_request_report(payload, ad_type='sd', record_type='pp_asin_daily', start_date='2024-06-16', end_date='2024-07-17')
    # response = ads_request_report(payload, ad_type='sd', record_type='pp_asin_summary', start_date='2024-06-16', end_date='2024-07-17')
    #

