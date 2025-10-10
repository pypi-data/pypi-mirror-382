import httpx
from laydata_core.errors import LayDataError, build_error_context
from laydata_core.types import TableData
from laydata.record import Record
from laydata.attachment_item import AttachmentItem


class Table:
    def __init__(self, client: httpx.AsyncClient, data: TableData):
        self._client = client
        self._data = data

    def query(self) -> "RecordsQuery":
        from laydata.query import RecordsQuery
        return RecordsQuery(self)

    # Chainable sugar: return a RecordsQuery primed with the condition
    def where(self, field: str, value) -> "RecordsQuery":
        return self.query().where(field, value)

    def eq(self, field: str, value) -> "RecordsQuery":
        return self.query().eq(field, value)

    def ne(self, field: str, value) -> "RecordsQuery":
        return self.query().ne(field, value)

    def gt(self, field: str, value) -> "RecordsQuery":
        return self.query().gt(field, value)

    def gte(self, field: str, value) -> "RecordsQuery":
        return self.query().gte(field, value)

    def lt(self, field: str, value) -> "RecordsQuery":
        return self.query().lt(field, value)

    def lte(self, field: str, value) -> "RecordsQuery":
        return self.query().lte(field, value)

    def contains(self, field: str, value: str) -> "RecordsQuery":
        return self.query().contains(field, value)

    def not_contains(self, field: str, value: str) -> "RecordsQuery":
        return self.query().not_contains(field, value)

    def in_(self, field: str, values: list) -> "RecordsQuery":
        return self.query().in_(field, values)

    def not_in(self, field: str, values: list) -> "RecordsQuery":
        return self.query().not_in(field, values)

    def is_empty(self, field: str) -> "RecordsQuery":
        return self.query().is_empty(field)

    def is_not_empty(self, field: str) -> "RecordsQuery":
        return self.query().is_not_empty(field)

    def between(self, field: str, lo, hi, inclusive: bool = True) -> "RecordsQuery":
        return self.query().between(field, lo, hi, inclusive=inclusive)

    def asc(self, field: str) -> "RecordsQuery":
        return self.query().asc(field)

    def desc(self, field: str) -> "RecordsQuery":
        return self.query().desc(field)

    def take_q(self, n: int) -> "RecordsQuery":
        return self.query().take(n)

    def skip_q(self, n: int) -> "RecordsQuery":
        return self.query().skip(n)

    def search_q(self, value: str, field: str, fuzzy: bool = True) -> "RecordsQuery":
        return self.query().search(value, field, fuzzy)

    # Async direct helpers
    async def get_by(self, field: str, value):
        return await self.query().eq(field, value).first()

    async def find_all_by(self, field: str, value):
        return await self.query().eq(field, value).all()

    async def top(self, n: int, *, order_field: str | None = None, desc: bool = True):
        q = self.query().take(n)
        if order_field:
            q = q.desc(order_field) if desc else q.asc(order_field)
        return await q.all()

    @property
    def id(self) -> str:
        return self._data["id"]

    @property
    def name(self) -> str:
        return self._data["name"]

    @property
    def base_id(self) -> str:
        return self._data["baseId"]

    @property
    def db_table_name(self) -> str | None:
        return self._data.get("dbTableName")

    @property
    def description(self) -> str | None:
        return self._data.get("description")

    @property
    def icon(self) -> str | None:
        return self._data.get("icon")

    @property
    def order(self) -> int | None:
        return self._data.get("order")

    @property
    def last_modified_time(self) -> str | None:
        return self._data.get("lastModifiedTime")

    @property
    def default_view_id(self) -> str | None:
        return self._data.get("defaultViewId")

    async def delete(self) -> None:
        from laydata_core.errors import map_teable_error
        try:
            response = await self._client.delete(f"/table/{self.id}?base_id={self.base_id}")
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            context = build_error_context(
                operation="Delete table",
                url=f"/table/{self.id}?base_id={self.base_id}",
                method="DELETE",
                status_code=e.response.status_code,
                table_id=self.id,
                base_id=self.base_id,
            )
            try:
                error_data = e.response.json()
                raise map_teable_error(
                    e.response.status_code,
                    error_data.get("detail", str(e)),
                    error_data.get("code"),
                    context
                )
            except Exception:
                raise map_teable_error(e.response.status_code, str(e), None, context)

    async def update_icon(self, icon: str) -> None:
        from laydata_core.errors import map_teable_error
        try:
            response = await self._client.put(
                f"/table/{self.id}/icon?base_id={self.base_id}",
                json={"icon": icon}
            )
            response.raise_for_status()
            self._data["icon"] = icon
        except httpx.HTTPStatusError as e:
            context = build_error_context(
                operation="Update table icon",
                url=f"/table/{self.id}/icon?base_id={self.base_id}",
                method="PUT",
                status_code=e.response.status_code,
                table_id=self.id,
                base_id=self.base_id,
                extra={"Icon": icon},
            )
            
            try:
                error_data = e.response.json()
                raise map_teable_error(
                    e.response.status_code,
                    error_data.get("detail", str(e)),
                    error_data.get("code"),
                    context
                )
            except Exception:
                raise map_teable_error(e.response.status_code, str(e), None, context)

    async def update_description(self, description: str | None) -> None:
        from laydata_core.errors import map_teable_error
        try:
            response = await self._client.put(
                f"/table/{self.id}/description?base_id={self.base_id}",
                json={"description": description}
            )
            response.raise_for_status()
            self._data["description"] = description
        except httpx.HTTPStatusError as e:
            context = build_error_context(
                operation="Update table description",
                url=f"/table/{self.id}/description?base_id={self.base_id}",
                method="PUT",
                status_code=e.response.status_code,
                table_id=self.id,
                base_id=self.base_id,
                extra={"Description": description},
            )
            
            try:
                error_data = e.response.json()
                raise map_teable_error(
                    e.response.status_code,
                    error_data.get("detail", str(e)),
                    error_data.get("code"),
                    context
                )
            except Exception:
                raise map_teable_error(e.response.status_code, str(e), None, context)

    async def records(self, take: int | None = None, skip: int | None = None, where: dict | None = None, order_by: list[dict] | None = None, search: list | tuple | None = None) -> list[Record]:
        from laydata_core.errors import map_teable_error
        try:
            import json as _json
            from datetime import datetime, date, timezone
            from laydata.types import Date as DateWrapper

            def to_iso_millis_z(dt: datetime) -> str:
                if dt.tzinfo is None:
                    dt_utc = dt.replace(tzinfo=timezone.utc)
                else:
                    dt_utc = dt.astimezone(timezone.utc)
                return dt_utc.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

            def _normalize_where(obj):
                if isinstance(obj, dict):
                    return {k: _normalize_where(v) for k, v in obj.items()}
                if isinstance(obj, list):
                    return [_normalize_where(v) for v in obj]
                if isinstance(obj, DateWrapper):
                    return obj.to_utc_iso_millis_z()
                if isinstance(obj, datetime):
                    return to_iso_millis_z(obj)
                if isinstance(obj, date):
                    dt = datetime(obj.year, obj.month, obj.day, 0, 0, 0, tzinfo=timezone.utc)
                    return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                return obj

            params = {}
            if take is not None:
                params["take"] = take
            if skip is not None:
                params["skip"] = skip
            if where is not None:
                params["where"] = _json.dumps(_normalize_where(where))
            if order_by is not None:
                params["order_by"] = _json.dumps(order_by)
            if search is not None:
                # send as repeated query params: search=value&search=field&search=true
                s = list(search) if not isinstance(search, list) else search
                coerced = []
                for token in s[:3]:
                    if isinstance(token, bool):
                        coerced.append("true" if token else "false")
                    else:
                        coerced.append(str(token))
                params["search"] = coerced
            
            response = await self._client.get(f"/table/{self.id}/record", params=params)
            response.raise_for_status()
            data = response.json()
            recs = data.get("records", [])
            wrapped = [self._wrap_attachments(r) for r in recs]
            return [Record(self, r) for r in wrapped]
        except httpx.HTTPStatusError as e:
            extras = {}
            if take is not None:
                extras["Take"] = take
            if skip is not None:
                extras["Skip"] = skip
            if where is not None:
                extras["Where"] = where
            if order_by is not None:
                extras["Order By"] = order_by
            if search is not None:
                extras["Search"] = search
            context = build_error_context(
                operation="Get records",
                url=f"/table/{self.id}/record",
                method="GET",
                status_code=e.response.status_code,
                table_id=self.id,
                base_id=self.base_id,
                extra=extras,
            )
            
            try:
                error_data = e.response.json()
                raise map_teable_error(
                    e.response.status_code,
                    error_data.get("detail", str(e)),
                    error_data.get("code"),
                    context
                )
            except Exception:
                raise map_teable_error(e.response.status_code, str(e), None, context)

    async def find(self, where: dict, take: int | None = None, skip: int | None = None, order_by: list[dict] | None = None, search: list | tuple | None = None) -> list[Record]:
        return await self.records(take=take, skip=skip, where=where, order_by=order_by, search=search)

    async def first(self, where: dict, order_by: list[dict] | None = None, search: list | tuple | None = None) -> Record | None:
        rows = await self.records(take=1, where=where, order_by=order_by, search=search)
        return rows[0] if rows else None

    async def search_records(
        self,
        value: str,
        field: str,
        fuzzy: bool = True,
        *,
        take: int | None = None,
        skip: int | None = None,
        where: dict | None = None,
        order_by: list[dict] | None = None,
    ) -> list[Record]:
        return await self.records(take=take, skip=skip, where=where, order_by=order_by, search=[value, field, fuzzy])

    @staticmethod
    def order_asc(field: str) -> dict:
        return {"field": field, "order": "asc"}

    @staticmethod
    def order_desc(field: str) -> dict:
        return {"field": field, "order": "desc"}

    async def get_record(self, record_id: str) -> Record:
        from laydata_core.errors import map_teable_error
        try:
            response = await self._client.get(f"/table/{self.id}/record/{record_id}")
            response.raise_for_status()
            rec = response.json()
            rec = self._wrap_attachments(rec)
            return Record(self, rec)
        except httpx.HTTPStatusError as e:
            context = build_error_context(
                operation="Get record",
                url=f"/table/{self.id}/record/{record_id}",
                method="GET",
                status_code=e.response.status_code,
                table_id=self.id,
                base_id=self.base_id,
                record_id=record_id,
            )
            
            try:
                error_data = e.response.json()
                raise map_teable_error(
                    e.response.status_code,
                    error_data.get("detail", str(e)),
                    error_data.get("code"),
                    context
                )
            except Exception:
                raise map_teable_error(e.response.status_code, str(e), None, context)

    async def add(self, fields: dict) -> Record:
        """
        Create a record.
        - Standard Python types are passed as-is (dates/datetimes auto-converted to ISO Z).
        - Use wrappers for non-standard behavior:
          Attachment("/path/to/file" or "https://..."), Date(...), SingleSelect("..."), MultiSelect(["..."]).
        Only Attachment triggers special post-create uploads.
        """
        from laydata_core.errors import map_teable_error
        from laydata_core.client_retry import client_retry, retry_with_client_backoff
        from laydata.types import Attachment, Date, SingleSelect, MultiSelect
        import os
        import mimetypes


        # Partition into non-attachments (JSON) and attachments (post-upload)
        non_attach: dict = {}
        attachments: dict[str, list[Attachment]] = {}

        hints: dict[str, str] = {}
        for name, value in fields.items():
            if isinstance(value, Attachment):
                # ⚠️ PERFORMANCE WARNING: Single attachments cause issues under concurrent load
                import warnings
                import os
                if not os.getenv("LAYDATA_ALLOW_ATTACHMENTS"):
                    warnings.warn(
                        f"⚠️ DEPRECATED: Attachment in field '{name}' may cause performance issues under concurrent load "
                        f"(15s+ timeouts with 5+ users). Use external storage + URLs for production. "
                        f"Example: {{'Photo': 'https://cdn.com/photo.jpg'}} instead of Attachment('/path'). "
                        f"To suppress: set LAYDATA_ALLOW_ATTACHMENTS=1 (not recommended for high-load scenarios).",
                        UserWarning,
                        stacklevel=3
                    )
                attachments.setdefault(name, []).append(value)
            elif isinstance(value, list) and all(isinstance(v, Attachment) for v in value):
                # ⚠️ SEVERE PERFORMANCE WARNING: Multiple attachments per field
                import warnings
                import os
                if not os.getenv("LAYDATA_ALLOW_ATTACHMENTS"):
                    warnings.warn(
                        f"⚠️ SEVERELY DEPRECATED: Multiple attachments in field '{name}' ({len(value)} attachments) "
                        f"cause severe performance degradation (30s+ timeouts, sequential uploads). "
                        f"Use external storage + URL arrays for production. "
                        f"Example: {{'Files': ['https://cdn.com/doc1.pdf', 'https://cdn.com/doc2.pdf']}}. "
                        f"To suppress: set LAYDATA_ALLOW_ATTACHMENTS=1 (strongly discouraged).",
                        UserWarning,
                        stacklevel=3
                    )
                attachments[name] = value
            elif isinstance(value, Date):
                non_attach[name] = value  # will be normalized below
            elif isinstance(value, SingleSelect):
                non_attach[name] = value.value
                hints[name] = "singleSelect"
            elif isinstance(value, MultiSelect):
                non_attach[name] = list(value.values)
                hints[name] = "multipleSelect"
            else:
                # Link field normalization: accept Record, rec-id strings, id dicts, or lists of those
                from laydata.record import Record as _Record
                def _link_obj(v):
                    if isinstance(v, _Record):
                        rid = v.get("id")
                        title = v.get("name")
                        return {"id": rid, **({"title": title} if title else {})}
                    if isinstance(v, dict) and isinstance(v.get("id"), str):
                        # keep only id and optional title if provided
                        out = {"id": v.get("id")}
                        if isinstance(v.get("title"), str):
                            out["title"] = v.get("title")
                        return out
                    if isinstance(v, str) and v.startswith("rec"):
                        return {"id": v}
                    return None
                
                if isinstance(value, _Record) or (isinstance(value, dict) and value.get("id")) or (isinstance(value, str) and value.startswith("rec")):
                    mapped = _link_obj(value)
                    non_attach[name] = mapped if mapped is not None else value
                elif isinstance(value, list):
                    mapped_list = []
                    any_link = False
                    for v in value:
                        m = _link_obj(v)
                        if m is not None:
                            any_link = True
                            mapped_list.append(m)
                        else:
                            mapped_list.append(v)
                    non_attach[name] = mapped_list if any_link else value
                else:
                    non_attach[name] = value

        # Step 1: create record with non-attachment fields
        from datetime import date, datetime
        from laydata.types import Date as DateWrapper

        def _normalize_payload_fields(d: dict) -> dict:
            from datetime import datetime, date, timezone
            def to_iso_millis_z(dt: datetime) -> str:
                # Ensure UTC and format like JS Date.toISOString() with milliseconds
                if dt.tzinfo is None:
                    dt_utc = dt.replace(tzinfo=timezone.utc)
                else:
                    dt_utc = dt.astimezone(timezone.utc)
                # Truncate microseconds to milliseconds
                return dt_utc.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

            out: dict = {}
            for k, v in d.items():
                if isinstance(v, DateWrapper):
                    out[k] = v.to_utc_iso_millis_z()
                elif isinstance(v, datetime):
                    out[k] = to_iso_millis_z(v)
                elif isinstance(v, date):
                    dt = datetime(v.year, v.month, v.day, 0, 0, 0, tzinfo=timezone.utc)
                    out[k] = dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                elif v == "":
                    out[k] = None
                else:
                    out[k] = v
            return out

        payload_fields = _normalize_payload_fields(non_attach)
        
        # Create record with client retry for reliability
        async def _create_record():
            response = await self._client.post(
                f"/table/{self.id}/record",
                json={"fields": payload_fields, "typeHints": hints}
            )
            response.raise_for_status()
            return response.json()
        
        try:
            # Use client retry for record creation
            has_attachments_flag = bool(attachments)
            record = await _create_record()
            record = self._wrap_attachments(record)
            record_id = record.get("id")
            rec_obj = Record(self, record)
        except httpx.HTTPStatusError as e:
            context = build_error_context(
                operation="Create record",
                url=f"/table/{self.id}/record",
                method="POST",
                status_code=e.response.status_code,
                table_id=self.id,
                base_id=self.base_id,
                fields=fields,
                payload=payload_fields,
            )
            
            try:
                error_data = e.response.json()
                raise map_teable_error(
                    e.response.status_code,
                    error_data.get("detail", str(e)),
                    error_data.get("code"),
                    context
                )
            except Exception:
                raise map_teable_error(e.response.status_code, str(e), None, context)

        # Step 2: upload attachments with retry logic
        for field, items in attachments.items():
            for att in items:
                if att.is_url():
                    # URL attachment upload with retry
                    async def _upload_url_attachment():
                        r = await self._client.post(
                            f"/table/{self.id}/record/{record_id}/attachment",
                            data={"field": field, "fileUrl": att.source},
                        )
                        r.raise_for_status()
                        return r.json()
                    
                    record = await retry_with_client_backoff(
                        _upload_url_attachment,
                        operation_name=f"upload_url_attachment_{field}",
                        is_attachment_operation=True
                    )
                else:
                    # File attachment upload with retry
                    file_path = att.source
                    filename = os.path.basename(file_path)
                    guessed, _ = mimetypes.guess_type(filename)
                    content_type = guessed or "application/octet-stream"
                    
                    async def _upload_file_attachment():
                        with open(file_path, "rb") as f:
                            r = await self._client.post(
                                f"/table/{self.id}/record/{record_id}/attachment",
                                data={"field": field},
                                files={"file": (filename, f, content_type)},
                            )
                            r.raise_for_status()
                            return r.json()
                    
                    record = await retry_with_client_backoff(
                        _upload_file_attachment,
                        operation_name=f"upload_file_attachment_{field}_{filename}",
                        is_attachment_operation=True,
                        max_attempts=3,  # Fewer attempts for file uploads to avoid long delays
                    )
                    record = self._wrap_attachments(record)

        return Record(self, record)

    async def update_record(self, record_id: str, fields: dict) -> Record:
        """
        Update a record.
        - Standard Python types are passed as-is (dates/datetimes auto-converted to ISO Z).
        - Use wrappers: Attachment, Date, SingleSelect, MultiSelect. Only Attachment triggers
          post-update uploads.
        """
        from laydata_core.errors import map_teable_error
        from laydata_core.client_retry import client_retry, retry_with_client_backoff
        from laydata.types import Attachment, Date, SingleSelect, MultiSelect
        import os
        import mimetypes

        #validate record_id
        if not record_id:
            raise ValueError("record_id is required")
        #validate fields
        if not fields or not isinstance(fields, dict):
            raise ValueError("fields is required")


        non_attach: dict = {}
        attachments: dict[str, list[Attachment]] = {}
        hints: dict[str, str] = {}
        for name, value in fields.items():
            if isinstance(value, Attachment):
                # ⚠️ PERFORMANCE WARNING: Single attachments cause issues under concurrent load
                import warnings
                import os
                if not os.getenv("LAYDATA_ALLOW_ATTACHMENTS"):
                    warnings.warn(
                        f"⚠️ DEPRECATED: Attachment in field '{name}' may cause performance issues under concurrent load "
                        f"(15s+ timeouts with 5+ users). Use external storage + URLs for production. "
                        f"Example: {{'Photo': 'https://cdn.com/photo.jpg'}} instead of Attachment('/path'). "
                        f"To suppress: set LAYDATA_ALLOW_ATTACHMENTS=1 (not recommended for high-load scenarios).",
                        UserWarning,
                        stacklevel=3
                    )
                attachments.setdefault(name, []).append(value)
            elif isinstance(value, list) and all(isinstance(v, Attachment) for v in value):
                # ⚠️ SEVERE PERFORMANCE WARNING: Multiple attachments in field '{name}' ({len(value)} attachments) 
                import warnings
                import os
                if not os.getenv("LAYDATA_ALLOW_ATTACHMENTS"):
                    warnings.warn(
                        f"⚠️ SEVERELY DEPRECATED: Multiple attachments in field '{name}' ({len(value)} attachments) "
                        f"cause severe performance degradation (30s+ timeouts, sequential uploads). "
                        f"Use external storage + URL arrays for production. "
                        f"Example: {{'Files': ['https://cdn.com/doc1.pdf', 'https://cdn.com/doc2.pdf']}}. "
                        f"To suppress: set LAYDATA_ALLOW_ATTACHMENTS=1 (strongly discouraged).",
                        UserWarning,
                        stacklevel=3
                    )
                attachments[name] = value
            elif isinstance(value, Date):
                non_attach[name] = value
            elif isinstance(value, SingleSelect):
                non_attach[name] = value.value
                hints[name] = "singleSelect"
            elif isinstance(value, MultiSelect):
                non_attach[name] = list(value.values)
                hints[name] = "multipleSelect"
            else:
                # Link field normalization: accept Record, rec-id strings, id dicts, or lists of those
                from laydata.record import Record as _Record
                def _link_obj(v):
                    if isinstance(v, _Record):
                        rid = v.get("id")
                        title = v.get("name")
                        return {"id": rid, **({"title": title} if title else {})}
                    if isinstance(v, dict) and isinstance(v.get("id"), str):
                        out = {"id": v.get("id")}
                        if isinstance(v.get("title"), str):
                            out["title"] = v.get("title")
                        return out
                    if isinstance(v, str) and v.startswith("rec"):
                        return {"id": v}
                    return None
                
                if isinstance(value, _Record) or (isinstance(value, dict) and value.get("id")) or (isinstance(value, str) and value.startswith("rec")):
                    mapped = _link_obj(value)
                    non_attach[name] = mapped if mapped is not None else value
                elif isinstance(value, list):
                    mapped_list = []
                    any_link = False
                    for v in value:
                        m = _link_obj(v)
                        if m is not None:
                            any_link = True
                            mapped_list.append(m)
                        else:
                            mapped_list.append(v)
                    non_attach[name] = mapped_list if any_link else value
                else:
                    non_attach[name] = value

        # Step 1: JSON update for non-attachments
        from datetime import date, datetime
        from laydata.types import Date as DateWrapper

        def _normalize_payload_fields(d: dict) -> dict:
            from datetime import datetime, date, timezone
            def to_iso_millis_z(dt: datetime) -> str:
                if dt.tzinfo is None:
                    dt_utc = dt.replace(tzinfo=timezone.utc)
                else:
                    dt_utc = dt.astimezone(timezone.utc)
                return dt_utc.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

            out: dict = {}
            for k, v in d.items():
                if isinstance(v, DateWrapper):
                    out[k] = v.to_utc_iso_millis_z()
                elif isinstance(v, datetime):
                    out[k] = to_iso_millis_z(v)
                elif isinstance(v, date):
                    dt = datetime(v.year, v.month, v.day, 0, 0, 0, tzinfo=timezone.utc)
                    out[k] = dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                elif v == "":
                    out[k] = None
                else:
                    out[k] = v
            return out

        payload_fields = _normalize_payload_fields(non_attach)
        # Update record with client retry for reliability
        async def _update_record():
            response = await self._client.patch(
                f"/table/{self.id}/record/{record_id}",
                json={"fields": payload_fields, "typeHints": hints}
            )
            response.raise_for_status()
            return response.json()
        
        try:
            # Use client retry for record update
            has_attachments_flag = bool(attachments)
            record = await _update_record()
            record = self._wrap_attachments(record)
            rec_obj = Record(self, record)
        except httpx.HTTPStatusError as e:
            context = build_error_context(
                operation="Update record",
                url=f"/table/{self.id}/record/{record_id}",
                method="PATCH",
                status_code=e.response.status_code,
                table_id=self.id,
                base_id=self.base_id,
                record_id=record_id,
                fields=fields,
                payload=payload_fields,
            )
            
            try:
                error_data = e.response.json()
                raise map_teable_error(
                    e.response.status_code,
                    error_data.get("detail", str(e)),
                    error_data.get("code"),
                    context
                )
            except Exception:
                raise map_teable_error(e.response.status_code, str(e), None, context)

        # Step 2: upload attachments
        for field, items in attachments.items():
            for att in items:
                if att.is_url():
                    r = await self._client.post(
                        f"/table/{self.id}/record/{record_id}/attachment",
                        data={"field": field, "fileUrl": att.source},
                    )
                    r.raise_for_status()
                    record = r.json()
                else:
                    file_path = att.source
                    filename = os.path.basename(file_path)
                    guessed, _ = mimetypes.guess_type(filename)
                    content_type = guessed or "application/octet-stream"
                    with open(file_path, "rb") as f:
                        r = await self._client.post(
                            f"/table/{self.id}/record/{record_id}/attachment",
                            data={"field": field},
                            files={"file": (filename, f, content_type)},
                        )
                        r.raise_for_status()
                        record = r.json()
                        record = self._wrap_attachments(record)

        return Record(self, record)

    async def delete_record(self, record_id: str) -> None:
        from laydata_core.errors import map_teable_error
        try:
            response = await self._client.delete(f"/table/{self.id}/record/{record_id}")
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            context = build_error_context(
                operation="Delete record",
                url=f"/table/{self.id}/record/{record_id}",
                method="DELETE",
                status_code=e.response.status_code,
                table_id=self.id,
                base_id=self.base_id,
                record_id=record_id,
            )
            
            try:
                error_data = e.response.json()
                raise map_teable_error(
                    e.response.status_code,
                    error_data.get("detail", str(e)),
                    error_data.get("code"),
                    context
                )
            except Exception:
                raise map_teable_error(e.response.status_code, str(e), None, context)

    def __repr__(self) -> str:
        return f"Table(id={self.id}, name={self.name}, base_id={self.base_id})"

    def _wrap_attachments(self, record: dict) -> dict:
        try:
            fields = record.get("fields")
            if not isinstance(fields, dict):
                return record
            for fname, value in list(fields.items()):
                if isinstance(value, list) and value and all(isinstance(i, dict) for i in value):
                    # Heuristic: detect attachment objects by presence of token/mimetype/presignedUrl
                    if any("token" in i or "presignedUrl" in i or "mimetype" in i for i in value):
                        fields[fname] = [AttachmentItem(self._client, i) for i in value]
            return record
        except Exception:
            return record



    async def upload_attachment(
        self,
        record_id: str,
        field: str,
        *,
        file_path: str | None = None,
        file_url: str | None = None,
    ) -> dict:
        """
        Convenience for uploading a single attachment to a record field by name.
        Exactly one of file_path or file_url must be provided.
        """
        from laydata_core.errors import map_teable_error
        import os
        import mimetypes

        if (file_path is None and not file_url) or (file_path is not None and file_url):
            raise ValueError("Provide exactly one of file_path or file_url")

        try:
            if file_path is not None:
                filename = os.path.basename(file_path)
                guessed, _ = mimetypes.guess_type(filename)
                content_type = guessed or "application/octet-stream"
                with open(file_path, "rb") as f:
                    files = {"file": (filename, f, content_type)}
                    data = {"field": field}
                    r = await self._client.post(
                        f"/table/{self.id}/record/{record_id}/attachment",
                        data=data,
                        files=files,
                    )
            else:
                r = await self._client.post(
                    f"/table/{self.id}/record/{record_id}/attachment",
                    data={"field": field, "fileUrl": file_url},
                )
            r.raise_for_status()
            return r.json()
        except httpx.HTTPStatusError as e:
            context = build_error_context(
                operation="Upload attachment",
                url=f"/table/{self.id}/record/{record_id}/attachment",
                method="POST",
                status_code=e.response.status_code,
                table_id=self.id,
                base_id=self.base_id,
                record_id=record_id,
                file_path=file_path,
                file_url=file_url,
                extra={"Field": field},
            )
            
            try:
                error_data = e.response.json()
                raise map_teable_error(
                    e.response.status_code,
                    error_data.get("detail", str(e)),
                    error_data.get("code"),
                    context
                )
            except Exception:
                raise map_teable_error(e.response.status_code, str(e), None, context)


