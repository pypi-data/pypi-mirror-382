"""Pipedream tap class."""

from __future__ import annotations

from singer_sdk import Stream, Tap
from singer_sdk import typing as th

from tap_pipedream import streams


class TapPipedream(Tap):
    """Singer tap for Pipedream."""

    name = "tap-pipedream"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "token",
            th.StringType,
            required=True,
            description="API Token for Pipedream",
        ),
        th.Property(
            "start_date",
            th.IntegerType,
            description="Earliest timestamp to get data from",
        ),
        th.Property(
            "organizations",
            th.ArrayType(th.StringType),
            description="List of organization IDs to get data from",
        ),
    ).to_dict()

    def discover_streams(self) -> list[Stream]:
        """Return a list of discovered streams.

        Returns:
            A list of Pipedream streams.
        """
        tap_streams: list[Stream] = [
            streams.UserSources(self),
            streams.UserSubscriptions(self),
            streams.UserSourceEvents(self),
            streams.Webhooks(self),
        ]

        if self.config.get("organizations"):
            tap_streams.extend(
                [
                    streams.OrganizationSources(self),
                    streams.OrganizationSubscriptions(self),
                    streams.OrganizationSourceEvents(self),
                ],
            )

        return tap_streams
