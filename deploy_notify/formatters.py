"""Formatters that convert DeploymentEvent into Slack or Discord message payloads."""

from __future__ import annotations

from typing import Any

from deploy_notify.payload_parser import DeploymentEvent, status_emoji


def format_slack(event: DeploymentEvent) -> dict[str, Any]:
    """Return a Slack Block Kit message payload for the given deployment event."""
    emoji = status_emoji(event.status)
    header_text = f"{emoji} *{event.service}* deployed to *{event.environment}*"

    fields = [
        {"type": "mrkdwn", "text": f"*Status:*\n{event.status}"},
        {"type": "mrkdwn", "text": f"*Commit:*\n`{event.commit}`"},
    ]

    if event.author:
        fields.append({"type": "mrkdwn", "text": f"*Author:*\n{event.author}"})
    if event.branch:
        fields.append({"type": "mrkdwn", "text": f"*Branch:*\n{event.branch}"})
    if event.duration_seconds is not None:
        fields.append(
            {"type": "mrkdwn", "text": f"*Duration:*\n{event.duration_seconds}s"}
        )

    blocks: list[dict[str, Any]] = [
        {"type": "section", "text": {"type": "mrkdwn", "text": header_text}},
        {"type": "section", "fields": fields},
    ]

    if event.message:
        blocks.append(
            {
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": event.message}],
            }
        )

    return {"blocks": blocks}


def format_discord(event: DeploymentEvent) -> dict[str, Any]:
    """Return a Discord webhook embed payload for the given deployment event."""
    emoji = status_emoji(event.status)

    COLOR_MAP = {
        "success": 0x2ECC71,
        "failure": 0xE74C3C,
        "started": 0x3498DB,
        "cancelled": 0x95A5A6,
    }
    color = COLOR_MAP.get(event.status.lower(), 0x7F8C8D)

    description_parts = []
    if event.message:
        description_parts.append(event.message)

    embed: dict[str, Any] = {
        "title": f"{emoji} {event.service} → {event.environment}",
        "color": color,
        "fields": [
            {"name": "Status", "value": event.status, "inline": True},
            {"name": "Commit", "value": f"`{event.commit}`", "inline": True},
        ],
    }

    if event.author:
        embed["fields"].append({"name": "Author", "value": event.author, "inline": True})
    if event.branch:
        embed["fields"].append({"name": "Branch", "value": event.branch, "inline": True})
    if event.duration_seconds is not None:
        embed["fields"].append(
            {"name": "Duration", "value": f"{event.duration_seconds}s", "inline": True}
        )
    if description_parts:
        embed["description"] = "\n".join(description_parts)

    return {"embeds": [embed]}
