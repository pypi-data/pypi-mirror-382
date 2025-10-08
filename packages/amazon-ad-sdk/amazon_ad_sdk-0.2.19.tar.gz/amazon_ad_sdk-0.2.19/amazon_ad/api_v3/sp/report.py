# -*- coding: utf-8 -*-

from amazon_ad.api_v3.base import ZADOpenAPIV3
from amazon_ad.api_v3.adapters import SPCampaignReportsAdapter, SPTargetingReportsAdapter, SPSearchTermReportsAdapter, \
    SPAdvertisedProductReportsAdapter, SPPurchasedProductReportsAdapter


class SpReportV3(ZADOpenAPIV3):

    def request(self, data: dict):
        path = "/reporting/reports"
        return self.post(path, data)

    def campaign_daily(self, start_date: str, end_date: str):
        data = SPCampaignReportsAdapter(
            group_by=["campaign"], time_unit="DAILY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def campaign_summary(self, start_date: str, end_date: str):
        data = SPCampaignReportsAdapter(
            group_by=["campaign"], time_unit="SUMMARY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def ad_group_daily(self, start_date: str, end_date: str):
        data = SPCampaignReportsAdapter(
            group_by=["adGroup"], time_unit="DAILY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def ad_group_summary(self, start_date: str, end_date: str):
        data = SPCampaignReportsAdapter(
            group_by=["adGroup"], time_unit="SUMMARY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def campaign_placement_daily(self, start_date: str, end_date: str):
        data = SPCampaignReportsAdapter(
            group_by=["campaignPlacement"], time_unit="DAILY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def campaign_placement_summary(self, start_date: str, end_date: str):
        data = SPCampaignReportsAdapter(
            group_by=["campaignPlacement"], time_unit="SUMMARY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def campaign_ad_group_daily(self, start_date: str, end_date: str):
        data = SPCampaignReportsAdapter(
            group_by=["campaign", "adGroup"], time_unit="DAILY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def campaign_ad_group_summary(self, start_date: str, end_date: str):
        data = SPCampaignReportsAdapter(
            group_by=["campaign", "adGroup"], time_unit="SUMMARY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def campaign_campaign_placement_daily(self, start_date: str, end_date: str):
        data = SPCampaignReportsAdapter(
            group_by=["campaign", "campaignPlacement"], time_unit="DAILY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def campaign_campaign_placement_summary(self, start_date: str, end_date: str):
        data = SPCampaignReportsAdapter(
            group_by=["campaign", "campaignPlacement"], time_unit="SUMMARY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def targeting_daily(self, start_date: str, end_date: str):
        data = SPTargetingReportsAdapter(
            group_by=["targeting"], time_unit="DAILY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def targeting_summary(self, start_date: str, end_date: str):
        data = SPTargetingReportsAdapter(
            group_by=["targeting"], time_unit="SUMMARY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def search_term_daily(self, start_date: str, end_date: str):
        data = SPSearchTermReportsAdapter(
            group_by=["searchTerm"], time_unit="DAILY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def search_term_summary(self, start_date: str, end_date: str):
        data = SPSearchTermReportsAdapter(
            group_by=["searchTerm"], time_unit="SUMMARY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def advertiser_daily(self, start_date: str, end_date: str):
        data = SPAdvertisedProductReportsAdapter(
            group_by=["advertiser"], time_unit="DAILY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def advertiser_summary(self, start_date: str, end_date: str):
        data = SPAdvertisedProductReportsAdapter(
            group_by=["advertiser"], time_unit="SUMMARY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def asin_daily(self, start_date: str, end_date: str):
        data = SPPurchasedProductReportsAdapter(
            group_by=["asin"], time_unit="DAILY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def asin_summary(self, start_date: str, end_date: str):
        data = SPPurchasedProductReportsAdapter(
            group_by=["asin"], time_unit="SUMMARY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def campaign_placement_b2b_daily(self, start_date: str, end_date: str):
        data = SPCampaignReportsAdapter(
            group_by=["campaignPlacement"], time_unit="DAILY", start_date=start_date, end_date=end_date,
        ).get_data_raw()

        columns = data['configuration']['columns']
        columns += [
            'campaignId',
            'campaignName', 'campaignStatus', 'campaignBudgetAmount', 'campaignBudgetType', 'campaignRuleBasedBudgetAmount',
            'campaignApplicableBudgetRuleId', 'campaignApplicableBudgetRuleName', 'campaignBudgetCurrencyCode'
        ]
        data['configuration']['columns'] = columns

        data['configuration']['filters'] = [
            {
                "field": "campaignSite",
                "values": ["AmazonBusiness"],
                "include": True
            },
        ]
        return self.request(data)
