#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  config.py
@Date    :  2021/7/27
@Author  :  Yaronzz
@Version :  1.0
@Contact :  yaronhuang@foxmail.com
@Desc    :
"""
import json
import os

import aigpy

from b2a.common import getBasePath

_CONFIG_FILE_PATH = f"{getBasePath()}auth.json"
_ALI_KEY = "ali-refresh_token"
_BDY_KEY = "bdy-cookies"
_DLPATH_KEY = "dl-path"


class B2aConfig(object):
    def __init__(self):
        aigpy.path.mkdirs(getBasePath())
        self.aliKey = ""
        self.bdyKey = ""
        self.path = ""
        self.load()

    def load(self):
        authJson = aigpy.file.getJson(_CONFIG_FILE_PATH)
        self.aliKey = authJson.get(_ALI_KEY)
        self.bdyKey = authJson.get(_BDY_KEY)
        self.path = authJson.get(_DLPATH_KEY)

    def save(self) -> bool:
        content = dict()
        content[_ALI_KEY] = self.aliKey
        content[_BDY_KEY] = self.bdyKey
        content[_DLPATH_KEY] = self.path
        if not aigpy.file.write(_CONFIG_FILE_PATH, json.dumps(content), 'w+'):
            return False
        return True
