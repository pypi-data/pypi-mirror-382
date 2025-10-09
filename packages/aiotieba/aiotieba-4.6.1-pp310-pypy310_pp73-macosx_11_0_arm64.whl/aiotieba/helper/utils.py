from __future__ import annotations

import asyncio
import functools
import logging
import sys
from datetime import datetime
from typing import Any, Callable

from ..logging import get_logger

if sys.version_info >= (3, 11):
    async_timeout = asyncio
else:
    import async_timeout

try:
    import orjson as jsonlib

    def pack_json(obj: Any) -> str:
        bjson: bytes = jsonlib.dumps(obj)
        return bjson.decode("utf-8")

except ImportError:
    import json as jsonlib

    pack_json = functools.partial(jsonlib.dumps, separators=(",", ":"))

parse_json = jsonlib.loads


def is_portrait(portrait: Any) -> bool:
    """
    简单判断输入是否符合portrait格式
    """

    return isinstance(portrait, str) and portrait.startswith("tb.")


def is_user_name(user_name: Any) -> bool:
    """
    简单判断输入是否符合user_name格式
    """

    return isinstance(user_name, str) and not user_name.startswith("tb.")


def default_datetime() -> datetime:
    return datetime(1970, 1, 1)


def timeout(delay: float, loop: asyncio.AbstractEventLoop) -> async_timeout.Timeout:
    now = loop.time()
    when = round(now) + delay
    return async_timeout.timeout_at(when)


def handle_exception(
    null_factory: Callable[[], Any],
    ok_log_level: int = logging.NOTSET,
    err_log_level: int = logging.WARNING,
):
    """
    处理request抛出的异常 只能用于装饰类成员函数

    Args:
        null_factory (Callable[[], Any]): 空构造工厂 用于返回一个默认值
        ok_log_level (int, optional): 正常日志等级. Defaults to logging.NOTSET.
        err_log_level (int, optional): 异常日志等级. Defaults to logging.WARNING.
    """

    def wrapper(func):
        @functools.wraps(func)
        async def awrapper(self, *args, **kwargs):
            def _log(log_level: int, err: Exception | None = None) -> None:
                logger = get_logger()
                if logger.isEnabledFor(err_log_level):
                    if err is None:
                        err = "Succeeded"
                    log_str = f"{err}. args={args} kwargs={kwargs}"
                    record = logger.makeRecord(logger.name, log_level, None, 0, log_str, None, None, func.__name__)
                    logger.handle(record)

            try:
                ret = await func(self, *args, **kwargs)

                if ok_log_level:
                    _log(ok_log_level)

            except Exception as err:
                _log(err_log_level, err)

                ret = null_factory()
                ret.err = err

                return ret

            else:
                return ret

        return awrapper

    return wrapper
