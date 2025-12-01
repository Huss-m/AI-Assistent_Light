from __future__ import annotations
import datetime as dt
from typing import Any, Dict, List

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


def fetch_unread_emails(creds: Credentials, max_results: int = 10) -> List[Dict[str, Any]]:
    service = build("gmail", "v1", credentials=creds)
    today = dt.datetime.now(dt.timezone.utc).strftime("%Y/%m/%d")
    query = f"is:unread after:{today}"

    resp = (
        service.users()
        .messages()
        .list(userId="me", q=query, maxResults=max_results)
        .execute()
    )
    messages = resp.get("messages", []) or []
    results: List[Dict[str, Any]] = []

    for m in messages:
        full = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=m["id"],
                format="metadata",
                metadataHeaders=["From", "To", "Subject", "Date"],
            )
            .execute()
        )
        headers = {
            h["name"]: h["value"]
            for h in full.get("payload", {}).get("headers", [])
        }
        results.append(
            {
                "id": full.get("id"),
                "subject": headers.get("Subject", "(no subject)"),
                "from": headers.get("From", ""),
                "date": headers.get("Date", ""),
                "snippet": full.get("snippet", ""),
            }
        )
    return results
