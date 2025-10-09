"""Tools for interacting with PagerDuty log entries."""

from __future__ import annotations

from typing import Any

from pagerduty_mcp.client import get_client
from pagerduty_mcp.models import LogEntry, LogEntryInclude


def get_log_entry(incident_id: str, log_entry_id: str) -> LogEntry:
    """Retrieve a single PagerDuty log entry for an incident.
    Args:
        incident_id: The ID of the incident to retrieve the log entry for.
        log_entry_id: The ID of the log entry to retrieve.
    Returns:
        The log entry.
    """

    params: dict[str, Any] | None = None

    params = {"include[]": "channels"}

    endpoint = f"/log_entries/{log_entry_id}"

    response = get_client().rget(endpoint, params=params)

    return LogEntry.model_validate(response)
