# -*- coding: utf-8 -*-
# Authored by: Josh (joshzda@gmail.com)

from amazon_ad.api.base import ZADOpenAPI

# 该变量貌似未被使用到
ALLOW_REPORT_TYPES = [
    "campaigns",
    "adGroups",
    "keywords",
    "productAds",
    "targets",
    "asins",  # 一直都有这个类型为啥不添加
]


# 不同类型的SP报表的默认指标
# https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Reports/requestReport
DEFAULT_REPORT_METRICS = {
    "campaigns":  [
        # "bidPlus",  # v2

        "campaignName",
        "campaignId",
        "campaignStatus",
        "campaignBudget",

        # "campaignRuleBasedBudget",  # v2
        # "applicableBudgetRuleId",  # v2
        # "applicableBudgetRuleName",  # v2

        "impressions",
        "clicks",
        "cost",
        "attributedConversions1d",
        "attributedConversions7d",
        "attributedConversions14d",
        "attributedConversions30d",
        "attributedConversions1dSameSKU",
        "attributedConversions7dSameSKU",
        "attributedConversions14dSameSKU",
        "attributedConversions30dSameSKU",
        "attributedUnitsOrdered1d",
        "attributedUnitsOrdered7d",
        "attributedUnitsOrdered14d",
        "attributedUnitsOrdered30d",
        "attributedSales1d",
        "attributedSales7d",
        "attributedSales14d",
        "attributedSales30d",
        "attributedSales1dSameSKU",
        "attributedSales7dSameSKU",
        "attributedSales14dSameSKU",
        "attributedSales30dSameSKU",
        "attributedUnitsOrdered1dSameSKU",
        "attributedUnitsOrdered7dSameSKU",
        "attributedUnitsOrdered14dSameSKU",
        "attributedUnitsOrdered30dSameSKU",

        # "attributedKindleEditionNormalizedPagesRead14d",  # v2
        # "attributedKindleEditionNormalizedPagesRoyalties14d",  # v2
    ],
    "adGroups": [
        "campaignName",
        "campaignId",
        "adGroupName",
        "adGroupId",
        "impressions",
        "clicks",
        "cost",
        "attributedConversions1d",
        "attributedConversions7d",
        "attributedConversions14d",
        "attributedConversions30d",
        "attributedConversions1dSameSKU",
        "attributedConversions7dSameSKU",
        "attributedConversions14dSameSKU",
        "attributedConversions30dSameSKU",
        "attributedUnitsOrdered1d",
        "attributedUnitsOrdered7d",
        "attributedUnitsOrdered14d",
        "attributedUnitsOrdered30d",
        "attributedSales1d",
        "attributedSales7d",
        "attributedSales14d",
        "attributedSales30d",
        "attributedSales1dSameSKU",
        "attributedSales7dSameSKU",
        "attributedSales14dSameSKU",
        "attributedSales30dSameSKU",
        "attributedUnitsOrdered1dSameSKU",
        "attributedUnitsOrdered7dSameSKU",
        "attributedUnitsOrdered14dSameSKU",
        "attributedUnitsOrdered30dSameSKU",

        # "attributedKindleEditionNormalizedPagesRead14d",  # v2
        # "attributedKindleEditionNormalizedPagesRoyalties14d",  # v2
    ],
    "keywords": [
        "campaignName",
        "campaignId",
        "adGroupName",
        "adGroupId",
        "keywordId",
        "keywordText",
        "matchType",
        "impressions",
        "clicks",
        "cost",
        "attributedConversions1d",
        "attributedConversions7d",
        "attributedConversions14d",
        "attributedConversions30d",
        "attributedConversions1dSameSKU",
        "attributedConversions7dSameSKU",
        "attributedConversions14dSameSKU",
        "attributedConversions30dSameSKU",
        "attributedUnitsOrdered1d",
        "attributedUnitsOrdered7d",
        "attributedUnitsOrdered14d",
        "attributedUnitsOrdered30d",
        "attributedSales1d",
        "attributedSales7d",
        "attributedSales14d",
        "attributedSales30d",
        "attributedSales1dSameSKU",
        "attributedSales7dSameSKU",
        "attributedSales14dSameSKU",
        "attributedSales30dSameSKU",
        "attributedUnitsOrdered1dSameSKU",
        "attributedUnitsOrdered7dSameSKU",
        "attributedUnitsOrdered14dSameSKU",
        "attributedUnitsOrdered30dSameSKU",

        # "attributedKindleEditionNormalizedPagesRead14d",  # v2
        # "attributedKindleEditionNormalizedPagesRoyalties14d",  # v2
    ],
    "productAds": [
        # "bidPlus",
        "campaignName",
        "campaignId",
        "adGroupName",
        "adGroupId",
        "impressions",
        "clicks",
        "cost",
        "currency",
        "asin",
        "sku",
        "attributedConversions1d",
        "attributedConversions7d",
        "attributedConversions14d",
        "attributedConversions30d",
        "attributedConversions1dSameSKU",
        "attributedConversions7dSameSKU",
        "attributedConversions14dSameSKU",
        "attributedConversions30dSameSKU",
        "attributedUnitsOrdered1d",
        "attributedUnitsOrdered7d",
        "attributedUnitsOrdered14d",
        "attributedUnitsOrdered30d",
        "attributedSales1d",
        "attributedSales7d",
        "attributedSales14d",
        "attributedSales30d",
        "attributedSales1dSameSKU",
        "attributedSales7dSameSKU",
        "attributedSales14dSameSKU",
        "attributedSales30dSameSKU",
        "attributedUnitsOrdered1dSameSKU",
        "attributedUnitsOrdered7dSameSKU",
        "attributedUnitsOrdered14dSameSKU",
        "attributedUnitsOrdered30dSameSKU",

        # "attributedKindleEditionNormalizedPagesRead14d",  # v2
        # "attributedKindleEditionNormalizedPagesRoyalties14d",  # v2
    ],
    "targets": [
        "campaignName",
        "campaignId",
        "adGroupName",
        "adGroupId",
        "targetId",
        "targetingExpression",
        "targetingText",
        "targetingType",
        "impressions",
        "clicks",
        "cost",
        "attributedConversions1d",
        "attributedConversions7d",
        "attributedConversions14d",
        "attributedConversions30d",
        "attributedConversions1dSameSKU",
        "attributedConversions7dSameSKU",
        "attributedConversions14dSameSKU",
        "attributedConversions30dSameSKU",
        "attributedUnitsOrdered1d",
        "attributedUnitsOrdered7d",
        "attributedUnitsOrdered14d",
        "attributedUnitsOrdered30d",
        "attributedSales1d",
        "attributedSales7d",
        "attributedSales14d",
        "attributedSales30d",
        "attributedSales1dSameSKU",
        "attributedSales7dSameSKU",
        "attributedSales14dSameSKU",
        "attributedSales30dSameSKU",
        "attributedUnitsOrdered1dSameSKU",
        "attributedUnitsOrdered7dSameSKU",
        "attributedUnitsOrdered14dSameSKU",
        "attributedUnitsOrdered30dSameSKU",

        # "attributedKindleEditionNormalizedPagesRead14d",  # v2
        # "attributedKindleEditionNormalizedPagesRoyalties14d",  # v2
    ],
    "asins": [
        "campaignName",
        "campaignId",
        "adGroupName",
        "adGroupId",
        "keywordId",
        "keywordText",
        "asin",
        "otherAsin",
        "sku",
        "currency",
        "matchType",
        "attributedUnitsOrdered1d",
        "attributedUnitsOrdered7d",
        "attributedUnitsOrdered14d",
        "attributedUnitsOrdered30d",
        "attributedUnitsOrdered1dOtherSKU",
        "attributedUnitsOrdered7dOtherSKU",
        "attributedUnitsOrdered14dOtherSKU",
        "attributedUnitsOrdered30dOtherSKU",
        "attributedSales1dOtherSKU",
        "attributedSales7dOtherSKU",
        "attributedSales14dOtherSKU",
        "attributedSales30dOtherSKU",

        # "targetId",  # v2
        # "targetingText",  # v2
        # "targetingType",  # v2
        # "attributedKindleEditionNormalizedPagesRead14d",  # v2
        # "attributedKindleEditionNormalizedPagesRoyalties14d",  # v2
    ],
    "asins_keyword": [
        "campaignName",
        "campaignId",
        "adGroupName",
        "adGroupId",
        "keywordId",
        "keywordText",
        "asin",
        "otherAsin",
        "sku",
        "currency",
        "matchType",
        "attributedUnitsOrdered1d",
        "attributedUnitsOrdered7d",
        "attributedUnitsOrdered14d",
        "attributedUnitsOrdered30d",
        "attributedUnitsOrdered1dOtherSKU",
        "attributedUnitsOrdered7dOtherSKU",
        "attributedUnitsOrdered14dOtherSKU",
        "attributedUnitsOrdered30dOtherSKU",
        "attributedSales1dOtherSKU",
        "attributedSales7dOtherSKU",
        "attributedSales14dOtherSKU",
        "attributedSales30dOtherSKU",

        # "targetId",  # v2
        # "targetingText",  # v2
        # "targetingType",  # v2
        # "attributedKindleEditionNormalizedPagesRead14d",  # v2
        # "attributedKindleEditionNormalizedPagesRoyalties14d",  # v2
    ],
    "asins_target": [
        "campaignName",
        "campaignId",
        "adGroupName",
        "adGroupId",
        # "keywordId",
        # "keywordText",
        "asin",
        "otherAsin",
        "sku",
        "currency",
        "matchType",
        "attributedUnitsOrdered1d",
        "attributedUnitsOrdered7d",
        "attributedUnitsOrdered14d",
        "attributedUnitsOrdered30d",
        "attributedUnitsOrdered1dOtherSKU",
        "attributedUnitsOrdered7dOtherSKU",
        "attributedUnitsOrdered14dOtherSKU",
        "attributedUnitsOrdered30dOtherSKU",
        "attributedSales1dOtherSKU",
        "attributedSales7dOtherSKU",
        "attributedSales14dOtherSKU",
        "attributedSales30dOtherSKU",

        "targetId",  # v2
        "targetingText",  # v2
        "targetingType",  # v2
        # "attributedKindleEditionNormalizedPagesRead14d",  # v2
        # "attributedKindleEditionNormalizedPagesRoyalties14d",  # v2
    ]
}


