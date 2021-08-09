#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  trans.py
@Date    :  2021/7/27
@Author  :  Yaronzz
@Version :  1.0
@Contact :  yaronhuang@foxmail.com
@Desc    :
"""
import os

import aigpy

from b2a import AliPlat, BdyPlat
from b2a.common import printInfo, printErr
from b2a.platformImp import FileAttr

_DOWNLOAD_PATH = './b2a/download/'
aigpy.path.mkdirs(_DOWNLOAD_PATH)


class Trans(object):
    def __init__(self, aliplat: AliPlat, bdyPlat: BdyPlat):
        self._aliplat = aliplat
        self._bdyplat = bdyPlat
        self.successCnt = 0
        self.errCnt = 0
        self.skipCnt = 0
        self.index = 0
        self.baseFromPath = ''
        self.baseToPath = ''

    def clearCnt(self):
        self.successCnt = 0
        self.errCnt = 0
        self.skipCnt = 0
        self.index = 0

    def moveFile(self, item: FileAttr):
        self.index += 1

        uploadFilePath = self.baseToPath + item.path[len(self.baseFromPath):]
        if self._aliplat.isFileExist(uploadFilePath):
            self.skipCnt += 1
            printInfo(f"[{self.index}] 跳过文件: {item.path}")
            return True

        printInfo(f"[{self.index}] 迁移文件: {item.path}")
        localFilePath = _DOWNLOAD_PATH + item.path
        if aigpy.file.getSize(localFilePath) <= 0:
            tmpFile = localFilePath + ".tmp"
            check = self._bdyplat.downloadFile(item, tmpFile)
            if not check:
                aigpy.path.remove(tmpFile)
                printErr("[错误] 下载失败!")
                self.errCnt += 1
                return False
            else:
                printInfo("下载成功！")
                os.rename(tmpFile, localFilePath)

        check = self._aliplat.uploadFile(localFilePath, uploadFilePath)
        if not check:
            printErr("[错误] 上传失败!")
            self.errCnt += 1
        else:
            self.successCnt += 1

        aigpy.path.remove(localFilePath)

    def __movePath__(self, fromPath: str):
        array = self._bdyplat.list(fromPath)
        for item in array:
            if item.isfile:
                self.moveFile(item)
        for item in array:
            if not item.isfile:
                self.__movePath__(item.path)

    def setPath(self, fromPath: str, toPath: str):
        self.baseFromPath = fromPath
        self.baseToPath = toPath

    def start(self):
        self.clearCnt()
        self.__movePath__(self.baseFromPath)
        aigpy.path.remove(_DOWNLOAD_PATH)
        printInfo(f"迁移文件：{self.successCnt}；失败：{self.errCnt}；跳过：{self.skipCnt}")
