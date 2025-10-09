import yarl

from ...const import APP_BASE_HOST
from ...core import HttpCore
from ...exception import BoolResponse, TiebaServerError
from ...helper import parse_json


def parse_body(body: bytes) -> None:
    res_json = parse_json(body)
    if code := int(res_json["error_code"]):
        raise TiebaServerError(code, res_json["error_msg"])
    if code := int(res_json["data"]["is_push_success"]) != 1:
        raise TiebaServerError(code, res_json["data"]["msg"])


async def request(http_core: HttpCore, fid: int, tid: int) -> BoolResponse:
    data = [
        ("BDUSS", http_core.account.BDUSS),
        ("forum_id", fid),
        ("thread_id", tid),
    ]

    request = http_core.pack_form_request(
        yarl.URL.build(scheme="http", host=APP_BASE_HOST, path="/c/c/bawu/pushRecomToPersonalized"), data
    )

    body = await http_core.net_core.send_request(request, read_bufsize=2 * 1024)
    parse_body(body)

    return BoolResponse()
