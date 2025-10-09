from __future__ import annotations

import dataclasses as dcs
from functools import cached_property
from typing import TYPE_CHECKING

from ...exception import TbErrorExt
from .._classdef import Containers

if TYPE_CHECKING:
    from collections.abc import Mapping


@dcs.dataclass
class Fan:
    """
    用户信息

    Attributes:
        user_id (int): user_id
        portrait (str): portrait
        user_name (str): 用户名
        nick_name_new (str): 新版昵称

        nick_name (str): 用户昵称
        show_name (str): 显示名称
        log_name (str): 用于在日志中记录用户信息
    """

    user_id: int = 0
    portrait: str = ""
    user_name: str = ""
    nick_name_new: str = ""

    @staticmethod
    def from_tbdata(data_map: Mapping) -> Fan:
        user_id = int(data_map["id"])
        portrait = data_map["portrait"]
        if "?" in portrait:
            portrait = portrait[:-13]
        user_name = data_map["name"]
        nick_name_new = data_map["name_show"]
        return Fan(user_id, portrait, user_name, nick_name_new)

    def __str__(self) -> str:
        return self.user_name or self.portrait or str(self.user_id)

    def __eq__(self, obj: Fan) -> bool:
        return self.user_id == obj.user_id

    def __hash__(self) -> int:
        return self.user_id

    def __bool__(self) -> bool:
        return bool(self.user_id)

    @property
    def nick_name(self) -> str:
        return self.nick_name_new

    @property
    def show_name(self) -> str:
        return self.nick_name_new or self.user_name

    @cached_property
    def log_name(self) -> str:
        if self.user_name:
            return self.user_name
        elif self.portrait:
            return f"{self.nick_name_new}/{self.portrait}"
        else:
            return str(self.user_id)


@dcs.dataclass
class Page_fan:
    """
    页信息

    Attributes:
        page_size (int): 页大小
        current_page (int): 当前页码
        total_page (int): 总页码
        total_count (int): 总计数

        has_more (bool): 是否有后继页
        has_prev (bool): 是否有前驱页
    """

    page_size: int = 0
    current_page: int = 0
    total_page: int = 0
    total_count: int = 0

    has_more: bool = False
    has_prev: bool = False

    @staticmethod
    def from_tbdata(data_map: Mapping) -> Page_fan:
        page_size = int(data_map["page_size"])
        current_page = int(data_map["current_page"])
        total_page = int(data_map["total_page"])
        total_count = int(data_map["total_count"])
        has_more = bool(int(data_map["has_more"]))
        has_prev = bool(int(data_map["has_prev"]))
        return Page_fan(page_size, current_page, total_page, total_count, has_more, has_prev)


@dcs.dataclass
class Fans(TbErrorExt, Containers[Fan]):
    """
    粉丝列表

    Attributes:
        objs (list[Fan]): 粉丝列表
        err (Exception | None): 捕获的异常

        page (Page_fan): 页信息
        has_more (bool): 是否还有下一页
    """

    page: Page_fan = dcs.field(default_factory=Page_fan)

    @staticmethod
    def from_tbdata(data_map: Mapping) -> Fans:
        objs = [Fan.from_tbdata(m) for m in data_map["user_list"]]
        page = Page_fan.from_tbdata(data_map["page"])
        return Fans(objs, page)

    @property
    def has_more(self) -> bool:
        return self.page.has_more
