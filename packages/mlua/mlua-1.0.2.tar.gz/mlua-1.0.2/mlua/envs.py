__all__ = ["MLuaOperator", "MLuaPackager"]

from json import loads as jloads, dumps as jdumps
from os import mkdir
from pathlib import Path
from pickle import dumps as pdumps, loads as ploads
from zlib import compress, decompress

from .cores import MLuaModule
from .errors import MLuaModuleError
from .roots import MLuaBase


class MLuaOperator(MLuaBase):

    @staticmethod
    def save(*modules: MLuaModule, directory="./mlua_modules") -> bool:
        try:
            mkdir(directory)
        except FileExistsError:
            pass

        configuration = {}
        for module in modules:
            configuration[module.name] = module.path

        return bool(Path(directory, "index.json").write_text(jdumps(configuration)))

    @staticmethod
    def load(directory="./mlua_modules") -> list[MLuaModule]:
        configuration = jloads(Path(directory, "index.json").read_text())
        temp_modules = []
        for module_path in configuration.values():
            temp_modules.append(MLuaModule(module_path))

        return temp_modules

    @staticmethod
    def use(*modules: str, directory="./mlua_modules") -> list[MLuaModule]:
        configuration: dict[str, str] = jloads(Path(directory, "index.json").read_text())
        temp_modules = []
        for module in modules:
            temp_module = configuration.get(module)
            if temp_module is None:
                raise MLuaModuleError(f"module \"{module}\" has not been found in mlua repository \"{directory}\"")

            temp_modules.append(MLuaModule(temp_module))

        return temp_modules


class MLuaPackager(MLuaBase):

    @staticmethod
    def pack(*modules: MLuaModule) -> bytes:
        return compress(pdumps({module.name: module for module in modules}))

    @staticmethod
    def unpack(data: bytes) -> dict[str, MLuaModule]:
        return ploads(decompress(data))
