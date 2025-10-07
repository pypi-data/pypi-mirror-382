"""Stream type classes for tap-betterstack."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

from singer_sdk import typing as th
from singer_sdk.helpers._typing import TypeConformanceLevel

from tap_betterstack.client import BetterStackStream

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:
    from urllib.parse import ParseResult

    from singer_sdk.helpers.types import Context

__all__ = [
    "EscalationPolicies",
    "HeartbeatGroups",
    "Heartbeats",
    "IncidentTimelineEvents",
    "Incidents",
    "MonitorGroups",
    "Monitors",
    "OnCalls",
]

Rule = th.ObjectType(
    th.Property("created_at", th.DateTimeType),
    th.Property("updated_at", th.DateTimeType),
    th.Property("rule_target", th.StringType),
    th.Property("match_type", th.StringType),
    th.Property("content", th.StringType),
)

Field = th.ObjectType(
    th.Property("name", th.StringType),
    th.Property("special_type", th.StringType),
    th.Property("field_target", th.StringType),
    th.Property("match_type", th.StringType),
    th.Property("content", th.StringType),
    th.Property("content_before", th.StringType),
    th.Property("content_after", th.StringType),
)


class BaseUptimeStream(BetterStackStream):
    """Base Better Stack Uptime stream class."""

    url_base = "https://uptime.betterstack.com/api/v2"


class Monitors(BaseUptimeStream):
    """Monitors stream."""

    TYPE_CONFORMANCE_LEVEL = TypeConformanceLevel.ROOT_ONLY

    name = "monitors"
    path = "/monitors"
    replication_key = None

    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("type", th.StringType),
        th.Property("attributes__url", th.StringType),
        th.Property("attributes__pronounceable_name", th.StringType),
        th.Property("attributes__monitor_type", th.StringType),
        th.Property("attributes__monitor_group_id", th.StringType),
        th.Property("attributes__last_checked_at", th.StringType),
        th.Property("attributes__status", th.StringType),
        th.Property("attributes__required_keyword", th.StringType),
        th.Property("attributes__verify_ssl", th.BooleanType),
        th.Property("attributes__check_frequency", th.IntegerType),
        th.Property("attributes__call", th.BooleanType),
        th.Property("attributes__sms", th.BooleanType),
        th.Property("attributes__email", th.BooleanType),
        th.Property("attributes__push", th.BooleanType),
        th.Property("attributes__team_wait", th.IntegerType),
        th.Property("attributes__http_method", th.StringType),
        th.Property("attributes__request_timeout", th.IntegerType),
        th.Property("attributes__recovery_period", th.IntegerType),
        th.Property(
            "attributes__request_headers",
            th.ArrayType(
                th.ObjectType(
                    th.Property("id", th.StringType),
                    th.Property("name", th.StringType),
                    th.Property("value", th.StringType),
                ),
            ),
        ),
        th.Property("attributes__request_body", th.StringType),
        th.Property("attributes__paused_at", th.DateTimeType),
        th.Property("attributes__created_at", th.DateTimeType),
        th.Property("attributes__updated_at", th.DateTimeType),
        th.Property("attributes__ssl_expiration", th.IntegerType),
        th.Property("attributes__domain_expiration", th.IntegerType),
        th.Property("attributes__regions", th.ArrayType(th.StringType)),
        th.Property("attributes__port", th.StringType),
        th.Property("attributes__confirmation_period", th.IntegerType),
        th.Property("attributes__expected_status_codes", th.ArrayType(th.IntegerType)),
        th.Property("attributes__policy_id", th.StringType),
        th.Property("attributes__follow_redirects", th.BooleanType),
        th.Property("attributes__remember_cookies", th.BooleanType),
        th.Property("attributes__paused", th.BooleanType),
        th.Property("attributes__maintenance_from", th.DateTimeType),
        th.Property("attributes__maintenance_to", th.DateTimeType),
        th.Property("attributes__maintenance_timezone", th.StringType),
        th.Property("relationships", th.ObjectType()),
    ).to_dict()


class MonitorGroups(BaseUptimeStream):
    """Monitor groups stream."""

    TYPE_CONFORMANCE_LEVEL = TypeConformanceLevel.ROOT_ONLY

    name = "monitor_groups"
    path = "/monitor-groups"
    replication_key = None

    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("type", th.StringType),
        th.Property("attributes__name", th.StringType),
        th.Property("attributes__sort_index", th.IntegerType),
        th.Property("attributes__created_at", th.DateTimeType),
        th.Property("attributes__updated_at", th.DateTimeType),
        th.Property("attributes__paused", th.BooleanType),
    ).to_dict()


class Heartbeats(BaseUptimeStream):
    """Heartbeats stream."""

    TYPE_CONFORMANCE_LEVEL = TypeConformanceLevel.ROOT_ONLY

    name = "heartbeats"
    path = "/heartbeats"
    replication_key = None

    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("type", th.StringType),
        th.Property("attributes__name", th.StringType),
        th.Property("attributes__period", th.IntegerType),
        th.Property("attributes__grace", th.IntegerType),
        th.Property("attributes__call", th.BooleanType),
        th.Property("attributes__sms", th.BooleanType),
        th.Property("attributes__email", th.BooleanType),
        th.Property("attributes__push", th.BooleanType),
        th.Property("attributes__team_wait", th.IntegerType),
        th.Property("attributes__heartbeat_group_id", th.StringType),
        th.Property("attributes__sort_index", th.IntegerType),
        th.Property("attributes__paused_at", th.DateTimeType),
        th.Property("attributes__created_at", th.DateTimeType),
        th.Property("attributes__updated_at", th.DateTimeType),
        th.Property("attributes__status", th.StringType),
    ).to_dict()


class HeartbeatGroups(BaseUptimeStream):
    """Heartbeat groups stream."""

    TYPE_CONFORMANCE_LEVEL = TypeConformanceLevel.ROOT_ONLY

    name = "heartbeat_groups"
    path = "/heartbeat-groups"
    replication_key = None

    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("type", th.StringType),
        th.Property("attributes__name", th.StringType),
        th.Property("attributes__sort_index", th.IntegerType),
        th.Property("attributes__created_at", th.DateTimeType),
        th.Property("attributes__updated_at", th.DateTimeType),
        th.Property("attributes__paused", th.BooleanType),
    ).to_dict()


class OnCalls(BaseUptimeStream):
    """On-calls stream."""

    TYPE_CONFORMANCE_LEVEL = TypeConformanceLevel.ROOT_ONLY

    name = "on_calls"
    path = "/on-calls"
    replication_key = None

    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("type", th.StringType),
        th.Property("attributes__name", th.StringType),
        th.Property("attributes__default_calendar", th.BooleanType),
        th.Property("relationships", th.ObjectType()),
    ).to_dict()


class EscalationPolicies(BaseUptimeStream):
    """Escalation policies stream."""

    TYPE_CONFORMANCE_LEVEL = TypeConformanceLevel.ROOT_ONLY

    name = "escalation_policies"
    path = "/policies"
    replication_key = None

    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("type", th.StringType),
        th.Property("attributes__name", th.StringType),
        th.Property("attributes__repeat_count", th.IntegerType),
        th.Property("attributes__repeat_delay", th.IntegerType),
        th.Property("attributes__incident_token", th.StringType),
        th.Property(
            "attributes__steps",
            th.ArrayType(
                th.ObjectType(
                    th.Property("type", th.StringType),
                    th.Property("wait_before", th.IntegerType),
                    th.Property("urgency_id", th.IntegerType),
                    th.Property("timezone", th.StringType),
                    th.Property("days", th.ArrayType(th.StringType)),
                    th.Property("time_from", th.StringType),
                    th.Property("time_to", th.StringType),
                    th.Property("policy_id", th.StringType),
                    th.Property("step_members", th.ArrayType(th.ObjectType())),
                ),
            ),
        ),
    ).to_dict()


class Incidents(BaseUptimeStream):
    """Incidents stream."""

    TYPE_CONFORMANCE_LEVEL = TypeConformanceLevel.ROOT_ONLY

    name = "incidents"
    path = "/incidents"
    replication_key = None

    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("type", th.StringType),
        th.Property("attributes__name", th.StringType),
        th.Property("attributes__url", th.StringType),
        th.Property("attributes__http_method", th.StringType),
        th.Property("attributes__cause", th.StringType),
        th.Property("attributes__incident_group_id", th.IntegerType),
        th.Property("attributes__started_at", th.DateTimeType),
        th.Property("attributes__acknowledged_at", th.DateTimeType),
        th.Property("attributes__acknowledged_by", th.StringType),
        th.Property("attributes__resolved_at", th.DateTimeType),
        th.Property("attributes__resolved_by", th.StringType),
        th.Property("attributes__response_content", th.StringType),
        th.Property("attributes__response_options", th.StringType),
        th.Property("attributes__regions", th.ArrayType(th.StringType)),
        th.Property("attributes__response_url", th.StringType),
        th.Property("attributes__screenshot_url", th.StringType),
        th.Property("attributes__origin_url", th.StringType),
        th.Property("attributes__escalation_policy_id", th.StringType),
        th.Property("attributes__call", th.BooleanType),
        th.Property("attributes__sms", th.BooleanType),
        th.Property("attributes__email", th.BooleanType),
        th.Property("attributes__push", th.BooleanType),
        th.Property(
            "relationships",
            th.ObjectType(
                th.Property(
                    "monitor",
                    th.ObjectType(
                        th.Property(
                            "data",
                            th.ObjectType(
                                th.Property("id", th.StringType),
                            ),
                        ),
                        th.Property("type", th.StringType),
                    ),
                ),
            ),
        ),
    ).to_dict()

    @override
    def get_url_params(
        self,
        context: Context | None,
        next_page_token: ParseResult | None,
    ) -> dict[str, Any]:
        """Return a dictionary of params to use in the API request."""
        params = super().get_url_params(context, next_page_token)
        params["per_page"] = 50

        starting_timestamp = self.get_starting_timestamp(context)
        if starting_timestamp:
            params["from"] = starting_timestamp
        return params

    @override
    def get_child_context(self, record: dict, context: Context | None) -> dict | None:
        """Return a child context for the given record."""
        return {"incident_id": record["id"]}


class IncidentTimelineEvents(BaseUptimeStream):
    """Incident timeline events stream."""

    TYPE_CONFORMANCE_LEVEL = TypeConformanceLevel.ROOT_ONLY

    name = "incident_events"
    path = "/incidents/{incident_id}/timeline"
    replication_key = None
    parent_stream_type = Incidents

    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("type", th.StringType),
        th.Property("incident_id", th.StringType),
        th.Property("attributes__item_type", th.StringType),
        th.Property("attributes__at", th.DateTimeType),
        th.Property("attributes__data", th.ObjectType()),
    ).to_dict()


class EmailIntegrations(BaseUptimeStream):
    """Email integrations stream."""

    TYPE_CONFORMANCE_LEVEL = TypeConformanceLevel.ROOT_ONLY

    name = "email_integrations"
    path = "/email-integrations"
    replication_key = None

    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("type", th.StringType),
        th.Property("attributes__name", th.StringType),
        th.Property("attributes__created_at", th.DateTimeType),
        th.Property("attributes__updated_at", th.DateTimeType),
        th.Property("attributes__policy_id", th.StringType),
        th.Property("attributes__call", th.BooleanType),
        th.Property("attributes__sms", th.BooleanType),
        th.Property("attributes__email", th.BooleanType),
        th.Property("attributes__push", th.BooleanType),
        th.Property("attributes__team_wait", th.IntegerType),
        th.Property("attributes__recovery_period", th.IntegerType),
        th.Property("attributes__email_address", th.StringType),
        th.Property("attributes__paused", th.BooleanType),
        th.Property("attributes__started_rule_type", th.StringType),
        th.Property("attributes__acknowledged_rule_type", th.StringType),
        th.Property("attributes__resolved_rule_type", th.StringType),
        th.Property("attributes__started_rules", th.ArrayType(Rule)),
        th.Property("attributes__acknowledged_rules", th.ArrayType(Rule)),
        th.Property("attributes__resolved_rules", th.ArrayType(Rule)),
        th.Property("attributes__caused_field", Field),
        th.Property("attributes__started_alert_id_field", Field),
        th.Property("attributes__acknowledged_alert_id_field", Field),
        th.Property("attributes__resolved_alert_id_field", Field),
        th.Property("attributes__other_started_fields", th.ArrayType(Field)),
        th.Property("attributes__other_acknowledged_fields", th.ArrayType(Field)),
        th.Property("attributes__other_resolved_fields", th.ArrayType(Field)),
    ).to_dict()


class IncomingWebhooks(BaseUptimeStream):
    """Incoming webhooks stream."""

    TYPE_CONFORMANCE_LEVEL = TypeConformanceLevel.ROOT_ONLY

    name = "incoming_webhooks"
    path = "/incoming-webhooks"
    replication_key = None

    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("type", th.StringType),
        th.Property("attributes__name", th.StringType),
        th.Property("attributes__created_at", th.DateTimeType),
        th.Property("attributes__updated_at", th.DateTimeType),
        th.Property("attributes__policy_id", th.StringType),
        th.Property("attributes__call", th.BooleanType),
        th.Property("attributes__sms", th.BooleanType),
        th.Property("attributes__email", th.BooleanType),
        th.Property("attributes__push", th.BooleanType),
        th.Property("attributes__team_wait", th.IntegerType),
        th.Property("attributes__recovery_period", th.IntegerType),
        th.Property("attributes__url", th.StringType),
        th.Property("attributes__paused", th.BooleanType),
        th.Property("attributes__started_rule_type", th.StringType),
        th.Property("attributes__acknowledged_rule_type", th.StringType),
        th.Property("attributes__resolved_rule_type", th.StringType),
        th.Property("attributes__started_rules", th.ArrayType(Rule)),
        th.Property("attributes__acknowledged_rules", th.ArrayType(Rule)),
        th.Property("attributes__resolved_rules", th.ArrayType(Rule)),
        th.Property("attributes__caused_field", Field),
        th.Property("attributes__started_alert_id_field", Field),
        th.Property("attributes__acknowledged_alert_id_field", Field),
        th.Property("attributes__resolved_alert_id_field", Field),
        th.Property("attributes__other_started_fields", th.ArrayType(Field)),
        th.Property("attributes__other_acknowledged_fields", th.ArrayType(Field)),
        th.Property("attributes__other_resolved_fields", th.ArrayType(Field)),
    ).to_dict()


class StatusPages(BaseUptimeStream):
    """Status pages stream."""

    TYPE_CONFORMANCE_LEVEL = TypeConformanceLevel.ROOT_ONLY

    name = "status_pages"
    path = "/status-pages"
    replication_key = None

    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("type", th.StringType),
        th.Property("attributes__company_name", th.StringType),
        th.Property("attributes__company_url", th.StringType),
        th.Property("attributes__contact_url", th.StringType),
        th.Property("attributes__logo_url", th.StringType),
        th.Property("attributes__timezone", th.StringType),
        th.Property("attributes__subdomain", th.StringType),
        th.Property("attributes__custom_domain", th.StringType),
        th.Property("attributes__custom_css", th.StringType),
        th.Property("attributes__google_analytics_id", th.StringType),
        th.Property("attributes__min_incident_length", th.IntegerType),
        th.Property("attributes__announcement", th.StringType),
        th.Property("attributes__announcement_embed_enabled", th.BooleanType),
        th.Property("attributes__announcement_embed_css", th.StringType),
        th.Property("attributes__announcement_embed_link", th.StringType),
        th.Property("attributes__subscribable", th.BooleanType),
        th.Property("attributes__hide_from_search_engines", th.BooleanType),
        th.Property("attributes__password_enabled", th.BooleanType),
        th.Property("attributes__history", th.IntegerType),
        th.Property("attributes__aggregate_state", th.StringType),
        th.Property("attributes__created_at", th.DateTimeType),
        th.Property("attributes__updated_at", th.DateTimeType),
    ).to_dict()
