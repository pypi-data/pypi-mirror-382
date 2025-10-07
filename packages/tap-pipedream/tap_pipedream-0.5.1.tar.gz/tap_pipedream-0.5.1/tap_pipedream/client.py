"""REST client handling, including PipedreamStream base class."""

from __future__ import annotations

import typing as t

from singer_sdk import RESTStream
from singer_sdk.authenticators import BearerTokenAuthenticator

if t.TYPE_CHECKING:
    from singer_sdk.helpers.types import Context


class PipedreamStream(RESTStream[str]):
    """Pipedream stream class."""

    url_base = "https://api.pipedream.com/v1"
    records_jsonpath = "$.data[*]"
    next_page_token_jsonpath = "$.page_info.end_cursor"  # noqa: S105

    page_size = 100

    @property
    def authenticator(self) -> BearerTokenAuthenticator:
        """Get an authenticator object.

        Returns:
            The authenticator instance for this REST stream.
        """
        return BearerTokenAuthenticator(token=self.config["token"])

    @property
    def http_headers(self) -> dict[str, str]:
        """Return the http headers needed.

        Returns:
            A dictionary of HTTP headers.
        """
        return {"User-Agent": f"{self.tap_name}/{self._tap.plugin_version}"}

    def get_url_params(
        self,
        context: Context | None,  # noqa: ARG002
        next_page_token: str | None,
    ) -> dict[str, t.Any]:
        """Get URL query parameters.

        Args:
            context: Stream sync context.
            next_page_token: Next offset.

        Returns:
            Mapping of URL query parameters.
        """
        return {
            "limit": self.page_size,
            "after": next_page_token,
        }
