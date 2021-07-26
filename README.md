# B2A
同步百度云网盘到阿里云

## 📺 安装 
需要 Python 版本大于或等于 3.7
```shell
pip3 install b2a --upgrade
```

## 🤖 功能

- 登录百度云盘
- 登录阿里云盘
- 迁移文件
- 显示目录

## 💽 界面

![](https://raw.githubusercontent.com/yaronzz/BaiduYunToAliYun/main/image/1.png)

## 🎄使用

1. 登录阿里云，需要获取`refresh_token`

![](https://raw.githubusercontent.com/yaronzz/BaiduYunToAliYun/main/image/2.png)

2. 登录百度云，需要获取`cookies`

![](https://raw.githubusercontent.com/yaronzz/BaiduYunToAliYun/main/image/3.png)

3. 使用

| 功能               | 说明                       |
| ------------------ | -------------------------- |
| 打开交互操作       | b2a                        |
| 显示命令行说明     | b2a -h                     |
| 显示版本号         | b2a -v                     |
| 登录阿里云         | b2a -a "你的refresh_token" |
| 登录百度云         | b2a -b "你的cookies"       |
| 显示阿里云目录     | b2a --alist="/电影"        |
| 显示百度云目录     | b2a --blist="/文档"        |
| 迁移百度云到阿里云 | b2a -f "/文档" -t "/文档"  |

## 🎨库与引用

- [aigpy](https://github.com/yaronzz/AIGPY)
- [BaiduPCS](https://github.com/PeterDing/BaiduPCS-Py)
- [aliyundrive-uploader](https://github.com/Hidove/aliyundrive-uploader)
- [aliyunpan](https://github.com/wxy1343/aliyunpan)

## 📜 免责声明 
1. 本软件为免费开源项目，无任何形式的盈利行为
2. 本软件不提供各种破解与加速等功能实现
3. 本软件仅供个人数据的多端备份使用
4. 严禁使用本软件进行盈利、损坏官方、散落任何违法信息等行为