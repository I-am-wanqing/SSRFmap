import logging
import os
import time
from importlib.machinery import SourceFileLoader
from pathlib import Path

from core.handler import Handler
from core.requester import Requester


class SSRF(object):
    modules = set()
    handler = None
    requester = None

    def __init__(self, args):

        # 设置工作目录，以便访问所有库
        self.change_current_dir()

        # 将模块加载到内存
        self.load_modules()

        # 启动反弹 Shell 处理器
        if args.handler and args.lport and args.handler == "1":
            handler = Handler(args.lport)
            handler.start()
        elif args.handler and args.lport:
            self.load_handler(args.handler)
            handler = self.handler.exploit(args.lport)
            handler.start()

        proxies = None
        if args.proxy:
            proxies = {
                "http": args.proxy,
                "https": args.proxy,
            }

        # 初始化 Requester
        self.requester = Requester(args.reqfile, args.useragent, args.ssl, proxies)

        # 注意：若 args.param 为 None，则测试所有参数
        if args.param == None:
            logging.warning("未定义参数（-p），不会测试任何内容！")

        # 注意：若 args.modules 为 None，则尝试所有模块
        if args.modules == None:
            logging.warning("未定义模块（-m），将测试所有模块！")
            for module in self.modules:
                module.exploit(self.requester, args)
        else:
            for modname in args.modules.split(","):
                for module in self.modules:
                    if module.name == modname:
                        module.exploit(self.requester, args)
                        break

        # 处理 Shell 交互
        while args.handler:
            handler.listen_command()
            time.sleep(5)

    def load_modules(self):
        for name in os.listdir("./modules"):
            location = os.path.join("./modules", name)
            if ".py" in location:
                mymodule = SourceFileLoader(name, location).load_module()
                self.modules.add(mymodule)

    def load_handler(self, name):
        handler_file = f"{name}.py"
        try:
            location = os.path.join("./handlers", handler_file)
            self.handler = SourceFileLoader(handler_file, location).load_module()
        except Exception as e:
            logging.error(f"处理模块不存在或无效：{name}")
            exit(1)

    def change_current_dir(self):
        try:
            os.chdir(str(Path(__file__).resolve().parent.parent))
        except PermissionError:
            project_directory = Path(__file__).resolve().parent.parent
            logging.error(
                "错误：无权访问目录 %s，请检查执行权限。",
                project_directory,
            )
