"""REST client handling, including BetterStackStream base class."""

from __future__ import annotations

import sys
from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar
from urllib.parse import parse_qsl

from singer_sdk import RESTStream
from singer_sdk.authenticators import BearerTokenAuthenticator
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.pagination import BaseAPIPaginator, BaseHATEOASPaginator

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:
    from urllib.parse import ParseResult

    from requests import Response
    from singer_sdk.helpers.types import Context


class BetterStackPaginator(BaseHATEOASPaginator):
    """Better Stack paginator class."""

    @override
    def get_next_url(self, response: Response) -> str | None:
        """Return the next page URL from the response."""
        data = response.json()
        return next(extract_jsonpath("$.pagination.next", data), None)


class BetterStackStream(RESTStream, metaclass=ABCMeta):
    """Better Stack stream class."""

    records_jsonpath = "$.data[*]"  # Or override `parse_response`.
    next_page_token_jsonpath = "$.next_page"  # noqa: S105
    primary_keys: ClassVar[list[str]] = ["id"]

    @property
    @abstractmethod
    def url_base(self) -> str:
        """Product-specific base URL for API requests."""
        raise NotImplementedError

    @property
    @override
    def authenticator(self) -> BearerTokenAuthenticator:
        return BearerTokenAuthenticator(token=self.config["token"])

    @override
    def get_new_paginator(self) -> BaseAPIPaginator:
        """Get a new paginator object."""
        return BetterStackPaginator()

    @override
    def get_url_params(
        self,
        context: Context | None,
        next_page_token: ParseResult | None,
    ) -> dict[str, Any]:
        return dict(parse_qsl(next_page_token.query)) if next_page_token else {}

    @override
    def post_process(
        self,
        row: dict,
        context: Context | None = None,
    ) -> dict | None:
        """Post-process a record with attributes."""
        attributes = row.pop("attributes", {})
        for key, value in attributes.items():
            row[f"attributes__{key}"] = value
        return row
