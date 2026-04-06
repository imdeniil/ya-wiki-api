from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# --- Enums ---


class PageType(str, Enum):
    page = "page"
    grid = "grid"
    cloud_page = "cloud_page"
    wysiwyg = "wysiwyg"
    template = "template"


class TextFormat(str, Enum):
    yfm = "yfm"
    wom = "wom"
    plain = "plain"


class ColumnType(str, Enum):
    string = "string"
    number = "number"
    date = "date"
    select = "select"
    staff = "staff"
    checkbox = "checkbox"
    ticket = "ticket"
    ticket_field = "ticket_field"


class BGColor(str, Enum):
    blue = "blue"
    yellow = "yellow"
    pink = "pink"
    red = "red"
    green = "green"
    mint = "mint"
    grey = "grey"
    orange = "orange"
    magenta = "magenta"
    purple = "purple"
    copper = "copper"
    ocean = "ocean"


class SortDirection(str, Enum):
    asc = "asc"
    desc = "desc"


class OperationType(str, Enum):
    test = "test"
    export = "export"
    move = "move"
    clone = "clone"
    clone_grid = "clone_grid"
    clone_inline_grid = "clone_inline_grid"
    apply_template = "apply_template"
    e2e_prepare = "e2e_prepare"
    e2e_cleanup = "e2e_cleanup"


class UserPermission(str, Enum):
    create_page = "create_page"
    delete = "delete"
    edit = "edit"
    view = "view"
    comment = "comment"
    change_authors = "change_authors"
    change_acl = "change_acl"
    set_redirect = "set_redirect"
    manage_invite = "manage_invite"
    view_invite = "view_invite"
    admin = "admin"


class ResourceType(str, Enum):
    attachment = "attachment"
    grid = "grid"
    sharepoint_resource = "sharepoint_resource"


class Ms365DocType(str, Enum):
    docx = "docx"
    pptx = "pptx"
    xlsx = "xlsx"


class TicketFieldType(str, Enum):
    assignee = "assignee"
    components = "components"
    created_at = "created_at"
    deadline = "deadline"
    description = "description"
    end = "end"
    estimation = "estimation"
    fixversions = "fixversions"
    followers = "followers"
    key = "key"
    last_comment_updated_at = "last_comment_updated_at"
    original_estimation = "original_estimation"
    parent = "parent"
    pending_reply_from = "pending_reply_from"
    priority = "priority"
    project = "project"
    queue = "queue"
    reporter = "reporter"
    resolution = "resolution"
    resolved_at = "resolved_at"
    sprint = "sprint"
    start = "start"
    status = "status"
    status_start_time = "status_start_time"
    status_type = "status_type"
    storypoints = "storypoints"
    subject = "subject"
    tags = "tags"
    type = "type"
    updated_at = "updated_at"
    votes = "votes"


# --- Common Schemas ---


class UserIdentity(BaseModel):
    uid: str | None = None
    cloud_uid: str | None = None


class UserIdentityExtended(BaseModel):
    uid: str | None = None
    cloud_uid: str | None = None
    username: str | None = None


class UserSchema(BaseModel):
    id: int
    identity: UserIdentity | None = None
    username: str | None = None
    display_name: str | None = None
    is_dismissed: bool | None = None


class UnresolvedUserSchema(BaseModel):
    username: str | None = None
    identity: UserIdentity | None = None


class TicketSchema(BaseModel):
    key: str
    resolved: bool | None = None


class TrackerEnumField(BaseModel):
    display: str | None = None
    key: str | None = None


class PageIdentity(BaseModel):
    id: int | None = None
    slug: str | None = None


# --- Page Schemas ---


class PageAttributes(BaseModel):
    created_at: datetime | None = None
    modified_at: datetime | None = None
    lang: str | None = None
    is_readonly: bool | None = None
    comments_count: int | None = None
    comments_enabled: bool | None = None
    keywords: list[str] | None = None
    is_collaborative: bool | None = None
    is_draft: bool | None = None


class Breadcrumb(BaseModel):
    id: int | None = None
    title: str
    slug: str
    page_exists: bool | None = None


class RedirectTarget(BaseModel):
    id: int
    slug: str | None = None
    title: str | None = None
    page_type: PageType | None = None


class Redirect(BaseModel):
    page_id: int | None = None
    redirect_target: RedirectTarget | None = None


class CloudPageEmbed(BaseModel):
    iframe_src: str | None = None
    edit_src: str | None = None


