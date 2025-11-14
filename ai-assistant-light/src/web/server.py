# src/web/server.py
from __future__ import annotations
import datetime as dt
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from services.gmail_service import build_gmail_service, list_today_unread
from services.calendar_service import build_calendar_service, list_todays_events
from services.ai_summarizer import summarize_day, simple_fallback_priorities

app = FastAPI(title="AI-Assistant Light")

app.mount("/static", StaticFiles(directory="src/web/static"), name="static")
templates = Jinja2Templates(directory="src/web/templates")


def generate_report():
    gmail = build_gmail_service()
    calendar = build_calendar_service()

    emails = list_today_unread(gmail, max_results=10)
    events = list_todays_events(calendar, max_results=20)

    try:
        report = summarize_day(emails, events)
    except Exception:
        report = simple_fallback_priorities(emails, events)

    return {
        "generated_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "emails": emails,
        "events": events,
        "summary_text": report["summary_text"],
        "source": report.get("source", "fallback"),
    }


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    data = generate_report()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            **data,
        },
    )


@app.get("/health")
def health():
    return {"status": "ok"}
