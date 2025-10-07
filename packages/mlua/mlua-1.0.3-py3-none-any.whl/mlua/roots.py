__all__ = ["MLuaBase", "MLuaObject"]


class MLuaBase:

    def __str__(self) -> str:
        return f"{type(self).__name__}()"


class MLuaObject(MLuaBase):

    def __init__(self) -> None:
        self.functions = self._Functions()
        self.values = self._Values()

    class _Functions:

        def __str__(self) -> str:
            return str(self.__dict__)

    class _Values:

        def __str__(self) -> str:
            return str(self.__dict__)

    def __str__(self) -> str:
        return f"{type(self).__name__}({self.functions.__str__()}, {self.values.__str__()})"
