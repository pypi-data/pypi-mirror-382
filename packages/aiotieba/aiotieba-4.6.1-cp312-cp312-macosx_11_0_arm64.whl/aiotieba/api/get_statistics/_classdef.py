from __future__ import annotations

import dataclasses as dcs
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


@dcs.dataclass
class Statistics:
    """
    吧务后台统计信息
    时间从旧到新

    Attributes:
        view (list[int]): 浏览量
        thread (list[int]): 主题帖数
        new_member (list[int]): 新增吧会员数
        post (list[int]): 回复数
        sign_ratio (list[int]): 签到率
        avg_time (list[int]): 人均浏览时长
        avg_times (list[int]): 人均进吧次数
        recommend (list[int]): 首页推荐数
    """

    view: list[int] = dcs.field(default_factory=list)
    thread: list[int] = dcs.field(default_factory=list)
    new_member: list[int] = dcs.field(default_factory=list)
    post: list[int] = dcs.field(default_factory=list)
    sign_ratio: list[int] = dcs.field(default_factory=list)
    avg_time: list[int] = dcs.field(default_factory=list)
    avg_times: list[int] = dcs.field(default_factory=list)
    recommend: list[int] = dcs.field(default_factory=list)

    @staticmethod
    def from_tbdata(data_seq: Sequence) -> Statistics:
        def extract(i: int) -> list[int]:
            seq: list = data_seq[i]["group"][1]["values"]
            seq = [int(item["value"]) for item in seq]
            return seq

        view = extract(0)
        thread = extract(1)
        new_member = extract(2)
        post = extract(3)
        sign_ratio = extract(4)
        avg_time = extract(5)
        avg_times = extract(6)
        recommend = extract(7)

        return Statistics(view, thread, new_member, post, sign_ratio, avg_time, avg_times, recommend)
