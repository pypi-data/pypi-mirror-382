# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa
from typing import Any, Dict, List, Literal

from pydantic import BaseModel

from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.composio_models import ComposioResult
from ..models.tools.googledrive_models import (
    AddFileSharingPreferenceInput,
    CopyFileInput,
    CreateCommentInput,
    CreateDriveInput,
    CreateFileFromTextInput,
    CreateFileInput,
    CreateFolderInput,
    CreateReplyInput,
    CreateShortcutToFileInput,
    DeleteCommentInput,
    DeleteDriveInput,
    DeletePermissionInput,
    DeleteReplyInput,
    DownloadFileInput,
    EditFileInput,
    EmptyTrashInput,
    FilesModifyLabelsInput,
    FindFileInput,
    FindFolderInput,
    GenerateIdsInput,
)


__all__ = [
    "AddFileSharingPreferenceInput",
    "CopyFileInput",
    "CreateCommentInput",
    "CreateDriveInput",
    "CreateFileFromTextInput",
    "CreateFileInput",
    "CreateFolderInput",
    "CreateReplyInput",
    "CreateShortcutToFileInput",
    "DeleteCommentInput",
    "DeleteDriveInput",
    "DeletePermissionInput",
    "DeleteReplyInput",
    "DownloadFileInput",
    "EditFileInput",
    "EmptyTrashInput",
    "FilesModifyLabelsInput",
    "FindFileInput",
    "FindFolderInput",
    "GenerateIdsInput",
    "add_file_sharing_preference",
    "copy_file",
    "create_comment",
    "create_drive",
    "create_file",
    "create_file_from_text",
    "create_folder",
    "create_reply",
    "create_shortcut_to_file",
    "delete_comment",
    "delete_drive",
    "delete_permission",
    "delete_reply",
    "download_file",
    "edit_file",
    "empty_trash",
    "files_modify_labels",
    "find_file",
    "find_folder",
    "generate_ids",
]


