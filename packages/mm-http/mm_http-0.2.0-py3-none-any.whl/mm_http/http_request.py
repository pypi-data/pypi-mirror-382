from typing import Any

import aiohttp
from aiohttp import (
    ClientConnectionError,
    ClientConnectorError,
    ClientHttpProxyError,
    ClientSSLError,
    InvalidUrlClientError,
    ServerConnectionError,
    ServerDisconnectedError,
)
from aiohttp.typedefs import LooseCookies
from aiohttp_socks import ProxyConnectionError, ProxyConnector
from multidict import CIMultiDictProxy

from .response import HttpResponse, TransportError, TransportErrorDetail


async def http_request(
    url: str,
    *,
    method: str = "GET",
    params: dict[str, Any] | None = None,
    data: dict[str, Any] | None = None,
    json: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
    cookies: LooseCookies | None = None,
    user_agent: str | None = None,
    proxy: str | None = None,
    timeout: float | None = 10.0,
) -> HttpResponse:
    """
    Send an HTTP request and return the response.
    """
    timeout_ = aiohttp.ClientTimeout(total=timeout) if timeout else None
    if user_agent:
        if not headers:
            headers = {}
        headers["User-Agent"] = user_agent

    try:
        if proxy and proxy.startswith("socks"):
            return await _request_with_socks_proxy(
                url,
                method=method,
                params=params,
                data=data,
                json=json,
                headers=headers,
                cookies=cookies,
                proxy=proxy,
                timeout=timeout_,
            )
        return await _request_with_http_or_none_proxy(
            url,
            method=method,
            params=params,
            data=data,
            json=json,
            headers=headers,
            cookies=cookies,
            proxy=proxy,
            timeout=timeout_,
        )
    except TimeoutError as err:
        return HttpResponse(transport_error=TransportErrorDetail(type=TransportError.TIMEOUT, message=str(err)))
    except (aiohttp.ClientProxyConnectionError, ProxyConnectionError, ClientHttpProxyError) as err:
        return HttpResponse(transport_error=TransportErrorDetail(type=TransportError.PROXY, message=str(err)))
    except InvalidUrlClientError as e:
        return HttpResponse(transport_error=TransportErrorDetail(type=TransportError.INVALID_URL, message=str(e)))
    except (
        ClientConnectorError,
        ServerConnectionError,
        ServerDisconnectedError,
        ClientSSLError,
        ClientConnectionError,
    ) as err:
        return HttpResponse(transport_error=TransportErrorDetail(type=TransportError.CONNECTION, message=str(err)))
    except Exception as err:
        return HttpResponse(transport_error=TransportErrorDetail(type=TransportError.ERROR, message=str(err)))


async def _request_with_http_or_none_proxy(
    url: str,
    *,
    method: str = "GET",
    params: dict[str, Any] | None = None,
    data: dict[str, Any] | None = None,
    json: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
    cookies: LooseCookies | None = None,
    proxy: str | None = None,
    timeout: aiohttp.ClientTimeout | None,
) -> HttpResponse:
    async with aiohttp.request(
        method, url, params=params, data=data, json=json, headers=headers, cookies=cookies, proxy=proxy, timeout=timeout
    ) as res:
        return HttpResponse(
            status_code=res.status,
            body=await res.text(),
            headers=headers_dict(res.headers),
        )


async def _request_with_socks_proxy(
    url: str,
    *,
    method: str = "GET",
    proxy: str,
    params: dict[str, Any] | None = None,
    data: dict[str, Any] | None = None,
    json: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
    cookies: LooseCookies | None = None,
    timeout: aiohttp.ClientTimeout | None,
) -> HttpResponse:
    connector = ProxyConnector.from_url(proxy)
    async with (
        aiohttp.ClientSession(connector=connector) as session,
        session.request(
            method, url, params=params, data=data, json=json, headers=headers, cookies=cookies, timeout=timeout
        ) as res,
    ):
        return HttpResponse(
            status_code=res.status,
            body=await res.text(),
            headers=headers_dict(res.headers),
        )


def headers_dict(headers: CIMultiDictProxy[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for key in headers:
        values = headers.getall(key)
        if len(values) == 1:
            result[key] = values[0]
        else:
            result[key] = ", ".join(values)
    return result
