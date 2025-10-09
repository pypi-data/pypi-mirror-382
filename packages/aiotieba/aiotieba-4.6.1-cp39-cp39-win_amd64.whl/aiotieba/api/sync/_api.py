from __future__ import annotations

from typing import TYPE_CHECKING

import yarl

from ...const import APP_BASE_HOST, MAIN_VERSION
from ...exception import TiebaServerError
from ...helper import parse_json

if TYPE_CHECKING:
    from ...core import HttpCore


def parse_body(body: bytes) -> tuple[str, str]:
    res_json = parse_json(body)
    if code := int(res_json["error_code"]):
        raise TiebaServerError(code, res_json["error_msg"])

    client_id = res_json["client"]["client_id"]
    sample_id = res_json["wl_config"]["sample_id"]

    return client_id, sample_id


async def request(http_core: HttpCore) -> tuple[str, str]:
    data = [
        ("BDUSS", http_core.account.BDUSS),
        ("_client_version", MAIN_VERSION),
        ("cuid", http_core.account.cuid_galaxy2),
    ]

    request = http_core.pack_form_request(yarl.URL.build(scheme="http", host=APP_BASE_HOST, path="/c/s/sync"), data)

    body = await http_core.net_core.send_request(request, read_bufsize=64 * 1024)
    return parse_body(body)
