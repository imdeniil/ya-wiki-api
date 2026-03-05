# ya-wiki-api — справочник для LLM

Ты работаешь с Python-клиентом для Yandex Wiki API. Пакет: `ya-wiki-api` (PyPI).

## Установка

```python
# pip
pip install ya-wiki-api

# uv
uv add ya-wiki-api
```

## Инициализация

```python
from ya_wiki_api import WikiClient, WikiAPIError

# OAuth (Яндекс 360)
client = WikiClient(token="y0_...", org_id="123456")

# IAM (Yandex Cloud)
client = WikiClient(token="t1.9e...", cloud_org_id="bpf...", is_iam=True)

# Обязательно закрывай после использования
client.close()
# или через context manager:
with WikiClient(token="...", org_id="...") as client:
    ...
```

## Структура клиента

```
client.pages          — работа со страницами
client.grids          — работа с таблицами
client.grids.rows     — строки таблицы
client.grids.columns  — столбцы таблицы
client.grids.cells    — ячейки таблицы
```

---

## Страницы — client.pages

### Получить страницу по slug

```python
page = client.pages.get(slug="users/ivanov/my-page")
page = client.pages.get(slug="users/ivanov/my-page", fields="attributes,content,breadcrumbs")
# page.id -> int
# page.title -> str
# page.content -> str (только если запросил fields="content")
# page.attributes.created_at -> datetime
```

### Получить страницу по ID

```python
page = client.pages.get_by_id(12345, fields="attributes,content")
```

### Создать страницу

```python
page = client.pages.create(
    page_type="wysiwyg",   # "page", "wysiwyg", "grid", "cloud_page", "template"
    title="Название",
    slug="team/docs/new-page",
    content="Текст страницы",
)
# page.id -> ID созданной страницы
```

### Обновить страницу

```python
page = client.pages.update(
    12345,
    title="Новое название",        # необязательно
    content="Новый текст",          # необязательно
    allow_merge=True,               # 3-way merge при конфликтах
)
```

### Дописать текст

```python
# В конец
client.pages.append_content(12345, content="Дополнительный текст", location="bottom")

# В начало
client.pages.append_content(12345, content="Текст в начало", location="top")

# Под якорем
client.pages.append_content(12345, content="Текст", anchor_name="#section-name")
```

### Удалить страницу

```python
result = client.pages.delete(12345)
# result.recovery_token -> str (для восстановления)
```

### Клонировать страницу

```python
op = client.pages.clone(12345, target="team/docs/copy")
# op.status_url -> URL для проверки статуса операции
```

### Список таблиц на странице

```python
grids = client.pages.get_grids(12345, page_size=50)
# grids.results -> list[PageGridItem]  (id, title, created_at)
# grids.has_next -> bool
# grids.next_cursor -> str (для пагинации)
```

### Список ресурсов (вложения, файлы)

```python
resources = client.pages.get_resources(12345, types="attachment", q="report")
# resources.results -> list[Resource]
# resource.type -> "attachment" | "grid" | "sharepoint_resource"
# resource.item -> AttachmentItem | PageGridItem | SharepointItem
```

---

## Таблицы — client.grids

### Создать таблицу

```python
grid = client.grids.create(title="Моя таблица", page_id=12345)
# grid.id -> str (UUID)
# grid.revision -> str
```

### Получить таблицу

```python
grid = client.grids.get("uuid-id")
grid = client.grids.get("uuid-id", filter="[status] ~ done", sort="name, -created")
# grid.structure.columns -> list[ColumnSchema]
# grid.rows -> list[GridRow]
# grid.revision -> str
```

### Обновить таблицу (название, сортировка)

```python
result = client.grids.update("uuid-id", title="Новое название", revision="5")
# result.revision -> str
```

### Удалить таблицу

```python
client.grids.delete("uuid-id")  # возвращает None
```

### Клонировать таблицу

```python
op = client.grids.clone("uuid-id", target="team/table-copy", with_data=True)
```

---

## Столбцы — client.grids.columns

### Добавить столбцы

**Важно: `slug` и `required` обязательны, хотя в документации Яндекса помечены как optional.**

