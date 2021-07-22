#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  __init__.py
@Date    :  2021/06/17
@Author  :  Yaronzz
@Version :  1.0
@Contact :  yaronhuang@foxmail.com
@Desc    :
"""
import os
import time

import aigpy
from prettytable import prettytable

from b2a.aliplat import AliPlat, AliKey
from b2a.bdyplat import BdyPlat, BdyKey
from b2a.platformImp import PlatformImp

__LOGO__ = '''
         /$$$$$$$   /$$$$$$   /$$$$$$         
        | $$__  $$ /$$__  $$ /$$__  $$        
        | $$  \ $$|__/  \ $$| $$  \ $$        
 /$$$$$$| $$$$$$$   /$$$$$$/| $$$$$$$$ /$$$$$$
|______/| $$__  $$ /$$____/ | $$__  $$|______/
        | $$  \ $$| $$      | $$  | $$        
        | $$$$$$$/| $$$$$$$$| $$  | $$        
        |_______/ |________/|__/  |__/        

  https://github.com/yaronzz/BaiduYunToAliYun 
'''
VERSION = '2021.7.22.1'

__CONFIG_PATH__ = os.path.expanduser('~') + '/b2a/'
__AUTH_PATH__ = f"{__CONFIG_PATH__}auth.json"
__DOWNLOAD_PATH__ = './b2a/download/'

aplat = AliPlat()
bdyplat = BdyPlat()

aigpy.path.mkdirs(__CONFIG_PATH__)
aigpy.path.mkdirs(__DOWNLOAD_PATH__)
authJson = aigpy.file.getJson(__AUTH_PATH__)


def loginAli(token: str):
    key = AliKey()
    if not key.login(token):
        aigpy.cmd.printErr("登录阿里云失败!")
        return
    aigpy.cmd.printInfo("登录阿里云成功!")
    aplat.setKey(key)
    authJson['ali-refresh_token'] = key.refreshToken
    aigpy.file.writeJson(__AUTH_PATH__, authJson)


def loginBdy(cookies: str):
    key = BdyKey()
    if not key.login(cookies):
        aigpy.cmd.printErr("登录百度云失败!")
        return
    aigpy.cmd.printInfo("登录百度云成功!")
    bdyplat.setKey(key)
    authJson['bdy-cookies'] = key.cookies
    aigpy.file.writeJson(__AUTH_PATH__, authJson)


def listPath(plat: PlatformImp, remotePath: str):
    array = plat.list(remotePath)
    aigpy.cmd.printInfo(f"目录列表项共有：{len(array)}项")
    for item in array:
        print(item.path)


def asyncPath(bdyFromPath: str, aliToPath: str):
    array = bdyplat.list(bdyFromPath, True)
    count = len(array)
    countErr = 0
    countSuccess = 0
    countSkip = 0
    for index, item in enumerate(array):
        if not item.isfile:
            continue

        aigpy.cmd.printInfo(f"[{index}/{count}] 迁移文件: {item.path}")

        localFilePath = __DOWNLOAD_PATH__ + item.path
        uploadFilePath = aliToPath + '/' + item.path.lstrip(bdyFromPath)
        if aplat.isFileExist(uploadFilePath):
            countSkip += 1
            continue

        if aigpy.file.getSize(localFilePath) <= 0:
            check = bdyplat.downloadFile(item.path, localFilePath)
            if not check:
                aigpy.cmd.printErr("[错误] 下载失败!")
                countErr += 1
                continue

        check = aplat.uploadFile(localFilePath, uploadFilePath)
        if not check:
            aigpy.cmd.printErr("[错误] 上传失败!")
            countErr += 1
        else:
            countSuccess += 1

        aigpy.path.remove(localFilePath)

    aigpy.cmd.printInfo(f"迁移文件：{countSuccess}；失败：{countErr}；跳过：{countSkip}")


def printChoices():
    print("====================================================")
    tb = prettytable.PrettyTable()
    tb.field_names = ["功能", "选项"]
    tb.align = 'l'
    tb.set_style(prettytable.PLAIN_COLUMNS)
    tb.add_row([aigpy.cmd.green("输入" + " '0':"), "退出"])
    tb.add_row([aigpy.cmd.green("输入" + " '1':"), "登录阿里云"])
    tb.add_row([aigpy.cmd.green("输入" + " '2':"), "登录百度云"])
    tb.add_row([aigpy.cmd.green("输入" + " '3':"), "显示阿里云目录"])
    tb.add_row([aigpy.cmd.green("输入" + " '4':"), "显示百度云目录"])
    tb.add_row([aigpy.cmd.green("输入" + " '5':"), "文件迁移"])
    print(tb)
    print("====================================================")


def printLogo():
    string = __LOGO__ + '\n               v' + VERSION
    print(string)


def main():
    printLogo()

    token = authJson.get('ali-refresh_token')
    cookies = authJson.get('bdy-cookies')
    if token:
        loginAli(token)
    if cookies:
        loginBdy(cookies)

    while True:
        printChoices()
        choice = aigpy.cmd.inputInt(aigpy.cmd.yellow("选项:"), 0)
        if choice == 0:
            return
        elif choice == 1:
            para = input(aigpy.cmd.yellow("请输入refresh_token:"))
            loginAli(para)
        elif choice == 2:
            para = input(aigpy.cmd.yellow("请输入cookies:"))
            loginBdy(para)
        elif choice == 3:
            para = input(aigpy.cmd.yellow("请输入路径:"))
            listPath(aplat, para)
        elif choice == 4:
            para = input(aigpy.cmd.yellow("请输入路径:"))
            listPath(bdyplat, para)
        elif choice == 5:
            fromPath = input(aigpy.cmd.yellow("请输入百度云路径:"))
            toPath = input(aigpy.cmd.yellow("请输入阿里云路径:"))
            asyncPath(fromPath, toPath)


if __name__ == "__main__":
    main()
