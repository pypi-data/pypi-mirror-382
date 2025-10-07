# This is a generated file by scripts/codegen/composio.py, do not edit manually
# ruff: noqa: E501  # Ignore line length issues in generated files
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class AddFileSharingPreferenceInput(BaseModel):
    """Input model for GOOGLEDRIVE_ADD_FILE_SHARING_PREFERENCE"""

    domain: Optional[str] = Field(
        default=None,
        description="""Domain to grant permission to (e.g., 'example.com'). Required if 'type' is 'domain'. Please provide a value of type string.""",
    )  # noqa: E501

    email_address: Optional[str] = Field(
        default=None,
        description="""Email address of the user or group. Required if 'type' is 'user' or 'group'. Please provide a value of type string.""",
    )  # noqa: E501

    file_id: str = Field(
        description="""Unique identifier of the file to update sharing settings for. Use GOOGLEDRIVE_FIND_FILE or GOOGLEDRIVE_LIST_FILES to get valid file IDs from your Google Drive. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    role: str = Field(
        description="""Permission role to grant. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    type: str = Field(
        description="""Type of grantee for the permission. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501


class CopyFileInput(BaseModel):
    """Input model for GOOGLEDRIVE_COPY_FILE"""

    file_id: str = Field(
        description="""The unique identifier for the file on Google Drive that you want to copy. This ID can be retrieved from the file's shareable link or via other Google Drive API calls. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    new_title: Optional[str] = Field(
        default=None,
        description="""The title to assign to the new copy of the file. If not provided, the copied file will have the same title as the original, prefixed with 'Copy of '. Please provide a value of type string.""",
    )  # noqa: E501


class CreateCommentInput(BaseModel):
    """Input model for GOOGLEDRIVE_CREATE_COMMENT"""

    anchor: Optional[str] = Field(
        default=None,
        description="""A JSON string representing the region of the document to which the comment is anchored (e.g., {'type': 'line', 'line': 12}). Please provide a value of type string.""",
    )  # noqa: E501

    content: str = Field(
        description="""The plain text content of the comment. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    file_id: str = Field(
        description="""The ID of the file. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    quoted_file_content_mime_type: Optional[str] = Field(
        default=None,
        description="""The MIME type of the quoted content. Please provide a value of type string.""",
    )  # noqa: E501

    quoted_file_content_value: Optional[str] = Field(
        default=None,
        description="""The quoted content itself. Please provide a value of type string.""",
    )  # noqa: E501


class CreateDriveInput(BaseModel):
    """Input model for GOOGLEDRIVE_CREATE_DRIVE"""

    backgroundImageFile: Optional[dict[str, Any]] = Field(
        default=None,
        description="""An image file and cropping parameters from which a background image for this shared drive is set. This is a write only field; it can only be set on drive.drives.update requests that don't set themeId. When specified, all fields of the backgroundImageFile must be set.""",
    )  # noqa: E501

    colorRgb: Optional[str] = Field(
        default=None,
        description="""The color of this shared drive as an RGB hex string. It can only be set on a drive.drives.update request that does not set themeId. Please provide a value of type string.""",
    )  # noqa: E501

    hidden: Optional[bool] = Field(
        default=False,
        description="""Whether the shared drive is hidden from default view. Please provide a value of type boolean.""",
    )  # noqa: E501

    name: str = Field(
        description="""The name of this shared drive. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    requestId: str = Field(
        description="""An ID, such as a random UUID, which uniquely identifies this user's request for idempotent creation of a shared drive. A repeated request by the same user and with the same request ID will avoid creating duplicates by attempting to create the same shared drive. If the shared drive already exists a 409 error will be returned. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    themeId: Optional[str] = Field(
        default=None,
        description="""The ID of the theme from which the background image and color will be set. The set of possible driveThemes can be retrieved from a drive.about.get response. When not specified on a drive.drives.create request, a random theme is chosen from which the background image and color are set. This is a write-only field; it can only be set on requests that don't set colorRgb or backgroundImageFile. Please provide a value of type string.""",
    )  # noqa: E501


class CreateFileInput(BaseModel):
    """Input model for GOOGLEDRIVE_CREATE_FILE"""

    description: Optional[str] = Field(
        default=None,
        description="""A short description of the file. Please provide a value of type string.""",
    )  # noqa: E501

    fields: Optional[str] = Field(
        default=None,
        description="""A comma-separated list of fields to include in the response. Please provide a value of type string.""",
    )  # noqa: E501

    mimeType: Optional[str] = Field(
        default=None,
        description="""The MIME type of the file. Please provide a value of type string.""",
    )  # noqa: E501

    name: Optional[str] = Field(
        default=None,
        description="""The name of the file. Please provide a value of type string.""",
    )  # noqa: E501

    parents: Optional[list[Any]] = Field(
        default=None, description="""The IDs of parent folders."""
    )  # noqa: E501

    starred: Optional[bool] = Field(
        default=None,
        description="""Whether the user has starred the file. Please provide a value of type boolean.""",
    )  # noqa: E501


class CreateFileFromTextInput(BaseModel):
    """Input model for GOOGLEDRIVE_CREATE_FILE_FROM_TEXT"""

    file_name: str = Field(
        description="""Desired name for the new file on Google Drive. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    mime_type: Optional[str] = Field(
        default="text/plain",
        description="""MIME type for the new file, determining how Google Drive interprets its content. Please provide a value of type string.""",
    )  # noqa: E501

    parent_id: Optional[str] = Field(
        default=None,
        description="""ID of the parent folder in Google Drive; if omitted, the file is created in the root of 'My Drive'. Must be a valid Google Drive folder ID, not a folder name. Use GOOGLEDRIVE_FIND_FOLDER to get the folder ID from a folder name. Please provide a value of type string.""",
    )  # noqa: E501

    text_content: str = Field(
        description="""Plain text content to be written into the new file. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501


class CreateFolderInput(BaseModel):
    """Input model for GOOGLEDRIVE_CREATE_FOLDER"""

    folder_name: str = Field(
        description="""Name for the new folder. This is a required field. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    parent_id: Optional[str] = Field(
        default=None,
        description="""ID or name of the parent folder. If a name is provided, the action attempts to find it. If an ID is provided, it must be a valid Google Drive folder ID. If omitted, the folder is created in the Drive root. Please provide a value of type string.""",
    )  # noqa: E501


class CreateReplyInput(BaseModel):
    """Input model for GOOGLEDRIVE_CREATE_REPLY"""

    action: Optional[str] = Field(
        default=None,
        description="""The action the reply performed to the parent comment. Valid values are: resolve, reopen. Please provide a value of type string.""",
    )  # noqa: E501

    comment_id: str = Field(
        description="""The ID of the comment. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    content: str = Field(
        description="""The plain text content of the reply. HTML content is not supported. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    fields: Optional[str] = Field(
        default=None,
        description="""Selector specifying which fields to include in a partial response. Please provide a value of type string.""",
    )  # noqa: E501

    file_id: str = Field(
        description="""The ID of the file. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501


class CreateShortcutToFileInput(BaseModel):
    """Input model for GOOGLEDRIVE_CREATE_SHORTCUT_TO_FILE"""

    ignoreDefaultVisibility: Optional[bool] = Field(
        default=None,
        description="""Whether to ignore the domain's default visibility settings for the created file. Please provide a value of type boolean.""",
    )  # noqa: E501

    includeLabels: Optional[str] = Field(
        default=None,
        description="""A comma-separated list of IDs of labels to include in the labelInfo part of the response. Please provide a value of type string.""",
    )  # noqa: E501

    includePermissionsForView: Optional[str] = Field(
        default=None,
        description="""Specifies which additional view's permissions to include in the response. Only 'published' is supported. Please provide a value of type string.""",
    )  # noqa: E501

    keepRevisionForever: Optional[bool] = Field(
        default=None,
        description="""Whether to set the 'keepForever' field in the new head revision. Please provide a value of type boolean.""",
    )  # noqa: E501

    name: str = Field(
        description="""The name of the shortcut. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    supportsAllDrives: Optional[bool] = Field(
        default=None,
        description="""Whether the requesting application supports both My Drives and shared drives. Recommended to set to true if interacting with shared drives. Please provide a value of type boolean.""",
    )  # noqa: E501

    target_id: str = Field(
        description="""The ID of the file or folder that this shortcut points to. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    target_mime_type: Optional[str] = Field(
        default=None,
        description="""The MIME type of the target file or folder. While optional, providing it can be helpful. Please provide a value of type string.""",
    )  # noqa: E501


class DeleteCommentInput(BaseModel):
    """Input model for GOOGLEDRIVE_DELETE_COMMENT"""

    comment_id: str = Field(
        description="""The ID of the comment. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    file_id: str = Field(
        description="""The ID of the file. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501


class DeleteDriveInput(BaseModel):
    """Input model for GOOGLEDRIVE_DELETE_DRIVE"""

    allowItemDeletion: Optional[bool] = Field(
        default=None,
        description="""Whether any items inside the shared drive should also be deleted. This option is only supported when `useDomainAdminAccess` is also set to `true`. Please provide a value of type boolean.""",
    )  # noqa: E501

    driveId: str = Field(
        description="""The ID of the shared drive. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    useDomainAdminAccess: Optional[bool] = Field(
        default=None,
        description="""Issue the request as a domain administrator; if set to true, then the requester will be granted access if they are an administrator of the domain to which the shared drive belongs. Please provide a value of type boolean.""",
    )  # noqa: E501


class DeletePermissionInput(BaseModel):
    """Input model for GOOGLEDRIVE_DELETE_PERMISSION"""

    file_id: str = Field(
        description="""The ID of the file or shared drive. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    permission_id: str = Field(
        description="""The ID of the permission. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    supportsAllDrives: Optional[bool] = Field(
        default=None,
        description="""Whether the requesting application supports both My Drives and shared drives. Please provide a value of type boolean.""",
    )  # noqa: E501

    useDomainAdminAccess: Optional[bool] = Field(
        default=None,
        description="""Issue the request as a domain administrator; if set to true, then the requester will be granted access if the file ID parameter refers to a shared drive and the requester is an administrator of the domain to which the shared drive belongs. Please provide a value of type boolean.""",
    )  # noqa: E501


class DeleteReplyInput(BaseModel):
    """Input model for GOOGLEDRIVE_DELETE_REPLY"""

    comment_id: str = Field(
        description="""The ID of the comment. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    file_id: str = Field(
        description="""The ID of the file. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    reply_id: str = Field(
        description="""The ID of the reply. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501


class DownloadFileInput(BaseModel):
    """Input model for GOOGLEDRIVE_DOWNLOAD_FILE"""

    file_id: str = Field(
        description="""The unique identifier of the file to be downloaded from Google Drive. This ID can typically be found in the file's URL in Google Drive or obtained from API calls that list files. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    mime_type: Optional[
        Literal[
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
    ] = Field(
        default=None,
        description="""Target MIME type for exporting Google Workspace documents (e.g., Google Doc, Sheet, Slide). Supported export formats vary by file type; e.g., text/plain is only supported for Google Docs, not Sheets or Slides. This parameter is automatically ignored for non-Google Workspace files, which are downloaded in their native format. Only specify this when you want to export a Google Workspace document to a different format (e.g., export Google Doc to PDF). Please provide a value of type string.""",
    )  # noqa: E501


class EditFileInput(BaseModel):
    """Input model for GOOGLEDRIVE_EDIT_FILE"""

    content: str = Field(
        description="""New textual content to overwrite the existing file; will be UTF-8 encoded for upload. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    file_id: str = Field(
        description="""Identifier of the Google Drive file to update. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    mime_type: Optional[str] = Field(
        default="text/plain",
        description="""MIME type of the 'content' being uploaded; must accurately represent its format. Please provide a value of type string.""",
    )  # noqa: E501


class EmptyTrashInput(BaseModel):
    """Input model for GOOGLEDRIVE_EMPTY_TRASH"""

    driveId: Optional[str] = Field(
        default=None,
        description="""If set, empties the trash of the provided shared drive. This parameter is ignored if the item is not in a shared drive. Please provide a value of type string.""",
    )  # noqa: E501

    enforceSingleParent: Optional[bool] = Field(
        default=None,
        description="""Deprecated: If an item is not in a shared drive and its last parent is deleted but the item itself is not, the item will be placed under its owner's root. This parameter is ignored if the item is not in a shared drive. Please provide a value of type boolean.""",
    )  # noqa: E501


class FilesModifyLabelsInput(BaseModel):
    """Input model for GOOGLEDRIVE_FILES_MODIFY_LABELS"""

    file_id: str = Field(
        description="""The ID of the file. Please provide a value of type string. This parameter is required."""
    )  # noqa: E501

    kind: Optional[str] = Field(
        default="drive#modifyLabelsRequest",
        description="""This is always drive#modifyLabelsRequest. Please provide a value of type string.""",
    )  # noqa: E501

    label_modifications: list[Any] = Field(
        description="""The list of modifications to apply to the labels on the file. This parameter is required."""
    )  # noqa: E501


class FindFileInput(BaseModel):
    """Input model for GOOGLEDRIVE_FIND_FILE"""

    corpora: Optional[Literal["user", "drive", "domain", "allDrives"]] = Field(
        default=None,
        description="""Corpora to query. 'user' for user's personal files, 'drive' for files in a specific shared drive (requires 'driveId'), 'domain' for files shared with the domain, 'allDrives' for all drives the user has access to. Please provide a value of type string.""",
    )  # noqa: E501

    driveId: Optional[str] = Field(
        default=None,
        description="""ID of the shared drive to search. Required if 'corpora' is 'drive'. Please provide a value of type string.""",
    )  # noqa: E501

    fields: Optional[str] = Field(
        default="*",
        description="""Selector specifying which fields to include in a partial response. Use '*' for all fields or a comma-separated list, e.g., 'nextPageToken,files(id,name,mimeType)'. Please provide a value of type string.""",
    )  # noqa: E501

    includeItemsFromAllDrives: Optional[bool] = Field(
        default=False,
        description="""Whether both My Drive and shared drive items should be included in results. If true, 'supportsAllDrives' should also be true. Please provide a value of type boolean.""",
    )  # noqa: E501

    orderBy: Optional[str] = Field(
        default=None,
        description="""A comma-separated list of sort keys. Valid keys are 'createdTime', 'folder', 'modifiedByMeTime', 'modifiedTime', 'name', 'name_natural', 'quotaBytesUsed', 'recency', 'sharedWithMeTime', 'starred', and 'viewedByMeTime'. Each key sorts ascending by default, but may be reversed with the 'desc' modifier. Example: 'modifiedTime desc,name'. Please provide a value of type string.""",
    )  # noqa: E501

    pageSize: Optional[int] = Field(
        default=100,
        description="""The maximum number of files to return per page. Please provide a value of type integer.""",
    )  # noqa: E501

    pageToken: Optional[str] = Field(
        default=None,
        description="""The token for continuing a previous list request on the next page. Please provide a value of type string.""",
    )  # noqa: E501

    q: Optional[str] = Field(
        default=None,
        description="""A query for filtering the file results. See Google Drive API documentation for query syntax. Example: \"name contains 'report' and mimeType = 'application/pdf'\". Please provide a value of type string.""",
    )  # noqa: E501

    spaces: Optional[str] = Field(
        default="drive",
        description="""A comma-separated list of spaces to query. Supported values are 'drive', 'appDataFolder' and 'photos'. Please provide a value of type string.""",
    )  # noqa: E501

    supportsAllDrives: Optional[bool] = Field(
        default=True,
        description="""Whether the requesting application supports both My Drives and shared drives. If 'includeItemsFromAllDrives' is true, this must also be true. Please provide a value of type boolean.""",
    )  # noqa: E501


class FindFolderInput(BaseModel):
    """Input model for GOOGLEDRIVE_FIND_FOLDER"""

    full_text_contains: Optional[str] = Field(
        default=None,
        description="""A string to search for within the full text content of files within folders (if applicable and supported by Drive for the folder type or its contents). This search is case-insensitive. Please provide a value of type string.""",
    )  # noqa: E501

    full_text_not_contains: Optional[str] = Field(
        default=None,
        description="""A string to exclude from the full text content of files within folders. This search is case-insensitive. Please provide a value of type string.""",
    )  # noqa: E501

    modified_after: Optional[str] = Field(
        default=None,
        description="""Search for folders modified after a specific date and time. The timestamp must be in RFC 3339 format (e.g., '2023-01-15T10:00:00Z' or '2023-01-15T10:00:00.000Z'). Please provide a value of type string.""",
    )  # noqa: E501

    name_contains: Optional[str] = Field(
        default=None,
        description="""A substring to search for within folder names as a string. This search is case-insensitive. Please provide a value of type string.""",
    )  # noqa: E501

    name_exact: Optional[str] = Field(
        default=None,
        description="""The exact name of the folder to search for as a string. This search is case-sensitive. Do not pass numbers - convert to string if needed. Please provide a value of type string.""",
    )  # noqa: E501

    name_not_contains: Optional[str] = Field(
        default=None,
        description="""A substring to exclude from folder names as a string. Folders with names containing this substring will not be returned. This search is case-insensitive. Please provide a value of type string.""",
    )  # noqa: E501

    starred: Optional[bool] = Field(
        default=None,
        description="""Set to true to search for folders that are starred, or false for those that are not. Please provide a value of type boolean.""",
    )  # noqa: E501


class GenerateIdsInput(BaseModel):
    """Input model for GOOGLEDRIVE_GENERATE_IDS"""

    count: Optional[int] = Field(
        default=None,
        description="""The number of IDs to return. Value must be between 1 and 1000, inclusive. Please provide a value of type integer.""",
    )  # noqa: E501

    space: Optional[str] = Field(
        default=None,
        description="""The space in which the IDs can be used. Supported values are 'drive' and 'appDataFolder'. Please provide a value of type string.""",
    )  # noqa: E501

    type: Optional[str] = Field(
        default=None,
        description="""The type of items for which the IDs can be used. For example, 'files' or 'shortcuts'. Please provide a value of type string.""",
    )  # noqa: E501
