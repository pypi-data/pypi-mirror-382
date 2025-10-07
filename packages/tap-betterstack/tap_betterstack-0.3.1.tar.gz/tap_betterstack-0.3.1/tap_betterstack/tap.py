"""Better Stack tap class."""

from __future__ import annotations

import sys

from singer_sdk import Stream, Tap
from singer_sdk import typing as th

from tap_betterstack.streams import uptime

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


class TapBetterStack(Tap):
    """Singer tap for Better Stack."""

    name = "tap-betterstack"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "token",
            th.StringType,
            required=True,
            description="API Token for Better Stack",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="Earliest datetime to get data from",
        ),
        additional_properties=False,
    ).to_dict()

    @override
    def discover_streams(self) -> list[Stream]:
        return [
            uptime.Monitors(tap=self),
            uptime.MonitorGroups(tap=self),
            uptime.Heartbeats(tap=self),
            uptime.HeartbeatGroups(tap=self),
            uptime.OnCalls(tap=self),
            uptime.EscalationPolicies(tap=self),
            uptime.Incidents(tap=self),
            uptime.IncidentTimelineEvents(tap=self),
            uptime.EmailIntegrations(tap=self),
            uptime.IncomingWebhooks(tap=self),
            uptime.StatusPages(tap=self),
        ]
