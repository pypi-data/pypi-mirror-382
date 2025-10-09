from __future__ import annotations

import dataclasses as dcs

import aiohttp
import yarl


@dcs.dataclass
class ProxyConfig:
    """
    代理配置

    Args:
        url (str | yarl.URL, optional): 代理url. Defaults to None.
        auth (aiohttp.BasicAuth, optional): 代理认证. Defaults to None.
    """

    url: yarl.URL | None = None
    auth: aiohttp.BasicAuth | None = None

    def __init__(self, url: str | yarl.URL | None = None, auth: aiohttp.BasicAuth | None = None) -> None:
        if isinstance(url, str):
            url = yarl.URL(url)
        self.url = url
        self.auth = auth

    @staticmethod
    def from_env() -> ProxyConfig:
        proxy_info = aiohttp.helpers.proxies_from_env().get("http", None)
        if proxy_info is None:
            url, auth = None, None
        else:
            url, auth = proxy_info.proxy, proxy_info.proxy_auth
        return ProxyConfig(url, auth)


@dcs.dataclass
class TimeoutConfig:
    """
    各种超时配置

    Args:
        http_acquire_conn (float, optional): 从连接池获取一个可用连接的超时时间. Defaults to 4.0.
        http_read (float, optional): 从发送http请求到读取全部响应的超时时间. Defaults to 12.0.
        http_connect (float, optional): 新建一个socket连接的超时时间. Defaults to 3.0.
        http_keepalive (float, optional): http长连接的保持时间. Defaults to 30.0.
        ws_send (float, optional): websocket发送数据的超时时间. Defaults to 3.0.
        ws_read (float, optional): 从发送websocket数据到结束等待响应的超时时间. Defaults to 8.0.
        ws_close (float, optional): 等待websocket终止连接的时间. Defaults to 10.0.
        ws_keepalive (float, optional): websocket在长达ws_keepalive的时间内未发生IO则发送close信号关闭连接. Defaults to 300.0.
        ws_heartbeat (float, optional): websocket心跳间隔. 为None则不发送心跳. Defaults to None.
        dns_ttl (int, optional): dns的本地缓存超时时间. Defaults to 600.

    Note:
        所有时间均以秒为单位
    """

    http_acquire_conn: float = 4.0
    http_read: float = 12.0
    http_connect: float = 3.0
    http_keepalive: float = 30.0
    ws_send: float = 3.0
    ws_read: float = 8.0
    ws_close: float = 10.0
    ws_keepalive: float = 300.0
    ws_heartbeat: float | None = None
    dns_ttl: int = 600

    @property
    def http_timeout(self) -> aiohttp.ClientTimeout:
        return aiohttp.ClientTimeout(
            connect=self.http_acquire_conn, sock_read=self.http_read, sock_connect=self.http_connect
        )

    @property
    def ws_timeout(self) -> aiohttp.ClientWSTimeout:
        return aiohttp.ClientWSTimeout(self.ws_read, self.ws_close)
