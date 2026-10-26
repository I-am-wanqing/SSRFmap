import concurrent.futures
import logging
import socket
import struct
import sys
from datetime import datetime

from core.utils import *

name = "networkscan"
description = "网络扫描 - HTTP Ping 扫描"
author = "Swissky"
documentation = []


class exploit:
    ips = set()

    def __init__(self, requester, args):
        logging.info(f"模块 '{name}' 已启动！")

        # 使用并发请求以缩短耗时
        self.add_range("192.168.1.0/24")  # 默认网段
        self.add_range("192.168.0.0/24")  # 默认网段

        # 如需扫描更多网段，取消以下注释
        # self.add_range("172.17.0.0/16")   # Docker 网段
        # self.add_range("172.18.0.0/16")   # Docker 网段

        r = requester.do_request(args.param, "")
        with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
            future_to_url = {
                executor.submit(self.concurrent_request, requester, args.param, ip, "80", r): ip
                for ip in self.ips
            }

    def add_range(self, ip_cidr):
        (ip, cidr) = ip_cidr.split("/")
        cidr = int(cidr)
        host_bits = 32 - cidr
        i = struct.unpack(">I", socket.inet_aton(ip))[0]  # 注意字节序
        start = (i >> host_bits) << host_bits  # 清零主机位
        end = start | ((1 << host_bits) - 1)

        # 排除子网中的第一个和最后一个地址
        for i in range(start, end):
            self.ips.add(socket.inet_ntoa(struct.pack(">I", i)))

    def concurrent_request(self, requester, param, host, port, compare):
        try:
            payload = wrapper_http("", host, port.strip())
            r = requester.do_request(param, payload)

            if (not "Connection refused" in r.text) and (r.text != compare.text):
                timer = datetime.today().time().replace(microsecond=0)
                print(f"\t[{timer}] 发现主机 :{host + ' ' * 40}")

            timer = datetime.today().time().replace(microsecond=0)
        except Exception as e:
            pass
