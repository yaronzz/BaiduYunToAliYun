#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :  cloudSync.py
@Date    :  2021/07/09
@Author  :  Yaronzz
@Version :  1.0
@Contact :  yaronhuang@foxmail.com
@Desc    :  
'''

import sys
import aigpy
from bypy import ByPy
from io import StringIO
from alipy import ObjectAttr, AliPy


class SyncBdy2Ali(object):
    def __init__(self):
        self.__sysStdout = sys.stdout
        print(aigpy.cmd.green('================Login Bdy==================='))
        self.__bdyHandle = ByPy()
        print(aigpy.cmd.green('================Login Ali==================='))
        self.__aliHandle = AliPy()

    def mapAliPath(self, path: str = '/') -> dict:
        check, pathId = self.__aliHandle.mkdirs(path)
        if not check:
            return []

        array = self.__aliHandle.list(pathId, path)
        names = {}
        for item in array:
            names[item.name] = item
        return names

    def listBdyPath(self, path: str = '/') -> list:
        bdyStdout = StringIO()
        sys.stdout = bdyStdout
        sep = '#&*&#'
        fmt = '$t{}$f{}$s{}$m{}$d'.format(sep, sep, sep, sep)
        check = self.__bdyHandle.list(remotepath=path, fmt=fmt)
        sys.stdout = self.__sysStdout

        if not int(check) == 0:
            return []

        output = bdyStdout.getvalue()
        if len(output) == 0:
            return []

        lines = output.split('\n')
        if len(lines) > 0:
            del lines[0]

        res = []
        for item in lines:
            if len(item) <= 0:
                continue
            objs = item.split(sep)
            attr = ObjectAttr(objs[0] != 'D', objs[1], objs[2], path)
            if not attr.isfile:
                res.append(attr)
            else:
                res.insert(0, attr)
        return res

    def downloadBdyFile(self, remoteObjectAttr: ObjectAttr, downloadPath: str) -> bool:
        srcpath = '{}/{}'.format(remoteObjectAttr.path, remoteObjectAttr.name)
        descdir = '{}/{}'.format(downloadPath, remoteObjectAttr.path)
        descpath = '{}/{}'.format(descdir, remoteObjectAttr.name)

        aigpy.path.mkdirs(descdir)

        bdyStdout = StringIO()
        sys.stdout = bdyStdout
        check = self.__bdyHandle.downfile(srcpath, descpath)
        sys.stdout = self.__sysStdout
        if int(check) == 0:
            return True

        return self.checkLocalExistFile(remoteObjectAttr, downloadPath)

    def checkLocalExistFile(self, remoteObjectAttr: ObjectAttr, downloadPath: str) -> bool:
        descpath = '{}/{}/{}'.format(downloadPath, remoteObjectAttr.path, remoteObjectAttr.name)
        descSize = aigpy.file.getSize(descpath)
        if descSize <= 0:
            return False
        if descSize != remoteObjectAttr.size:
            return False
        return True

    def syncFolder(self, bdyPath='/', aliPath='/', downloadPath='./'):

        bdyArray = self.listBdyPath(bdyPath)
        aliMap = self.mapAliPath(aliPath)

        for item in bdyArray:
            if item.isfile:
                if item.name in aliMap:
                    print(aigpy.cmd.green("Exist:") + item.name)
                    continue

                if not self.checkLocalExistFile(item, downloadPath):
                    print(aigpy.cmd.green("Info:") + "download " + item.name)
                    if not self.downloadBdyFile(item, downloadPath):
                        print(aigpy.cmd.red("Err:") + 'dl failed. ')
                        continue
                    print('')

                localFilePath = '{}/{}/{}'.format(downloadPath, item.path, item.name)
                remoteFilePath = '{}/{}'.format(aliPath, item.name)
                if not self.__aliHandle.uploadLoaclFile(localFilePath, remoteFilePath):
                    print(aigpy.cmd.red("Err:") + 'upload failed. ' + item.name)
                else:
                    print(aigpy.cmd.green("Info:") + 'upload success. ' + item.name)
                    
                aigpy.path.remove(localFilePath)

            else:
                self.syncFolder(bdyPath + '/' + item.name, aliPath + '/' + item.name, downloadPath)
