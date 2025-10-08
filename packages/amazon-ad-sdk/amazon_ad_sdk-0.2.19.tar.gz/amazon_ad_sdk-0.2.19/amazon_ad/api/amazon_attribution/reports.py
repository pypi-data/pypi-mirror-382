# -*- coding: utf-8 -*-
"""
https://advertising.amazon.com/API/docs/en-us/amazon-attribution-prod-3p/#/Reports
"""

from amazon_ad.api.base import ZADOpenAPI


class AttributionReports(ZADOpenAPI):

    def request(self, data: dict):
        path = '/attribution/report'
        return self.post(path, data)

    def products(self, start_date: str, end_date: str, cursor_id: str = None) -> dict:
        """
        :param start_date: "20220525"
        :param end_date: "20220601"
        :param cursor_id: '{"values":[5868519,161600],"page":1,"fields":["campaign_id","day_timestamp"],"version":"V2"}'
        :return:
        """
        data = {
            "reportType": "PRODUCTS",
            "startDate": start_date,
            "endDate": end_date,
            "count": 5000,
            "cursorId": cursor_id
        }
        return self.request(data)

    def performance_campaign(self, start_date: str, end_date: str, cursor_id: str = None) -> dict:
        data = {
            "reportType": "PERFORMANCE",
            "groupBy": "CAMPAIGN",
            "startDate": start_date,
            "endDate": end_date,
            "count": 5000,
            "cursorId": cursor_id
        }
        return self.request(data)

    def performance_adgroup(self, start_date: str, end_date: str, cursor_id: str = None) -> dict:
        data = {
            "reportType": "PERFORMANCE",
            "groupBy": "ADGROUP",
            "startDate": start_date,
            "endDate": end_date,
            "count": 5000,
            "cursorId": cursor_id
        }
        return self.request(data)

    def performance_creative(self, start_date: str, end_date: str, cursor_id: str = None) -> dict:
        data = {
            "reportType": "PERFORMANCE",
            "groupBy": "CREATIVE",
            "startDate": start_date,
            "endDate": end_date,
            "count": 5000,
            "cursorId": cursor_id
        }
        return self.request(data)