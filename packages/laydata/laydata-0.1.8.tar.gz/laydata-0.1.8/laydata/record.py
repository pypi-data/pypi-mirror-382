from __future__ import annotations
import httpx
from typing import Any


from laydata.attachment_item import AttachmentItem


class Record(dict):
    """
    Dict-like record with convenience methods for updates and attachments.
    Backed by a Table instance and the httpx client.
    """
    def __init__(self, table: "Table", data: dict[str, Any]):
        super().__init__(data)
        self._table = table

    @property
    def id(self) -> str:
        return super().get("id")

    @property
    def fields(self) -> dict[str, Any]:
        return super().get("fields")
    
    def field(self, name: str, default: Any | None = None) -> Any:
        fields = self.fields or {}
        return fields.get(name, default)

    async def upload_attachment(self, **field_to_source):
        """
        Usage: await record.upload_attachment(PassportPhoto="/path/to/file.jpg")
        or: await record.upload_attachment(Gallery="https://example.com/img.jpg")
        """
        for field, source in field_to_source.items():
            if isinstance(source, str):
                if source.startswith("http://") or source.startswith("https://"):
                    updated = await self._table.upload_attachment(self.id, field, file_url=source)
                else:
                    updated = await self._table.upload_attachment(self.id, field, file_path=source)
                self.clear(); super().update(updated)
            else:
                # Accept Attachment wrapper or list of them via table.update_record path
                from laydata.types import Attachment
                if isinstance(source, Attachment) or (
                    isinstance(source, list) and all(isinstance(x, Attachment) for x in source)
                ):
                    updated = await self._table.update_record(self.id, {field: source})
                    self.clear(); super().update(updated)
                else:
                    raise TypeError(f"Unsupported attachment source type for field '{field}'")

    async def update(self, fields_dict: dict[str, Any] | None = None, /, **fields):  # keyword-only update for explicitness
        """
        Usage: 
        - await record.update(Email="john@example.com", Gallery=[Attachment(...), ...])
        - await record.update({"Email": "john@example.com", "Gallery": [Attachment(...), ...]})
        - await record.update({"Email": "john@example.com"}, Gallery=[Attachment(...), ...])
        """
        if fields_dict is not None:
            fields = {**fields_dict, **fields}
        
        if not fields:
            raise ValueError("No fields provided for update")
            
        updated = await self._table.update_record(self.id, fields)
        self.clear(); super().update(updated)
        return self

    async def edit(self, fields_dict: dict[str, Any] | None = None, /, **fields):
        """
        Alias for update() method. Same functionality, shorter name.
        Usage: 
        - await record.edit(Email="john@example.com", Gallery=[Attachment(...), ...])
        - await record.edit({"Email": "john@example.com", "Gallery": [Attachment(...), ...]})
        - await record.edit({"Email": "john@example.com"}, Gallery=[Attachment(...), ...])
        """
        return await self.update(fields_dict, **fields)

    def attachments(self, field: str) -> list[AttachmentItem]:
        vals = self.field(field)
        if isinstance(vals, list):
            return [v for v in vals if isinstance(v, AttachmentItem)]
        return []
