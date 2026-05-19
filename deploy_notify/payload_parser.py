"""Parse incoming webhook payloads into structured deployment summaries."""

from dataclasses import dataclass, field
from typing import Optional
import re


@dataclass
class DeploymentEvent:
    """Structured representation of a deployment event."""

    service: str
    environment: str
    version: str
    status: str  # 'success' | 'failure' | 'in_progress'
    deployed_by: Optional[str] = None
    commit_sha: Optional[str] = None
    commit_message: Optional[str] = None
    repo_url: Optional[str] = None
    duration_seconds: Optional[int] = None
    extra: dict = field(default_factory=dict)

    @property
    def short_sha(self) -> Optional[str]:
        """Return first 7 characters of commit SHA."""
        if self.commit_sha:
            return self.commit_sha[:7]
        return None

    @property
    def status_emoji(self) -> str:
        """Return an emoji representing the deployment status."""
        return {
            "success": "✅",
            "failure": "❌",
            "in_progress": "🔄",
        }.get(self.status, "❓")


class PayloadParser:
    """Parse raw webhook payload dicts into DeploymentEvent instances."""

    REQUIRED_FIELDS = {"service", "environment", "version", "status"}
    VALID_STATUSES = {"success", "failure", "in_progress"}

    def parse(self, payload: dict) -> DeploymentEvent:
        """Parse a payload dict and return a DeploymentEvent.

        Raises:
            ValueError: If required fields are missing or status is invalid.
        """
        missing = self.REQUIRED_FIELDS - payload.keys()
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(sorted(missing))}")

        status = payload["status"].lower()
        if status not in self.VALID_STATUSES:
            raise ValueError(
                f"Invalid status '{status}'. Must be one of: {', '.join(self.VALID_STATUSES)}"
            )

        known_keys = {
            "service", "environment", "version", "status",
            "deployed_by", "commit_sha", "commit_message",
            "repo_url", "duration_seconds",
        }
        extra = {k: v for k, v in payload.items() if k not in known_keys}

        return DeploymentEvent(
            service=str(payload["service"]),
            environment=str(payload["environment"]),
            version=str(payload["version"]),
            status=status,
            deployed_by=payload.get("deployed_by"),
            commit_sha=payload.get("commit_sha"),
            commit_message=payload.get("commit_message"),
            repo_url=payload.get("repo_url"),
            duration_seconds=payload.get("duration_seconds"),
            extra=extra,
        )
