__all__ = ["MLuaLogger", "MLuaLogsGenerator", "MLuaLogsPrinter", "MLuaLogsDecorator"]

from datetime import datetime
from pathlib import Path
from time import time
from typing import Any

import colorama

from .roots import MLuaBase

colorama.init(autoreset=True)


class MLuaLogger(MLuaBase):

    def __init__(self) -> None:
        raise NotImplementedError("MLuaLogger is an abstract class and cannot be instantiated.")


class MLuaLogsGenerator(MLuaLogger):

    @staticmethod
    def info(message: str, datetime_enabled=True, bright_text=False) -> str:
        return f"{colorama.Style.BRIGHT if bright_text else ""}{colorama.Fore.GREEN}[{datetime.now().strftime('%Y-%m-%d %H:%M:%S ') if datetime_enabled else ""}INFO] {message}"

    @staticmethod
    def warn(message: str, datetime_enabled=True, bright_text=False) -> str:
        return f"{colorama.Style.BRIGHT if bright_text else ""}{colorama.Fore.YELLOW}[{datetime.now().strftime('%Y-%m-%d %H:%M:%S ') if datetime_enabled else ""}WARN] {message}"

    @staticmethod
    def error(message: str, datetime_enabled=True, bright_text=False) -> str:
        return f"{colorama.Style.BRIGHT if bright_text else ""}{colorama.Fore.RED}[{datetime.now().strftime('%Y-%m-%d %H:%M:%S ') if datetime_enabled else ""}ERROR] {message}"


class MLuaLogsPrinter(MLuaLogger):

    @staticmethod
    def info(*args, **kwargs) -> None:
        print(MLuaLogsGenerator.info(*args, **kwargs))

    @staticmethod
    def warn(*args, **kwargs) -> None:
        print(MLuaLogsGenerator.warn(*args, **kwargs))

    @staticmethod
    def error(*args, **kwargs) -> None:
        print(MLuaLogsGenerator.error(*args, **kwargs))


class MLuaLogsDecorator(MLuaLogger):

    @staticmethod
    def info(message: str) -> callable:
        def temp(function) -> callable:
            def run(*args, **kwargs) -> Any:
                MLuaLogsPrinter.info(message)
                return function(*args, **kwargs)

            return run

        return temp

    @staticmethod
    def warn(message: str) -> callable:
        def temp(function: callable) -> callable:
            def run(*args, **kwargs) -> Any:
                MLuaLogsPrinter.warn(message)
                return function(*args, **kwargs)

            return run

        return temp

    @staticmethod
    def error(message: str) -> callable:
        def temp(function: callable) -> callable:
            def run(*args, **kwargs) -> Any:
                MLuaLogsPrinter.error(message)
                return function(*args, **kwargs)

            return run

        return temp

    @staticmethod
    def timer(ms=True) -> callable:
        def temp(function: callable) -> callable:
            def run(*args, **kwargs) -> Any:
                start_time = time()
                results: Any = function(*args, **kwargs)
                end_time = time() - start_time
                MLuaLogsPrinter.info(f"Time taken: {end_time * 1000 if ms else end_time} {"ms" if ms else "s"}.")
                return results

            return run

        return temp


class MLuaLogsRecorder(MLuaLogger):

    def __init__(self) -> None:
        self.logs = []

    def info(self, message: str) -> None:
        self.logs.append(MLuaLogsGenerator.info(message))

    def warn(self, message: str) -> None:
        self.logs.append(MLuaLogsGenerator.warn(message))

    def error(self, message: str) -> None:
        self.logs.append(MLuaLogsGenerator.error(message))

    def display(self) -> None:
        for log in self.logs:
            print(log)

    def save(self, path="./mlua_logs.txt") -> None:
        Path(path).write_text("\n".join(self.logs))

    def load(self, path="./mlua_logs.txt") -> None:
        self.logs = Path(path).read_text().split("\n")

    def __str__(self) -> str:
        return f"{type(self).__name__}({self.logs})"
