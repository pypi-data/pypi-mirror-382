# -*- coding: utf-8 -*-
# Authored by: Josh (joshzda@gmail.com)
import gzip
from io import BytesIO
from amazon_ad.core.utils.text import to_text
from amazon_ad.api.base import ZADOpenAPI


class ReportGet(ZADOpenAPI):

    def get_report(self, report_id, ad_type):
        """
        Retrieves a previously requested report identified by the reportId
        """

        if ad_type == 'dsp':
            path = '/dsp/reports/{report_id}'.format(report_id=report_id)
        else:
            path = '/v2/reports/{report_id}'.format(report_id=report_id)
        return self.get(path)


class ReportDownload(ZADOpenAPI):

    @staticmethod
    def handle_download(response, client=None, **kwargs):
        buf = BytesIO(response.content)
        gzip_file = gzip.GzipFile(fileobj=buf)
        content = to_text(gzip_file.read())
        return content

    def download_report(self, url):
        """
        Downloading reports
        :param url:
        :return:
        """
        return self.download(url, response_processor=self.handle_download)