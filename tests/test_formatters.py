"""Tests for Slack and Discord message formatters."""

from __future__ import annotations

import pytest

from deploy_notify.formatters import format_discord, format_slack
from deploy_notify.payload_parser import DeploymentEvent


@pytest.fixture()
def minimal_event() -> DeploymentEvent:
    return DeploymentEvent(
        service="api",
        environment="production",
        status="success",
        commit="abc1234",
    )


@pytest.fixture()
def full_event() -> DeploymentEvent:
    return DeploymentEvent(
        service="worker",
        environment="staging",
        status="failure",
        commit="deadbeef",
        author="alice",
        branch="main",
        message="OOM in container",
        duration_seconds=42,
    )


class TestFormatSlack:
    def test_returns_blocks_key(self, minimal_event: DeploymentEvent) -> None:
        payload = format_slack(minimal_event)
        assert "blocks" in payload

    def test_header_contains_service_and_env(self, minimal_event: DeploymentEvent) -> None:
        payload = format_slack(minimal_event)
        header = payload["blocks"][0]["text"]["text"]
        assert "api" in header
        assert "production" in header

    def test_commit_present_in_fields(self, minimal_event: DeploymentEvent) -> None:
        payload = format_slack(minimal_event)
        fields_block = payload["blocks"][1]
        field_texts = [f["text"] for f in fields_block["fields"]]
        assert any("abc1234" in t for t in field_texts)

    def test_optional_fields_included_when_present(self, full_event: DeploymentEvent) -> None:
        payload = format_slack(full_event)
        fields_block = payload["blocks"][1]
        field_texts = " ".join(f["text"] for f in fields_block["fields"])
        assert "alice" in field_texts
        assert "main" in field_texts
        assert "42" in field_texts

    def test_message_appended_as_context(self, full_event: DeploymentEvent) -> None:
        payload = format_slack(full_event)
        last_block = payload["blocks"][-1]
        assert last_block["type"] == "context"
        assert "OOM in container" in last_block["elements"][0]["text"]

    def test_no_context_block_when_no_message(self, minimal_event: DeploymentEvent) -> None:
        payload = format_slack(minimal_event)
        types = [b["type"] for b in payload["blocks"]]
        assert "context" not in types


class TestFormatDiscord:
    def test_returns_embeds_key(self, minimal_event: DeploymentEvent) -> None:
        payload = format_discord(minimal_event)
        assert "embeds" in payload
        assert len(payload["embeds"]) == 1

    def test_title_contains_service_and_env(self, minimal_event: DeploymentEvent) -> None:
        embed = format_discord(minimal_event)["embeds"][0]
        assert "api" in embed["title"]
        assert "production" in embed["title"]

    def test_success_color(self, minimal_event: DeploymentEvent) -> None:
        embed = format_discord(minimal_event)["embeds"][0]
        assert embed["color"] == 0x2ECC71

    def test_failure_color(self, full_event: DeploymentEvent) -> None:
        embed = format_discord(full_event)["embeds"][0]
        assert embed["color"] == 0xE74C3C

    def test_description_set_from_message(self, full_event: DeploymentEvent) -> None:
        embed = format_discord(full_event)["embeds"][0]
        assert embed.get("description") == "OOM in container"

    def test_no_description_when_no_message(self, minimal_event: DeploymentEvent) -> None:
        embed = format_discord(minimal_event)["embeds"][0]
        assert "description" not in embed

    def test_optional_fields_in_embed(self, full_event: DeploymentEvent) -> None:
        embed = format_discord(full_event)["embeds"][0]
        field_names = [f["name"] for f in embed["fields"]]
        assert "Author" in field_names
        assert "Branch" in field_names
        assert "Duration" in field_names
