"""Unit tests for log entry tools."""

from __future__ import annotations

import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from pagerduty_mcp.models import LogEntry, LogEntryQuery
from pagerduty_mcp.tools.log_entries import get_log_entry


class TestLogEntryTools(unittest.TestCase):
    """Test cases for log entry tools."""

    def setUp(self):
        self.sample_log_entry = {
            "id": "PLOG123",
            "type": "trigger_log_entry",
            "summary": "Triggered by monitoring",
            "created_at": "2024-01-01T00:00:00Z",
            "service": {"id": "PSVC123", "type": "service_reference"},
            "incident": {"id": "PINC123", "type": "incident_reference"},
            "channel": {"type": "api"},
        }

    @patch("pagerduty_mcp.tools.log_entries.get_client")
    def test_get_log_entry_global(self, mock_get_client):
        """Fetching a log entry by ID hits the global endpoint by default."""

        mock_client = MagicMock()
        mock_client.rget.return_value = self.sample_log_entry
        mock_get_client.return_value = mock_client

        result = get_log_entry("PLOG123")

        mock_client.rget.assert_called_once_with("/log_entries/PLOG123", params=None)
        self.assertIsInstance(result, LogEntry)
        self.assertEqual(result.id, "PLOG123")
        self.assertEqual(result.channel, {"type": "api"})

    @patch("pagerduty_mcp.tools.log_entries.get_client")
    def test_get_log_entry_scoped(self, mock_get_client):
        """Fetching a log entry scoped to an incident uses the incident endpoint."""

        mock_client = MagicMock()
        mock_client.rget.return_value = self.sample_log_entry
        mock_get_client.return_value = mock_client

        _ = get_log_entry("PLOG123", incident_id="PINC123", include=["services"])

        mock_client.rget.assert_called_once_with(
            "/incidents/PINC123/log_entries/PLOG123",
            params={"include[]": ["services"]},
        )

    def test_log_entry_query_to_params(self):
        """Ensure ``LogEntryQuery.to_params`` serialises filters correctly."""

        query = LogEntryQuery(
            since=datetime(2024, 1, 1),
            until=datetime(2024, 1, 2),
            is_overview=True,
            service_ids=["PSVC123"],
            team_ids=["PTEAM123"],
            user_ids=["PUSER123"],
            urgencies=["high"],
            include=["channels", "users"],
            limit=10,
        )

        params = query.to_params()

        self.assertEqual(params["since"], query.since.isoformat())
        self.assertEqual(params["until"], query.until.isoformat())
        self.assertEqual(params["is_overview"], "true")
        self.assertEqual(params["service_ids[]"], ["PSVC123"])
        self.assertEqual(params["team_ids[]"], ["PTEAM123"])
        self.assertEqual(params["user_ids[]"], ["PUSER123"])
        self.assertEqual(params["urgencies[]"], ["high"])
        self.assertEqual(params["include[]"], ["channels", "users"])
        self.assertEqual(params["limit"], 10)


if __name__ == "__main__":
    unittest.main()