```python
result = client.grids.columns.add("grid-uuid", columns=[
    {"slug": "name", "title": "Имя", "type": "string", "required": False},
    {"slug": "age", "title": "Возраст", "type": "number", "required": False},
    {"slug": "done", "title": "Готово", "type": "checkbox", "required": False},
    {"slug": "role", "title": "Роль", "type": "select", "required": False, "select_options": ["dev", "pm", "qa"]},
])
# result.revision -> str
```

Типы столбцов: `string`, `number`, `date`, `select`, `staff`, `checkbox`, `ticket`, `ticket_field`.

### Удалить столбцы

```python
result = client.grids.columns.delete("grid-uuid", column_slugs=["age", "done"], revision="3")
```

### Переместить столбец

```python
result = client.grids.columns.move("grid-uuid", column_slug="name", position=0, revision="4")
```

---

## Строки — client.grids.rows

### Добавить строки

```python
result = client.grids.rows.add("grid-uuid", rows=[
    {"name": "Алиса", "age": 30},
    {"name": "Боб", "age": 25},
])
# result.revision -> str
# result.results -> list[GridRow]  (с id каждой строки)
# result.results[0].id -> str
```

### Удалить строки

```python
result = client.grids.rows.delete("grid-uuid", row_ids=["1", "2"], revision="5")
```

### Переместить строку

```python
result = client.grids.rows.move("grid-uuid", row_id="1", position=0, revision="6")
```

---

## Ячейки — client.grids.cells

### Обновить ячейки

```python
result = client.grids.cells.update("grid-uuid", cells=[
    {"row_id": 1, "column_slug": "name", "value": "Алиса (ред.)"},
    {"row_id": 2, "column_slug": "age", "value": 26},
    {"row_id": 1, "column_slug": "done", "value": True},
], revision="7")
# result.revision -> str
# result.cells -> list[CellResult]
```

---

## Обработка ошибок

```python
from ya_wiki_api import WikiAPIError

try:
    page = client.pages.get(slug="nonexistent/page")
except WikiAPIError as e:
    e.status_code   # 404
    e.detail        # {"error_code": "NOT_FOUND", "message": "..."}
```

Типичные коды:
- `401` — невалидный/просроченный токен
- `400` — ошибка валидации (тело содержит `error_code`, `message`, `details`)
- `403` — нет прав
- `404` — страница/таблица не найдена

---

## Типичные сценарии

### Создать страницу с таблицей

```python
with WikiClient(token=TOKEN, org_id=ORG) as client:
    page = client.pages.create(page_type="wysiwyg", title="Отчёт", slug="team/report", content="# Отчёт")
    grid = client.grids.create(title="Данные", page_id=page.id)
    client.grids.columns.add(grid.id, columns=[
        {"slug": "task", "title": "Задача", "type": "string", "required": True},
        {"slug": "status", "title": "Статус", "type": "select", "required": False, "select_options": ["todo", "doing", "done"]},
    ])
    client.grids.rows.add(grid.id, rows=[
        {"task": "Подготовить данные", "status": "done"},
        {"task": "Написать отчёт", "status": "doing"},
    ])
```

### Прочитать таблицу и обновить строки

```python
with WikiClient(token=TOKEN, org_id=ORG) as client:
    grid = client.grids.get("grid-uuid")
    col_map = {c.slug: c for c in grid.structure.columns}
    for row in grid.rows:
        row_id = row.id
        # row.row — список значений в порядке столбцов

    # Обновить конкретные ячейки
    client.grids.cells.update("grid-uuid", cells=[
        {"row_id": row_id, "column_slug": "status", "value": "done"},
    ], revision=grid.revision)
```

### Найти страницу и дописать текст

```python
with WikiClient(token=TOKEN, org_id=ORG) as client:
    page = client.pages.get(slug="team/log", fields="content")
    client.pages.append_content(page.id, content=f"\n- {new_entry}", location="bottom")
```

---

## Важные нюансы

1. **`fields` по умолчанию не возвращает `content`, `attributes`, `breadcrumbs`, `redirect`** — запрашивай явно: `fields="attributes,content"`
2. **`revision`** — при изменении таблиц API возвращает новую revision. Передавай её в следующий запрос для оптимистичной блокировки.
3. **Колонки: `slug` и `required` обязательны** при добавлении, несмотря на документацию.
4. **Пагинация** — используй `cursor`/`next_cursor` для итерации по большим спискам.
5. **Async** — все методы доступны через `AsyncWikiClient` с `await`.
