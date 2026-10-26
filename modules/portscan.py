import concurrent.futures
import logging
from datetime import datetime

from core.utils import *

name = "portscan"
description = "扫描目标端口"
author = "Swissky"
documentation = []


class exploit:
    def __init__(self, requester, args):
        logging.info(f"模块 '{name}' 已启动！")
        r = requester.do_request(args.param, "")

        load_ports = ""
        with open("data/ports", "r") as f:
            load_ports = f.readlines()

        # 使用生成器创建主机列表
        gen_host = gen_ip_list("127.0.0.1", args.level)
        for ip in gen_host:
            # 使用 with 语句确保线程及时清理
            with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
                future_to_url = {
                    executor.submit(
                        self.concurrent_request, requester, args.param, ip, port, r
                    ): port
                    for port in load_ports
                }

    def concurrent_request(self, requester, param, host, port, compare):
        try:
            payload = wrapper_http("", host, port.strip())
            r = requester.do_request(param, payload)

            # 显示开放端口
            if r != None and not "Connection refused" in r.text:
                timer = datetime.today().time().replace(microsecond=0)
                port = port.strip() + " " * 20

                # 检查请求响应是否与默认响应相同
                if r.text != "" and r.text != compare.text:
                    print(
                        f"\t[{timer}] IP:{host:12s}, 发现 \033[32m开放      \033[0m 端口 n°{port}"
                    )
                else:
                    print(
                        f"\t[{timer}] IP:{host:12s}, 发现 \033[31m被过滤    \033[0m 端口 n°{port}"
                    )

            timer = datetime.today().time().replace(microsecond=0)
            port = port.strip() + " " * 20
            (print(f"\t[{timer}] 正在检查端口 n°{port}", end="\r"),)

        # 超时也可能意味着端口开放
        except Exception as e:
            print(e)
            timer = datetime.today().time().replace(microsecond=0)
            port = port.strip() + " " * 20
            print(f"\t[{timer}] IP:{host:212}, \033[33m已超时\033[0m  端口 n°{port}")
            pass
