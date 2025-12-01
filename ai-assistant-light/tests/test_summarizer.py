import pytest
from unittest.mock import patch, MagicMock
from src.services.summarizer import summarize_day, fallback_summary


class TestFallbackSummary:
    def test_empty_data(self):
        result = fallback_summary([], [])
        assert result["source"] == "fallback"
        assert "Olästa mejl: 0" in result["summary_text"]
        assert "Händelser idag: 0" in result["summary_text"]

    def test_with_emails(self):
        emails = [
            {"subject": "Test Subject", "from": "test@example.com"},
            {"subject": "Another Subject", "from": "another@example.com"},
        ]
        result = fallback_summary(emails, [])
        assert "Olästa mejl: 2" in result["summary_text"]
        assert "Test Subject" in result["summary_text"]

    def test_with_events(self):
        events = [
            {"summary": "Meeting", "start": "09:00"},
            {"summary": "Lunch", "start": "12:00"},
        ]
        result = fallback_summary([], events)
        assert "Händelser idag: 2" in result["summary_text"]
        assert "Meeting" in result["summary_text"]

    def test_with_both(self):
        emails = [{"subject": "Email", "from": "test@test.com"}]
        events = [{"summary": "Event", "start": "10:00"}]
        result = fallback_summary(emails, events)
        assert "Olästa mejl: 1" in result["summary_text"]
        assert "Händelser idag: 1" in result["summary_text"]


class TestSummarizeDay:
    @patch("src.services.summarizer.OPENAI_API_KEY", None)
    def test_no_api_key_uses_fallback(self):
        result = summarize_day([], [])
        assert result["source"] == "fallback"

    @patch("src.services.summarizer.OPENAI_API_KEY", "fake-key")
    @patch("src.services.summarizer.OpenAI")
    def test_openai_success(self, mock_openai):
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="AI Summary"))]
        mock_client.chat.completions.create.return_value = mock_response

        result = summarize_day([], [])
        assert result["source"] == "openai"
        assert result["summary_text"] == "AI Summary"

    @patch("src.services.summarizer.OPENAI_API_KEY", "fake-key")
    @patch("src.services.summarizer.OpenAI")
    def test_openai_error_uses_fallback(self, mock_openai):
        mock_openai.side_effect = Exception("API Error")
        result = summarize_day([], [])
        assert result["source"] == "fallback"
