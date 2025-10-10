"""Contact resource client using TypedDict shapes (no Pydantic)."""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from .types import (
    APIError,
    ContactDeleteResponse,
    Contact,
    ContactUpdate,
    ContactUpdateResponse,
    ContactUpsert,
    ContactUpsertResponse,
    ContactCreate,
    ContactCreateResponse,
)


class Contacts:
    """Client for `/contactBooks` endpoints."""

    def __init__(self, unsent: "unsent") -> None:
        self.unsent = unsent

    def create(
        self, book_id: str, payload: ContactCreate
    ) -> Tuple[Optional[ContactCreateResponse], Optional[APIError]]:
        data, err = self.unsent.post(
            f"/contactBooks/{book_id}/contacts",
            payload,
        )
        return (data, err)  # type: ignore[return-value]

    def get(
        self, book_id: str, contact_id: str
    ) -> Tuple[Optional[Contact], Optional[APIError]]:
        data, err = self.unsent.get(
            f"/contactBooks/{book_id}/contacts/{contact_id}"
        )
        return (data, err)  # type: ignore[return-value]

    def update(
        self, book_id: str, contact_id: str, payload: ContactUpdate
    ) -> Tuple[Optional[ContactUpdateResponse], Optional[APIError]]:
        data, err = self.unsent.patch(
            f"/contactBooks/{book_id}/contacts/{contact_id}",
            payload,
        )
        return (data, err)  # type: ignore[return-value]

    def upsert(
        self, book_id: str, contact_id: str, payload: ContactUpsert
    ) -> Tuple[Optional[ContactUpsertResponse], Optional[APIError]]:
        data, err = self.unsent.put(
            f"/contactBooks/{book_id}/contacts/{contact_id}",
            payload,
        )
        return (data, err)  # type: ignore[return-value]

    def delete(
        self, *, book_id: str, contact_id: str
    ) -> Tuple[Optional[ContactDeleteResponse], Optional[APIError]]:
        data, err = self.unsent.delete(
            f"/contactBooks/{book_id}/contacts/{contact_id}"
        )
        return (data, err)  # type: ignore[return-value]


from .unsent import unsent  # noqa: E402  pylint: disable=wrong-import-position
