from __future__ import annotations
import datetime as dt
import os
from typing import Optional
if os.getenv("ENV", "dev") != "prod":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from src.services.ai_summarizer import summarize_day, simple_fallback_priorities
from src.services.gmail_service import fetch_unread_emails_for_credentials
from src.services.calendar_service import fetch_todays_events_for_credentials
from googleapiclient.discovery import build
from src.services.firestore_service import save_user_credentials, load_user_credentials

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
]

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

app = FastAPI(title="AI-Assistant Light")

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", "dev-secret-key-change-me"),
    same_site="lax",
)

app.mount("/static", StaticFiles(directory="src/web/static"), name="static")
templates = Jinja2Templates(directory="src/web/templates")


def create_flow(state: Optional[str] = None) -> Flow:
    client_config = {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [GOOGLE_REDIRECT_URI],
        }
    }

    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=GOOGLE_REDIRECT_URI,
    )
    if state:
        flow.state = state
    return flow


def get_credentials_from_session(request: Request) -> Optional[Credentials]:
    email = request.session.get("user_email")
    if not email:
        return None

    return load_user_credentials(email)



@app.get("/auth/login")
def login_with_google(request: Request):
    flow = create_flow()
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    request.session["oauth_state"] = state
    return RedirectResponse(authorization_url)


@app.get("/auth/callback")
def auth_callback(request: Request):
    state = request.session.get("oauth_state")
    if not state:
        return RedirectResponse(url="/")

    flow = create_flow(state=state)

    authorization_response = str(request.url)

    if os.getenv("ENV") == "prod" and authorization_response.startswith("http://"):
        authorization_response = authorization_response.replace("http://", "https://", 1)

    flow.fetch_token(authorization_response=authorization_response)
    creds = flow.credentials

    gmail_service = build("gmail", "v1", credentials=creds)
    profile = gmail_service.users().getProfile(userId="me").execute()
    email = profile.get("emailAddress")

    if not email:
        return RedirectResponse(url="/")

    save_user_credentials(email, creds)

    request.session["user_email"] = email

    request.session.pop("oauth_state", None)

    return RedirectResponse(url="/")



@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    creds = get_credentials_from_session(request)

    if not creds:
        return templates.TemplateResponse(
            "login.html",
            {"request": request},
        )

    emails, events = [], []
    
    try:
        emails = fetch_unread_emails_for_credentials(creds, max_results=10)
    except Exception:
        pass
    
    try:
        events = fetch_todays_events_for_credentials(creds, max_results=20)
    except Exception:
        pass

    try:
        report = summarize_day(emails, events)
    except Exception:
        report = simple_fallback_priorities(emails, events)

    data = {
        "generated_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "emails": emails,
        "events": events,
        "summary_text": report["summary_text"],
        "source": report.get("source", "fallback"),
    }

    return templates.TemplateResponse(
        "index.html",
        {"request": request, **data},
    )


@app.get("/health")
def health():
    return {"status": "ok", "timestamp": dt.datetime.now().isoformat()}
