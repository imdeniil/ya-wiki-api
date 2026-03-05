# ya-wiki-api

Типизированный Python-клиент для [Yandex Wiki API](https://yandex.ru/support/wiki/ru/api-ref/about). Синхронный и асинхронный. Все 21 эндпоинт покрыты и протестированы на реальном API.

## Установка

```bash
pip install ya-wiki-api
```

## Быстрый старт

```python
from ya_wiki_api import WikiClient

with WikiClient(token="your-oauth-token", org_id="your-org-id") as client:
    # Страницы
    page = client.pages.create(
        page_type="wysiwyg",
        title="Моя страница",
        slug="path/to/page",
        content="Привет!",
    )
    page = client.pages.get(slug="path/to/page")
    page = client.pages.get_by_id(page.id, fields="attributes,content")
    client.pages.update(page.id, content="Обновлённый текст")
    client.pages.append_content(page.id, content="\nЕщё текст", location="bottom")

    # Динамические таблицы
    grid = client.grids.create(title="Моя таблица", page_id=page.id)
    client.grids.columns.add(grid.id, columns=[
        {"slug": "name", "title": "Имя", "type": "string", "required": False},
        {"slug": "score", "title": "Баллы", "type": "number", "required": False},
    ])
    client.grids.rows.add(grid.id, rows=[
        {"name": "Алиса", "score": 95},
        {"name": "Боб", "score": 87},
    ])
    client.grids.cells.update(grid.id, cells=[
        {"row_id": 1, "column_slug": "score", "value": 100},
    ])

    # Очистка
    client.grids.delete(grid.id)
    client.pages.delete(page.id)
```

## Async

```python
from ya_wiki_api import AsyncWikiClient

async with AsyncWikiClient(token="...", org_id="...") as client:
    page = await client.pages.get(slug="my/page")
    grid = await client.grids.get("grid-uuid")
```

## Аутентификация

**OAuth 2.0** (Яндекс 360 для бизнеса):
```python
client = WikiClient(token="oauth-token", org_id="org-id")
```

**IAM-токен** (Yandex Cloud):
```python
client = WikiClient(token="iam-token", cloud_org_id="cloud-org-id", is_iam=True)
```

Получение OAuth-токена:
1. Создайте приложение на https://oauth.yandex.ru/
2. Выберите «Для доступа к API или отладки»
3. Добавьте права: `wiki:write` (полный доступ) или `wiki:read` (только чтение)
4. Получите токен: `https://oauth.yandex.ru/authorize?response_type=token&client_id=<ClientID>`

## Покрытие API

### Страницы (`client.pages`)

| Метод | Эндпоинт |
|-------|----------|
| `get(slug)` | `GET /v1/pages?slug=...` |
| `get_by_id(id)` | `GET /v1/pages/{id}` |
| `create(...)` | `POST /v1/pages` |
| `update(id, ...)` | `POST /v1/pages/{id}` |
| `delete(id)` | `DELETE /v1/pages/{id}` |
| `clone(id, target)` | `POST /v1/pages/{id}/clone` |
| `append_content(id, content)` | `POST /v1/pages/{id}/append-content` |
| `get_grids(id)` | `GET /v1/pages/{id}/grids` |
| `get_resources(id)` | `GET /v1/pages/{id}/resources` |

### Таблицы (`client.grids`)

| Метод | Эндпоинт |
|-------|----------|
| `get(id)` | `GET /v1/grids/{id}` |
| `create(...)` | `POST /v1/grids` |
| `update(id, ...)` | `POST /v1/grids/{id}` |
| `delete(id)` | `DELETE /v1/grids/{id}` |
| `clone(id, target)` | `POST /v1/grids/{id}/clone` |
| `rows.add(id, rows)` | `POST /v1/grids/{id}/rows` |
| `rows.delete(id, row_ids)` | `DELETE /v1/grids/{id}/rows` |
| `rows.move(id, row_id)` | `POST /v1/grids/{id}/rows/move` |
| `columns.add(id, columns)` | `POST /v1/grids/{id}/columns` |
| `columns.delete(id, slugs)` | `DELETE /v1/grids/{id}/columns` |
| `columns.move(id, slug)` | `POST /v1/grids/{id}/columns/move` |
| `cells.update(id, cells)` | `POST /v1/grids/{id}/cells` |

## Обработка ошибок

```python
from ya_wiki_api import WikiAPIError

try:
    client.pages.get(slug="nonexistent")
except WikiAPIError as e:
    print(e.status_code)  # 404
    print(e.detail)       # {"error_code": "...", "message": "..."}
```

## Лицензия

MIT
