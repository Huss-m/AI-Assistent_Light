from __future__ import annotations
import datetime as dt
from typing import List, Dict, Any

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


def fetch_todays_events(creds: Credentials, max_results: int = 20) -> List[Dict[str, Any]]:
    service = build("calendar", "v3", credentials=creds)
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