class CloudPageContent(BaseModel):
    embed: CloudPageEmbed | None = None
    acl_management: str | None = None
    type: Ms365DocType | None = None
    filename: str | None = None
    error: str | None = None


class Page(BaseModel):
    id: int
    slug: str | None = None
    title: str | None = None
    page_type: PageType | None = None
    attributes: PageAttributes | None = None
    breadcrumbs: list[Breadcrumb] | None = None
    content: Any | None = None
    redirect: Redirect | None = None


class DeletePageResult(BaseModel):
    recovery_token: str


class Ms365UploadSession(BaseModel):
    upload_to: str
    upload_session: str


# --- Operation Schema ---


class OperationIdentity(BaseModel):
    type: OperationType
    id: str


class OperationResult(BaseModel):
    operation: OperationIdentity
    dry_run: bool = False
    status_url: str | None = None


# --- Grid Schemas ---


class GridSortItem(BaseModel):
    slug: str | None = None
    title: str | None = None
    direction: SortDirection | None = None


class ColumnSchema(BaseModel):
    id: str | None = None
    slug: str | None = None
    title: str | None = None
    type: ColumnType | None = None
    required: bool | None = None
    width: int | None = None
    width_units: str | None = None
    pinned: str | None = None
    color: BGColor | None = None
    multiple: bool | None = None
    format: TextFormat | None = None
    ticket_field: TicketFieldType | None = None
    select_options: list[str] | None = None
    mark_rows: bool | None = None
    description: str | None = None


class NewColumn(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    type: ColumnType
    slug: str
    required: bool = False
    id: str | None = None
    width: int | None = None
    width_units: str | None = None
    pinned: str | None = None
    color: BGColor | None = None
    multiple: bool | None = None
    format: TextFormat | None = None
    ticket_field: TicketFieldType | None = None
    select_options: list[str] | None = None
    mark_rows: bool | None = None
    description: str | None = Field(None, max_length=1024)


class GridStructure(BaseModel):
    default_sort: list[GridSortItem] | None = None
    columns: list[ColumnSchema] | None = None


class GridRow(BaseModel):
    id: str
    row: list[Any] | None = None
    pinned: bool | None = None
    color: BGColor | None = None


class GridAttributes(BaseModel):
    created_at: datetime | None = None
    modified_at: datetime | None = None


class Grid(BaseModel):
    id: str | int
    created_at: datetime | None = None
    title: str | None = None
    page: PageIdentity | None = None
    structure: GridStructure | None = None
    rich_text_format: TextFormat | None = None
    rows: list[GridRow] | None = None
    revision: str | None = None
    attributes: GridAttributes | None = None
    user_permissions: list[UserPermission] | None = None
    template_id: int | None = None


class RevisionResult(BaseModel):
    revision: str


class AddRowsResult(BaseModel):
    revision: str
    results: list[GridRow] | None = None


class UpdateCellRequest(BaseModel):
    row_id: int | str
    column_slug: str
    value: Any = None


class CellResult(BaseModel):
    row_id: str
    column_slug: str
    value: Any = None


class UpdateCellsResult(BaseModel):
    revision: str
    cells: list[CellResult] | None = None


# --- Page Resources Schemas ---


class AttachmentItem(BaseModel):
    id: int
    name: str | None = None
    download_url: str | None = None
    size: str | None = None
    description: str | None = None
    user: UserSchema | None = None
    created_at: datetime | None = None
    mimetype: str | None = None
    has_preview: bool | None = None


class PageGridItem(BaseModel):
    id: str
    title: str | None = None
    created_at: datetime | None = None


class SharepointItem(BaseModel):
    id: str
    title: str | None = None
    created_at: datetime | None = None
    doctype: Ms365DocType | None = None


class Resource(BaseModel):
    type: ResourceType
    item: AttachmentItem | PageGridItem | SharepointItem | dict[str, Any]


# --- Paginated Responses ---


class PaginatedGrids(BaseModel):
    results: list[PageGridItem]
    next_cursor: str | None = None
    prev_cursor: str | None = None
    has_next: bool | None = None
    page_id: int | None = None


class PaginatedPages(BaseModel):
    results: list[PageIdentity]
    next_cursor: str | None = None
    prev_cursor: str | None = None
    page_id: int | None = None


class PaginatedResources(BaseModel):
    results: list[Resource]
    next_cursor: str | None = None
    prev_cursor: str | None = None
