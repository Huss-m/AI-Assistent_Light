# src/main.py
from __future__ import annotations
from services.gmail_service import build_gmail_service, list_today_unread
from services.calendar_service import build_calendar_service, list_todays_events
from services.ai_summarizer import summarize_day
from utils.cli_report import block


def main() -> None:
    try:
        gmail = build_gmail_service()
        calendar = build_calendar_service()

        emails = list_today_unread(gmail, max_results=10)
        events = list_todays_events(calendar, max_results=20)
    except Exception as e:
        print(f"Fel vid hämtning av data: {e}")
        emails, events = [], []

    print(block(
        "Dagens olästa mejl",
        "\n".join([f"{e['subject']} | {e['from']}" for e in emails]) or "(Inga)"
    ))

    print(block(
        "Dagens händelser",
        "\n".join([f"{ev['summary']} @ {ev['start']}" for ev in events]) or "(Inga)"
    ))

    report = summarize_day(emails, events)
    print(block("Dagsrapport", report["summary_text"]))
    if report.get("source"):
        print(f"(källa: {report['source']})")


if __name__ == "__main__":
    main()

