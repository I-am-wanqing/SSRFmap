#!/usr/bin/python
import argparse
import logging
import os
from pathlib import Path

import urllib3

from core.ssrf import SSRF


def display_banner():
    print(r" _____ _________________                     ")
    print(r"/  ___/  ___| ___ \  ___|                    ")
    print(r"\ `--.\ `--.| |_/ / |_ _ __ ___   __ _ _ __  ")
    print(r" `--. \`--. \    /|  _| '_ ` _ \ / _` | '_ \ ")
    print(r"/\__/ /\__/ / |\ \| | | | | | | | (_| | |_) |")
    print(r"\____/\____/\_| \_\_| |_| |_| |_|\__,_| .__/ ")
    print(r"                                      | |    ")
    print(r"                                      |_|    ")


def parse_args():
    example_text = """示例:
    uv run python ssrfmap.py -r examples/request2.txt -p url -m portscan
    uv run python ssrfmap.py -r examples/request.txt -p url -m redis
    uv run python ssrfmap.py -r examples/request.txt -p url -m portscan --ssl --uagent "SSRFmapAgent"
    uv run python ssrfmap.py -r examples/request.txt -p url -m redis --lhost=127.0.0.1 --lport=4242 -l 4242
    uv run python ssrfmap.py -r examples/request.txt -p url -m readfiles --rfiles
    """
    parser = argparse.ArgumentParser(
        epilog=example_text, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-r", action="store", dest="reqfile", help="SSRF 请求文件", required=True
    )
    parser.add_argument(
        "-p", action="store", dest="param", help="要攻击的 SSRF 参数", required=True
    )
    parser.add_argument("-m", action="store", dest="modules", help="要启用的 SSRF 模块")
    parser.add_argument(
        "-l",
        action="store",
        dest="handler",
        help="启动一个反弹 Shell 处理器",
        nargs="?",
        const="1",
    )
    parser.add_argument("-v", action="store_true", dest="verbose", help="启用详细输出")
    parser.add_argument(
        "--lhost",
        action="store",
        dest="lhost",
        help="反弹 Shell 的 LHOST 或网络内目标 IP",
    )
    parser.add_argument(
        "--lport",
        action="store",
        dest="lport",
        help="反弹 Shell 的 LPORT 或网络内目标端口",
    )
    parser.add_argument(
        "--ldomain",
        action="store",
        dest="ldomain",
        help="AXFR 查询或域名相关模块的目标域名",
    )
    parser.add_argument(
        "--rfiles",
        action="store",
        dest="targetfiles",
        help="readfiles 模块要读取的文件",
        nargs="?",
        const=True,
    )
    parser.add_argument("--uagent", action="store", dest="useragent", help="要使用的 User Agent")
    parser.add_argument(
        "--ssl",
        action="store",
        dest="ssl",
        help="使用 HTTPS 且不校验证书",
        nargs="?",
        const=True,
    )
    parser.add_argument(
        "--proxy",
        action="store",
        dest="proxy",
        help="使用 HTTP(s) 代理（例：http://localhost:8080）",
    )
    parser.add_argument(
        "--level",
        action="store",
        dest="level",
        help="测试级别（1-5，默认：1）",
        nargs="?",
        const=1,
        default=1,
        type=int,
    )
    parser.add_argument("--logfile", action="store", dest="logfile", help="SSRFmap 日志文件")
    results = parser.parse_args()
    return results


if __name__ == "__main__":
    # 禁用自签名证书的 SSL 告警
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    display_banner()

    args = parse_args()
    args.reqfile = os.path.abspath(args.reqfile)

    # 将日志文件默认位置设为 ssrfmap.py 同目录下的 SSRFmap.log
    if args.logfile is None:
        log_file_path = str(Path(__file__).resolve().parent) + "/SSRFmap.log"
    else:
        log_file_path = args.logfile

    print(f"[INFO] 日志文件 '{log_file_path}'")
    # 启用自定义日志
    try:
        logging.basicConfig(
            level=logging.INFO,
            format="[%(levelname)s]:%(message)s",
            handlers=[logging.FileHandler(log_file_path, mode="w"), logging.StreamHandler()],
        )
    # 处理日志文件无写入权限的情况
    except Exception as e:
        print(f"{e}")

    logging.addLevelName(
        logging.WARNING, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.WARNING)
    )
    logging.addLevelName(
        logging.ERROR, "\033[1;41m%s\033[1;0m" % logging.getLevelName(logging.ERROR)
    )

    # 处理详细输出
    if args.verbose is True:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("已启用详细输出")

    # SSRFmap
    ssrf = SSRF(args)
