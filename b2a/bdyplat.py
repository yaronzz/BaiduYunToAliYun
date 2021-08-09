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
# from common.io import RangeRequestIO
from baidupcs_py.common.io import RangeRequestIO

from b2a.common import printErr
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

    def fileStream(self, url: str):
        headers = {
            "Cookie": "; ".join(
                [f"{k}={v if v is not None else ''}" for k, v in self.api.cookies.items()]
            ),
            "User-Agent": "netdisk;2.2.51.6;netdisk;10.0.63;PC;android-android",
            "Connection": "Keep-Alive",
        }
        return RangeRequestIO(
            'GET',
            url,
            headers=headers,
            max_chunk_size=10 * 1024 * 1024,
            callback=None,
            encrypt_password=b"",
        )


class BdyPlat(PlatformImp):
    def __init__(self):
        super().__init__()

    def __safeAPI__(self, method, para):
        retry = 10
        while retry > 0:
            try:
                if method == 'list':
                    return self.key.api.list(para)
                elif method == 'download_link':
                    return self.key.api.download_link(para)
                elif method == 'is_file':
                    return self.key.api.is_file(para)
                elif method == 'file_stream':
                    return self.key.api.file_stream(para)
            except:
                printErr("重新尝试获取：BdyPlat " + method)
                retry -= 1
        return None

    def list(self, remotePath: str, includeSubDir: bool = False) -> List[FileAttr]:
        array = []
        if len(remotePath) <= 0:
            remotePath = '/'

        res = self.__safeAPI__('list', remotePath)
        for item in res:
            obj = FileAttr()
            obj.isfile = item.is_file
            obj.name = aigpy.path.getFileName(item.path)
            obj.path = item.path
            obj.size = item.size
            obj.uid = item.fs_id
            array.append(obj)

            if includeSubDir and item.is_dir:
                subList = self.list(item.path, includeSubDir)
                array.extend(subList)
        return array

    def downloadFile(self, fileAttr: FileAttr, localFilePath: str) -> bool:
        path = aigpy.path.getDirName(localFilePath)
        name = aigpy.path.getFileName(localFilePath)
        check = aigpy.path.mkdirs(path)

        # stream = self.__safeAPI__('file_stream', fileAttr.path)
        # if not stream:
        #     return False
        #
        # curSize = 0
        # part = 1024 * 1024 * 1
        # totalSize = len(stream)
        # with open(localFilePath, 'wb+') as f:
        #     with tqdm.wrapattr(stream, "read", desc='下载中', miniters=1, total=totalSize, ascii=True) as fs:
        #         while True:
        #             data = fs.read(part)
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

        link = self.__safeAPI__('download_link', fileAttr.path)
        if not link or len(link) <= 0:
            return False

        dl = Downloader(link, headers, localFilePath, fileAttr.size, 6)
        check = dl.run()
        return check

    def uploadFile(self, localFilePath: str, remoteFilePath: str) -> bool:
        return False

    def downloadLink(self, remoteFilePath: str):
        link = self.__safeAPI__('download_link', remoteFilePath)
        return link

    def uploadLink(self, localFilePath: str, remoteFilePath: str):
        return None

    def isFileExist(self, remoteFilePath: str) -> bool:
        return self.__safeAPI__('is_file', remoteFilePath)


