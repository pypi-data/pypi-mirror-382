from __future__ import annotations

import dataclasses as dcs


@dcs.dataclass
class TbErrorExt:
    """
    为类型添加一个`err`项 用于保存捕获到的异常
    """

    err: Exception | None = dcs.field(default=None, init=False, repr=False)


@dcs.dataclass
class BoolResponse(TbErrorExt):
    """
    bool返回值
    不是内置bool的子类 可能不支持部分bool操作

    Attributes:
        err (Exception | None): 捕获的异常
    """

    def __bool__(self) -> bool:
        return self.err is None

    def __int__(self) -> int:
        return int(bool(self))

    def __repr__(self) -> str:
        return str(bool(self))

    def __hash__(self) -> int:
        return hash(bool(self))


@dcs.dataclass
class IntResponse(TbErrorExt, int):
    """
    int返回值
    是内置int的子类

    Attributes:
        err (Exception | None): 捕获的异常
    """

    def __new__(cls, i: int = 0) -> IntResponse:
        obj = super().__new__(cls, i)
        return obj

    def __init__(self, i: int = 0) -> None:
        pass

    def __repr__(self) -> str:
        return str(int(self))

    def __hash__(self) -> int:
        return hash(int(self))


@dcs.dataclass
class StrResponse(TbErrorExt, str):
    """
    str返回值
    是内置str的子类

    Attributes:
        err (Exception | None): 捕获的异常
    """

    __slots__ = []

    def __new__(cls, s: str = "") -> StrResponse:
        obj = super().__new__(cls, s)
        return obj

    def __init__(self, s: str = "") -> None:
        pass

    def __hash__(self) -> int:
        return hash(str(self))


class TiebaServerError(RuntimeError):
    """
    贴吧服务器异常
    """

    __slots__ = ["code", "msg"]

    def __init__(self, code: int, msg: str) -> None:
        super().__init__(code, msg)
        self.code = code
        self.msg = msg


class HTTPStatusError(RuntimeError):
    """
    错误的状态码
    """

    __slots__ = ["code", "msg"]

    def __init__(self, code: int, msg: str) -> None:
        super().__init__(code, msg)
        self.code = code
        self.msg = msg


class TiebaValueError(RuntimeError):
    """
    意外的字段值
    """


class ContentTypeError(RuntimeError):
    """
    无法解析响应头中的content-type
    """
