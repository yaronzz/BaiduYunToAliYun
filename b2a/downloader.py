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
from threading import Lock
from urllib.request import Request, urlopen

import aigpy.cmdHelper
from tqdm import tqdm


class Downloader(object):
    def __init__(self, url, headers, filePath, size, threadNum=6):
        self.url = url
        self.threadNum = threadNum
        self.filePath = filePath
        self.size = size

        self._error = False
        self._headers = headers
        self._lock = Lock()
        self._bar = tqdm(total=self.size, desc="下载中", unit_scale=True)

    def __createFile__(self):
        try:
            fp = open(self.filePath, "wb")
            fp.truncate(self.size)
            fp.close()
            return True
        except Exception as e:
            aigpy.cmd.printErr("创建文件失败：" + str(e))
            return False

    def down(self, start, end, fp):
        try:
            req = Request(url=self.url, method='GET')
            req.headers['Range'] = 'bytes={}-{}'.format(start, end)
            req.headers.update(self._headers)
            r = urlopen(req)

            while not self._error:
                data = r.read(1024*5)
                tmpSize = len(data)
                if tmpSize <= 0:
                    break
                fp.write(data)
                self._lock.acquire()
                self._bar.update(tmpSize)
                self._lock.release()
        except Exception as e:
            aigpy.cmd.printErr("下载文件块失败：" + str(e))
            self._error = True

    def run(self):
        try:
            if not self.__createFile__():
                return False

            partSize = self.size // self.threadNum
            pool = ThreadPoolExecutor(max_workers=self.threadNum)
            futures = []
            for i in range(self.threadNum):
                start = partSize * i
                if i == self.threadNum - 1:
                    end = self.size
                else:
                    end = start + partSize - 1

                fp = open(self.filePath, "wb")
                fp.seek(start)
                futures.append(pool.submit(self.down, start, end, fp))
            wait(futures)
            self._bar.close()
            return not self._error
        except Exception as e:
            aigpy.cmdHelper.printErr("下载失败：" + str(e))
            self._error = True
            return False
