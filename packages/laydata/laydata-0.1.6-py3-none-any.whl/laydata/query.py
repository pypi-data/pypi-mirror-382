from __future__ import annotations
from typing import Any, List


class RecordsQuery:
    """
    Friendly, chainable query builder over Table.records().
    Supports a simple AND of field conditions plus sorting, pagination, and search.
    """
    def __init__(self, table: "Table"):
        self._table = table
        self._where: dict[str, Any] = {}
        self._order_by: list[dict] = []
        self._take: int | None = None
        self._skip: int | None = None
        self._search: list | None = None

    # --- where helpers (AND) ---
    def where(self, field: str, value: Any) -> "RecordsQuery":
        # value can be scalar, list (interpreted as IN), or dict of op->val
        if isinstance(value, list):
            self._merge_field(field, {"in": value})
        else:
            self._merge_field(field, value)
        return self

    def eq(self, field: str, value: Any) -> "RecordsQuery":
        return self.where(field, value)

    def ne(self, field: str, value: Any) -> "RecordsQuery":
        self._merge_field(field, {"!=": value})
        return self

    def gt(self, field: str, value: Any) -> "RecordsQuery":
        self._merge_field(field, {">": value})
        return self

    def gte(self, field: str, value: Any) -> "RecordsQuery":
        self._merge_field(field, {">=": value})
        return self

    def lt(self, field: str, value: Any) -> "RecordsQuery":
        self._merge_field(field, {"<": value})
        return self

    def lte(self, field: str, value: Any) -> "RecordsQuery":
        self._merge_field(field, {"<=": value})
        return self

    def contains(self, field: str, value: str) -> "RecordsQuery":
        self._merge_field(field, {"contains": value})
        return self

    def not_contains(self, field: str, value: str) -> "RecordsQuery":
        self._merge_field(field, {"doesNotContain": value})
        return self

    def in_(self, field: str, values: List[Any]) -> "RecordsQuery":
        self._merge_field(field, {"in": values})
        return self

    def not_in(self, field: str, values: List[Any]) -> "RecordsQuery":
        self._merge_field(field, {"notIn": values})
        return self

    def is_empty(self, field: str) -> "RecordsQuery":
        self._merge_field(field, {"isEmpty": None})
        return self

    def is_not_empty(self, field: str) -> "RecordsQuery":
        self._merge_field(field, {"isNotEmpty": None})
        return self

    def between(self, field: str, lo: Any, hi: Any, inclusive: bool = True) -> "RecordsQuery":
        if inclusive:
            self._merge_field(field, {">=": lo, "<=": hi})
        else:
            self._merge_field(field, {">": lo, "<": hi})
        return self

    def _merge_field(self, field: str, value: Any) -> None:
        existing = self._where.get(field)
        if existing is None:
            self._where[field] = value
            return
        # if both are dicts, merge ops
        if isinstance(existing, dict) and isinstance(value, dict):
            merged = dict(existing)
            merged.update(value)
            self._where[field] = merged
        else:
            # last one wins (common simple cases)
            self._where[field] = value

    # --- sorting / paging / search ---
    def order_by(self, field: str, order: str = "asc") -> "RecordsQuery":
        self._order_by.append({"field": field, "order": order})
        return self

    def asc(self, field: str) -> "RecordsQuery":
        return self.order_by(field, "asc")

    def desc(self, field: str) -> "RecordsQuery":
        return self.order_by(field, "desc")

    def take(self, n: int) -> "RecordsQuery":
        self._take = n
        return self

    def skip(self, n: int) -> "RecordsQuery":
        self._skip = n
        return self

    def search(self, value: str, field: str, fuzzy: bool = True) -> "RecordsQuery":
        self._search = [value, field, fuzzy]
        return self

    # --- execution ---
    async def all(self):
        return await self._table.records(
            take=self._take,
            skip=self._skip,
            where=self._where if self._where else None,
            order_by=self._order_by if self._order_by else None,
            search=self._search,
        )

    async def first(self):
        rows = await self._table.records(
            take=1,
            where=self._where if self._where else None,
            order_by=self._order_by if self._order_by else None,
            search=self._search,
        )
        return rows[0] if rows else None