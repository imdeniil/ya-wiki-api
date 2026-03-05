from __future__ import annotations

from typing import Any

import httpx

BASE_URL = "https://api.wiki.yandex.net/v1"


class WikiAPIError(Exception):
    def __init__(self, status_code: int, detail: Any, response: httpx.Response | None = None):
        self.status_code = status_code
        self.detail = detail
        self.response = response
        super().__init__(f"HTTP {status_code}: {detail}")



class AuthConfig:
    def __init__(
        self,
        token: str,
        org_id: str | None = None,
        cloud_org_id: str | None = None,
        is_iam: bool = False,
    ):
        if not org_id and not cloud_org_id:
            raise ValueError("Either org_id or cloud_org_id must be provided")
        self.token = token
        self.org_id = org_id
        self.cloud_org_id = cloud_org_id
        self.is_iam = is_iam

    def headers(self) -> dict[str, str]:
        h: dict[str, str] = {}
        if self.is_iam:
            h["Authorization"] = f"Bearer {self.token}"
        else:
            h["Authorization"] = f"OAuth {self.token}"
        if self.org_id:
            h["X-Org-Id"] = self.org_id
        if self.cloud_org_id:
            h["X-Cloud-Org-Id"] = self.cloud_org_id
        return h


class HttpClient:
    def __init__(self, auth: AuthConfig, base_url: str = BASE_URL, timeout: float = 30.0):
        self._client = httpx.Client(
            base_url=base_url,
            headers=auth.headers(),
            timeout=timeout,
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> httpx.Response:
        clean_params = _strip_none(params) if params else None
        clean_json = _strip_none(json) if json else None
        resp = self._client.request(method, path, params=clean_params, json=clean_json)
        if not resp.is_success:
            try:
                detail = resp.json()
            except Exception:
                detail = resp.text
            raise WikiAPIError(resp.status_code, detail, response=resp)
        return resp

    def get(self, path: str, *, params: dict[str, Any] | None = None) -> httpx.Response:
        return self.request("GET", path, params=params)

    def post(
        self, path: str, *, params: dict[str, Any] | None = None, json: dict[str, Any] | None = None
    ) -> httpx.Response:
        return self.request("POST", path, params=params, json=json)

    def delete(
        self, path: str, *, params: dict[str, Any] | None = None, json: dict[str, Any] | None = None
    ) -> httpx.Response:
        return self.request("DELETE", path, params=params, json=json)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> HttpClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


class AsyncHttpClient:
    def __init__(self, auth: AuthConfig, base_url: str = BASE_URL, timeout: float = 30.0):
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers=auth.headers(),
            timeout=timeout,
        )

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> httpx.Response:
        clean_params = _strip_none(params) if params else None
        clean_json = _strip_none(json) if json else None
        resp = await self._client.request(method, path, params=clean_params, json=clean_json)
        if not resp.is_success:
            try:
                detail = resp.json()
            except Exception:
                detail = resp.text
            raise WikiAPIError(resp.status_code, detail, response=resp)
        return resp

    async def get(self, path: str, *, params: dict[str, Any] | None = None) -> httpx.Response:
        return await self.request("GET", path, params=params)

    async def post(
        self, path: str, *, params: dict[str, Any] | None = None, json: dict[str, Any] | None = None
    ) -> httpx.Response:
        return await self.request("POST", path, params=params, json=json)

    async def delete(
        self, path: str, *, params: dict[str, Any] | None = None, json: dict[str, Any] | None = None
    ) -> httpx.Response:
        return await self.request("DELETE", path, params=params, json=json)

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> AsyncHttpClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()


def _strip_none(d: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None}
