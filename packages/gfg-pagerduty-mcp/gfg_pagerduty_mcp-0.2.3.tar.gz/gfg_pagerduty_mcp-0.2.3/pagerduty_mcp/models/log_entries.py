"""Pydantic models for PagerDuty log entries."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from pagerduty_mcp.models.base import MAX_RESULTS
from pagerduty_mcp.models.incidents import Urgency
from pagerduty_mcp.models.references import IncidentReference, ServiceReference, TeamReference, UserReference

LogEntryInclude = Literal["channels", "incidents", "services", "teams", "users"]


class LogEntryQuery(BaseModel):
    """Query parameters for fetching PagerDuty log entries."""

    model_config = ConfigDict(extra="forbid")

    incident_id: str | None = Field(
        default=None,
        description="Optional incident ID to scope log entries to a specific incident.",
    )
    since: datetime | None = Field(default=None, description="Fetch log entries created at or after this time.")
    until: datetime | None = Field(default=None, description="Fetch log entries created at or before this time.")
    is_overview: bool | None = Field(
        default=None,
        description=(
            "When true, only the most important log entries are returned. Available when querying a specific incident."
        ),
    )
    service_ids: list[str] | None = Field(default=None, description="Filter log entries by service IDs.")
    team_ids: list[str] | None = Field(default=None, description="Filter log entries by team IDs.")
    user_ids: list[str] | None = Field(default=None, description="Filter log entries by user IDs.")
    urgencies: list[Urgency] | None = Field(default=None, description="Filter log entries by urgency.")
    include: list[LogEntryInclude] | None = Field(
        default=None,
        description="Include related entities in the response (channels, incidents, services, teams, users).",
    )
    limit: int | None = Field(
        default=MAX_RESULTS,
        ge=1,
        le=MAX_RESULTS,
        description="Maximum number of log entries to return.",
    )

    def to_params(self) -> dict[str, Any]:
        """Convert the query into request parameters for the PagerDuty API."""

        params: dict[str, Any] = {}

        if self.since:
            params["since"] = self.since.isoformat()
        if self.until:
            params["until"] = self.until.isoformat()
        if self.is_overview is not None:
            params["is_overview"] = str(self.is_overview).lower()
        if self.service_ids:
            params["service_ids[]"] = self.service_ids
        if self.team_ids:
            params["team_ids[]"] = self.team_ids
        if self.user_ids:
            params["user_ids[]"] = self.user_ids
        if self.urgencies:
            params["urgencies[]"] = self.urgencies
        if self.include:
            params["include[]"] = self.include
        if self.limit is not None:
            params["limit"] = self.limit

        return params


class LogEntry(BaseModel):
    """Representation of a PagerDuty log entry."""

    model_config = ConfigDict(extra="allow")

    id: str = Field(description="Unique identifier of the log entry.")
    type: str = Field(description="Type of the log entry.")
    summary: str | None = Field(default=None, description="Short description of the log entry.")
    created_at: datetime = Field(description="Timestamp when the log entry was created.")
    agent: UserReference | dict[str, Any] | None = Field(
        default=None,
        description="The entity that performed the action recorded by the log entry.",
    )
    service: ServiceReference | None = Field(default=None, description="Service associated with the log entry.")
    incident: IncidentReference | None = Field(default=None, description="Incident associated with the log entry.")
    teams: list[TeamReference] | None = Field(
        default=None,
        description="Teams referenced by the log entry.",
    )
    channel: dict[str, Any] | None = Field(
        default=None,
        description="Channel details describing where the log entry originated.",
    )
    event_details: dict[str, Any] | None = Field(
        default=None,
        description="Additional event details provided by PagerDuty.",
    )


