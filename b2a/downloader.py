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
import os
from concurrent.futures import ThreadPoolExecutor, wait
from threading import Lock

import aigpy.cmdHelper
from aigpy.convertHelper import MemoryUnit, convertMemoryUnitAuto
from aigpy.progressHelper import ProgressTool
from requests import get, head
from tqdm import tqdm


class Downloader(object):
    def __init__(self, url, headers, filePath, size, threadNum=6):
        self.url = url
        self.threadNum = threadNum
        self.filePath = filePath
        self.size = size

        self._fp = None
        self._error = False
        self._headers = headers
        self._blockSize = 1 * 1024 * 1024
        self._lock = Lock()
        self._bar = tqdm(total=self.size, desc="下载中", unit_scale=True)

    def __getSize__(self, headers):
        r = head(self.url, headers=headers)
        while r.status_code == 302:
            url = r.headers['Location']
            r = head(url, headers=headers)
        if r.status_code == 200:
            return int(r.headers['Content-Length'])
        return 0

    def __createFile__(self):
        try:
            fp = open(self.filePath, "wb")
            fp.truncate(self.size)
            fp.close()
            return True
        except Exception as e:
            aigpy.cmd.printErr("创建文件失败：" + str(e))
            return False

    def down(self, start, end):
        try:
            if self._error:
                return False

            headers = {'Range': 'bytes={}-{}'.format(start, end)}
            r = get(self.url, headers=headers.update(self._headers), stream=True)
            r.raise_for_status()

            self._lock.acquire()
            if not self._error:
                self._fp.seek(start)
                self._fp.write(r.content)
                self._bar.update(end - start)
            self._lock.release()
            return True
        except Exception as e:
            aigpy.cmd.printErr("下载文件块失败：" + str(e))
            self._error = True
            return False

    def run(self):
        try:
            if not self.__createFile__():
                return False

            self._fp = open(self.filePath, "rb+")

            num = self.size // self._blockSize
            pool = ThreadPoolExecutor(max_workers=self.threadNum)
            futures = []
            for i in range(num):
                start = self._blockSize * i
                # 最后一块
                if i == num - 1:
                    end = self.size
                else:
                    end = start + self._blockSize - 1
                futures.append(pool.submit(self.down, start, end))
            wait(futures)
            self._bar.close()
            self._fp.close()
            return ~self._error
        except Exception as e:
            aigpy.cmdHelper.printErr("下载失败：" + str(e))
            self._error = True
            return False
