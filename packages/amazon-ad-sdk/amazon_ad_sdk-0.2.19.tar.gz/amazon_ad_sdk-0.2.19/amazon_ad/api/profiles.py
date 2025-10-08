# -*- coding: utf-8 -*-
# Authored by: Josh (joshzda@gmail.com)
from amazon_ad.api.base import ZADOpenAPI


class Profiles(ZADOpenAPI):
    api_path = '/v2/profiles'

    def list(self):
        """
        Get profile list
        :return:
        [{'profileId': 4358504360586791, 'countryCode': 'US', 'currencyCode': 'USD', 'dailyBudget': 0.0, 'timezone': 'America/Los_Angeles', 'accountInfo': {'marketplaceStringId': 'ATVPDKIKX0DER', 'id': 'AE48L746A830O', 'type': 'seller'}}, {'profileId': 1698667544300378, 'countryCode': 'CA', 'currencyCode': 'CAD', 'dailyBudget': 0.0, 'timezone': 'America/Los_Angeles', 'accountInfo': {'marketplaceStringId': 'A2EUQ1WTGCTBG2', 'id': 'AE48L746A830O', 'type': 'seller'}}]
        """
        path = self.api_path
        return self.get(path)

    def update(self, data):
        path = self.api_path
        return self.put(path, data)

    def retrieve(self, pk):
        """
        Get profile
        :param pk:
        :return:
        {'profileId': 4358504360586791, 'countryCode': 'US', 'currencyCode': 'USD', 'dailyBudget': 0.0, 'timezone': 'America/Los_Angeles', 'accountInfo': {'marketplaceStringId': 'ATVPDKIKX0DER', 'id': 'AE48L746A830O', 'type': 'seller'}}
        """
        path = "{api_path}/{pk}".format(api_path=self.api_path, pk=pk)
        return self.get(path)
