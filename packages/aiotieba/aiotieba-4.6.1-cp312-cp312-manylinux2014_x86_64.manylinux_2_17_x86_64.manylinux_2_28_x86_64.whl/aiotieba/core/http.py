from __future__ import annotations

import dataclasses as dcs
import urllib.parse
from http.cookies import Morsel
from typing import TYPE_CHECKING

import aiohttp

from ..__version__ import __version__
from ..const import APP_BASE_HOST
from ..helper.crypto import sign

if TYPE_CHECKING:
    import yarl

    from .account import Account
    from .net import NetCore


@dcs.dataclass
class HttpContainer:
    """
    用于保存会话headers与cookies的容器
    """

    headers: dict[str, str]
    cookie_jar: aiohttp.CookieJar

    def __init__(self, headers: dict[str, str], cookie_jar: aiohttp.CookieJar) -> None:
        self.headers: dict[str, str] = headers
        self.cookie_jar: aiohttp.CookieJar = cookie_jar


@dcs.dataclass
class HttpCore:
    """
    保存http接口相关状态的核心容器
    """

    account: Account
    net_core: NetCore
    app: HttpContainer
    app_proto: HttpContainer
    web: HttpContainer

    def __init__(self, account: Account, net_core: NetCore) -> None:
        self.net_core = net_core

        from aiohttp import hdrs

        app_headers = {
            hdrs.USER_AGENT: f"aiotieba/{__version__}",
            hdrs.ACCEPT_ENCODING: "gzip",
            hdrs.CONNECTION: "keep-alive",
            hdrs.HOST: APP_BASE_HOST,
        }
        self.app = HttpContainer(app_headers, aiohttp.DummyCookieJar())

        app_proto_headers = {
            hdrs.USER_AGENT: f"aiotieba/{__version__}",
            "x_bd_data_type": "protobuf",
            hdrs.ACCEPT_ENCODING: "gzip",
            hdrs.CONNECTION: "keep-alive",
            hdrs.HOST: APP_BASE_HOST,
        }
        self.app_proto = HttpContainer(app_proto_headers, aiohttp.DummyCookieJar())

        web_headers = {
            hdrs.USER_AGENT: f"aiotieba/{__version__}",
            hdrs.ACCEPT_ENCODING: "gzip, deflate",
            hdrs.CACHE_CONTROL: "no-cache",
            hdrs.CONNECTION: "keep-alive",
        }
        self.web = HttpContainer(web_headers, aiohttp.CookieJar())

        self.set_account(account)

    def set_account(self, new_account: Account) -> None:
        self.account = new_account

        BDUSS_morsel = Morsel()
        BDUSS_morsel.set("BDUSS", new_account.BDUSS, new_account.BDUSS)
        BDUSS_morsel["domain"] = "baidu.com"
        self.web.cookie_jar._cookies["baidu.com", ""]["BDUSS"] = BDUSS_morsel
        STOKEN_morsel = Morsel()
        STOKEN_morsel.set("STOKEN", new_account.STOKEN, new_account.STOKEN)
        STOKEN_morsel["domain"] = "tieba.baidu.com"
        self.web.cookie_jar._cookies["tieba.baidu.com", ""]["STOKEN"] = STOKEN_morsel

    def pack_form_request(self, url: yarl.URL, data: list[tuple[str, str]]) -> aiohttp.ClientRequest:
        """
        自动签名参数元组列表
        并将其打包为移动端表单请求

        Args:
            url (yarl.URL): 链接
            data (list[tuple[str, str]]): 参数元组列表

        Returns:
            aiohttp.ClientRequest
        """

        payload = aiohttp.payload.BytesPayload(
            urllib.parse.urlencode(sign(data), doseq=True).encode("utf-8"),
            content_type="application/x-www-form-urlencoded",
        )

        request = aiohttp.ClientRequest(
            aiohttp.hdrs.METH_POST,
            url,
            headers=self.app.headers,
            data=payload,
            proxy=self.net_core.proxy.url,
            proxy_auth=self.net_core.proxy.auth,
            ssl=False,
        )

        return request

    def pack_proto_request(self, url: yarl.URL, data: bytes) -> aiohttp.ClientRequest:
        """
        打包移动端protobuf请求

        Args:
            url (yarl.URL): 链接
            data (bytes): protobuf序列化后的二进制数据

        Returns:
            aiohttp.ClientRequest
        """

        writer = aiohttp.MultipartWriter("form-data", boundary="-*_r1999")
        payload_headers = {
            aiohttp.hdrs.CONTENT_DISPOSITION: aiohttp.helpers.content_disposition_header(
                "form-data", name="data", filename="file"
            )
        }
        payload = aiohttp.BytesPayload(data, content_type="", headers=payload_headers)
        payload.headers.popone(aiohttp.hdrs.CONTENT_TYPE)
        writer._parts.append((payload, None, None))

        request = aiohttp.ClientRequest(
            aiohttp.hdrs.METH_POST,
            url,
            headers=self.app_proto.headers,
            data=writer,
            proxy=self.net_core.proxy.url,
            proxy_auth=self.net_core.proxy.auth,
            ssl=False,
        )

        return request

    def pack_web_get_request(
        self, url: yarl.URL, params: list[tuple[str, str]], *, extra_headers: list[tuple[str, str]] | None = None
    ) -> aiohttp.ClientRequest:
        """
        打包网页端参数请求

        Args:
            url (yarl.URL): 链接
            params (list[tuple[str, str]]): 参数元组列表
            extra_headers (list[tuple[str, str]]): 额外的请求头

        Returns:
            aiohttp.ClientRequest
        """

        url = url.update_query(params)
        headers = self.web.headers
        if extra_headers:
            headers |= extra_headers

        request = aiohttp.ClientRequest(
            aiohttp.hdrs.METH_GET,
            url,
            headers=headers,
            cookies=self.web.cookie_jar.filter_cookies(url),
            proxy=self.net_core.proxy.url,
            proxy_auth=self.net_core.proxy.auth,
            ssl=False,
        )

        return request

    def pack_web_form_request(
        self, url: yarl.URL, data: list[tuple[str, str]], *, extra_headers: list[tuple[str, str]] | None = None
    ) -> aiohttp.ClientRequest:
        """
        打包网页端表单请求

        Args:
            url (yarl.URL): 链接
            data (list[tuple[str, str]]): 参数元组列表
            extra_headers (list[tuple[str, str]]): 额外的请求头

        Returns:
            aiohttp.ClientRequest
        """

        headers = self.web.headers
        if extra_headers:
            headers |= extra_headers

        payload = aiohttp.payload.BytesPayload(
            urllib.parse.urlencode(data, doseq=True).encode("utf-8"),
            content_type="application/x-www-form-urlencoded",
        )

        request = aiohttp.ClientRequest(
            aiohttp.hdrs.METH_POST,
            url,
            headers=headers,
            data=payload,
            cookies=self.web.cookie_jar.filter_cookies(url),
            proxy=self.net_core.proxy.url,
            proxy_auth=self.net_core.proxy.auth,
            ssl=False,
        )

        return request
