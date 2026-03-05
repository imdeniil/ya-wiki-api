"""
Smoke-test every Yandex Wiki API endpoint on real data.

Reads credentials from .env.local:
    WIKI_TOKEN=...
    ORG_ID=...          (Yandex 360)
    CLOUD_ORG_ID=...    (or Yandex Cloud)

Run:
    uv run python test_all_endpoints.py
"""

from __future__ import annotations

import os
import sys
import time

from dotenv import load_dotenv

from ya_wiki_api import WikiClient

load_dotenv(".env.local")

TOKEN = os.environ.get("WIKI_TOKEN", "")
ORG_ID = os.environ.get("ORG_ID")
CLOUD_ORG_ID = os.environ.get("CLOUD_ORG_ID")

if not TOKEN or TOKEN == "your-oauth-token-here":
    print("Set WIKI_TOKEN in .env.local")
    sys.exit(1)

TEST_SLUG = "ya-wiki-api-test/smoke"
TEST_GRID_SLUG = "ya-wiki-api-test/smoke-grid"

passed: list[str] = []
failed: list[tuple[str, str]] = []


def step(name: str):
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")


def ok(name: str, detail: str = ""):
    tag = f"  OK: {name}"
    if detail:
        tag += f" — {detail}"
    print(tag)
    passed.append(name)


def fail(name: str, err: Exception):
    msg = f"{type(err).__name__}: {err}"
    print(f"  FAIL: {name} — {msg}")
    failed.append((name, msg))


