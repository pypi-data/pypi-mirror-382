# -*- coding: utf-8 -*-
# Authored by: Josh (joshzda@gmail.com)

from __future__ import absolute_import, unicode_literals

import json


class ObjectDict(dict):
    """Makes a dictionary behave like an object, with attribute-style access.
    """

    def __getattr__(self, key):
        if key in self:
            return self[key]
        return None

    def __setattr__(self, key, value):
        self[key] = value



def json_loads(s, object_hook=ObjectDict, **kwargs):
    return json.loads(s, object_hook=object_hook, **kwargs)