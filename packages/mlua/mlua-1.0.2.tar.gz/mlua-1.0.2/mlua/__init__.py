from .cores import *
from .envs import *
from .errors import *
from .logs import *
from .roots import *


@MLuaLogsDecorator.info("Checking status.")
def status():
    MLuaLogsPrinter.info("Normal.")


def requirements() -> None:
    print("\n".join(["lupa", "colorama"]))


@MLuaLogsDecorator.info("Testing module.")
@MLuaLogsDecorator.timer()
def test(path: str) -> None:
    lua = MLuaEnvironment()
    module = MLuaModule(path)
    results = module.mount(lua)
    print(results)
