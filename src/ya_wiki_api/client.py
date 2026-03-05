from __future__ import annotations

from ._http import AsyncHttpClient, AuthConfig, HttpClient
from .grids import AsyncGrids, Grids
from .pages import AsyncPages, Pages


class WikiClient:
    """Synchronous Yandex Wiki API client.

    Usage:
        client = WikiClient(token="...", org_id="...")
        page = client.pages.get(slug="users/test/page")
        grid = client.grids.get("grid-uuid")
        client.grids.rows.add("grid-uuid", rows=[{"col": "val"}])
    """

    def __init__(
        self,
        token: str,
        *,
        org_id: str | None = None,
        cloud_org_id: str | None = None,
        is_iam: bool = False,
        base_url: str = "https://api.wiki.yandex.net/v1",
        timeout: float = 30.0,
    ) -> None:
        auth = AuthConfig(token, org_id=org_id, cloud_org_id=cloud_org_id, is_iam=is_iam)
        self._http = HttpClient(auth, base_url=base_url, timeout=timeout)
        self.pages = Pages(self._http)
        self.grids = Grids(self._http)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> WikiClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


class AsyncWikiClient:
    """Asynchronous Yandex Wiki API client.

    Usage:
        async with AsyncWikiClient(token="...", org_id="...") as client:
            page = await client.pages.get(slug="users/test/page")
            grid = await client.grids.get("grid-uuid")
    """

    def __init__(
        self,
        token: str,
        *,
        org_id: str | None = None,
        cloud_org_id: str | None = None,
        is_iam: bool = False,
        base_url: str = "https://api.wiki.yandex.net/v1",
        timeout: float = 30.0,
    ) -> None:
        auth = AuthConfig(token, org_id=org_id, cloud_org_id=cloud_org_id, is_iam=is_iam)
        self._http = AsyncHttpClient(auth, base_url=base_url, timeout=timeout)
        self.pages = AsyncPages(self._http)
        self.grids = AsyncGrids(self._http)

    async def close(self) -> None:
        await self._http.close()

    async def __aenter__(self) -> AsyncWikiClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()
