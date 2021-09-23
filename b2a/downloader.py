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
import threading
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
        self._lock = threading.Lock()

    def __getStream__(self, start):
        stream = RangeRequestIO('GET',
                                self.url,
                                headers=self._headers,
                                max_chunk_size=10 * 1024 * 1024,
                                callback=None,
                                encrypt_password=b"",
                                timeout=(5, 60))
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

    def __readStream__(self, stream, part, offset):
        retry = 3
        while True:
            try:
                data = stream.read(part)
                return data
            except Exception as e:
                stream.seek(offset)
                retry -= 1
                if retry > 0:
                    continue
                raise e
        return None

    def __getFileStream__(self, offset):
        fp = open(self.filePath, 'wb')
        fp.seek(offset)
        return fp

    def down(self, start, end):
        try:
            r = self.__getStream__(start)
            fp = self.__getFileStream__(start)
        except Exception as e:
            printErr("下载文件块失败：" + str(e))
            self._error = True
            return

        try:
            size = end - start
            offset = start
            while not self._error:
                part = min(self._readSize, size)
                data = self.__readStream__(r, part, offset)

                self._lock.acquire()
                fp.write(data)
                self._bar.update(part)
                self._lock.release()

                size -= part
                offset += part
                if self._error:
                    break
                if size <= 0:
                    break
        except Exception as e:
            printErr("下载文件块失败：" + str(e))
            self._error = True
        r.close()
        fp.close()

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
