# -*- coding: utf-8 -*-

import gzip
from io import BytesIO
from amazon_ad.core.utils.text import to_text
from amazon_ad.api_v3.base import ZADOpenAPIV3


class ReportGetV3(ZADOpenAPIV3):

    def get_report(self, report_id):
        """
        Gets a generation status of report by id
        """
        path = f'/reporting/reports/{report_id}'
        return self.get(path)


class ReportDownloadV3(ZADOpenAPIV3):

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
