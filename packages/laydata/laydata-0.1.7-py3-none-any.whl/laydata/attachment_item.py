from __future__ import annotations
import os
from pathlib import Path
import httpx


class AttachmentItem(dict):
    """
    Dict-like attachment item with a convenient async download method.
    Expects keys like: name, mimetype, presignedUrl (optional), token (optional), size, etc.
    """
    def __init__(self, http_client: httpx.AsyncClient, data: dict):
        super().__init__(data)
        self._client = http_client

    async def download(self, destination: str) -> str:
        """
        Download the attachment to a directory or a custom full path.
        - If destination is a directory, uses the item's name as filename.
        - If destination is a file path, uses it as-is.
        Returns the full file path.
        """
        url = self.get("presignedUrl")
        if not url:
            raise ValueError("Attachment does not include presignedUrl; cannot download")

        # Determine target path
        dest_path = Path(destination)
        if dest_path.exists() and dest_path.is_dir():
            filename = self.get("name") or "download.bin"
            dest_path = dest_path / filename
        else:
            # Ensure parent dir exists
            if dest_path.parent and not dest_path.parent.exists():
                dest_path.parent.mkdir(parents=True, exist_ok=True)

        async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            content = resp.content
            # Optionally, validate content-type matches expected mimetype
            expected = (self.get("mimetype") or "").split(";")[0]
            received = (resp.headers.get("content-type", "").split(";")[0].strip())
            # Only assert if expected is present
            if expected and received and expected != received:
                # Do not fail hard; keep behavior permissive but you can choose to raise
                pass
            with open(dest_path, "wb") as f:
                f.write(content)
        return str(dest_path)