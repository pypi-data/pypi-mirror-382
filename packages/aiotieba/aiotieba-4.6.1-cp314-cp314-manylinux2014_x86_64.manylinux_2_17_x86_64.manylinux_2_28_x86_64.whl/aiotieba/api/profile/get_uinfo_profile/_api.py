from __future__ import annotations

from typing import TYPE_CHECKING

import yarl

from ....const import APP_BASE_HOST, MAIN_VERSION
from ....exception import TiebaServerError
from .._classdef import UserInfo_pf
from .._const import CMD
from ..protobuf import ProfileReqIdl_pb2, ProfileResIdl_pb2

if TYPE_CHECKING:
    from ....core import HttpCore, WsCore


def pack_proto(uid_or_portrait: str | int) -> bytes:
    req_proto = ProfileReqIdl_pb2.ProfileReqIdl()
    req_proto.data.common._client_version = MAIN_VERSION
    req_proto.data.common._client_type = 2
    req_proto.data.need_post_count = 1
    req_proto.data.page = 1

    if isinstance(uid_or_portrait, int):
        req_proto.data.uid = uid_or_portrait
    else:
        req_proto.data.friend_uid_portrait = uid_or_portrait

    return req_proto.SerializeToString()


def parse_body(body: bytes) -> UserInfo_pf:
    res_proto = ProfileResIdl_pb2.ProfileResIdl()
    res_proto.ParseFromString(body)

    if code := res_proto.error.errorno:
        raise TiebaServerError(code, res_proto.error.errmsg)

    data_proto = res_proto.data
    user = UserInfo_pf.from_tbdata(data_proto)

    return user


async def request_http(http_core: HttpCore, uid_or_portrait: str | int) -> UserInfo_pf:
    data = pack_proto(uid_or_portrait)

    request = http_core.pack_proto_request(
        yarl.URL.build(scheme="http", host=APP_BASE_HOST, path="/c/u/user/profile", query_string=f"cmd={CMD}"),
        data,
    )

    body = await http_core.net_core.send_request(request, read_bufsize=8 * 1024)
    return parse_body(body)


async def request_ws(ws_core: WsCore, uid_or_portrait: str | int) -> UserInfo_pf:
    data = pack_proto(uid_or_portrait)

    response = await ws_core.send(data, CMD)
    return parse_body(await response.read())
