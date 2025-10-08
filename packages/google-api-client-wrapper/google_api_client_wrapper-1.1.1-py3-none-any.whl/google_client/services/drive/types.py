from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


from google_client.services.drive.constants import GOOGLE_DOCS_MIME_TYPE, GOOGLE_SHEETS_MIME_TYPE, \
    GOOGLE_SLIDES_MIME_TYPE


class Permission(BaseModel):
    """
    Represents a permission for a Drive file or folder.
    """
    permission_id: str = Field(..., description="The unique identifier for this permission")
    type: Optional[str] = Field(None, description="The type of permission (user, group, domain, anyone)")
    role: Optional[str] = Field(None, description="The role of the permission (reader, writer, commenter, owner)")
    email_address: Optional[str] = Field(None, description="The email address for user/group permissions")
    domain: Optional[str] = Field(None, description="The domain name for domain permissions")
    display_name: Optional[str] = Field(None, description="Display name of the person/group")
    deleted: bool = Field(False, description="Whether this permission has been deleted")

    def to_dict(self) -> dict:
        """
        Converts the Permission instance to a dictionary representation.
        Returns:
            A dictionary containing the permission data.
        """
        result = {}
        if self.permission_id:
            result["id"] = self.permission_id
        if self.type:
            result["type"] = self.type
        if self.role:
            result["role"] = self.role
        if self.email_address:
            result["emailAddress"] = self.email_address
        if self.domain:
            result["domain"] = self.domain
        if self.display_name:
            result["displayName"] = self.display_name
        if self.deleted:
            result["deleted"] = self.deleted
        return result

    def __str__(self):
        if self.email_address:
            return f"{self.display_name or self.email_address} ({self.role})"
        elif self.domain:
            return f"Domain: {self.domain} ({self.role})"
        else:
            return f"{self.type} ({self.role})"


class DriveItem(BaseModel):
    """
    Base class for items in Google Drive (files and folders).
    """
    item_id: str = Field(..., description="Unique identifier for the Drive item")
    name: Optional[str] = Field(None, description="Name of the Drive item")
    created_time: Optional[datetime] = Field(None, description="When the item was created")
    modified_time: Optional[datetime] = Field(None, description="When the item was last modified")
    parent_ids: List[str] = Field(default_factory=list, description="List of parent folder IDs")
    web_view_link: Optional[str] = Field(None, description="Link to view the item in a web browser")
    owners: List[str] = Field(default_factory=list, description="List of owner email addresses")
    permissions: List[Permission] = Field(default_factory=list, description="List of permissions for the item")
    description: Optional[str] = Field(None, description="Description of the item")
    starred: bool = Field(False, description="Whether the item is starred")
    trashed: bool = Field(False, description="Whether the item is in the trash")
    shared: bool = Field(False, description="Whether the item is shared with others")

    def get_parent_folder_id(self) -> Optional[str]:
        """
        Get the first parent folder ID.
        Returns:
            The first parent folder ID, or None if no parents.
        """
        return self.parent_ids[0] if self.parent_ids else None

    def has_parent(self) -> bool:
        """
        Check if this item has a parent folder.
        Returns:
            True if item has at least one parent folder.
        """
        return bool(self.parent_ids)

    def get_all_parent_ids(self) -> List[str]:
        """
        Get all parent folder IDs.
        Returns:
            List of all parent folder IDs.
        """
        return self.parent_ids.copy()

    def is_in_folder(self, folder_id: str) -> bool:
        """
        Check if this item is in a specific parent folder.
        Args:
            folder_id: ID of the folder to check
        Returns:
            True if this item is in the specified folder.
        """
        return folder_id in self.parent_ids

    def to_dict(self) -> dict:
        """
        Converts the DriveItem instance to a dictionary representation.
        Returns:
            A dictionary containing the item data.
        """
        result = {
            "id": self.item_id,
            "name": self.name,
            "createdTime": self.created_time.isoformat() + "Z" if self.created_time else None,
            "modifiedTime": self.modified_time.isoformat() + "Z" if self.modified_time else None,
            "parents": self.parent_ids,
            "webViewLink": self.web_view_link,
            "description": self.description,
            "permissions": [p.to_dict() for p in self.permissions],
            "starred": self.starred,
            "trashed": self.trashed,
            "shared": self.shared,
        }
        return result


class DriveFile(DriveItem):
    """
    Represents a file in Google Drive.
    """
    mime_type: Optional[str] = Field(None, description="MIME type of the file")
    size: Optional[int] = Field(None, description="Size of the file in bytes")
    web_content_link: Optional[str] = Field(None, description="Direct download link for the file")
    original_filename: Optional[str] = Field(None, description="Original filename when uploaded")
    file_extension: Optional[str] = Field(None, description="File extension")
    md5_checksum: Optional[str] = Field(None, description="MD5 checksum of the file")

    @property
    def file_id(self):
        return self.item_id

    def is_google_doc(self) -> bool:
        """
        Check if this file is a Google Workspace document.
        Returns:
            True if the file is a Google Workspace document.
        """
        google_mime_types = [
            GOOGLE_DOCS_MIME_TYPE,
            GOOGLE_SHEETS_MIME_TYPE,
            GOOGLE_SLIDES_MIME_TYPE,
            "application/vnd.google-apps.drawing",
            "application/vnd.google-apps.form",
        ]
        return self.mime_type in google_mime_types

    def human_readable_size(self) -> str:
        """
        Get human-readable file size.
        Returns:
            Size in human-readable format (e.g., "1.2 MB").
        """
        if self.size is None:
            return "Unknown"
        
        if self.size == 0:
            return "0 B"
        
        size = self.size
        units = ["B", "KB", "MB", "GB", "TB"]
        unit_index = 0
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        return f"{size:.1f} {units[unit_index]}"

    def to_dict(self) -> dict:
        """
        Converts the DriveFile instance to a dictionary representation.
        Returns:
            A dictionary containing the file data.
        """
        result = super().to_dict()
        result.update({
            "mimeType": self.mime_type,
            "size": str(self.size) if self.size is not None else None,
            "webContentLink": self.web_content_link,
        })
        return result

    def __str__(self):
        size_str = f"({self.human_readable_size()})"
        return f"{self.name} {size_str}"

    def __repr__(self):
        return f"DriveFile(id={self.item_id!r}, name={self.name!r}, mime_type={self.mime_type!r})"


class DriveFolder(DriveItem):
    """
    Represents a folder in Google Drive.
    """
    @property
    def folder_id(self):
        return self.item_id

    @property
    def parents(self):
        return self.parent_ids

    @parents.setter
    def parents(self, value):
        self.parent_ids = value

    def to_dict(self) -> dict:
        """
        Converts the DriveFolder instance to a dictionary representation.
        Returns:
            A dictionary containing the folder data.
        """
        result = super().to_dict()
        result["mimeType"] = "application/vnd.google-apps.folder"
        return result

    def __str__(self):
        return f"[Folder] {self.name}"

    def __repr__(self):
        return f"DriveFolder(id={self.item_id!r}, name={self.name!r})"
