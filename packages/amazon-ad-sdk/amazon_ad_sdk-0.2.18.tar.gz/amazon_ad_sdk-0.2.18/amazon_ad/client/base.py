# -*- coding: utf-8 -*-
# Authored by: Josh (joshzda@gmail.com)
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
import inspect
import json
import logging
from urllib.parse import urljoin

import requests

from amazon_ad.core import exceptions
from amazon_ad.api.base import ZADBaseAPI
from amazon_ad.core.utils.serialize import json_loads

logger = logging.getLogger('zad')


class BaseClient(object):
    _http = requests.Session()

    API_BASE_URL = None

    def __new__(cls, *args, **kwargs):
        self = super(BaseClient, cls).__new__(cls)
        api_endpoints = inspect.getmembers(self, cls._is_api_endpoint)
        for name, api in api_endpoints:
            api_cls = type(api)
            api = api_cls(self)
            setattr(self, name, api)
        return self

    def __init__(self, prepare_mode=False, timeout=None, auto_retry=True, *args, **kwargs):
        self.prepare_mode = prepare_mode
        self.timeout = timeout
        self.auto_retry = auto_retry
        self._http = requests.Session()

    def get_api_base_url(self):
        return self.API_BASE_URL

    @staticmethod
    def _is_api_endpoint(obj):
        return isinstance(obj, ZADBaseAPI)

    def _prepare_request(self, method, url_or_endpoint, kwargs):
        api_base_url = kwargs.pop('api_base_url', self.get_api_base_url())
        if not url_or_endpoint.startswith(('http://', 'https://')):
            url = urljoin(api_base_url, url_or_endpoint)
        else:
            url = url_or_endpoint

        if 'params' not in kwargs:
            kwargs['params'] = {}
        if isinstance(kwargs.get('data', ''), dict):
            body = json.dumps(kwargs['data'], ensure_ascii=False)
            body = body.encode('utf-8')
            kwargs['data'] = body
            if 'headers' not in kwargs:
                kwargs['headers'] = {}

            # reporting version3 POST 'application/vnd.createasyncreportrequest.v3+json'
            if not kwargs['headers'].get('Content-Type'):
                kwargs['headers']['Content-Type'] = 'application/json'

        kwargs['timeout'] = kwargs.get('timeout', self.timeout)
        response_processor = kwargs.pop('response_processor', None)
        result_processor = kwargs.pop('result_processor', None)
        top_response_key = kwargs.pop('top_response_key', None)

        return method, url, kwargs, response_processor, result_processor, top_response_key

    def _request(self, method, url_or_endpoint, **kwargs):
        method, url, kwargs, response_processor, result_processor, top_response_key = self._prepare_request(method,
                                                                                                            url_or_endpoint,
                                                                                                            kwargs)
        res = self._http.request(
            method=method,
            url=url,
            **kwargs
        )

        self._check_request_response(res, url, method, **kwargs)

        result = self._handle_result(
            res, method, url, result_processor, top_response_key, response_processor, **kwargs
        )

        logger.debug(u"\n【请求地址】: %s\n【请求方法】: %s\n【请求参数】：%s \n%s\n【响应数据】：%s",
                     url, method, kwargs.get('params', ''), kwargs.get('data', ''), result)
        return result

    def _check_request_response(self, response, url, method, **kwargs):
        try:
            response.raise_for_status()
        except requests.RequestException as req_ex:
            self._log_request_error(req_ex, url, method, **kwargs)
            raise exceptions.ZADClientException(
                message=None,
                client=self,
                request=req_ex.request,
                response=req_ex.response
            )

    def _log_request_error(self, req_ex, url, method, **kwargs):
        logger.error("\n【请求地址】: %s\n【请求方法】: %s\n【请求参数】：%s \n%s\n【异常信息】：%s",
                     url, method, kwargs.get('params', ''), kwargs.get('data', ''), req_ex)

    def _decode_result(self, res):
        try:
            result = json_loads(res.content.decode('utf-8', 'ignore'), strict=False)
        except (TypeError, ValueError):
            # Return origin response object if we can not decode it as JSON
            logger.debug('Can not decode response as JSON', exc_info=True)
            return res
        return result

    def _top_result_processor(self, res, result, **kwargs):
        # 在此可以做接口业务的结果判断处理
        # if 'error_response' in result:
        #     error_response = result['error_response']
        #     logger.error("\n【请求地址】: %s\n【请求方法】: %s\n【请求参数】：%s \n%s\n【错误信息】：%s",
        #                  res.url, res.request.method, kwargs.get('params', ''), kwargs.get('data', ''), result)
        #     raise exceptions.ZADClientException(
        #         error_response.get('code', -1),
        #         error_response.get('sub_msg', ''),
        #         client=self,
        #         request=res.request,
        #         response=res
        #     )
        return result

    def _handle_result(self, res, method=None, url=None, result_processor=None, top_result_processor=None,
                       response_processor=None, **kwargs):

        if response_processor:
            return response_processor(response=res, client=self, **kwargs)

        if not isinstance(res, dict):
            result = self._decode_result(res)
        else:
            result = res

        if not isinstance(result, dict):
            return result

        if top_result_processor:
            result = top_result_processor(res, result, **kwargs)
        else:
            result = self._top_result_processor(res, result, **kwargs)

        return result if not result_processor else result_processor(result, response=res, client=self, **kwargs)

    def _handle_pre_request(self, method, uri, kwargs):
        return method, uri, kwargs

    def _handle_request_except(self, e, func, *args, **kwargs):
        raise e

    def request(self, method, uri, **kwargs):
        method, uri, kwargs = self._handle_pre_request(method, uri, kwargs)
        if self.prepare_mode:
            method, url, kwargs, response_processor, result_processor, top_response_key = self._prepare_request(method, uri, kwargs)
            return {
                'method':method,
                'url':url,
                'kwargs': kwargs,
            }
        try:
            return self._request(method, uri, **kwargs)
        except exceptions.ZADClientException as e:
            return self._handle_request_except(e, self.request, method, uri, **kwargs)

    def get(self, uri, params=None, **kwargs):
        """
        get 接口请求

        :param uri: 请求url
        :param params: get 参数（dict 格式）
        """
        if params is not None:
            kwargs['params'] = params
        return self.request('GET', uri, **kwargs)

    def post(self, uri, data=None, params=None, **kwargs):
        """
        post 接口请求

        :param uri: 请求url
        :param data: post 数据（dict 格式会自动转换为json）
        :param params: post接口中url问号后参数（dict 格式）
        """
        if data is not None:
            kwargs['data'] = data
        if params is not None:
            kwargs['params'] = params
        return self.request('POST', uri, **kwargs)

    def put(self, uri, data=None, params=None, **kwargs):
        """
        post 接口请求

        :param uri: 请求url
        :param data: post 数据（dict 格式会自动转换为json）
        :param params: put接口中url问号后参数（dict 格式）
        """
        if data is not None:
            kwargs['data'] = data
        if params is not None:
            kwargs['params'] = params
        return self.request('PUT', uri, **kwargs)
