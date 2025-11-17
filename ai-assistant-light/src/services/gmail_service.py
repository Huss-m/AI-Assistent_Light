# src/services/gmail_service.py
from __future__ import annotations
import os
import pickle
import datetime as dt
from typing import Any, Dict, List, Optional

from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
]

TOKEN_PATH = "token.pickle"
CREDENTIALS_PATH = "credentials.json"


def get_google_creds() -> Credentials:
    creds: Optional[Credentials] = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(
                    "credentials.json saknas i projektroten. Ladda ned från Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "wb") as f:
            pickle.dump(creds, f)
    return creds


def build_gmail_service():
    creds = get_google_creds()
    return build("gmail", "v1", credentials=creds)


def list_today_unread(service, max_results: int = 10) -> List[Dict[str, Any]]:
    """Hämta dagens olästa mejl (enkelt, baserat på dagens datum)."""
    today = dt.datetime.now().strftime("%Y/%m/%d")
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