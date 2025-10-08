# -*- coding: utf-8 -*-

from amazon_ad.api_v3.base import ZADOpenAPIV3
from amazon_ad.api_v3 import adapters


class SdReportV3(ZADOpenAPIV3):

    def request(self, data: dict):
        path = "/reporting/reports"
        return self.post(path, data)

    def c_campaign_daily(self, start_date: str, end_date: str):
        data = adapters.SDCampaignReportsAdapter(
            group_by=["campaign"], time_unit="DAILY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def c_campaign_summary(self, start_date: str, end_date: str):
        data = adapters.SDCampaignReportsAdapter(
            group_by=["campaign"], time_unit="SUMMARY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def c_matched_target_daily(self, start_date: str, end_date: str):
        data = adapters.SDCampaignReportsAdapter(
            group_by=["matchedTarget"], time_unit="DAILY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def c_matched_target_summary(self, start_date: str, end_date: str):
        data = adapters.SDCampaignReportsAdapter(
            group_by=["matchedTarget"], time_unit="SUMMARY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def c_campaign_matched_target_daily(self, start_date: str, end_date: str):
        data = adapters.SDCampaignReportsAdapter(
            group_by=["campaign", "matchedTarget"], time_unit="DAILY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def c_campaign_matched_target_summary(self, start_date: str, end_date: str):
        data = adapters.SDCampaignReportsAdapter(
            group_by=["campaign", "matchedTarget"], time_unit="SUMMARY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)


    def ag_ad_group_daily(self, start_date: str, end_date: str):
        data = adapters.SDAdGroupReportsAdapter(
            group_by=["adGroup"], time_unit="DAILY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def ag_ad_group_summary(self, start_date: str, end_date: str):
        data = adapters.SDAdGroupReportsAdapter(
            group_by=["adGroup"], time_unit="SUMMARY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def ag_matched_target_daily(self, start_date: str, end_date: str):
        data = adapters.SDAdGroupReportsAdapter(
            group_by=["matchedTarget"], time_unit="DAILY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def ag_matched_target_summary(self, start_date: str, end_date: str):
        data = adapters.SDAdGroupReportsAdapter(
            group_by=["matchedTarget"], time_unit="SUMMARY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def ag_ad_group_matched_target_daily(self, start_date: str, end_date: str):
        data = adapters.SDAdGroupReportsAdapter(
            group_by=["adGroup", "matchedTarget"], time_unit="DAILY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def ag_ad_group_matched_target_summary(self, start_date: str, end_date: str):
        data = adapters.SDAdGroupReportsAdapter(
            group_by=["adGroup", "matchedTarget"], time_unit="SUMMARY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)


    def t_targeting_daily(self, start_date: str, end_date: str):
        data = adapters.SDTargetingReportsAdapter(
            group_by=["targeting"], time_unit="DAILY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def t_targeting_summary(self, start_date: str, end_date: str):
        data = adapters.SDTargetingReportsAdapter(
            group_by=["targeting"], time_unit="SUMMARY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def t_matched_target_daily(self, start_date: str, end_date: str):
        data = adapters.SDTargetingReportsAdapter(
            group_by=["matchedTarget"], time_unit="DAILY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def t_matched_target_summary(self, start_date: str, end_date: str):
        data = adapters.SDTargetingReportsAdapter(
            group_by=["matchedTarget"], time_unit="SUMMARY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def t_targeting_matched_target_daily(self, start_date: str, end_date: str):
        data = adapters.SDTargetingReportsAdapter(
            group_by=["targeting", "matchedTarget"], time_unit="DAILY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def t_targeting_matched_target_summary(self, start_date: str, end_date: str):
        data = adapters.SDTargetingReportsAdapter(
            group_by=["targeting", "matchedTarget"], time_unit="SUMMARY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)


    def ap_advertiser_daily(self, start_date: str, end_date: str):
        data = adapters.SDAdvertisedProductReportsAdapter(
            group_by=["advertiser"], time_unit="DAILY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def ap_advertiser_summary(self, start_date: str, end_date: str):
        data = adapters.SDAdvertisedProductReportsAdapter(
            group_by=["advertiser"], time_unit="SUMMARY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)


    def pp_asin_daily(self, start_date: str, end_date: str):
        data = adapters.SDPurchasedProductReportsAdapter(
            group_by=["asin"], time_unit="DAILY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def pp_asin_summary(self, start_date: str, end_date: str):
        data = adapters.SDPurchasedProductReportsAdapter(
            group_by=["asin"], time_unit="SUMMARY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)


    def gait_campaign_daily(self, start_date: str, end_date: str):
        data = adapters.SDGrossAndInvalidTrafficReportsAdapter(
            group_by=["campaign"], time_unit="DAILY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)

    def gait_campaign_summary(self, start_date: str, end_date: str):
        data = adapters.SDGrossAndInvalidTrafficReportsAdapter(
            group_by=["campaign"], time_unit="SUMMARY", start_date=start_date, end_date=end_date,
        ).get_data_raw()
        return self.request(data)