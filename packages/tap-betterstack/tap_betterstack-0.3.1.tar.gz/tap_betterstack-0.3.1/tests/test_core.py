"""Tests standard tap features using the built-in SDK tests library."""

from __future__ import annotations

from typing import Any

from singer_sdk.testing import SuiteConfig, get_tap_test_class

from tap_betterstack.tap import TapBetterStack

SAMPLE_CONFIG: dict[str, Any] = {}

TestTapBetterStack = get_tap_test_class(
    TapBetterStack,
    config=SAMPLE_CONFIG,
    suite_config=SuiteConfig(
        ignore_no_records_for_streams=[
            "monitor_groups",
            "heartbeat_groups",
            "heartbeats",
            "escalation_policies",
            "email_integrations",
            "incoming_webhooks",
            "status_pages",
            "incident_events",
            "incidents",
        ],
    ),
)
