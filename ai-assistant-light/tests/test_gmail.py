from unittest.mock import patch, MagicMock
from src.services.gmail import fetch_unread_emails


class TestFetchUnreadEmails:
    @patch("src.services.gmail.build")
    def test_no_messages(self, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.users().messages().list().execute.return_value = {"messages": []}

        mock_creds = MagicMock()
        result = fetch_unread_emails(mock_creds, max_results=10)
        
        assert result == []

    @patch("src.services.gmail.build")
    def test_with_messages(self, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        mock_service.users().messages().list().execute.return_value = {
            "messages": [{"id": "123"}]
        }
        mock_service.users().messages().get().execute.return_value = {
            "id": "123",
            "snippet": "Test snippet",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Test Subject"},
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "Date", "value": "2025-12-01"},
                ]
            }
        }

        mock_creds = MagicMock()
        result = fetch_unread_emails(mock_creds, max_results=10)
        
        assert len(result) == 1
        assert result[0]["subject"] == "Test Subject"
        assert result[0]["from"] == "sender@example.com"
        assert result[0]["snippet"] == "Test snippet"
