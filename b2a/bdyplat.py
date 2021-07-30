#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  bdyplat.py
@Date    :  2021/06/17
@Author  :  Yaronzz
@Version :  1.0
@Contact :  yaronhuang@foxmail.com
@Desc    :
"""
import aigpy
from baidupcs_py.baidupcs import BaiduPCSApi
from requests import head
from tqdm import *

from b2a.downloader import Downloader
from b2a.platformImp import *


class BdyKey(object):
    def __init__(self):
        super().__init__()
        self.api = None
        self.cookies = ''

    def login(self, cookiesStr: str) -> bool:
        try:
            cookies = dict()
            array = cookiesStr.split(';')
            for item in array:
                values = item.split('=')
                cookies[values[0].strip(' ')] = values[1]
            self.api = BaiduPCSApi(bduss=cookies['BDUSS'], cookies=cookies)
            self.cookies = cookiesStr
            return True
        except:
            return False


class BdyPlat(PlatformImp):
    def __init__(self):
        super().__init__()

    def list(self, remotePath: str, includeSubDir: bool = False) -> List[FileAttr]:
        array = []
        if len(remotePath) <= 0:
            remotePath = '/'
        res = self.key.api.list(remotePath)
        for item in res:
            obj = FileAttr()
            obj.isfile = item.is_file
            obj.name = aigpy.path.getFileName(item.path)
            obj.path = item.path
            obj.size = item.size
            obj.uid = item.fs_id
            array.append(obj)

            if includeSubDir and item.is_dir:
                subarr = self.list(item.path, includeSubDir)
                array.extend(subarr)
        return array

    def downloadFile(self, fileAttr: FileAttr, localFilePath: str) -> bool:
        path = aigpy.path.getDirName(localFilePath)
        name = aigpy.path.getFileName(localFilePath)
        check = aigpy.path.mkdirs(path)

        # stream = self.key.api.file_stream(fileAttr.path)
        # if not stream:
        #     return False
        #
        # curSize = 0
        # totalSize = len(stream)
        # with open(localFilePath, 'wb+') as f:
        #     with tqdm.wrapattr(stream, "read", desc='下载中', miniters=1, total=totalSize, ascii=True) as fs:
        #         while True:
        #             data = fs.read(2097152)
        #             f.write(data)
        #             curSize += len(data)
        #             if curSize >= totalSize:
        #                 break
        #
        # stream.close()
        # return True

        headers = {
            "Cookie ": "; ".join(
                [f"{k}={v if v is not None else ''}" for k, v in self.key.api.cookies.items()]
            ),
            "User-Agent": "netdisk;2.2.51.6;netdisk;10.0.63;PC;android-android",
            "Connection": "Keep-Alive",
        }

        link = self.key.api.download_link(fileAttr.path)
        if not link or len(link) <= 0:
            return False

        dl = Downloader(link, headers, localFilePath, fileAttr.size)
        check = dl.run()
        return check

    def uploadFile(self, localFilePath: str, remoteFilePath: str) -> bool:
        return False

    def downloadLink(self, remoteFilePath: str):
        link = self.key.api.download_link(remoteFilePath)
        return link

    def uploadLink(self, localFilePath: str, remoteFilePath: str):
        return None

    def isFileExist(self, remoteFilePath: str) -> bool:
        return self.key.api.is_file(remoteFilePath)


