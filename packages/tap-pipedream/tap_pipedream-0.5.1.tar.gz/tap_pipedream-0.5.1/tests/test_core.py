"""Tests standard tap features using the built-in SDK tests library."""

from __future__ import annotations

from typing import Any

from singer_sdk.testing import SuiteConfig, get_tap_test_class

from tap_pipedream.tap import TapPipedream

SAMPLE_CONFIG: dict[str, Any] = {}


TestTapPipedream = get_tap_test_class(
    TapPipedream,
    config=SAMPLE_CONFIG,
    suite_config=SuiteConfig(
        ignore_no_records_for_streams=[
            "user_source_events",
            "user_sources",
            "user_subscriptions",
            "webhooks",
        ]
    ),
)
