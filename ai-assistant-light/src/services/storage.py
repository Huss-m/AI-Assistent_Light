from __future__ import annotations
import json
from typing import Optional

from google.oauth2.credentials import Credentials


_credentials_cache: dict[str, str] = {}


def _serialize_credentials(creds: Credentials) -> str:
    return creds.to_json()


def _deserialize_credentials(data: str) -> Credentials:
    return Credentials.from_authorized_user_info(json.loads(data))


def save_credentials(email: str, creds: Credentials) -> None:
    _credentials_cache[email.lower()] = _serialize_credentials(creds)


def load_credentials(email: str) -> Optional[Credentials]:
    data = _credentials_cache.get(email.lower())
    if data:
        return _deserialize_credentials(data)
    return None


def clear_credentials(email: str) -> None:
    _credentials_cache.pop(email.lower(), None)
