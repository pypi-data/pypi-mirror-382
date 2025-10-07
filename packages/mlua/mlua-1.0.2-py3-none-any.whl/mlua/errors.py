from .roots import MLuaBase


class MLuaError(Exception, MLuaBase):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class MLuaModuleError(MLuaError):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class MLuaRuntimeError(MLuaError):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
