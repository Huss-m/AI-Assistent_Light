from __future__ import annotations
import json
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken
from google.cloud import firestore
from google.oauth2.credentials import Credentials
from src.config import CREDENTIAL_ENC_KEY

_db: Optional[firestore.Client] = None
_fernet: Optional[Fernet] = None


def _get_db() -> firestore.Client:
    global _db
    if _db is None:
        _db = firestore.Client()
    return _db


def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        if not CREDENTIAL_ENC_KEY:
            raise RuntimeError("CREDENTIAL_ENC_KEY saknas.")
        _fernet = Fernet(CREDENTIAL_ENC_KEY)
    return _fernet


def _encrypt_credentials(creds: Credentials) -> str:
    payload = creds.to_json().encode("utf-8")
    return _get_fernet().encrypt(payload).decode("utf-8")


def _decrypt_credentials(token: str) -> Credentials:
    try:
        decrypted = _get_fernet().decrypt(token.encode("utf-8"))
    except InvalidToken as exc:
        raise RuntimeError("Misslyckades decrypta credentials.") from exc
    data = json.loads(decrypted.decode("utf-8"))
    return Credentials.from_authorized_user_info(data)


def save_credentials(email: str, creds: Credentials) -> None:
    doc_ref = _get_db().collection("users").document(email.lower())
    doc_ref.set(
        {
            "email": email.lower(),
            "credentials_encrypted": _encrypt_credentials(creds),
            "updated_at": firestore.SERVER_TIMESTAMP,
        },
        merge=True,
    )


def load_credentials(email: str) -> Optional[Credentials]:
    doc_ref = _get_db().collection("users").document(email.lower())
    snapshot = doc_ref.get()

    if not snapshot.exists:
        return None

    data = snapshot.to_dict()
    encrypted = data.get("credentials_encrypted")
    if encrypted:
        return _decrypt_credentials(encrypted)

    legacy = data.get("credentials")
    if legacy:
        return Credentials.from_authorized_user_info(legacy)
    return None
