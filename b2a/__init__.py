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
import getopt
import os
import sys

import json
import aigpy
from prettytable import prettytable

from b2a.aliplat import AliPlat, AliKey
from b2a.bdyplat import BdyPlat, BdyKey
from b2a.platformImp import PlatformImp


class AsyncCount(object):
    index = 0
    err = 0
    success = 0
    skip = 0


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
VERSION = '2021.7.26.1'

__CONFIG_PATH__ = os.path.expanduser('~') + '/b2a/'
__AUTH_PATH__ = f"{__CONFIG_PATH__}auth.json"
__DOWNLOAD_PATH__ = './b2a/download/'

aplat = AliPlat()
bdyplat = BdyPlat()
asyncCount = AsyncCount()

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
    if not aigpy.file.write(__AUTH_PATH__, json.dumps(authJson), 'w+'):
        aigpy.cmd.printErr("保存登录信息文件失败!")


def loginBdy(cookies: str):
    key = BdyKey()
    if not key.login(cookies):
        aigpy.cmd.printErr("登录百度云失败!")
        return
    aigpy.cmd.printInfo("登录百度云成功!")
    bdyplat.setKey(key)
    authJson['bdy-cookies'] = key.cookies
    if not aigpy.file.write(__AUTH_PATH__, json.dumps(authJson), 'w+'):
        aigpy.cmd.printErr("保存登录信息文件失败!")


def listPath(plat: PlatformImp, remotePath: str):
    array = plat.list(remotePath)
    aigpy.cmd.printInfo(f"目录列表项共有：{len(array)}项")
    for item in array:
        print(item.path)


def bdyToAli(bdyFromPath: str, aliToPath: str):
    array = bdyplat.list(bdyFromPath)
    for item in array:
        if not item.isfile:
            continue

        asyncCount.index += 1

        localFilePath = __DOWNLOAD_PATH__ + item.path
        uploadFilePath = aliToPath + '/' + item.path[len(bdyFromPath):]
        if aplat.isFileExist(uploadFilePath):
            asyncCount.skip += 1
            aigpy.cmd.printInfo(f"[{asyncCount.index}] 跳过文件: {item.path}")
            continue

        aigpy.cmd.printInfo(f"[{asyncCount.index}] 迁移文件: {item.path}")
        if aigpy.file.getSize(localFilePath) <= 0:
            check = bdyplat.downloadFile(item.path, localFilePath)
            if not check:
                aigpy.cmd.printErr("[错误] 下载失败!")
                asyncCount.err += 1
                continue

        check = aplat.uploadFile(localFilePath, uploadFilePath)
        if not check:
            aigpy.cmd.printErr("[错误] 上传失败!")
            asyncCount.err += 1
        else:
            asyncCount.success += 1

        aigpy.path.remove(localFilePath)

    for item in array:
        if item.isfile:
            continue
        bdyToAli(item.path, aliToPath + '/' + item.name)


def asyncPath(bdyFromPath: str, aliToPath: str):
    asyncCount.err = 0
    asyncCount.skip = 0
    asyncCount.success = 0
    asyncCount.index = 0

    bdyToAli(bdyFromPath, aliToPath)

    aigpy.cmd.printInfo(f"迁移文件：{asyncCount.success}；失败：{asyncCount.err}；跳过：{asyncCount.skip}")


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


def printUsage():
    print("=============B2A HELP==============")
    tb = prettytable.PrettyTable()
    tb.field_names = ["功能", "描述"]
    tb.align = 'l'
    tb.add_row(["-h or --help", "显示帮助"])
    tb.add_row(["-v or --version", "显示版本"])
    tb.add_row(["-a or --ali", "登录阿里云，参数为refresh_token"])
    tb.add_row(["-b or --bdy", "登录百度云，参数为cookies"])
    tb.add_row(["-f or --from", "待迁移的百度云目录"])
    tb.add_row(["-t or --to", "要存放的阿里云目录"])
    tb.add_row(["--alist", "显示阿里云目录"])
    tb.add_row(["--blist", "显示百度云目录"])
    print(tb)


def mainCommand():
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "hva:b:f:t:",
                                   ["help", "version", "ali=", "bdy=", "from=", "to=", "alist=", "blist="])
    except getopt.GetoptError as errmsg:
        aigpy.cmd.printErr("输入参数错误!")
        printUsage()
        return

    bdyPath = ''
    aliPath = ''
    for opt, val in opts:
        if opt in ('-h', '--help'):
            printUsage()
            return
        if opt in ('-v', '--version'):
            printLogo()
            return
        if opt in ('-a', '--ali'):
            loginAli(val)
            continue
        if opt in ('-b', '--bdy'):
            loginBdy(val)
            continue
        if opt in ('-f', '--from'):
            bdyPath = val
            continue
        if opt in ('-t', '--to'):
            aliPath = val
            continue
        if opt in ('--alist'):
            listPath(aplat, val)
            continue
        if opt in ('--blist'):
            listPath(bdyplat, val)
            continue

    if aliPath == '' or bdyPath == '':
        return

    aigpy.cmd.printInfo(f"====迁移百度云[{bdyPath}]到阿里云[{aliPath}]====")
    asyncPath(bdyPath, aliPath)


def main():
    token = authJson.get('ali-refresh_token')
    cookies = authJson.get('bdy-cookies')
    if token:
        loginAli(token)
    if cookies:
        loginBdy(cookies)

    if len(sys.argv) > 1:
        mainCommand()
        return

    printLogo()
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
