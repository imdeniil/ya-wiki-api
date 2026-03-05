from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .models import (
    AddRowsResult,
    Grid,
    NewColumn,
    OperationResult,
    RevisionResult,
    UpdateCellRequest,
    UpdateCellsResult,
)

if TYPE_CHECKING:
    from ._http import AsyncHttpClient, HttpClient


class Rows:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def add(
        self,
        grid_id: str,
        *,
        rows: list[dict[str, Any]],
        revision: str | None = None,
        position: int | None = None,
        after_row_id: str | None = None,
    ) -> AddRowsResult:
        body: dict[str, Any] = {"rows": rows}
        if revision is not None:
            body["revision"] = revision
        if position is not None:
            body["position"] = position
        if after_row_id is not None:
            body["after_row_id"] = after_row_id
        resp = self._http.post(f"/grids/{grid_id}/rows", json=body)
        return AddRowsResult.model_validate(resp.json())

    def delete(
        self,
        grid_id: str,
        *,
        row_ids: list[str],
        revision: str | None = None,
    ) -> RevisionResult:
        body: dict[str, Any] = {"row_ids": row_ids}
        if revision is not None:
            body["revision"] = revision
        resp = self._http.delete(f"/grids/{grid_id}/rows", json=body)
        return RevisionResult.model_validate(resp.json())

    def move(
        self,
        grid_id: str,
        *,
        row_id: str,
        position: int | None = None,
        after_row_id: str | None = None,
        rows_count: int | None = None,
        revision: str | None = None,
    ) -> RevisionResult:
        body: dict[str, Any] = {"row_id": row_id}
        if position is not None:
            body["position"] = position
        if after_row_id is not None:
            body["after_row_id"] = after_row_id
        if rows_count is not None:
            body["rows_count"] = rows_count
        if revision is not None:
            body["revision"] = revision
        resp = self._http.post(f"/grids/{grid_id}/rows/move", json=body)
        return RevisionResult.model_validate(resp.json())


class Columns:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def add(
        self,
        grid_id: str,
        *,
        columns: list[NewColumn | dict[str, Any]],
        revision: str | None = None,
        position: int | None = None,
    ) -> RevisionResult:
        cols = [c.model_dump(exclude_none=True) if isinstance(c, NewColumn) else c for c in columns]
        body: dict[str, Any] = {"columns": cols}
        if revision is not None:
            body["revision"] = revision
        if position is not None:
            body["position"] = position
        resp = self._http.post(f"/grids/{grid_id}/columns", json=body)
        return RevisionResult.model_validate(resp.json())

    def delete(
        self,
        grid_id: str,
        *,
        column_slugs: list[str],
        revision: str | None = None,
    ) -> RevisionResult:
        body: dict[str, Any] = {"column_slugs": column_slugs}
        if revision is not None:
            body["revision"] = revision
        resp = self._http.delete(f"/grids/{grid_id}/columns", json=body)
        return RevisionResult.model_validate(resp.json())

    def move(
        self,
        grid_id: str,
        *,
        column_slug: str,
        position: int,
        columns_count: int | None = None,
        revision: str | None = None,
    ) -> RevisionResult:
        body: dict[str, Any] = {"column_slug": column_slug, "position": position}
        if columns_count is not None:
            body["columns_count"] = columns_count
        if revision is not None:
            body["revision"] = revision
        resp = self._http.post(f"/grids/{grid_id}/columns/move", json=body)
        return RevisionResult.model_validate(resp.json())


class Cells:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def update(
        self,
        grid_id: str,
        *,
        cells: list[UpdateCellRequest | dict[str, Any]],
        revision: str | None = None,
    ) -> UpdateCellsResult:
        cell_data = [
            c.model_dump(exclude_none=True) if isinstance(c, UpdateCellRequest) else c for c in cells
        ]
        body: dict[str, Any] = {"cells": cell_data}
        if revision is not None:
            body["revision"] = revision
        resp = self._http.post(f"/grids/{grid_id}/cells", json=body)
        return UpdateCellsResult.model_validate(resp.json())


