# -*- coding: utf-8 -*-
# Authored by: Josh (joshzda@gmail.com)
from amazon_ad.core import consts


def get_region(country):
    return dict(consts.COUNTRIES_REGION).get(country, None)

def get_country_endpoint(country, endpoint_type=None):
    region = get_region(country)
    if region is None:
        raise ValueError("country %s is not supported" % country)

    endpoints = consts.REGIONS_ENDPOINTS.get(region)
    if endpoints is None:
        raise ValueError("endpoint %s is not supported" % country)
    if not endpoint_type:
        return endpoints

    return endpoints.get(endpoint_type)

def get_region_endpoint(region, endpoint_type=None):

    endpoints = consts.REGIONS_ENDPOINTS.get(region)
    if endpoints is None:
        raise ValueError("endpoint %s is not supported" % region)
    if not endpoint_type:
        return endpoints

    return endpoints.get(endpoint_type)