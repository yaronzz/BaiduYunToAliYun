#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :  main.py
@Date    :  2021/07/08
@Author  :  Yaronzz
@Version :  1.0
@Contact :  yaronhuang@foxmail.com
@Desc    :  
'''
import sys
import aigpy
from bypy import ByPy
from io import StringIO
from cloudSync import SyncBdy2Ali


sync = SyncBdy2Ali()
sync.syncFolder('/','/','./download')