class TableClient:
    def __init__(self, client: httpx.AsyncClient, base_id: str):
        self._client = client
        self._base_id = base_id

    async def list(self) -> list[Table]:
        try:
            response = await self._client.get(f"/table?base_id={self._base_id}")
            response.raise_for_status()
            tables_data = response.json()
            return [Table(self._client, table) for table in tables_data]
        except httpx.HTTPStatusError as e:
            from laydata_core.errors import map_teable_error
            context = build_error_context(
                operation="List tables",
                url=f"/table?base_id={self._base_id}",
                method="GET",
                status_code=e.response.status_code,
                base_id=self._base_id,
            )
            
            try:
                error_data = e.response.json()
                raise map_teable_error(
                    e.response.status_code,
                    error_data.get("detail", str(e)),
                    error_data.get("code"),
                    context
                )
            except Exception:
                raise map_teable_error(e.response.status_code, str(e), None, context)

    async def create_or_get(self, name: str, icon: str | None = None, description: str | None = None) -> Table:
        try:
            payload = {"name": name}
            if icon is not None:
                payload["icon"] = icon
            if description is not None:
                payload["description"] = description
            
            response = await self._client.post(
                f"/table?base_id={self._base_id}",
                json=payload
            )
            response.raise_for_status()
            table_data = response.json()
            return Table(self._client, table_data)
        except httpx.HTTPStatusError as e:
            from laydata_core.errors import map_teable_error
            extras = {"Name": name}
            if icon is not None:
                extras["Icon"] = icon
            if description is not None:
                extras["Description"] = description
            context = build_error_context(
                operation="Create or get table",
                url=f"/table?base_id={self._base_id}",
                method="POST",
                status_code=e.response.status_code,
                base_id=self._base_id,
                extra=extras,
            )
            
            try:
                error_data = e.response.json()
                raise map_teable_error(
                    e.response.status_code,
                    error_data.get("detail", str(e)),
                    error_data.get("code"),
                    context
                )
            except Exception:
                raise map_teable_error(e.response.status_code, str(e), None, context)

