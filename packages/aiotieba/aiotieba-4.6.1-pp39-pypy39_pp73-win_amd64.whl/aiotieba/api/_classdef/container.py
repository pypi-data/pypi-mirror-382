from __future__ import annotations

import dataclasses as dcs
from typing import TYPE_CHECKING, Generic, SupportsIndex, TypeVar, overload

if TYPE_CHECKING:
    from collections.abc import Iterator

TypeContainer = TypeVar("TypeContainer")


@dcs.dataclass
class Containers(Generic[TypeContainer]):
    """
    内容列表的泛型基类
    约定取内容的通用接口

    Attributes:
        objs (list[TypeContainer]): 内容列表
    """

    objs: list[TypeContainer] = dcs.field(default_factory=list)

    def __iter__(self) -> Iterator[TypeContainer]:
        return self.objs.__iter__()

    @overload
    def __getitem__(self, idx: SupportsIndex) -> TypeContainer: ...

    @overload
    def __getitem__(self, idx: slice) -> list[TypeContainer]: ...

    def __getitem__(self, idx):
        return self.objs.__getitem__(idx)

    def __setitem__(self, idx, val):
        raise NotImplementedError

    def __delitem__(self, idx):
        raise NotImplementedError

    def __len__(self) -> int:
        return self.objs.__len__()

    def __bool__(self) -> bool:
        return bool(self.objs)
