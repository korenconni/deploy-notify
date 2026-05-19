"""deploy-notify: Webhook bridge for structured deployment summaries."""

from deploy_notify.formatters import format_discord, format_slack
from deploy_notify.payload_parser import DeploymentEvent, PayloadParser, parse

__all__ = [
    "DeploymentEvent",
    "PayloadParser",
    "parse",
    "format_slack",
    "format_discord",
]