def add_file_sharing_preference(
    *,
    domain: str | None = DEFAULT,
    email_address: str | None = DEFAULT,
    file_id: str,
    role: str,
    type: str,
) -> ComposioResult:
    """Execute Googledrive: Add File Sharing Preference"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = AddFileSharingPreferenceInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googledrive",
        name="add_file_sharing_preference",
        input=input_model.model_dump(),
    )
    return ComposioResult.model_validate(output_model)


def copy_file(*, file_id: str, new_title: str | None = DEFAULT) -> ComposioResult:
    """Execute Googledrive: Copy File"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = CopyFileInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googledrive", name="copy_file", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def create_comment(
    *,
    anchor: str | None = DEFAULT,
    content: str,
    file_id: str,
    quoted_file_content_mime_type: str | None = DEFAULT,
    quoted_file_content_value: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Googledrive: Create Comment"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = CreateCommentInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googledrive", name="create_comment", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def create_drive(
    *,
    backgroundImageFile: dict[str, Any] | None = DEFAULT,
    colorRgb: str | None = DEFAULT,
    hidden: bool | None = DEFAULT,
    name: str,
    requestId: str,
    themeId: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Googledrive: Create Drive"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = CreateDriveInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googledrive", name="create_drive", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def create_file(
    *,
    description: str | None = DEFAULT,
    fields: str | None = DEFAULT,
    mimeType: str | None = DEFAULT,
    name: str | None = DEFAULT,
    parents: list[Any] | None = DEFAULT,
    starred: bool | None = DEFAULT,
) -> ComposioResult:
    """Execute Googledrive: Create File"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = CreateFileInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googledrive", name="create_file", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def create_file_from_text(
    *,
    file_name: str,
    mime_type: str | None = DEFAULT,
    parent_id: str | None = DEFAULT,
    text_content: str,
) -> ComposioResult:
    """Execute Googledrive: Create File From Text"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = CreateFileFromTextInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googledrive",
        name="create_file_from_text",
        input=input_model.model_dump(),
    )
    return ComposioResult.model_validate(output_model)


def create_folder(*, folder_name: str, parent_id: str | None = DEFAULT) -> ComposioResult:
    """Execute Googledrive: Create Folder"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = CreateFolderInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googledrive", name="create_folder", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def create_reply(
    *,
    action: str | None = DEFAULT,
    comment_id: str,
    content: str,
    fields: str | None = DEFAULT,
    file_id: str,
) -> ComposioResult:
    """Execute Googledrive: Create Reply"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = CreateReplyInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googledrive", name="create_reply", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def create_shortcut_to_file(
    *,
    ignoreDefaultVisibility: bool | None = DEFAULT,
    includeLabels: str | None = DEFAULT,
    includePermissionsForView: str | None = DEFAULT,
    keepRevisionForever: bool | None = DEFAULT,
    name: str,
    supportsAllDrives: bool | None = DEFAULT,
    target_id: str,
    target_mime_type: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Googledrive: Create Shortcut To File"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = CreateShortcutToFileInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googledrive",
        name="create_shortcut_to_file",
        input=input_model.model_dump(),
    )
    return ComposioResult.model_validate(output_model)


def delete_comment(*, comment_id: str, file_id: str) -> ComposioResult:
    """Execute Googledrive: Delete Comment"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = DeleteCommentInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googledrive", name="delete_comment", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def delete_drive(
    *,
    allowItemDeletion: bool | None = DEFAULT,
    driveId: str,
    useDomainAdminAccess: bool | None = DEFAULT,
) -> ComposioResult:
    """Execute Googledrive: Delete Drive"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = DeleteDriveInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googledrive", name="delete_drive", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def delete_permission(
    *,
    file_id: str,
    permission_id: str,
    supportsAllDrives: bool | None = DEFAULT,
    useDomainAdminAccess: bool | None = DEFAULT,
) -> ComposioResult:
    """Execute Googledrive: Delete Permission"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = DeletePermissionInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googledrive", name="delete_permission", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def delete_reply(*, comment_id: str, file_id: str, reply_id: str) -> ComposioResult:
    """Execute Googledrive: Delete Reply"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = DeleteReplyInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googledrive", name="delete_reply", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def download_file(
    *,
    file_id: str,
    mime_type: Literal[
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.oasis.opendocument.text",
        "application/rtf",
        "application/pdf",
        "text/plain",
        "application/zip",
        "application/epub+zip",
        "text/markdown",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/x-vnd.oasis.opendocument.spreadsheet",
        "text/csv",
        "text/tab-separated-values",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "application/vnd.oasis.opendocument.presentation",
        "image/jpeg",
        "image/png",
        "image/svg+xml",
        "application/vnd.google-apps.script+json",
        "application/vnd.google-apps.vid",
    ]
    | None = DEFAULT,
) -> ComposioResult:
    """Execute Googledrive: Download File"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = DownloadFileInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googledrive", name="download_file", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def edit_file(
    *, content: str, file_id: str, mime_type: str | None = DEFAULT
) -> ComposioResult:
    """Execute Googledrive: Edit File"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = EditFileInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googledrive", name="edit_file", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def empty_trash(
    *, driveId: str | None = DEFAULT, enforceSingleParent: bool | None = DEFAULT
) -> ComposioResult:
    """Execute Googledrive: Empty Trash"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = EmptyTrashInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googledrive", name="empty_trash", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def files_modify_labels(
    *, file_id: str, kind: str | None = DEFAULT, label_modifications: list[Any]
) -> ComposioResult:
    """Execute Googledrive: Files Modify Labels"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = FilesModifyLabelsInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googledrive", name="files_modify_labels", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def find_file(
    *,
    corpora: Literal["user", "drive", "domain", "allDrives"] | None = DEFAULT,
    driveId: str | None = DEFAULT,
    fields: str | None = DEFAULT,
    includeItemsFromAllDrives: bool | None = DEFAULT,
    orderBy: str | None = DEFAULT,
    pageSize: int | None = DEFAULT,
    pageToken: str | None = DEFAULT,
    q: str | None = DEFAULT,
    spaces: str | None = DEFAULT,
    supportsAllDrives: bool | None = DEFAULT,
) -> ComposioResult:
    """Execute Googledrive: Find File"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = FindFileInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googledrive", name="find_file", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def find_folder(
    *,
    full_text_contains: str | None = DEFAULT,
    full_text_not_contains: str | None = DEFAULT,
    modified_after: str | None = DEFAULT,
    name_contains: str | None = DEFAULT,
    name_exact: str | None = DEFAULT,
    name_not_contains: str | None = DEFAULT,
    starred: bool | None = DEFAULT,
) -> ComposioResult:
    """Execute Googledrive: Find Folder"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = FindFolderInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googledrive", name="find_folder", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)


def generate_ids(
    *,
    count: int | None = DEFAULT,
    space: str | None = DEFAULT,
    type: str | None = DEFAULT,
) -> ComposioResult:
    """Execute Googledrive: Generate Ids"""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GenerateIdsInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="googledrive", name="generate_ids", input=input_model.model_dump()
    )
    return ComposioResult.model_validate(output_model)