def main():
    client = WikiClient(token=TOKEN, org_id=ORG_ID, cloud_org_id=CLOUD_ORG_ID)

    page_id: int | None = None
    grid_id: str | None = None
    grid_revision: str | None = None
    row_id: str | None = None
    cloned_page_id: int | None = None

    # ── Pages ──────────────────────────────────────────────

    # 1. Create page
    step("1. pages.create")
    try:
        page = client.pages.create(
            page_type="wysiwyg",
            title="Smoke Test Page",
            slug=TEST_SLUG,
            content="Hello from ya-wiki-api smoke test",
        )
        page_id = page.id
        ok("pages.create", f"id={page_id}")
    except Exception as e:
        fail("pages.create", e)

    # 2. Get page by slug
    step("2. pages.get")
    try:
        page = client.pages.get(slug=TEST_SLUG, fields="attributes,content")
        ok("pages.get", f"title={page.title!r}")
    except Exception as e:
        fail("pages.get", e)

    # 3. Get page by ID
    step("3. pages.get_by_id")
    if page_id:
        try:
            page = client.pages.get_by_id(page_id, fields="attributes,breadcrumbs")
            ok("pages.get_by_id", f"slug={page.slug!r}")
        except Exception as e:
            fail("pages.get_by_id", e)
    else:
        fail("pages.get_by_id", RuntimeError("no page_id from create"))

    # 4. Update page
    step("4. pages.update")
    if page_id:
        try:
            page = client.pages.update(page_id, title="Smoke Test Page (updated)", content="Updated content")
            ok("pages.update", f"title={page.title!r}")
        except Exception as e:
            fail("pages.update", e)
    else:
        fail("pages.update", RuntimeError("no page_id"))

    # 5. Append content
    step("5. pages.append_content")
    if page_id:
        try:
            page = client.pages.append_content(page_id, content="\n\nAppended line", location="bottom")
            ok("pages.append_content", f"id={page.id}")
        except Exception as e:
            fail("pages.append_content", e)
    else:
        fail("pages.append_content", RuntimeError("no page_id"))

    # 6. Get page grids (empty at this point)
    step("6. pages.get_grids")
    if page_id:
        try:
            grids = client.pages.get_grids(page_id)
            ok("pages.get_grids", f"count={len(grids.results)}")
        except Exception as e:
            fail("pages.get_grids", e)
    else:
        fail("pages.get_grids", RuntimeError("no page_id"))

    # 7. Get page resources
    step("7. pages.get_resources")
    if page_id:
        try:
            resources = client.pages.get_resources(page_id)
            ok("pages.get_resources", f"count={len(resources.results)}")
        except Exception as e:
            fail("pages.get_resources", e)
    else:
        fail("pages.get_resources", RuntimeError("no page_id"))

    # ── Grids ──────────────────────────────────────────────

    # 8. Create grid
    step("8. grids.create")
    if page_id:
        try:
            grid = client.grids.create(title="Smoke Test Table", page_id=page_id)
            grid_id = str(grid.id)
            grid_revision = grid.revision
            ok("grids.create", f"id={grid_id}")
        except Exception as e:
            fail("grids.create", e)
    else:
        fail("grids.create", RuntimeError("no page_id"))

    # 9. Add columns
    step("9. grids.columns.add")
    if grid_id:
        try:
            result = client.grids.columns.add(
                grid_id,
                columns=[
                    {"slug": "name", "title": "Name", "type": "string", "required": False},
                    {"slug": "age", "title": "Age", "type": "number", "required": False},
                    {"slug": "active", "title": "Active", "type": "checkbox", "required": False},
                ],
                revision=grid_revision,
            )
            grid_revision = result.revision
            ok("grids.columns.add", f"revision={grid_revision}")
        except Exception as e:
            fail("grids.columns.add", e)
    else:
        fail("grids.columns.add", RuntimeError("no grid_id"))

    # 10. Get grid (to see columns and get slugs)
    step("10. grids.get")
    col_slugs: list[str] = []
    if grid_id:
        try:
            grid = client.grids.get(grid_id)
            grid_revision = grid.revision
            if grid.structure and grid.structure.columns:
                col_slugs = [c.slug for c in grid.structure.columns if c.slug]
            ok("grids.get", f"columns={col_slugs}")
        except Exception as e:
            fail("grids.get", e)
    else:
        fail("grids.get", RuntimeError("no grid_id"))

    # 11. Add rows
    step("11. grids.rows.add")
    if grid_id and len(col_slugs) >= 2:
        try:
            name_col, age_col = col_slugs[0], col_slugs[1]
            result = client.grids.rows.add(
                grid_id,
                rows=[
                    {name_col: "Alice", age_col: 30},
                    {name_col: "Bob", age_col: 25},
                    {name_col: "Carol", age_col: 35},
                ],
                revision=grid_revision,
            )
            grid_revision = result.revision
            if result.results:
                row_id = result.results[0].id
            ok("grids.rows.add", f"added {len(result.results or [])} rows, first_row={row_id}")
        except Exception as e:
            fail("grids.rows.add", e)
    else:
        fail("grids.rows.add", RuntimeError("no grid_id or columns"))

    # 12. Update cells
    step("12. grids.cells.update")
    if grid_id and row_id and col_slugs:
        try:
            result = client.grids.cells.update(
                grid_id,
                cells=[{"row_id": row_id, "column_slug": col_slugs[0], "value": "Alice (updated)"}],
                revision=grid_revision,
            )
            grid_revision = result.revision
            ok("grids.cells.update", f"revision={grid_revision}")
        except Exception as e:
            fail("grids.cells.update", e)
    else:
        fail("grids.cells.update", RuntimeError("no grid/row/col"))

    # 13. Move rows
    step("13. grids.rows.move")
    if grid_id and row_id:
        try:
            result = client.grids.rows.move(grid_id, row_id=row_id, position=2, revision=grid_revision)
            grid_revision = result.revision
            ok("grids.rows.move", f"revision={grid_revision}")
        except Exception as e:
            fail("grids.rows.move", e)
    else:
        fail("grids.rows.move", RuntimeError("no grid/row"))

    # 14. Move columns
    step("14. grids.columns.move")
    if grid_id and len(col_slugs) >= 2:
        try:
            result = client.grids.columns.move(
                grid_id, column_slug=col_slugs[1], position=0, revision=grid_revision
            )
            grid_revision = result.revision
            ok("grids.columns.move", f"revision={grid_revision}")
        except Exception as e:
            fail("grids.columns.move", e)
    else:
        fail("grids.columns.move", RuntimeError("no grid/columns"))

    # 15. Update grid (title)
    step("15. grids.update")
    if grid_id:
        try:
            result = client.grids.update(grid_id, title="Smoke Test Table (updated)", revision=grid_revision)
            grid_revision = result.revision
            ok("grids.update", f"revision={grid_revision}")
        except Exception as e:
            fail("grids.update", e)
    else:
        fail("grids.update", RuntimeError("no grid_id"))

    # 16. Delete rows
    step("16. grids.rows.delete")
    if grid_id and row_id:
        try:
            result = client.grids.rows.delete(grid_id, row_ids=[row_id], revision=grid_revision)
            grid_revision = result.revision
            ok("grids.rows.delete", f"revision={grid_revision}")
        except Exception as e:
            fail("grids.rows.delete", e)
    else:
        fail("grids.rows.delete", RuntimeError("no grid/row"))

    # 17. Delete columns
    step("17. grids.columns.delete")
    if grid_id and len(col_slugs) >= 3:
        try:
            # refresh revision
            grid = client.grids.get(grid_id)
            grid_revision = grid.revision
            result = client.grids.columns.delete(
                grid_id, column_slugs=[col_slugs[2]], revision=grid_revision
            )
            grid_revision = result.revision
            ok("grids.columns.delete", f"revision={grid_revision}")
        except Exception as e:
            fail("grids.columns.delete", e)
    else:
        fail("grids.columns.delete", RuntimeError("no grid/columns"))

    # 18. Clone grid
    step("18. grids.clone")
    if grid_id:
        try:
            op = client.grids.clone(grid_id, target=TEST_GRID_SLUG, title="Cloned Table", with_data=True)
            ok("grids.clone", f"operation={op.operation.type}, status_url={op.status_url}")
            time.sleep(2)  # wait for async clone
        except Exception as e:
            fail("grids.clone", e)
    else:
        fail("grids.clone", RuntimeError("no grid_id"))

    # 19. Delete grid
    step("19. grids.delete")
    if grid_id:
        try:
            client.grids.delete(grid_id)
            ok("grids.delete", f"deleted {grid_id}")
        except Exception as e:
            fail("grids.delete", e)
    else:
        fail("grids.delete", RuntimeError("no grid_id"))

    # 20. Clone page
    step("20. pages.clone")
    if page_id:
        try:
            op = client.pages.clone(page_id, target=f"{TEST_SLUG}-clone", title="Cloned Page")
            ok("pages.clone", f"operation={op.operation.type}, status_url={op.status_url}")
            time.sleep(2)  # wait for async clone
            # get cloned page id for cleanup
            try:
                cloned = client.pages.get(slug=f"{TEST_SLUG}-clone")
                cloned_page_id = cloned.id
            except Exception:
                pass
        except Exception as e:
            fail("pages.clone", e)
    else:
        fail("pages.clone", RuntimeError("no page_id"))

    # 21. Delete page
    step("21. pages.delete")
    if page_id:
        try:
            result = client.pages.delete(page_id)
            ok("pages.delete", f"recovery_token={result.recovery_token}")
        except Exception as e:
            fail("pages.delete", e)
    else:
        fail("pages.delete", RuntimeError("no page_id"))

    # ── Cleanup ────────────────────────────────────────────

    step("Cleanup")
    # delete cloned page
    if cloned_page_id:
        try:
            client.pages.delete(cloned_page_id)
            print(f"  Deleted cloned page {cloned_page_id}")
        except Exception as e:
            print(f"  Cleanup cloned page: {e}")
    # delete grid clone page
    try:
        clone_page = client.pages.get(slug=TEST_GRID_SLUG)
        client.pages.delete(clone_page.id)
        print(f"  Deleted grid clone page {clone_page.id}")
    except Exception:
        print("  Grid clone page not found (ok)")

    client.close()

    # ── Summary ────────────────────────────────────────────

    print(f"\n{'='*60}")
    print(f"  RESULTS: {len(passed)} passed, {len(failed)} failed")
    print(f"{'='*60}")
    if failed:
        for name, msg in failed:
            print(f"  FAIL: {name} — {msg}")
        sys.exit(1)
    else:
        print("  All endpoints OK!")


if __name__ == "__main__":
    main()