class Grids:
    def __init__(self, http: HttpClient) -> None:
        self._http = http
        self.rows = Rows(http)
        self.columns = Columns(http)
        self.cells = Cells(http)

    def get(
        self,
        grid_id: str,
        *,
        fields: str | None = None,
        filter: str | None = None,
        only_cols: str | None = None,
        only_rows: str | None = None,
        revision: int | None = None,
        sort: str | None = None,
    ) -> Grid:
        resp = self._http.get(
            f"/grids/{grid_id}",
            params={
                "fields": fields,
                "filter": filter,
                "only_cols": only_cols,
                "only_rows": only_rows,
                "revision": revision,
                "sort": sort,
            },
        )
        return Grid.model_validate(resp.json())

    def create(
        self,
        *,
        title: str,
        page_id: int | None = None,
        page_slug: str | None = None,
    ) -> Grid:
        page: dict[str, Any] = {}
        if page_id is not None:
            page["id"] = page_id
        if page_slug is not None:
            page["slug"] = page_slug
        resp = self._http.post("/grids", json={"title": title, "page": page})
        return Grid.model_validate(resp.json())

    def update(
        self,
        grid_id: str,
        *,
        revision: str | None = None,
        title: str | None = None,
        default_sort: list[dict[str, str]] | None = None,
    ) -> RevisionResult:
        body: dict[str, Any] = {}
        if revision is not None:
            body["revision"] = revision
        if title is not None:
            body["title"] = title
        if default_sort is not None:
            body["default_sort"] = default_sort
        resp = self._http.post(f"/grids/{grid_id}", json=body)
        return RevisionResult.model_validate(resp.json())

    def delete(self, grid_id: str) -> None:
        self._http.delete(f"/grids/{grid_id}")

    def clone(
        self,
        grid_id: str,
        *,
        target: str,
        title: str | None = None,
        with_data: bool | None = None,
    ) -> OperationResult:
        body: dict[str, Any] = {"target": target}
        if title is not None:
            body["title"] = title
        if with_data is not None:
            body["with_data"] = with_data
        resp = self._http.post(f"/grids/{grid_id}/clone", json=body)
        return OperationResult.model_validate(resp.json())


# --- Async versions ---


class AsyncRows:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def add(
        self,
        grid_id: str,
        *,
        rows: list[dict[str, Any]],
        revision: str | None = None,
        position: int | None = None,
        after_row_id: str | None = None,
    ) -> AddRowsResult:
        body: dict[str, Any] = {"rows": rows}
        if revision is not None:
            body["revision"] = revision
        if position is not None:
            body["position"] = position
        if after_row_id is not None:
            body["after_row_id"] = after_row_id
        resp = await self._http.post(f"/grids/{grid_id}/rows", json=body)
        return AddRowsResult.model_validate(resp.json())

    async def delete(
        self,
        grid_id: str,
        *,
        row_ids: list[str],
        revision: str | None = None,
    ) -> RevisionResult:
        body: dict[str, Any] = {"row_ids": row_ids}
        if revision is not None:
            body["revision"] = revision
        resp = await self._http.delete(f"/grids/{grid_id}/rows", json=body)
        return RevisionResult.model_validate(resp.json())

    async def move(
        self,
        grid_id: str,
        *,
        row_id: str,
        position: int | None = None,
        after_row_id: str | None = None,
        rows_count: int | None = None,
        revision: str | None = None,
    ) -> RevisionResult:
        body: dict[str, Any] = {"row_id": row_id}
        if position is not None:
            body["position"] = position
        if after_row_id is not None:
            body["after_row_id"] = after_row_id
        if rows_count is not None:
            body["rows_count"] = rows_count
        if revision is not None:
            body["revision"] = revision
        resp = await self._http.post(f"/grids/{grid_id}/rows/move", json=body)
        return RevisionResult.model_validate(resp.json())


