# B2A
同步百度云网盘到阿里云

## 📺 安装 

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

