from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .models import (
    DeletePageResult,
    Ms365UploadSession,
    OperationResult,
    Page,
    PageType,
    PaginatedGrids,
    PaginatedResources,
    SortDirection,
    TextFormat,
)

if TYPE_CHECKING:
    from ._http import AsyncHttpClient, HttpClient


class Pages:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def get(
        self,
        slug: str,
        *,
        fields: str | None = None,
        raise_on_redirect: bool | None = None,
        revision_id: int | None = None,
    ) -> Page:
        resp = self._http.get(
            "/pages",
            params={
                "slug": slug,
                "fields": fields,
                "raise_on_redirect": raise_on_redirect,
                "revision_id": revision_id,
            },
        )
        return Page.model_validate(resp.json())

    def get_by_id(
        self,
        page_id: int,
        *,
        fields: str | None = None,
        raise_on_redirect: bool | None = None,
        revision_id: int | None = None,
    ) -> Page:
        resp = self._http.get(
            f"/pages/{page_id}",
            params={
                "fields": fields,
                "raise_on_redirect": raise_on_redirect,
                "revision_id": revision_id,
            },
        )
        return Page.model_validate(resp.json())

    def create(
        self,
        *,
        page_type: PageType | str,
        title: str,
        slug: str,
        content: str | None = None,
        grid_format: TextFormat | str | None = None,
        cloud_page: dict[str, Any] | None = None,
        fields: str | None = None,
        is_silent: bool | None = None,
    ) -> Page | Ms365UploadSession:
        body: dict[str, Any] = {"page_type": page_type, "title": title, "slug": slug}
        if content is not None:
            body["content"] = content
        if grid_format is not None:
            body["grid_format"] = grid_format
        if cloud_page is not None:
            body["cloud_page"] = cloud_page
        resp = self._http.post(
            "/pages",
            params={"_fields": fields, "is_silent": is_silent},
            json=body,
        )
        data = resp.json()
        if "upload_to" in data:
            return Ms365UploadSession.model_validate(data)
        return Page.model_validate(data)

    def update(
        self,
        page_id: int,
        *,
        title: str | None = None,
        content: str | None = None,
        redirect: dict[str, Any] | None = None,
        allow_merge: bool | None = None,
        fields: str | None = None,
        is_silent: bool | None = None,
    ) -> Page:
        body: dict[str, Any] = {}
        if title is not None:
            body["title"] = title
        if content is not None:
            body["content"] = content
        if redirect is not None:
            body["redirect"] = redirect
        resp = self._http.post(
            f"/pages/{page_id}",
            params={"allow_merge": allow_merge, "fields": fields, "is_silent": is_silent},
            json=body,
        )
        return Page.model_validate(resp.json())

    def delete(self, page_id: int) -> DeletePageResult:
        resp = self._http.delete(f"/pages/{page_id}")
        return DeletePageResult.model_validate(resp.json())

    def clone(
        self,
        page_id: int,
        *,
        target: str,
        title: str | None = None,
        subscribe_me: bool | None = None,
    ) -> OperationResult:
        body: dict[str, Any] = {"target": target}
        if title is not None:
            body["title"] = title
        if subscribe_me is not None:
            body["subscribe_me"] = subscribe_me
        resp = self._http.post(f"/pages/{page_id}/clone", json=body)
        return OperationResult.model_validate(resp.json())

    def get_grids(
        self,
        page_id: int,
        *,
        cursor: str | None = None,
        order_by: str | None = None,
        order_direction: SortDirection | str | None = None,
        page_size: int | None = None,
    ) -> PaginatedGrids:
        resp = self._http.get(
            f"/pages/{page_id}/grids",
            params={
                "cursor": cursor,
                "order_by": order_by,
                "order_direction": order_direction,
                "page_size": page_size,
            },
        )
        return PaginatedGrids.model_validate(resp.json())

    def get_resources(
        self,
        page_id: int,
        *,
        cursor: str | None = None,
        order_by: str | None = None,
        order_direction: SortDirection | str | None = None,
        page_size: int | None = None,
        q: str | None = None,
        types: str | None = None,
    ) -> PaginatedResources:
        resp = self._http.get(
            f"/pages/{page_id}/resources",
            params={
                "cursor": cursor,
                "order_by": order_by,
                "order_direction": order_direction,
                "page_size": page_size,
                "q": q,
                "types": types,
            },
        )
        return PaginatedResources.model_validate(resp.json())

    def append_content(
        self,
        page_id: int,
        *,
        content: str,
        location: str | None = None,
        section_id: int | None = None,
        section_location: str | None = None,
        anchor_name: str | None = None,
        anchor_fallback: bool | None = None,
        anchor_regex: bool | None = None,
        fields: str | None = None,
        is_silent: bool | None = None,
    ) -> Page:
        body: dict[str, Any] = {"content": content}
        if location is not None:
            body["body"] = {"location": location}
        if section_id is not None:
            section: dict[str, Any] = {"id": section_id}
            if section_location is not None:
                section["location"] = section_location
            body["section"] = section
        if anchor_name is not None:
            anchor: dict[str, Any] = {"name": anchor_name}
            if anchor_fallback is not None:
                anchor["fallback"] = anchor_fallback
            if anchor_regex is not None:
                anchor["regex"] = anchor_regex
            body["anchor"] = anchor
        resp = self._http.post(
            f"/pages/{page_id}/append-content",
            params={"fields": fields, "is_silent": is_silent},
            json=body,
        )
        return Page.model_validate(resp.json())


