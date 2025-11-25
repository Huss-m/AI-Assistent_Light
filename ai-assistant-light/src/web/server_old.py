# src/web/server.py
from __future__ import annotations
import datetime as dt
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from services.gmail_service import build_gmail_service, list_today_unread
from services.calendar_service import build_calendar_service, list_todays_events
from services.ai_summarizer import summarize_day, simple_fallback_priorities

app = FastAPI(title="AI-Assistant Light")

app.mount("/static", StaticFiles(directory="/app/src/web/static"), name="static")
templates = Jinja2Templates(directory="/app/src/web/templates")


def generate_report():
    # Demo data för Cloud Run
    if os.getenv("ENV") == "prod":
        emails = [
            {"subject": "Demo: Viktigt möte imorgon", "from": "chef@företag.se", "snippet": "Glöm inte att förbereda presentationen..."},
            {"subject": "Demo: Projektuppdatering", "from": "team@företag.se", "snippet": "Status för veckan som gått..."}
        ]
        events = [
            {"summary": "Demo: Teammöte", "start": "09:00", "location": "Konferensrum A"},
            {"summary": "Demo: Kundpresentation", "start": "14:00", "location": "Online"}
        ]
        report = {"summary_text": "Demo-läge: Visar exempeldata för Gmail och Calendar integration.", "source": "demo"}
    else:
        # Lokal utveckling: använd riktiga APIs
        try:
            gmail = build_gmail_service()
            calendar = build_calendar_service()
            emails = list_today_unread(gmail, max_results=10)
            events = list_todays_events(calendar, max_results=20)
        except Exception as e:
            print(f"Fel vid hämtning av Google data: {e}")
            emails, events = [], []

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
    return {"status": "ok", "timestamp": dt.datetime.now().isoformat()}

@app.get("/api/status")
def status():
    """Status endpoint för att testa att appen fungerar utan Google API-anrop"""
    return {
        "service": "ai-assistant-light",
        "status": "running",
        "env": os.getenv("ENV", "dev"),
        "timestamp": dt.datetime.now().isoformat()
    }

@app.get("/api/debug")
def debug():
    """Debug endpoint för att testa Google API access"""
    try:
        from services.gmail_service import build_gmail_service
        build_gmail_service()
        return {"gmail_service": "ok", "env": os.getenv("ENV", "dev")}
    except Exception as e:
        return {"gmail_service": "error", "error": str(e), "env": os.getenv("ENV", "dev")}
