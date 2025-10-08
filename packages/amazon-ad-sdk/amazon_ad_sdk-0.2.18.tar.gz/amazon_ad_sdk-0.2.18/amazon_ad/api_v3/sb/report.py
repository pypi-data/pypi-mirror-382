# -*- coding: utf-8 -*-

from amazon_ad.api_v3.base import ZADOpenAPIV3
from amazon_ad.api_v3.adapters import SBCampaignReportsAdapter, SBPlacementReportsAdapter, SBAdGroupReportsAdapter, \
    SBAdReportsAdapter, SBTargetingReportsAdapter, SBSearchTermReportsAdapter, SBPurchasedProductReportsAdapter


class SbReportV3(ZADOpenAPIV3):

    def request(self, data: dict):
        path = "/reporting/reports"
        return self.post(path, data)

    def c_campaign_daily(self, start_date: str, end_date: str):
        data = SBCampaignReportsAdapter(
            group_by=["campaign"], time_unit="DAILY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def c_campaign_summary(self, start_date: str, end_date: str):
        data = SBCampaignReportsAdapter(
            group_by=["campaign"], time_unit="SUMMARY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def cp_campaign_placement_daily(self, start_date: str, end_date: str):
        data = SBPlacementReportsAdapter(
            group_by=["campaignPlacement"], time_unit="DAILY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def cp_campaign_placement_summary(self, start_date: str, end_date: str):
        data = SBPlacementReportsAdapter(
            group_by=["campaignPlacement"], time_unit="SUMMARY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def ag_ad_group_daily(self, start_date: str, end_date: str):
        data = SBAdGroupReportsAdapter(
            group_by=["adGroup"], time_unit="DAILY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def ag_ad_group_summary(self, start_date: str, end_date: str):
        data = SBAdGroupReportsAdapter(
            group_by=["adGroup"], time_unit="SUMMARY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def a_ads_daily(self, start_date: str, end_date: str):
        data = SBAdReportsAdapter(
            group_by=["ads"], time_unit="DAILY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def a_ads_summary(self, start_date: str, end_date: str):
        data = SBAdReportsAdapter(
            group_by=["ads"], time_unit="SUMMARY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def t_targeting_daily(self, start_date: str, end_date: str):
        data = SBTargetingReportsAdapter(
            group_by=["targeting"], time_unit="DAILY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def t_targeting_summary(self, start_date: str, end_date: str):
        data = SBTargetingReportsAdapter(
            group_by=["targeting"], time_unit="SUMMARY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def st_search_term_daily(self, start_date: str, end_date: str):
        data = SBSearchTermReportsAdapter(
            group_by=["searchTerm"], time_unit="DAILY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def st_search_term_summary(self, start_date: str, end_date: str):
        data = SBSearchTermReportsAdapter(
            group_by=["searchTerm"], time_unit="SUMMARY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def purchased_asin_daily(self, start_date: str, end_date: str):
        data = SBPurchasedProductReportsAdapter(
            group_by=["purchasedAsin"], time_unit="DAILY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def purchased_asin_summary(self, start_date: str, end_date: str):
        data = SBPurchasedProductReportsAdapter(
            group_by=["purchasedAsin"], time_unit="SUMMARY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)
