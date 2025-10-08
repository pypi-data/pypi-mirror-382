from amazon_ad.api_v3.base import ZADOpenAPIV3


class BillingStatementReport(ZADOpenAPIV3):
    """
    广告发票
    """

    def get_header(self):
        _headers = super(BillingStatementReport, self).get_header()
        _headers['Content-Type'] = 'application/vnd.createbillingstatementsrequest.v1+json'
        return _headers

    def billing_statement(self, start_date: str, end_date: str, format="CSV", locale="en_US"):
        data = {
            "startDate": start_date,
            "endDate": end_date,
            "format": format,
            "locale": locale,
        }
        path = "/billingStatements"
        return self.post(path, data)

    def get_report(self, report_id):
        path = f'/billingStatements/{report_id}'
        return self.get(path)
