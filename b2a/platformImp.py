#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  platformImp.py
@Date    :  2021/06/17
@Author  :  Yaronzz
@Version :  1.0
@Contact :  yaronhuang@foxmail.com
@Desc    :
"""
import abc
from typing import List


class FileAttr(object):
    def __init__(self, isfile=False, name='', size=0, path='', uid=''):
        self.isfile = isfile
        self.name = name
        self.size = int(size)
        self.path = path
        self.uid = uid


class PlatformImp(metaclass=abc.ABCMeta):
    def __init__(self):
        self.key = None

    def hasKey(self) -> bool:
        return self.key is not None

    def setKey(self, key):
        self.key = key

    @abc.abstractmethod
    def list(self, remotePath: str) -> List[FileAttr]:
        pass

    @abc.abstractmethod
    def isFileExist(self, remoteFilePath: str) -> bool:
        pass

    @abc.abstractmethod
    def downloadFile(self, fileAttr: FileAttr, localFilePath: str) -> bool:
        pass

    @abc.abstractmethod
    def uploadFile(self, localFilePath: str, remoteFilePath: str) -> bool:
        pass

    @abc.abstractmethod
    def downloadLink(self, remoteFilePath: str):
        pass
    
    @abc.abstractmethod
    def uploadLink(self, localFilePath: str, remoteFilePath: str):
        pass
