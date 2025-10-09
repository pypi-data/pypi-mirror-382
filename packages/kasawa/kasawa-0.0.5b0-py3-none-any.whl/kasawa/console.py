import os
import ctypes
from pystyle import Colors
from datetime import datetime


class console:
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def title(text):
        ctypes.windll.kernel32.SetConsoleTitleW(text)

    class log:
        @staticmethod
        def info(text):
            now = datetime.now()
            timenow = now.strftime("%H:%M:%S")
            prefix = f"{Colors.gray}[{timenow}] | [{Colors.blue}|{Colors.gray}] | {Colors.blue}[INF]{Colors.reset} "
            message = f"{Colors.white}{text}"
            print(prefix + message)

        @staticmethod
        def error(text):
            now = datetime.now()
            timenow = now.strftime("%H:%M:%S")
            prefix = f"{Colors.gray}[{timenow}] | [{Colors.red}-{Colors.gray}] | {Colors.red}[ERR]{Colors.reset} "
            message = f"{Colors.white}{text}"
            print(prefix + message)

        @staticmethod
        def success(text):
            now = datetime.now()
            timenow = now.strftime("%H:%M:%S")
            prefix = f"{Colors.gray}[{timenow}] | [{Colors.green}+{Colors.gray}] | {Colors.green}[SUC]{Colors.reset} "
            message = f"{Colors.white}{text}"
            print(prefix + message)

        @staticmethod
        def warning(text):
            now = datetime.now()
            timenow = now.strftime("%H:%M:%S")
            prefix = f"{Colors.gray}[{timenow}] | [{Colors.yellow}!{Colors.gray}] | {Colors.yellow}[WAR]{Colors.reset} "
            message = f"{Colors.white}{text}"
            print(prefix + message)

        @staticmethod
        def ask(text):
            now = datetime.now()
            timenow = now.strftime("%H:%M:%S")
            prefix = f"{Colors.gray}[{timenow}] | [{Colors.yellow}?{Colors.gray}] | {Colors.yellow}[ASK]{Colors.reset} "
            message = f"{Colors.white}{text}"
            print(prefix + message)
