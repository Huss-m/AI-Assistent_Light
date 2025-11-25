# src/services/firestore_service.py
from __future__ import annotations

import json
from typing import Optional

from google.cloud import firestore
from google.oauth2.credentials import Credentials

# Firestore client uses Application Default Credentials:
# - Lokalt: kör `gcloud auth application-default login`
# - Cloud Run: använder tjänstens service account automatiskt
_db = firestore.Client()


def save_user_credentials(email: str, creds: Credentials) -> None:
    """
    Save or update Google OAuth credentials for a user in Firestore.
    Document ID = email.
    """
    doc_ref = _db.collection("users").document(email.lower())

    # Convert Credentials to plain dict via to_json()
    cred_info = json.loads(creds.to_json())

    doc_ref.set(
        {
            "email": email.lower(),
            "credentials": cred_info,
            "updated_at": firestore.SERVER_TIMESTAMP,
        },
        merge=True,
    )


def load_user_credentials(email: str) -> Optional[Credentials]:
    """
    Load Google OAuth credentials for a user from Firestore.
    Returns None if the document does not exist.
    """
    doc_ref = _db.collection("users").document(email.lower())
    snapshot = doc_ref.get()

    if not snapshot.exists:
        return None

    data = snapshot.to_dict()
    cred_info = data.get("credentials")
    if not cred_info:
        return None

    # Build Credentials from stored dict
    return Credentials.from_authorized_user_info(cred_info)
