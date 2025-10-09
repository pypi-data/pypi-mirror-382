from typing import Any

import requests
from requests.exceptions import (
    ConnectionError as RequestsConnectionError,
)
from requests.exceptions import (
    InvalidSchema,
    MissingSchema,
    ProxyError,
    SSLError,
)

from .response import HttpResponse, TransportError, TransportErrorDetail


def http_request_sync(
    url: str,
    *,
    method: str = "GET",
    params: dict[str, Any] | None = None,
    data: dict[str, Any] | None = None,
    json: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
    cookies: dict[str, Any] | None = None,
    user_agent: str | None = None,
    proxy: str | None = None,
    timeout: float | None = 10.0,
) -> HttpResponse:
    """
    Send a synchronous HTTP request and return the response.
    """
    if user_agent:
        if headers is None:
            headers = {}
        headers["User-Agent"] = user_agent

    proxies: dict[str, str] | None = None
    if proxy:
        proxies = {
            "http": proxy,
            "https": proxy,
        }

    try:
        res = requests.request(
            method=method,
            url=url,
            params=params,
            data=data,
            json=json,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            proxies=proxies,
        )
        return HttpResponse(
            status_code=res.status_code,
            body=res.text,
            headers=dict(res.headers),
        )
    except requests.Timeout as e:
        return HttpResponse(transport_error=TransportErrorDetail(type=TransportError.TIMEOUT, message=str(e)))
    except ProxyError as e:
        return HttpResponse(transport_error=TransportErrorDetail(type=TransportError.PROXY, message=str(e)))
    except (InvalidSchema, MissingSchema) as e:
        return HttpResponse(transport_error=TransportErrorDetail(type=TransportError.INVALID_URL, message=str(e)))
    except (RequestsConnectionError, SSLError) as e:
        return HttpResponse(transport_error=TransportErrorDetail(type=TransportError.CONNECTION, message=str(e)))
    except Exception as e:
        return HttpResponse(transport_error=TransportErrorDetail(type=TransportError.ERROR, message=str(e)))