class AsyncPages:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def get(
        self,
        slug: str,
        *,
        fields: str | None = None,
        raise_on_redirect: bool | None = None,
        revision_id: int | None = None,
    ) -> Page:
        resp = await self._http.get(
            "/pages",
            params={
                "slug": slug,
                "fields": fields,
                "raise_on_redirect": raise_on_redirect,
                "revision_id": revision_id,
            },
        )
        return Page.model_validate(resp.json())

    async def get_by_id(
        self,
        page_id: int,
        *,
        fields: str | None = None,
        raise_on_redirect: bool | None = None,
        revision_id: int | None = None,
    ) -> Page:
        resp = await self._http.get(
            f"/pages/{page_id}",
            params={
                "fields": fields,
                "raise_on_redirect": raise_on_redirect,
                "revision_id": revision_id,
            },
        )
        return Page.model_validate(resp.json())

    async def create(
        self,
        *,
        page_type: PageType | str,
        title: str,
        slug: str,
        content: str | None = None,
        grid_format: TextFormat | str | None = None,
        cloud_page: dict[str, Any] | None = None,
        fields: str | None = None,
        is_silent: bool | None = None,
    ) -> Page | Ms365UploadSession:
        body: dict[str, Any] = {"page_type": page_type, "title": title, "slug": slug}
        if content is not None:
            body["content"] = content
        if grid_format is not None:
            body["grid_format"] = grid_format
        if cloud_page is not None:
            body["cloud_page"] = cloud_page
        resp = await self._http.post(
            "/pages",
            params={"_fields": fields, "is_silent": is_silent},
            json=body,
        )
        data = resp.json()
        if "upload_to" in data:
            return Ms365UploadSession.model_validate(data)
        return Page.model_validate(data)

    async def update(
        self,
        page_id: int,
        *,
        title: str | None = None,
        content: str | None = None,
        redirect: dict[str, Any] | None = None,
        allow_merge: bool | None = None,
        fields: str | None = None,
        is_silent: bool | None = None,
    ) -> Page:
        body: dict[str, Any] = {}
        if title is not None:
            body["title"] = title
        if content is not None:
            body["content"] = content
        if redirect is not None:
            body["redirect"] = redirect
        resp = await self._http.post(
            f"/pages/{page_id}",
            params={"allow_merge": allow_merge, "fields": fields, "is_silent": is_silent},
            json=body,
        )
        return Page.model_validate(resp.json())

    async def delete(self, page_id: int) -> DeletePageResult:
        resp = await self._http.delete(f"/pages/{page_id}")
        return DeletePageResult.model_validate(resp.json())

    async def clone(
        self,
        page_id: int,
        *,
        target: str,
        title: str | None = None,
        subscribe_me: bool | None = None,
    ) -> OperationResult:
        body: dict[str, Any] = {"target": target}
        if title is not None:
            body["title"] = title
        if subscribe_me is not None:
            body["subscribe_me"] = subscribe_me
        resp = await self._http.post(f"/pages/{page_id}/clone", json=body)
        return OperationResult.model_validate(resp.json())

    async def get_grids(
        self,
        page_id: int,
        *,
        cursor: str | None = None,
        order_by: str | None = None,
        order_direction: SortDirection | str | None = None,
        page_size: int | None = None,
    ) -> PaginatedGrids:
        resp = await self._http.get(
            f"/pages/{page_id}/grids",
            params={
                "cursor": cursor,
                "order_by": order_by,
                "order_direction": order_direction,
                "page_size": page_size,
            },
        )
        return PaginatedGrids.model_validate(resp.json())

    async def get_resources(
        self,
        page_id: int,
        *,
        cursor: str | None = None,
        order_by: str | None = None,
        order_direction: SortDirection | str | None = None,
        page_size: int | None = None,
        q: str | None = None,
        types: str | None = None,
    ) -> PaginatedResources:
        resp = await self._http.get(
            f"/pages/{page_id}/resources",
            params={
                "cursor": cursor,
                "order_by": order_by,
                "order_direction": order_direction,
                "page_size": page_size,
                "q": q,
                "types": types,
            },
        )
        return PaginatedResources.model_validate(resp.json())

    async def append_content(
        self,
        page_id: int,
        *,
        content: str,
        location: str | None = None,
        section_id: int | None = None,
        section_location: str | None = None,
        anchor_name: str | None = None,
        anchor_fallback: bool | None = None,
        anchor_regex: bool | None = None,
        fields: str | None = None,
        is_silent: bool | None = None,
    ) -> Page:
        body: dict[str, Any] = {"content": content}
        if location is not None:
            body["body"] = {"location": location}
        if section_id is not None:
            section: dict[str, Any] = {"id": section_id}
            if section_location is not None:
                section["location"] = section_location
            body["section"] = section
        if anchor_name is not None:
            anchor: dict[str, Any] = {"name": anchor_name}
            if anchor_fallback is not None:
                anchor["fallback"] = anchor_fallback
            if anchor_regex is not None:
                anchor["regex"] = anchor_regex
            body["anchor"] = anchor
        resp = await self._http.post(
            f"/pages/{page_id}/append-content",
            params={"fields": fields, "is_silent": is_silent},
            json=body,
        )
        return Page.model_validate(resp.json())
