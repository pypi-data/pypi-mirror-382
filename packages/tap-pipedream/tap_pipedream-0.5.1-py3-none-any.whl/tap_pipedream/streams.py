"""Stream type classes for tap-pipedream."""

from __future__ import annotations

import typing as t

from singer_sdk import typing as th

from tap_pipedream.client import PipedreamStream

if t.TYPE_CHECKING:
    from singer_sdk.helpers.types import Context, Record


class UserSources(PipedreamStream):
    """Sources stream."""

    name = "user_sources"
    path = "/users/me/sources/"
    primary_keys = ("id",)

    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("component_id", th.StringType),
        th.Property("active", th.BooleanType),
        th.Property("created_at", th.IntegerType),
        th.Property("updated_at", th.IntegerType),
        th.Property("name", th.StringType),
        th.Property("name_slug", th.StringType),
        th.Property("owner_id", th.StringType),
        th.Property(
            "configured_props",
            th.ObjectType(
                th.Property(
                    "timer",
                    th.ObjectType(
                        th.Property("cron", th.StringType),
                        th.Property("interval_seconds", th.IntegerType),
                    ),
                ),
                th.Property(
                    "url",
                    th.StringType,
                ),
                th.Property(
                    "httpRequest",
                    th.ObjectType(
                        th.Property(
                            "auth",
                            th.ObjectType(
                                th.Property(
                                    "type",
                                    th.StringType,
                                ),
                                th.Property(
                                    "username",
                                    th.StringType,
                                ),
                                th.Property(
                                    "password",
                                    th.StringType,
                                ),
                                th.Property(
                                    "token",
                                    th.StringType,
                                ),
                            ),
                        ),
                        th.Property(
                            "body",
                            th.ObjectType(
                                th.Property(
                                    "contentType",
                                    th.StringType,
                                ),
                                th.Property(
                                    "fields",
                                    th.ArrayType(th.StringType),
                                ),
                                th.Property(
                                    "mode",
                                    th.StringType,
                                ),
                                th.Property(
                                    "type",
                                    th.StringType,
                                ),
                            ),
                        ),
                        th.Property(
                            "headers",
                            th.ArrayType(th.StringType),
                        ),
                        th.Property(
                            "method",
                            th.StringType,
                        ),
                        th.Property(
                            "params",
                            th.ArrayType(
                                th.ObjectType(
                                    th.Property(
                                        "name",
                                        th.StringType,
                                    ),
                                    th.Property(
                                        "value",
                                        th.StringType,
                                    ),
                                    th.Property(
                                        "disabled",
                                        th.BooleanType,
                                    ),
                                ),
                            ),
                        ),
                        th.Property(
                            "tab",
                            th.StringType,
                        ),
                        th.Property(
                            "url",
                            th.StringType,
                        ),
                    ),
                ),
                th.Property(
                    "emitBodyOnly",
                    th.BooleanType,
                ),
                th.Property(
                    "emitAsArray",
                    th.BooleanType,
                ),
            ),
        ),
    ).to_dict()

    def get_child_context(
        self,
        record: Record,
        context: Context | None,  # noqa: ARG002
    ) -> dict[str, t.Any]:
        """Return a dictionary of child context objects.

        Args:
            record: A dictionary representing one record from the API response.
            context: A dictionary of any context objects from the parent stream.

        Returns:
            A context dictionary.
        """
        return {"source_id": record["id"]}


class UserSourceEvents(PipedreamStream):
    """User Source Events stream."""

    name = "user_source_events"
    path = "/sources/{source_id}/events"
    primary_keys = ("id",)
    parent_stream_type = UserSources

    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("source_id", th.StringType),
        th.Property("e", th.StringType),
        th.Property("ts", th.IntegerType),
        th.Property("key", th.StringType),
    ).to_dict()

    def get_url_params(
        self,
        context: Context | None,  # noqa: ARG002
        next_page_token: str | None,  # noqa: ARG002
    ) -> dict[str, t.Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: A dictionary of any context objects from the parent stream.
            next_page_token: A string representing the next page of results.

        Returns:
            A dictionary of values to be used in URL parameterization.
        """
        return {
            "expand": "event",
            "limit": 100,
        }


class UserSubscriptions(PipedreamStream):
    """Subscriptions stream."""

    name = "user_subscriptions"
    path = "/users/me/subscriptions"
    primary_keys = ("id",)

    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("emitter_id", th.StringType),
        th.Property("listener_id", th.StringType),
        th.Property("event_name", th.StringType),
    ).to_dict()


class _BaseOrganizationStream(PipedreamStream):
    """Base Organization stream."""

    @property
    def partitions(self) -> list[dict[str, t.Any]] | None:
        """Return a list of partitions.

        Returns:
            A list of partitions.
        """
        return [{"org_id": org_id} for org_id in self.config.get("organizations", [])]


class OrganizationSources(UserSources, _BaseOrganizationStream):
    """Organization Sources stream."""

    name = "organization_sources"
    path = "/orgs/{org_id}/sources/"


class OrganizationSubscriptions(UserSubscriptions, _BaseOrganizationStream):
    """Organization Subscriptions stream."""

    name = "organization_subscriptions"
    path = "/orgs/{org_id}/subscriptions/"


class Webhooks(PipedreamStream):
    """Webhooks stream."""

    name = "webhooks"
    path = "/users/me/webhooks"
    primary_keys = ("id",)

    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("name", th.StringType),
        th.Property("description", th.StringType),
        th.Property("url", th.StringType),
        th.Property("active", th.BooleanType),
        th.Property("created_at", th.IntegerType),
        th.Property("updated_at", th.IntegerType),
    ).to_dict()


class OrganizationSourceEvents(UserSourceEvents):
    """Organization Source Events stream."""

    name = "organization_source_events"
    parent_stream_type = OrganizationSources
