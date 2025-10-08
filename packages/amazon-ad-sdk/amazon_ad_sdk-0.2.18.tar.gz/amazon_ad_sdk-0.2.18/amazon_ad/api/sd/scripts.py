# -*- coding: utf-8 -*-


def clean():
    # 页面上直接复制
    text = u"""Report Type	Metric	Tactic	Description
campaigns 	campaignName 	T00020,T00030,remarketing 	The name of the campaign.
campaigns 	campaignId 	T00020,T00030,remarketing 	The identifier of the campaign.
campaigns 	impressions 	T00020,T00030,remarketing 	Total number of ad impressions.
campaigns 	clicks 	T00020,T00030,remarketing 	Total number of ad clicks associated with the campaign.
campaigns 	cost 	T00020,T00030,remarketing 	The total cost of all ad clicks for the campaign. Divide cost by clicks to calculate average cost per click (CPC).
campaigns 	currency 	T00020,T00030,remarketing 	The currency code associated with the campaign.
campaigns 	attributedConversions1d 	T00020,T00030,remarketing 	Total number of attributed conversion events occurring within 24 hours of ad click.
campaigns 	attributedConversions7d 	T00020,T00030,remarketing 	Total number of attributed conversion events occurring within 7 days of ad click.
campaigns 	attributedConversions14d 	T00020,T00030,remarketing 	Total number of attributed conversion events occurring within 14 days of ad click.
campaigns 	attributedConversions30d 	T00020,T00030,remarketing 	Total number of attributed conversion events occurring within 30 days of ad click.
campaigns 	attributedConversions1dSameSKU 	T00020,T00030,remarketing 	Total number of attributed conversion events occurring within 24 hours of ad click, where the SKU of the product advertised and the SKU of the conversion event are equivalent.
campaigns 	attributedConversions7dSameSKU 	T00020,T00030,remarketing 	Total number of attributed conversion events occurring within 7 days of ad click, where the SKU of the product advertised and the SKU of the conversion event are equivalent.
campaigns 	attributedConversions14dSameSKU 	T00020,T00030,remarketing 	Total number of attributed conversion events occurring within 14 days of ad click, where the SKU of the product advertised and the SKU of the conversion event are equivalent.
campaigns 	attributedConversions30dSameSKU 	T00020,T00030,remarketing 	Total number of attributed conversion events occurring within 30 days of ad click, where the SKU of the product advertised and the SKU of the conversion event are equivalent.
campaigns 	attributedUnitsOrdered1d 	T00020,T00030,remarketing 	Total number of attributed units ordered within 24 hours of ad click.
campaigns 	attributedUnitsOrdered7d 	T00020,T00030,remarketing 	Total number of attributed units ordered within 7 days of ad click.
campaigns 	attributedUnitsOrdered14d 	T00020,T00030,remarketing 	Total number of attributed units ordered within 14 days of ad click.
campaigns 	attributedUnitsOrdered30d 	T00020,T00030,remarketing 	Total number of attributed units ordered within 30 days of ad click.
campaigns 	attributedSales1d 	T00020,T00030,remarketing 	Total number of attributed sales occurring within 24 hours of ad click.
campaigns 	attributedSales7d 	T00020,T00030,remarketing 	Total number of attributed sales occurring within 7 days of ad click.
campaigns 	attributedSales14d 	T00020,T00030,remarketing 	Total number of attributed sales occurring within 14 days of ad click.
campaigns 	attributedSales30d 	T00020,T00030,remarketing 	Total number of attributed sales occurring within 30 days of ad click.
campaigns 	attributedSales1dSameSKU 	T00020,T00030,remarketing 	Aggregate value of all attributed sales occurring within 24 hours of ad click, where the SKU of the product advertised and the SKU of the purchased item are equivalent.
campaigns 	attributedSales7dSameSKU 	T00020,T00030,remarketing 	Aggregate value of all attributed sales occurring within 7 days of ad click, where the SKU of the product advertised and the SKU of the purchased item are equivalent.
campaigns 	attributedSales14dSameSKU 	T00020,T00030,remarketing 	Aggregate value of all attributed sales occurring within 14 days of ad click, where the SKU of the product advertised and the SKU of the purchased item are equivalent.
campaigns 	attributedSales30dSameSKU 	T00020,T00030,remarketing 	Aggregate value of all attributed sales occurring within 30 days of ad click, where the SKU of the product advertised and the SKU of the purchased item are equivalent.
campaigns 	attributedOrdersNewToBrand14d 	T00020,T00030 	The number of first-time orders for products within the brand over a one-year lookback window.
campaigns 	attributedSalesNewToBrand14d 	T00020,T00030 	The total sales of new-to-brand orders for products within the brand over a one-year lookback window.
campaigns 	attributedUnitsOrderedNewToBrand14d 	T00020,T00030 	The number of units from first-time orders for products within the brand over a one-year lookback window.
campaigns 	costType 	T00020,T00030 	[NEW] Determines how the campaign will bid and charge.
campaigns 	viewImpressions 	T00020,T00030 	[NEW for 'vCPM' campaigns] Total number of ad viewable impressions.
campaigns 	viewAttributedConversions14d 	T00020,T00030 	[NEW for 'vCPM' campaigns] Total number of attributed conversion events occurring within 14 days of ad click or view.
campaigns 	viewAttributedSales14d 	T00020,T00030 	[NEW for 'vCPM' campaigns] Total number of attributed sales occurring within 14 days of ad click or view.
campaigns 	viewAttributedUnitsOrdered14d 	T00020,T00030 	[NEW for 'vCPM' campaigns] Total number of attributed units ordered occurring within 14 days of ad click or view.
adGroups 	campaignName 	T00020,T00030,remarketing 	The name of the campaign.
adGroups 	campaignId 	T00020,T00030,remarketing 	The identifier of the campaign.
adGroups 	adGroupName 	T00020,T00030,remarketing 	The name of the ad group.
adGroups 	adGroupId 	T00020,T00030,remarketing 	The identifier of the ad group.
adGroups 	impressions 	T00020,T00030,remarketing 	Total number of ad impressions.
adGroups 	clicks 	T00020,T00030,remarketing 	Total number of ad clicks associated with the campaign.
adGroups 	cost 	T00020,T00030,remarketing 	The total cost of all ad clicks for the campaign. Divide cost by clicks to calculate average cost per click (CPC).
adGroups 	currency 	T00020,T00030,remarketing 	The currency code associated with the campaign.
adGroups 	attributedConversions1d 	T00020,T00030,remarketing 	Total number of attributed conversion events occurring within 24 hours of ad click.
adGroups 	attributedConversions7d 	T00020,T00030,remarketing 	Total number of attributed conversion events occurring within 7 days of ad click.
adGroups 	attributedConversions14d 	T00020,T00030,remarketing 	Total number of attributed conversion events occurring within 14 days of ad click.
adGroups 	attributedConversions30d 	T00020,T00030,remarketing 	Total number of attributed conversion events occurring within 30 days of ad click.
adGroups 	attributedConversions1dSameSKU 	T00020,T00030,remarketing 	Total number of attributed conversion events occurring within 24 hours of ad click, where the SKU of the product advertised and the SKU of the conversion event are equivalent.
adGroups 	attributedConversions7dSameSKU 	T00020,T00030,remarketing 	Total number of attributed conversion events occurring within 7 days of ad click, where the SKU of the product advertised and the SKU of the conversion event are equivalent.
adGroups 	attributedConversions14dSameSKU 	T00020,T00030,remarketing 	Total number of attributed conversion events occurring within 14 days of ad click, where the SKU of the product advertised and the SKU of the conversion event are equivalent.
adGroups 	attributedConversions30dSameSKU 	T00020,T00030,remarketing 	Total number of attributed conversion events occurring within 30 days of ad click, where the SKU of the product advertised and the SKU of the conversion event are equivalent.
adGroups 	attributedUnitsOrdered1d 	T00020,T00030,remarketing 	Total number of attributed units ordered within 24 hours of ad click.
adGroups 	attributedUnitsOrdered7d 	T00020,T00030,remarketing 	Total number of attributed units ordered within 7 days of ad click.
adGroups 	attributedUnitsOrdered14d 	T00020,T00030,remarketing 	Total number of attributed units ordered within 14 days of ad click.
adGroups 	attributedUnitsOrdered30d 	T00020,T00030,remarketing 	Total number of attributed units ordered within 30 days of ad click.
adGroups 	attributedSales1d 	T00020,T00030,remarketing 	Total number of attributed sales occurring within 24 hours of ad click.
adGroups 	attributedSales7d 	T00020,T00030,remarketing 	Total number of attributed sales occurring within 7 days of ad click.
adGroups 	attributedSales14d 	T00020,T00030,remarketing 	Total number of attributed sales occurring within 14 days of ad click.
adGroups 	attributedSales30d 	T00020,T00030,remarketing 	Total number of attributed sales occurring within 30 days of ad click.
adGroups 	attributedSales1dSameSKU 	T00020,T00030,remarketing 	Aggregate value of all attributed sales occurring within 24 hours of ad click, where the SKU of the product advertised and the SKU of the purchased item are equivalent.
adGroups 	attributedSales7dSameSKU 	T00020,T00030,remarketing 	Aggregate value of all attributed sales occurring within 7 days of ad click, where the SKU of the product advertised and the SKU of the purchased item are equivalent.
adGroups 	attributedSales14dSameSKU 	T00020,T00030,remarketing 	Aggregate value of all attributed sales occurring within 14 days of ad click, where the SKU of the product advertised and the SKU of the purchased item are equivalent.
adGroups 	attributedSales30dSameSKU 	T00020,T00030,remarketing 	Aggregate value of all attributed sales occurring within 30 days of ad click, where the SKU of the product advertised and the SKU of the purchased item are equivalent.
adGroups 	attributedOrdersNewToBrand14d 	T00020,T00030 	The number of first-time orders for products within the brand over a one-year lookback window.
adGroups 	attributedSalesNewToBrand14d 	T00020,T00030 	The total sales of new-to-brand orders for products within the brand over a one-year lookback window.
adGroups 	attributedUnitsOrderedNewToBrand14d 	T00020,T00030 	The number of units from first-time orders for products within the brand over a one-year lookback window.
adGroups 	bidOptimization 	T00020,T00030 	[NEW for 'vCPM' campaigns] Bid Optimization for the Adgroup. Default behavior is to optimize for 'clicks'.
adGroups 	viewImpressions 	T00020,T00030 	[NEW for 'vCPM' campaigns] Total number of ad viewable impressions.
adGroups 	viewAttributedConversions14d 	T00020,T00030 	[NEW for 'vCPM' campaigns] Total number of attributed conversion events occurring within 14 days of ad click or view.
adGroups 	viewAttributedSales14d 	T00020,T00030 	[NEW for 'vCPM' campaigns] Total number of attributed sales occurring within 14 days of ad click or view.
adGroups 	viewAttributedUnitsOrdered14d 	T00020,T00030 	[NEW for 'vCPM' campaigns] Total number of attributed units ordered occurring within 14 days of ad click or view.
productAds 	campaignName 	T00020,T00030,remarketing 	The name of the campaign.
productAds 	campaignId 	T00020,T00030,remarketing 	The identifier of the campaign.
productAds 	adGroupName 	T00020,T00030,remarketing 	The name of the ad group.
productAds 	adGroupId 	T00020,T00030,remarketing 	The identifier of the ad group.
productAds 	asin 	T00020,T00030,remarketing 	The ASIN of the product.
productAds 	sku 	T00020,T00030,remarketing 	The SKU of the product.
productAds 	adId 	T00020,T00030,remarketing 	The unique numerical ID of the ad.
productAds 	impressions 	T00020,T00030,remarketing 	Total number of ad impressions.
productAds 	clicks 	T00020,T00030,remarketing 	Total number of ad clicks associated with the campaign.
productAds 	cost 	T00020,T00030,remarketing 	The total cost of all ad clicks for the campaign. Divide cost by clicks to calculate average cost per click (CPC).
productAds 	currency 	T00020,T00030,remarketing 	The currency code associated with the campaign.
productAds 	attributedConversions1d 	T00020,T00030,remarketing 	Total number of attributed conversion events occurring within 24 hours of ad click.
productAds 	attributedConversions7d 	T00020,T00030,remarketing 	Total number of attributed conversion events occurring within 7 days of ad click.
productAds 	attributedConversions14d 	T00020,T00030,remarketing 	Total number of attributed conversion events occurring within 14 days of ad click.
productAds 	attributedConversions30d 	T00020,T00030,remarketing 	Total number of attributed conversion events occurring within 30 days of ad click.
productAds 	attributedConversions1dSameSKU 	T00020,T00030,remarketing 	Total number of attributed conversion events occurring within 24 hours of ad click, where the SKU of the product advertised and the SKU of the conversion event are equivalent.
productAds 	attributedConversions7dSameSKU 	T00020,T00030,remarketing 	Total number of attributed conversion events occurring within 7 days of ad click, where the SKU of the product advertised and the SKU of the conversion event are equivalent.
productAds 	attributedConversions14dSameSKU 	T00020,T00030,remarketing 	Total number of attributed conversion events occurring within 14 days of ad click, where the SKU of the product advertised and the SKU of the conversion event are equivalent.
productAds 	attributedConversions30dSameSKU 	T00020,T00030,remarketing 	Total number of attributed conversion events occurring within 30 days of ad click, where the SKU of the product advertised and the SKU of the conversion event are equivalent.
productAds 	attributedUnitsOrdered1d 	T00020,T00030,remarketing 	Total number of attributed units ordered within 24 hours of ad click.
productAds 	attributedUnitsOrdered7d 	T00020,T00030,remarketing 	Total number of attributed units ordered within 7 days of ad click.
productAds 	attributedUnitsOrdered14d 	T00020,T00030,remarketing 	Total number of attributed units ordered within 14 days of ad click.
productAds 	attributedUnitsOrdered30d 	T00020,T00030,remarketing 	Total number of attributed units ordered within 30 days of ad click.
productAds 	attributedSales1d 	T00020,T00030,remarketing 	Total number of attributed sales occurring within 24 hours of ad click.
productAds 	attributedSales7d 	T00020,T00030,remarketing 	Total number of attributed sales occurring within 7 days of ad click.
productAds 	attributedSales14d 	T00020,T00030,remarketing 	Total number of attributed sales occurring within 14 days of ad click.
productAds 	attributedSales30d 	T00020,T00030,remarketing 	Total number of attributed sales occurring within 30 days of ad click.
productAds 	attributedSales1dSameSKU 	T00020,T00030,remarketing 	Aggregate value of all attributed sales occurring within 24 hours of ad click, where the SKU of the product advertised and the SKU of the purchased item are equivalent.
productAds 	attributedSales7dSameSKU 	T00020,T00030,remarketing 	Aggregate value of all attributed sales occurring within 7 days of ad click, where the SKU of the product advertised and the SKU of the purchased item are equivalent.
productAds 	attributedSales14dSameSKU 	T00020,T00030,remarketing 	Aggregate value of all attributed sales occurring within 14 days of ad click, where the SKU of the product advertised and the SKU of the purchased item are equivalent.
productAds 	attributedSales30dSameSKU 	T00020,T00030,remarketing 	Aggregate value of all attributed sales occurring within 30 days of ad click, where the SKU of the product advertised and the SKU of the purchased item are equivalent.
productAds 	attributedOrdersNewToBrand14d 	T00020,T00030 	The number of first-time orders for products within the brand over a one-year lookback window.
productAds 	attributedSalesNewToBrand14d 	T00020,T00030 	The total sales of new-to-brand orders for products within the brand over a one-year lookback window.
productAds 	attributedUnitsOrderedNewToBrand14d 	T00020,T00030 	The number of units from first-time orders for products within the brand over a one-year lookback window.
productAds 	viewImpressions 	T00020,T00030 	[NEW for 'vCPM' campaigns] Total number of ad viewable impressions.
productAds 	viewAttributedConversions14d 	T00020,T00030 	[NEW for 'vCPM' campaigns] Total number of attributed conversion events occurring within 14 days of ad click or view.
productAds 	viewAttributedSales14d 	T00020,T00030 	[NEW for 'vCPM' campaigns] Total number of attributed sales occurring within 14 days of ad click or view.
productAds 	viewAttributedUnitsOrdered14d 	T00020,T00030 	[NEW for 'vCPM' campaigns] Total number of attributed units ordered occurring within 14 days of ad click or view.
targets 	campaignName 	T00020,T00030 	The name of the campaign.
targets 	campaignId 	T00020,T00030 	The identifier of the campaign.
targets 	adGroupName 	T00020,T00030 	The name of the ad group.
targets 	adGroupId 	T00020,T00030 	The identifier of the ad group.
targets 	targetId 	T00020,T00030 	The identifier of the targeting expression used in a bid.
targets 	targetingExpression 	T00020,T00030 	The string representation of your expression object in targeting clauses.
targets 	targetingText 	T00020,T00030 	The resolved string representation of your expression object in targeting clauses.
targets 	targetingType 	T00020,T00030 	The type of match for the targeting expression used in bid. For manually created expressions, this value is TARGETING_EXPRESSION. For auto-targeting expressions this value is TARGETING_EXPRESSION_PREDEFINED.
targets 	impressions 	T00020,T00030 	Total number of ad impressions.
targets 	clicks 	T00020,T00030 	Total number of ad clicks associated with the campaign.
targets 	cost 	T00020,T00030 	The total cost of all ad clicks for the campaign. Divide cost by clicks to calculate average cost per click (CPC).
targets 	currency 	T00020,T00030 	The currency code associated with the campaign.
targets 	attributedConversions1d 	T00020,T00030 	Total number of attributed conversion events occurring within 24 hours of ad click.
targets 	attributedConversions7d 	T00020,T00030 	Total number of attributed conversion events occurring within 7 days of ad click.
targets 	attributedConversions14d 	T00020,T00030 	Total number of attributed conversion events occurring within 14 days of ad click.
targets 	attributedConversions30d 	T00020,T00030 	Total number of attributed conversion events occurring within 30 days of ad click.
targets 	attributedConversions1dSameSKU 	T00020,T00030 	Total number of attributed conversion events occurring within 24 hours of ad click, where the SKU of the product advertised and the SKU of the conversion event are equivalent.
targets 	attributedConversions7dSameSKU 	T00020,T00030 	Total number of attributed conversion events occurring within 7 days of ad click, where the SKU of the product advertised and the SKU of the conversion event are equivalent.
targets 	attributedConversions14dSameSKU 	T00020,T00030 	Total number of attributed conversion events occurring within 14 days of ad click, where the SKU of the product advertised and the SKU of the conversion event are equivalent.
targets 	attributedConversions30dSameSKU 	T00020,T00030 	Total number of attributed conversion events occurring within 30 days of ad click, where the SKU of the product advertised and the SKU of the conversion event are equivalent.
targets 	attributedUnitsOrdered1d 	T00020,T00030 	Total number of attributed units ordered within 24 hours of ad click.
targets 	attributedUnitsOrdered7d 	T00020,T00030 	Total number of attributed units ordered within 7 days of ad click.
targets 	attributedUnitsOrdered14d 	T00020,T00030 	Total number of attributed units ordered within 14 days of ad click.
targets 	attributedUnitsOrdered30d 	T00020,T00030 	Total number of attributed units ordered within 30 days of ad click.
targets 	attributedSales1d 	T00020,T00030 	Total number of attributed sales occurring within 24 hours of ad click.
targets 	attributedSales7d 	T00020,T00030 	Total number of attributed sales occurring within 7 days of ad click.
targets 	attributedSales14d 	T00020,T00030 	Total number of attributed sales occurring within 14 days of ad click.
targets 	attributedSales30d 	T00020,T00030 	Total number of attributed sales occurring within 30 days of ad click.
targets 	attributedSales1dSameSKU 	T00020,T00030 	Aggregate value of all attributed sales occurring within 24 hours of ad click, where the SKU of the product advertised and the SKU of the purchased item are equivalent.
targets 	attributedSales7dSameSKU 	T00020,T00030 	Aggregate value of all attributed sales occurring within 7 days of ad click, where the SKU of the product advertised and the SKU of the purchased item are equivalent.
targets 	attributedSales14dSameSKU 	T00020,T00030 	Aggregate value of all attributed sales occurring within 14 days of ad click, where the SKU of the product advertised and the SKU of the purchased item are equivalent.
targets 	attributedSales30dSameSKU 	T00020,T00030 	Aggregate value of all attributed sales occurring within 30 days of ad click, where the SKU of the product advertised and the SKU of the purchased item are equivalent.
targets 	attributedOrdersNewToBrand14d 	T00020,T00030 	The number of first-time orders for products within the brand over a one-year lookback window.
targets 	attributedSalesNewToBrand14d 	T00020,T00030 	The total sales of new-to-brand orders for products within the brand over a one-year lookback window.
targets 	attributedUnitsOrderedNewToBrand14d 	T00020,T00030 	The number of units from first-time orders for products within the brand over a one-year lookback window.
targets 	viewImpressions 	T00020,T00030 	[NEW for 'vCPM' campaigns] Total number of ad viewable impressions.
targets 	viewAttributedConversions14d 	T00020,T00030 	[NEW for 'vCPM' campaigns] Total number of attributed conversion events occurring within 14 days of ad click or view.
targets 	viewAttributedSales14d 	T00020,T00030 	[NEW for 'vCPM' campaigns] Total number of attributed sales occurring within 14 days of ad click or view.
targets 	viewAttributedUnitsOrdered14d 	T00020,T00030 	[NEW for 'vCPM' campaigns] Total number of attributed units ordered occurring within 14 days of ad click or view.
asins 	campaignName 	T00020,T00030 	The name of the campaign.
asins 	campaignId 	T00020,T00030 	The identifier of the campaign.
asins 	adGroupName 	T00020,T00030 	The name of the ad group.
asins 	adGroupId 	T00020,T00030 	The identifier of the ad group.
asins 	asin 	T00020,T00030 	The ASIN of the product.
asins 	otherAsin 	T00020,T00030 	The ASIN of the product other than the one advertised
asins 	sku 	T00020,T00030 	The SKU of the product.
asins 	currency 	T00020,T00030 	The currency code associated with the campaign.
asins 	attributedUnitsOrdered1dOtherSKU 	T00020,T00030 	Number of other ASIN (SKU) units sold. 1 day.
asins 	attributedUnitsOrdered7dOtherSKU 	T00020,T00030 	Number of other ASIN (SKU) units sold. 7 days.
asins 	attributedUnitsOrdered14dOtherSKU 	T00020,T00030 	Number of other ASIN (SKU) units sold. 14 days.
asins 	attributedUnitsOrdered30dOtherSKU 	T00020,T00030 	Number of other ASIN (SKU) units sold. 30 days.
asins 	attributedSales1dOtherSKU 	T00020,T00030 	Sales for another ASIN (SKU). 1 day.
asins 	attributedSales7dOtherSKU 	T00020,T00030 	Sales for another ASIN (SKU). 7 days.
asins 	attributedSales14dOtherSKU 	T00020,T00030 	Sales for another ASIN (sku). 14 days.
asins 	attributedSales30dOtherSKU 	T00020,T00030 	Sales for another ASIN (sku). 30 days.
campaigns 	campaignName 	T00001 	The name of the campaign.
campaigns 	campaignId 	T00001 	The identifier of the campaign.
campaigns 	campaignStatus 	T00001 	The status of the campaign.
campaigns 	currency 	T00001 	The currency code associated with the campaign.
campaigns 	impressions 	T00001 	Total number of ad impressions.
campaigns 	clicks 	T00001 	Total number of ad clicks associated with the campaign. Divide clicks by impressions to calculate click through rate (CTR).
campaigns 	cost 	T00001 	The total cost of all ad clicks for the campaign. Divide cost by clicks to calculate average cost per click (CPC).
campaigns 	attributedDPV14d 	T00001 	Number of attributed detail page views occurring within 14 days of click on an ad.
campaigns 	attributedUnitsSold14d 	T00001 	Number of attributed units sold occurring within 14 days of click on an ad.
campaigns 	attributedSales14d 	T00001 	Aggregate value of attributed sales occurring within 14 days of click on ad.
"""

    text_list = [i.strip() for i in text.split('\n') if i.strip()]

    keys = [i.strip().replace(' ', '_').lower() for i in text_list[0].split('\t') if i.strip()]
    keys_len = len(keys)

    result = dict()

    others = text_list[1:]
    for index, row in enumerate(others):
        row = [i.strip() for i in row.split('\t') if i.strip()]
        assert len(row) == keys_len
        # print(row)

        tmp = dict(zip(keys, row))
        # print(tmp)

        tactic = tmp['tactic']
        if ',' in tactic:
            tactic = [i.strip() for i in tactic.split(',') if i.strip()]
        else:
            tactic = [tactic]
        tmp['tactic'] = tactic

        print(tmp)
        # {'report_type': 'campaigns', 'metric': 'campaignName', 'tactic': ['T00020', 'T00030', 'remarketing'], 'description': 'The name of the campaign.'}

        report_type = tmp['report_type']
        metric = tmp['metric']
        tactic_list = tmp['tactic']
        description = tmp['description']

        for tactic in tactic_list:
            try:
                result[report_type][tactic].append(metric)
            except KeyError:
                if report_type not in result:
                    result[report_type] = dict()
                    result[report_type][tactic] = [metric]
                else:
                    if tactic not in result[report_type]:
                        result[report_type][tactic] = [metric]
        print(result)
        print('----------------------------------------')

        if index == 200000000:
            break

    return result


if __name__ == '__main__':
    res = clean()
    print(res)
