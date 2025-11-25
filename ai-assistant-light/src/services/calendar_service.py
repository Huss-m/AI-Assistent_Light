# src/services/calendar_service.py
from __future__ import annotations
import os
import pickle
import datetime as dt
from typing import Any, Dict, List, Optional
from google.oauth2.credentials import Credentials
from typing import List, Dict, Any
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
]

TOKEN_PATH = "calendar_token.pickle"
CREDENTIALS_PATH = "credentials.json"


def get_google_creds() -> Credentials:
    # Cloud Run: använd service account credentials
    if os.getenv("ENV") == "prod":
        from google.auth import default
        prod_creds, _ = default(scopes=SCOPES)
        return prod_creds
    
    # Lokal utveckling: använd OAuth2 flow
    local_creds: Optional[Credentials] = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as f:
            local_creds = pickle.load(f)

    if not local_creds or not local_creds.valid:
        if local_creds and local_creds.expired and local_creds.refresh_token:
            local_creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(
                    "credentials.json saknas i projektroten. Ladda ned från Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES
            )
            local_creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "wb") as f:
            pickle.dump(local_creds, f)
    return local_creds


def build_calendar_service():
    creds = get_google_creds()
    return build("calendar", "v3", credentials=creds)


def list_todays_events(service, max_results: int = 20) -> List[Dict[str, Any]]:
    """Hämta dagens kalenderhändelser från primary-kalendern."""
    now = dt.datetime.now(dt.timezone.utc)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=0).isoformat()

    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start_of_day,
            timeMax=end_of_day,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    items = events_result.get("items", []) or []

    events: List[Dict[str, Any]] = []
    for ev in items:
        start = ev.get("start", {}).get("dateTime") or ev.get("start", {}).get("date", "")
        end = ev.get("end", {}).get("dateTime") or ev.get("end", {}).get("date", "")
        events.append(
            {
                "summary": ev.get("summary", "(utan titel)"),
                "start": start,
                "end": end,
                "location": ev.get("location", ""),
            }
        )
    return events


def fetch_todays_events_for_credentials(
    creds: Credentials,
    max_results: int = 20,
) -> List[Dict[str, Any]]:
    """
    Variant av list_todays_events som använder Credentials från web-sessionen.
    """
    service = build("calendar", "v3", credentials=creds)
    return list_todays_events(service, max_results=max_results)
