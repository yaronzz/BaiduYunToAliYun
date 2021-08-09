#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  common.py
@Date    :  2021/8/4
@Author  :  Yaronzz
@Version :  1.0
@Contact :  yaronhuang@foxmail.com
@Desc    :
"""
import logging
import os

import aigpy.cmdHelper

_BASE_PATH = os.path.expanduser('~') + '/b2a/'
_LOG_FILE_PATH = f"{_BASE_PATH}b2a.log"

aigpy.cmd.mkdirs(_BASE_PATH)
logging.basicConfig(filename=_LOG_FILE_PATH,
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')


def getBasePath():
    return _BASE_PATH


def printErr(msg):
    aigpy.cmdHelper.printErr(msg)
    logging.error(msg)


def printInfo(msg):
    aigpy.cmdHelper.printInfo(msg)
    logging.info(msg)
