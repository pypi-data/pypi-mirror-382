# -*- coding: utf-8 -*-

import requests

from amazon_ad.api.profiles import Profiles
from amazon_ad.client.base import BaseClient
from amazon_ad.core import exceptions
from amazon_ad.core.utils.amazon import get_country_endpoint, get_region_endpoint, get_region
from amazon_ad.api.report import ReportGet, ReportDownload
from amazon_ad.api.sb.report import SbReport
from amazon_ad.api.sp.report import SpReport
from amazon_ad.api.sd.report import SdReport
from amazon_ad.api.dsp.report import DspReport
from amazon_ad.api.sb.campaigns import SbCampaigns
from amazon_ad.api.amazon_attribution.reports import AttributionReports
from amazon_ad.api.amazon_attribution.advertisers import AttributionAdvertisers
from amazon_ad.api.amazon_attribution.publishers import AttributionPublishers

from amazon_ad.api_v3.report import ReportGetV3, ReportDownloadV3
from amazon_ad.api_v3.sp.report import SpReportV3
from amazon_ad.api_v3.sb.report import SbReportV3
from amazon_ad.api_v3.sd.report import SdReportV3
from amazon_ad.api_v3.billing.report import BillingStatementReport


class ZADApiClient(BaseClient):
    API_BASE_URL = 'https://advertising-api-test.amazon.com'

    def __init__(self, client_id,  access_token, profile_id=None, region="NA", account_type=None, prepare_mode=False, timeout=None, auto_retry=True, *args, **kwargs):
        super(ZADApiClient, self).__init__(prepare_mode, timeout, auto_retry, *args, **kwargs)
        self.client_id = client_id
        self.access_token = access_token
        self.region = region
        self.profile_id = profile_id
        self.account_type = account_type

    def get_api_base_url(self):
        return get_region_endpoint(self.region, 'API')

    def _check_request_response(self, response, url, method, **kwargs):
        try:
            response.raise_for_status()
        except requests.Timeout as req_ex:
            self._log_request_error(req_ex, url, method, **kwargs)
            raise exceptions.ZADClientTimeoutException(
                message=None,
                client=self,
                request=req_ex.request,
                response=req_ex.response
            )
        except requests.HTTPError as req_ex:
            self._log_request_error(req_ex, url, method, **kwargs)
            if response.status_code == 401:
                raise exceptions.ZADClientAccessException(
                    message=response.content,
                    client=self,
                    request=req_ex.request,
                    response=req_ex.response
                )

            raise exceptions.ZADClientException(
                message=response.content,
                client=self,
                request=req_ex.request,
                response=req_ex.response
            )
        except requests.RequestException as req_ex:
            self._log_request_error(req_ex, url, method, **kwargs)
            raise exceptions.ZADClientException(
                message=None,
                client=self,
                request=req_ex.request,
                response=req_ex.response
            )


class ZADProfileClient(ZADApiClient):
    profiles = Profiles()

    def __init__(self, client_id,  access_token, region="NA", prepare_mode=False, timeout=(10, 10), auto_retry=True, *args, **kwargs):
        super(ZADProfileClient, self).__init__(client_id,  access_token, None, region, None, prepare_mode, timeout, auto_retry, *args, **kwargs)


class ZADServiceClient(ZADApiClient):
    report_get = ReportGet()
    report_download = ReportDownload()
    sp_report = SpReport()
    sb_report = SbReport()
    sd_report = SdReport()
    dsp_report = DspReport()

    sb_campaigns = SbCampaigns()

    # 接口类都放这里
    api_map = {
        'sb:campaigns:get': SbCampaigns().get_campaigns
    }

    # Amazon Attribution beta
    attribution_report = AttributionReports()
    attribution_advertisers = AttributionAdvertisers()
    attribution_publishers = AttributionPublishers()

    def __init__(self, client_id,  access_token, profile_id, country="US", account_type='seller', prepare_mode=False, timeout=(30, 300), auto_retry=True, *args, **kwargs):
        region = get_region(country)
        super(ZADServiceClient, self).__init__(client_id,  access_token, profile_id, region, account_type, prepare_mode, timeout, auto_retry, *args, **kwargs)
        self.country = country


class ZADServiceClientV3(ZADApiClient):
    """
    Version 3
    """
    report_get = ReportGetV3()
    report_download = ReportDownloadV3()
    sp_report = SpReportV3()
    sb_report = SbReportV3()
    sd_report = SdReportV3()

    # 广告发票
    billing = BillingStatementReport()

    def __init__(self, client_id,  access_token, profile_id, country="US", account_type='seller', prepare_mode=False, timeout=(30, 300), auto_retry=True, *args, **kwargs):
        region = get_region(country)
        super(ZADServiceClientV3, self).__init__(client_id,  access_token, profile_id, region, account_type, prepare_mode, timeout, auto_retry, *args, **kwargs)
        self.country = country
