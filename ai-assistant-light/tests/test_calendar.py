import pytest
from unittest.mock import patch, MagicMock
from src.services.calendar import fetch_todays_events


class TestFetchTodaysEvents:
    @patch("src.services.calendar.build")
    def test_no_events(self, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.events().list().execute.return_value = {"items": []}

        mock_creds = MagicMock()
        result = fetch_todays_events(mock_creds, max_results=20)
        
        assert result == []

    @patch("src.services.calendar.build")
    def test_with_events(self, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        mock_service.events().list().execute.return_value = {
            "items": [
                {
                    "summary": "Team Meeting",
                    "start": {"dateTime": "2025-12-01T09:00:00"},
                    "end": {"dateTime": "2025-12-01T10:00:00"},
                    "location": "Room A",
                }
            ]
        }

        mock_creds = MagicMock()
        result = fetch_todays_events(mock_creds, max_results=20)
        
        assert len(result) == 1
        assert result[0]["summary"] == "Team Meeting"
        assert result[0]["location"] == "Room A"

    @patch("src.services.calendar.build")
    def test_all_day_event(self, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        mock_service.events().list().execute.return_value = {
            "items": [
                {
                    "summary": "Holiday",
                    "start": {"date": "2025-12-01"},
                    "end": {"date": "2025-12-02"},
                }
            ]
        }

        mock_creds = MagicMock()
        result = fetch_todays_events(mock_creds, max_results=20)
        
        assert len(result) == 1
        assert result[0]["summary"] == "Holiday"
        assert result[0]["start"] == "2025-12-01"
