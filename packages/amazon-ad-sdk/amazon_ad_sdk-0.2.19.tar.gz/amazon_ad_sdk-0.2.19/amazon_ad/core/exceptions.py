# -*- coding: utf-8 -*-
# Authored by: Josh (joshzda@gmail.com)

from __future__ import absolute_import, unicode_literals

import six

from amazon_ad.core.utils.text import to_binary, to_text


class ZADException(Exception):

    def __init__(self, errcode, errmsg):
        """
        :param errcode: Error code
        :param errmsg: Error message
        """
        self.errcode = errcode
        self.errmsg = errmsg

    def __str__(self):
        _repr = 'Error code: {code}, message: {msg}'.format(
            code=self.errcode,
            msg=self.errmsg
        )

        if six.PY2:
            return to_binary(_repr)
        else:
            return to_text(_repr)

    def __repr__(self):
        _repr = '{klass}({code}, {msg})'.format(
            klass=self.__class__.__name__,
            code=self.errcode,
            msg=self.errmsg
        )
        if six.PY2:
            return to_binary(_repr)
        else:
            return to_text(_repr)


class InvalidSignatureException(ZADException):
    """Invalid signature exception class"""

    def __init__(self, errcode=10001, errmsg='Invalid signature'):
        super(InvalidSignatureException, self).__init__(errcode, errmsg)


class ParamTypeError(ZADException):
    def __init__(self, param_name, param_type):
        errcode = 10002
        errmsg = '%s should be %s' % (param_name, param_type)
        super(ParamTypeError, self).__init__(errcode, errmsg)


class ZADClientException(ZADException):
    """Amazon Advertising API client exception class"""
    errcode = 21001

    def __init__(self, message, client=None,
                 request=None, response=None):
        errcode = self.errcode
        errmsg = '%s' % message
        super(ZADClientException, self).__init__(errcode, errmsg)
        self.client = client
        self.request = request
        self.response = response


class ZADClientTimeoutException(ZADClientException):
    """连接超时"""
    errcode = 20001


class ZADClientAccessException(ZADClientException):
    """Amazon Advertising API 权限错误"""
    errcode = 20002
