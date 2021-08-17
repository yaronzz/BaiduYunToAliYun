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
import logging
import sys

import aigpy
import prettytable

from b2a.aliplat import AliPlat, AliKey
from b2a.bdyplat import BdyPlat, BdyKey
from b2a.common import printErr, printInfo
from b2a.config import B2aConfig
from b2a.platformImp import PlatformImp
from b2a.trans import Trans

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
VERSION = '2021.8.17.0'

aliplat = AliPlat()
bdyplat = BdyPlat()
config = B2aConfig()
trans = Trans(aliplat, bdyplat)


def loginAli(token: str) -> bool:
    key = AliKey()
    if not key.login(token):
        printErr("登录阿里云失败!")
        return False
    aliplat.setKey(key)
    config.aliKey = key.refreshToken
    if not config.save():
        printErr("保存登录信息文件失败!")
    return True


def loginBdy(cookies: str) -> bool:
    key = BdyKey()
    if not key.login(cookies):
        printErr("登录百度云失败!")
        return False
    bdyplat.setKey(key)
    config.bdyKey = key.cookies
    if not config.save():
        printErr("保存登录信息文件失败!")
    return True


def listPath(plat: PlatformImp, remotePath: str):
    array = plat.list(remotePath)
    printInfo(f"目录列表项共有：{len(array)}项")
    for item in array:
        print(item.path)


def isLogin():
    if not aliplat.hasKey():
        printErr("请先登录阿里云！")
        return False
    if not bdyplat.hasKey():
        printErr("请先登录百度云！")
        return False
    return True


def asyncPath(bdyFromPath: str, aliToPath: str):
    if not isLogin():
        return
    trans.clearCnt()
    trans.setPath(bdyFromPath, aliToPath)
    trans.start()


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


def printNewVersion():
    version = aigpy.pipHelper.getLastVersion('b2a')
    if aigpy.system.cmpVersion(version, VERSION) > 0:
        printInfo("发现新版本：" + version)


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
    if config.aliKey:
        loginAli(config.aliKey)
    if config.bdyKey:
        loginBdy(config.bdyKey)

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "hva:b:f:t:",
                                   ["help", "version", "ali=", "bdy=", "from=", "to=", "alist=", "blist="])
    except getopt.GetoptError as errmsg:
        printErr("输入参数错误!")
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
            if loginAli(val):
                printInfo("登录阿里云成功!")
            continue
        if opt in ('-b', '--bdy'):
            if loginBdy(val):
                printInfo("登录百度云成功!")
            continue
        if opt in ('-f', '--from'):
            bdyPath = val
            if aliPath == '':
                aliPath = val
            continue
        if opt in ('-t', '--to'):
            aliPath = val
            continue
        if opt in ('--alist'):
            if not aliplat.hasKey():
                printErr('请先登录阿里云！')
                return
            listPath(aliplat, val)
            continue
        if opt in ('--blist'):
            if not bdyplat.hasKey():
                printErr('请先登录百度云！')
                return
            listPath(bdyplat, val)
            continue

    if aliPath == '' or bdyPath == '':
        return

    printInfo(f"====迁移百度云[{bdyPath}]到阿里云[{aliPath}]====")
    asyncPath(bdyPath, aliPath)


def enter(desc):
    aigpy.cmd.printW(aigpy.cmd.yellow(desc), False)
    return input()


def test():
    aliplat.uploadFile('G:\\test\\Data.zip', "/apps/test/Data.zip")


def main():
    if len(sys.argv) > 1:
        mainCommand()
        return

    printLogo()
    printNewVersion()

    if config.aliKey and loginAli(config.aliKey):
        printInfo("登录阿里云成功!")
    if config.bdyKey and loginBdy(config.bdyKey):
        printInfo("登录百度云成功!")

    # test()

    while True:
        printChoices()
        choice = enter("选项:")
        if choice == '0':
            return
        elif choice == '1':
            para = enter("请输入refresh_token:")
            if loginAli(para):
                printInfo("登录阿里云成功!")
        elif choice == '2':
            para = enter("请输入cookies:")
            if loginBdy(para):
                printInfo("登录百度云成功!")
        elif choice == '3':
            para = enter("请输入路径:")
            listPath(aliplat, para)
        elif choice == '4':
            para = enter("请输入路径:")
            listPath(bdyplat, para)
        elif choice == '5':
            fromPath = enter("请输入百度云路径:")
            toPath = enter("请输入阿里云路径:")
            asyncPath(fromPath, toPath)


if __name__ == "__main__":
    main()
