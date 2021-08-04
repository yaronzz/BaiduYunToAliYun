#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  downloader.py
@Date    :  2021/7/29
@Author  :  Yaronzz
@Version :  1.0
@Contact :  yaronhuang@foxmail.com
@Desc    :
"""
from concurrent.futures import ThreadPoolExecutor, wait

import aigpy.cmdHelper
from baidupcs_py.common.io import RangeRequestIO
from tqdm import tqdm

from b2a.common import printErr


class Downloader(object):
    def __init__(self, url, headers, filePath, size, threadNum=6):
        self.url = url
        self.threadNum = threadNum
        self.filePath = filePath
        self.size = size

        self._pool = ThreadPoolExecutor(max_workers=self.threadNum)
        self._error = False
        self._headers = headers
        self._bar = tqdm(total=self.size, desc="下载中", unit_scale=True)
        self._readSize = 1024 * 1024 * 1

    def __getStream__(self, start):
        stream = RangeRequestIO('GET',
                                self.url,
                                headers=self._headers,
                                max_chunk_size=10 * 1024 * 1024,
                                callback=None,
                                encrypt_password=b"")
        stream.seek(start)
        return stream

    def __createFile__(self):
        try:
            fp = open(self.filePath, "wb")
            fp.truncate(self.size)
            fp.close()
            return True
        except Exception as e:
            printErr("创建文件失败：" + str(e))
            return False

    def __getParts__(self):
        parts = []
        partSize = self.size // self.threadNum
        for i in range(self.threadNum):
            start = partSize * i
            if i == self.threadNum - 1:
                end = self.size
            else:
                end = start + partSize

            parts.append([start, end])
        return parts

    def down(self, start, end):
        try:
            r = self.__getStream__(start)

            size = end - start
            with open(self.filePath, "wb") as fp:
                fp.seek(start)
                while not self._error:
                    part = min(self._readSize, size)
                    data = r.read(part)
                    fp.write(data)
                    self._bar.update(part)

                    size -= part
                    if self._error:
                        break
                    if size <= 0:
                        break
            r.close()
        except Exception as e:
            printErr("下载文件块失败：" + str(e))
            self._error = True

    def run(self):
        try:
            if not self.__createFile__():
                return False

            futures = []
            parts = self.__getParts__()
            for item in parts:
                futures.append(self._pool.submit(self.down, item[0], item[1]))

            wait(futures)
            self._bar.close()
            return not self._error

        except Exception as e:
            aigpy.cmdHelper.printErr("下载失败：" + str(e))
            self._error = True
            return False
