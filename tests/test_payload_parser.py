"""Tests for deploy_notify.payload_parser module."""

import pytest
from deploy_notify.payload_parser import DeploymentEvent, PayloadParser


MINIMAL_PAYLOAD = {
    "service": "api-gateway",
    "environment": "production",
    "version": "1.4.2",
    "status": "success",
}

FULL_PAYLOAD = {
    **MINIMAL_PAYLOAD,
    "deployed_by": "alice",
    "commit_sha": "abc1234567890",
    "commit_message": "fix: resolve timeout issue",
    "repo_url": "https://github.com/org/api-gateway",
    "duration_seconds": 42,
    "custom_field": "custom_value",
}


@pytest.fixture
def parser() -> PayloadParser:
    return PayloadParser()


class TestPayloadParserMinimal:
    def test_parses_minimal_payload(self, parser):
        event = parser.parse(MINIMAL_PAYLOAD)
        assert event.service == "api-gateway"
        assert event.environment == "production"
        assert event.version == "1.4.2"
        assert event.status == "success"

    def test_optional_fields_are_none(self, parser):
        event = parser.parse(MINIMAL_PAYLOAD)
        assert event.deployed_by is None
        assert event.commit_sha is None
        assert event.duration_seconds is None

    def test_extra_is_empty_for_minimal(self, parser):
        event = parser.parse(MINIMAL_PAYLOAD)
        assert event.extra == {}


class TestPayloadParserFull:
    def test_parses_full_payload(self, parser):
        event = parser.parse(FULL_PAYLOAD)
        assert event.deployed_by == "alice"
        assert event.commit_sha == "abc1234567890"
        assert event.duration_seconds == 42

    def test_extra_fields_captured(self, parser):
        event = parser.parse(FULL_PAYLOAD)
        assert event.extra == {"custom_field": "custom_value"}

    def test_short_sha(self, parser):
        event = parser.parse(FULL_PAYLOAD)
        assert event.short_sha == "abc1234"


class TestDeploymentEventProperties:
    @pytest.mark.parametrize("status,emoji", [
        ("success", "✅"),
        ("failure", "❌"),
        ("in_progress", "🔄"),
    ])
    def test_status_emoji(self, parser, status, emoji):
        payload = {**MINIMAL_PAYLOAD, "status": status}
        event = parser.parse(payload)
        assert event.status_emoji == emoji

    def test_short_sha_none_when_no_sha(self, parser):
        event = parser.parse(MINIMAL_PAYLOAD)
        assert event.short_sha is None


class TestPayloadParserValidation:
    def test_raises_on_missing_required_field(self, parser):
        payload = {k: v for k, v in MINIMAL_PAYLOAD.items() if k != "service"}
        with pytest.raises(ValueError, match="Missing required fields"):
            parser.parse(payload)

    def test_raises_on_invalid_status(self, parser):
        payload = {**MINIMAL_PAYLOAD, "status": "unknown"}
        with pytest.raises(ValueError, match="Invalid status"):
            parser.parse(payload)

    def test_status_normalized_to_lowercase(self, parser):
        payload = {**MINIMAL_PAYLOAD, "status": "SUCCESS"}
        event = parser.parse(payload)
        assert event.status == "success"
