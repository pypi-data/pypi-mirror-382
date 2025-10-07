from pathlib import Path
from typing import Any, Self

from lupa import LuaRuntime, lua_type

from .errors import MLuaModuleError
from .roots import MLuaBase, MLuaObject

__all__ = ["MLuaObject", "MLuaEnvironment", "MLuaModule", "MLuaManager", "MLuaResolver"]


class MLuaEnvironment(MLuaBase):

    def __init__(self, *args, **kwargs) -> None:
        self._runtime: LuaRuntime = None
        self.reset(*args, **kwargs)

    @property
    def lua_runtime(self) -> LuaRuntime:
        return self._runtime

    def reset(self, *args, **kwargs) -> None:
        self._runtime = LuaRuntime(*args, **kwargs)

    def __str__(self) -> str:
        return f"{type(self).__name__}({self._runtime})"


class MLuaModule(MLuaBase):

    def __init__(self, path: str) -> None:
        self._path = Path(path)
        self._name = self._path.stem
        self._data: str = self._path.read_text()
        self._requirements = {
            self._name: []
        }

    def mount(self, environment: MLuaEnvironment, security=True) -> MLuaObject:
        mlua_object = MLuaObject()
        functions = mlua_object.functions
        values = mlua_object.values
        modules: dict = environment.lua_runtime.execute(self._data)
        """
        两段循环意图为去除循环内判断的开销，遇到模块数据大的情况时有显著用处
        setattr会处理部分边缘情况
        __dict__访问更快
        模块量少的情况下建议选择第一种方式，即security不需要改动
        """
        if security:
            for key, value in modules.items():
                setattr(functions if lua_type(value) == "function" else values, key, value)

        else:
            for key, value in modules.items():
                (functions if lua_type(value) == "function" else values).__dict__[key] = value

        return mlua_object

    def mount_deeply(self, environment: MLuaEnvironment, security=True) -> dict[str, MLuaObject]:
        return MLuaManager(*MLuaResolver.requirements(self)).mount_all(environment, security=security)

    def inject(self, environment: MLuaEnvironment, globals_dict: dict[Any, Any]) -> None:
        globals_dict.update({key: value for key, value in environment.lua_runtime.execute(self._data).items()})

    def inject_deeply(self, environment: MLuaEnvironment, globals_dict) -> None:
        return MLuaManager(*MLuaResolver.requirements(self)).inject_all(environment, globals_dict)

    def require(self, *modules: Self) -> None:
        for module in modules:
            if module in self._requirements[self._name]:
                raise MLuaModuleError(f"module \"{module.name}\" has already been included in \"{self._name}\"")

            elif self in MLuaResolver.requirements(module):
                raise MLuaModuleError(f"module \"{module.name}\" has already required module \"{self._name}\"")

        self._requirements[self._name].extend(modules)

    def require_not(self, *modules: Self) -> None:
        for index, module in enumerate(modules):
            if not module in self._requirements[self._name]:
                raise MLuaModuleError(f"module \"{module.name}\" has not been included in \"{self._name}\"")

            del self._requirements[self._name][index]

    @property
    def requirements(self) -> list[Self]:
        return self._requirements[self._name]

    @property
    def name(self) -> str:
        return self._name

    @property
    def path(self) -> str:
        return str(self._path)

    @property
    def source(self) -> str:
        return self._data

    def __str__(self) -> str:
        return f"{type(self).__name__}({self.name})"


class MLuaManager(MLuaBase):

    def __init__(self, *modules: MLuaModule) -> None:
        self._modules = modules

    def mount_all(self, environment: MLuaEnvironment, security=True) -> dict[str, MLuaObject]:
        return {module.name: module.mount(environment, security=security) for module in self._modules}

    def inject_all(self, environment: MLuaEnvironment, globals_dict: dict[Any, Any], security=True) -> None:
        for module in self._modules:
            module.inject(environment, globals_dict)

    def __str__(self) -> str:
        return f"{type(self).__name__}({[str(module) for module in self._modules]})"


class MLuaResolver(MLuaBase):

    @staticmethod
    def requirements(*modules: MLuaModule) -> list[MLuaModule]:
        results = []

        def run(*son_requirements: MLuaModule) -> None:
            for son_requirement in son_requirements:
                requirements: list[MLuaModule] = son_requirement.requirements
                if requirements:
                    run(*requirements)

                results.append(son_requirement)

        run(*modules)
        return results

    @staticmethod
    def relationship(*modules: MLuaModule, indent_length=4, indent_style=".") -> None:
        def run(indent: int, *son_requirements: MLuaModule) -> None:
            for son_requirement in son_requirements:
                print(indent_style * indent + str(son_requirement))
                requirements: list[MLuaModule] = son_requirement.requirements
                if requirements:
                    run(indent + indent_length, *requirements)

        run(0, *modules)