# 只有这2种报表类型可以按维度细分
DEFAULT_REPORT_DIMENSIONAL = {
    "keywords": "query",
    "campaigns": "placement"
}


class SpReport(ZADOpenAPI):
    def request(self, record_type, report_date, metrics, segment=None):
        """

        :param record_type: SP报表类型。（用在 URL Parameters）
        :param report_date: 以 YYYYMMDD 格式检索性能报告的日期。
                            时区由用于请求报告的配置文件指定。
                            如果此日期是今天，则指标报告可能包含部分信息。（就是请求当天的数据会不完整）
                            报告不适用于超过 60 天的数据。（用在 Request body）
        :param metrics: 报表下载含哪些字段。（用在 Request body）
        :param segment: 报告的细分纬度。
                        Enum: [query, placement]
                        其中：
                            query，Only works for keywords reports.
                            placement，Only works for campaigns reports.
                        即，DEFAULT_REPORT_DIMENSIONAL 中设置的。（用在 Request body）


        也就是说除了 campaigns, adGroups, keywords, productAds, asins, targets 这6种大类型的报表外，
        还有2种细分报表，即：1、基于 keywords 类型报表，按 query 维度，生成的细分报表。
                        2、基于 campaigns 类型报表，按 placement 维度，生成的细分报表。

        :return:
        """

        # if record_type == 'asins':
        #     path = '/v2/{record_type}/report'.format(record_type=record_type)
        # else:
        #     path = '/v2/sp/{record_type}/report'.format(record_type=record_type)

        # V2版本没有提到区分路径
        path = '/v2/sp/{record_type}/report'.format(record_type=record_type)

        # 文档上描述的
        # [asins] [sku]: Unique SKU advertised. Not available for vendors.
        # [productAds] [sku]: The SKU that is being advertised. Not available for vendors.
        if self._client.account_type == "vendor" and record_type in ["productAds", "asins"]:
            if 'sku' in metrics:
                metrics.remove("sku")

        if isinstance(metrics, (list, tuple)):
            metrics = ','.join(metrics)

        data = {
           'reportDate': report_date,
           'metrics': metrics
        }

        # The type of campaign. Only required for asins report - don't use with other report types.
        if record_type == 'asins':
            data['campaignType'] = 'sponsoredProducts'

        if segment:
            data['segment'] = segment

        # data['stateFilter'] 这个过滤参数不使用

        return self.post(path, data)

    def _get_metrics(self, metrics, default):
        """获取（报表）指标

            即，筛选报表的那些字段需要导出（默认全部导出）
        """

        if not metrics:
            metrics = default

        return metrics

    def campaigns(self, report_date, metrics=None, **kwargs):
        # metrics = self._get_metrics(metrics, DEFAULT_REPORT_METRICS.get('campaigns'))

        metrics = ['campaignName',
                   'campaignId',
                   'campaignStatus',
                   'campaignBudget',
                   'impressions',
                   'clicks',
                   'cost',
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
                   'attributedUnitsOrdered1dSameSKU',
                   'attributedUnitsOrdered7dSameSKU',
                   'attributedUnitsOrdered14dSameSKU',
                   'attributedUnitsOrdered30dSameSKU',
                   'campaignBudgetType',
                   'applicableBudgetRuleId',
                   'applicableBudgetRuleName',
                   'campaignRuleBasedBudget',
                   'currency']

        return self.request('campaigns', report_date, metrics)

    # Exception: Segment '[QUERY]' is not supported for 'campaign' report for specified campaign type(s)
    # def campaigns_query(self, report_date, metrics=None, **kwargs):
    #     metrics = self._get_metrics(metrics, DEFAULT_REPORT_METRICS.get('campaigns'))
    #     return self.request('campaigns', report_date, metrics, segment='query')

    def campaigns_placement(self, report_date, metrics=None, **kwargs):
        metrics = self._get_metrics(metrics, DEFAULT_REPORT_METRICS.get('campaigns'))
        return self.request('campaigns', report_date, metrics, segment='placement')

    def placements(self, report_date, metrics=None, **kwargs):
        """考虑弃用, 由campaigns_placement 替代"""

        segment = DEFAULT_REPORT_DIMENSIONAL.get('campaigns')

        # metrics = self._get_metrics(metrics, DEFAULT_REPORT_METRICS.get('campaigns'))

        metrics = ['campaignName',
                   'campaignId',
                   'campaignStatus',
                   'campaignBudget',
                   'impressions',
                   'clicks',
                   'cost',
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
                   'attributedUnitsOrdered1dSameSKU',
                   'attributedUnitsOrdered7dSameSKU',
                   'attributedUnitsOrdered14dSameSKU',
                   'attributedUnitsOrdered30dSameSKU',
                   'campaignBudgetType',
                   'applicableBudgetRuleId',
                   'applicableBudgetRuleName',
                   'campaignRuleBasedBudget',
                   'bidPlus',
                   'currency']

        return self.request('campaigns', report_date, metrics, segment)

    def ad_groups(self, report_date, metrics=None, **kwargs):
        metrics = self._get_metrics(metrics, DEFAULT_REPORT_METRICS.get('adGroups'))
        return self.request('adGroups', report_date, metrics)

    # Exception: Segment '[QUERY]' is not supported for 'adGroup' report for specified campaign type(s)
    # def ad_groups_query(self, report_date, metrics=None, **kwargs):
    #     metrics = self._get_metrics(metrics, DEFAULT_REPORT_METRICS.get('adGroups'))
    #     return self.request('adGroups', report_date, metrics, segment='query')

    # Exception: Segment '[PLACEMENT]' is not supported for 'adGroup' report for specified campaign type(s)
    # def ad_groups_placement(self, report_date, metrics=None, **kwargs):
    #     metrics = self._get_metrics(metrics, DEFAULT_REPORT_METRICS.get('adGroups'))
    #     return self.request('adGroups', report_date, metrics, segment='placement')

    def keywords(self, report_date, metrics=None, **kwargs):
        # metrics = self._get_metrics(metrics, DEFAULT_REPORT_METRICS.get('keywords'))

        metrics = ['campaignName',
                   'campaignId',
                   'adGroupName',
                   'adGroupId',
                   'keywordId',
                   'keywordText',
                   'matchType',
                   'impressions',
                   'clicks',
                   'cost',
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
                   'attributedUnitsOrdered1dSameSKU',
                   'attributedUnitsOrdered7dSameSKU',
                   'attributedUnitsOrdered14dSameSKU',
                   'attributedUnitsOrdered30dSameSKU',
                   'campaignStatus',
                   'campaignBudget',
                   'campaignBudgetType',
                   'keywordStatus',
                   'keywordBid',
                   'currency']

        return self.request('keywords', report_date, metrics)

    def keywords_query(self, report_date, metrics=None, **kwargs):
        metrics = self._get_metrics(metrics, DEFAULT_REPORT_METRICS.get('keywords'))
        return self.request('keywords', report_date, metrics, segment='query')

    # Exception: Segment '[PLACEMENT]' is not supported for 'keyword' report for specified campaign type(s)
    # def keywords_placement(self, report_date, metrics=None, **kwargs):
    #     metrics = self._get_metrics(metrics, DEFAULT_REPORT_METRICS.get('keywords'))
    #     return self.request('keywords', report_date, metrics, segment='placement')

    def queries(self, report_date, metrics=None, **kwargs):
        """考虑弃用, 由keywords_query 替代"""

        segment = DEFAULT_REPORT_DIMENSIONAL.get('keywords')

        metrics = self._get_metrics(metrics, DEFAULT_REPORT_METRICS.get('keywords'))

        return self.request('keywords', report_date, metrics, segment)

    def product_ads(self, report_date, metrics=None, **kwargs):
        metrics = self._get_metrics(metrics, DEFAULT_REPORT_METRICS.get('productAds'))
        return self.request('productAds', report_date, metrics)

    # Exception: Segment '[QUERY]' is not supported for 'productAd' report for specified campaign type(s)
    # def product_ads_query(self, report_date, metrics=None, **kwargs):
    #     metrics = self._get_metrics(metrics, DEFAULT_REPORT_METRICS.get('productAds'))
    #     return self.request('productAds', report_date, metrics, segment='query')

    # Exception: Segment '[PLACEMENT]' is not supported for 'productAd' report for specified campaign type(s)
    # def product_ads_placement(self, report_date, metrics=None, **kwargs):
    #     metrics = self._get_metrics(metrics, DEFAULT_REPORT_METRICS.get('productAds'))
    #     return self.request('productAds', report_date, metrics, segment='placement')

    def targets(self, report_date, metrics=None, **kwargs):
        # metrics = self._get_metrics(metrics, DEFAULT_REPORT_METRICS.get('targets'))

        metrics = ['campaignName',
                   'campaignId',
                   'adGroupName',
                   'adGroupId',
                   'targetId',
                   'targetingExpression',
                   'targetingText',
                   'targetingType',
                   'impressions',
                   'clicks',
                   'cost',
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
                   'attributedUnitsOrdered1dSameSKU',
                   'attributedUnitsOrdered7dSameSKU',
                   'attributedUnitsOrdered14dSameSKU',
                   'attributedUnitsOrdered30dSameSKU',
                   'campaignStatus',
                   'campaignBudget',
                   'campaignBudgetType']

        return self.request('targets', report_date, metrics)

    def targets_query(self, report_date, metrics=None, **kwargs):
        metrics = self._get_metrics(metrics, DEFAULT_REPORT_METRICS.get('targets'))
        return self.request('targets', report_date, metrics, segment='query')

    # Exception: Segment '[PLACEMENT]' is not supported for 'targets' report for specified campaign type(s)
    # def targets_placement(self, report_date, metrics=None, **kwargs):
    #     metrics = self._get_metrics(metrics, DEFAULT_REPORT_METRICS.get('targets'))
    #     return self.request('targets', report_date, metrics, segment='placement')

    def asins(self, report_date, metrics=None, **kwargs):
        """考虑弃用, 由asins_keyword 替代"""

        metrics = self._get_metrics(metrics, DEFAULT_REPORT_METRICS.get('asins'))
        return self.request('asins', report_date, metrics)

    def asins_keyword(self, report_date, metrics=None, **kwargs):
        metrics = self._get_metrics(metrics, DEFAULT_REPORT_METRICS.get('asins_keyword'))
        return self.request('asins', report_date, metrics)

    # Exception: Segment '[QUERY]' is not supported for 'otherAsin' report for specified campaign type(s)
    # def asins_keyword_query(self, report_date, metrics=None, **kwargs):
    #     metrics = self._get_metrics(metrics, DEFAULT_REPORT_METRICS.get('asins_keyword'))
    #     return self.request('asins', report_date, metrics, segment='query')

    # Exception: Segment '[PLACEMENT]' is not supported for 'otherAsin' report for specified campaign type(s)
    # def asins_keyword_placement(self, report_date, metrics=None, **kwargs):
    #     metrics = self._get_metrics(metrics, DEFAULT_REPORT_METRICS.get('asins_keyword'))
    #     return self.request('asins', report_date, metrics, segment='placement')

    def asins_target(self, report_date, metrics=None, **kwargs):
        metrics = self._get_metrics(metrics, DEFAULT_REPORT_METRICS.get('asins_target'))
        return self.request('asins', report_date, metrics)

    #  Exception: Segment '[QUERY]' is not supported for 'otherAsin' report for specified campaign type(s)
    # def asins_target_query(self, report_date, metrics=None, **kwargs):
    #     metrics = self._get_metrics(metrics, DEFAULT_REPORT_METRICS.get('asins_target'))
    #     return self.request('asins', report_date, metrics, segment='query')

    # Exception: Segment '[PLACEMENT]' is not supported for 'otherAsin' report for specified campaign type(s)
    # def asins_target_placement(self, report_date, metrics=None, **kwargs):
    #     metrics = self._get_metrics(metrics, DEFAULT_REPORT_METRICS.get('asins_target'))
    #     return self.request('asins', report_date, metrics, segment='placement')

    def local_test(self, **kwargs):
        """
        测试用的接口
        """
        path = kwargs.get('path')
        data = kwargs.get('data')
        return self.post(path, data)


# 测试用的数据
LOCAL_TEST_SP_CASE = {
    # MT-EU-IT
    'sp:campaigns': {
        "ad_type": "sp", "record_type": "local_test", "past_days": [1],
        "local_test": {
            "path": "/v2/sp/{record_type}/report".format(record_type='campaigns'),
            "data": {
                "reportDate": "2021-10-20",
                "metrics": ','.join(DEFAULT_REPORT_METRICS['campaigns'])
            }
        }
    }
}


# if __name__ == '__main__':
#     import json
#     print(json.dumps(LOCAL_TEST_SP_CASE['sp:campaigns']))