class AsyncColumns:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def add(
        self,
        grid_id: str,
        *,
        columns: list[NewColumn | dict[str, Any]],
        revision: str | None = None,
        position: int | None = None,
    ) -> RevisionResult:
        cols = [c.model_dump(exclude_none=True) if isinstance(c, NewColumn) else c for c in columns]
        body: dict[str, Any] = {"columns": cols}
        if revision is not None:
            body["revision"] = revision
        if position is not None:
            body["position"] = position
        resp = await self._http.post(f"/grids/{grid_id}/columns", json=body)
        return RevisionResult.model_validate(resp.json())

    async def delete(
        self,
        grid_id: str,
        *,
        column_slugs: list[str],
        revision: str | None = None,
    ) -> RevisionResult:
        body: dict[str, Any] = {"column_slugs": column_slugs}
        if revision is not None:
            body["revision"] = revision
        resp = await self._http.delete(f"/grids/{grid_id}/columns", json=body)
        return RevisionResult.model_validate(resp.json())

    async def move(
        self,
        grid_id: str,
        *,
        column_slug: str,
        position: int,
        columns_count: int | None = None,
        revision: str | None = None,
    ) -> RevisionResult:
        body: dict[str, Any] = {"column_slug": column_slug, "position": position}
        if columns_count is not None:
            body["columns_count"] = columns_count
        if revision is not None:
            body["revision"] = revision
        resp = await self._http.post(f"/grids/{grid_id}/columns/move", json=body)
        return RevisionResult.model_validate(resp.json())


class AsyncCells:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def update(
        self,
        grid_id: str,
        *,
        cells: list[UpdateCellRequest | dict[str, Any]],
        revision: str | None = None,
    ) -> UpdateCellsResult:
        cell_data = [
            c.model_dump(exclude_none=True) if isinstance(c, UpdateCellRequest) else c for c in cells
        ]
        body: dict[str, Any] = {"cells": cell_data}
        if revision is not None:
            body["revision"] = revision
        resp = await self._http.post(f"/grids/{grid_id}/cells", json=body)
        return UpdateCellsResult.model_validate(resp.json())


class AsyncGrids:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http
        self.rows = AsyncRows(http)
        self.columns = AsyncColumns(http)
        self.cells = AsyncCells(http)

    async def get(
        self,
        grid_id: str,
        *,
        fields: str | None = None,
        filter: str | None = None,
        only_cols: str | None = None,
        only_rows: str | None = None,
        revision: int | None = None,
        sort: str | None = None,
    ) -> Grid:
        resp = await self._http.get(
            f"/grids/{grid_id}",
            params={
                "fields": fields,
                "filter": filter,
                "only_cols": only_cols,
                "only_rows": only_rows,
                "revision": revision,
                "sort": sort,
            },
        )
        return Grid.model_validate(resp.json())

    async def create(
        self,
        *,
        title: str,
        page_id: int | None = None,
        page_slug: str | None = None,
    ) -> Grid:
        page: dict[str, Any] = {}
        if page_id is not None:
            page["id"] = page_id
        if page_slug is not None:
            page["slug"] = page_slug
        resp = await self._http.post("/grids", json={"title": title, "page": page})
        return Grid.model_validate(resp.json())

    async def update(
        self,
        grid_id: str,
        *,
        revision: str | None = None,
        title: str | None = None,
        default_sort: list[dict[str, str]] | None = None,
    ) -> RevisionResult:
        body: dict[str, Any] = {}
        if revision is not None:
            body["revision"] = revision
        if title is not None:
            body["title"] = title
        if default_sort is not None:
            body["default_sort"] = default_sort
        resp = await self._http.post(f"/grids/{grid_id}", json=body)
        return RevisionResult.model_validate(resp.json())

    async def delete(self, grid_id: str) -> None:
        await self._http.delete(f"/grids/{grid_id}")

    async def clone(
        self,
        grid_id: str,
        *,
        target: str,
        title: str | None = None,
        with_data: bool | None = None,
    ) -> OperationResult:
        body: dict[str, Any] = {"target": target}
        if title is not None:
            body["title"] = title
        if with_data is not None:
            body["with_data"] = with_data
        resp = await self._http.post(f"/grids/{grid_id}/clone", json=body)
        return OperationResult.model_validate(resp.json())
