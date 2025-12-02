# AI-Assistant Light

En webapp för att visa Gmail och Kalender-data.

## Installation

```bash
cd ai-assistant-light
.\venv\Scripts\activate
pip install -r requirements.txt
```

## Kör lokalt

```bash
uvicorn src.web.app:app --reload --host 0.0.0.0 --port 8000
```


AI-Assistant-Light/
│
├── 📁 src/                          # Källkod
│   ├── __init__.py
│   ├── config.py                    # Konfiguration & miljövariabler
│   │
│   ├── 📁 services/                 # Affärslogik
│   │   ├── __init__.py
│   │   ├── gmail.py                 # Gmail API-integration
│   │   ├── calendar.py              # Google Calendar API-integration
│   │   ├── summarizer.py            # AI-sammanfattning (OpenAI)
│   │   └── storage.py               # Firestore-lagring av credentials
│   │
│   └── 📁 web/                      # Webbapplikation
│       ├── __init__.py
│       ├── app.py                   # FastAPI-applikation & routes
│       ├── 📁 static/
│       │   └── style.css            # Stilmallar
│       └── 📁 templates/
│           ├── index.html           # Huvudsida med sammanfattning
│           └── login.html           # Inloggningssida
│
├── 📁 tests/                        # Enhetstester
│   ├── __init__.py
│   ├── test_app.py                  # Tester för endpoints
│   ├── test_gmail.py                # Tester för Gmail-tjänst
│   ├── test_calendar.py             # Tester för Calendar-tjänst
│   └── test_summarizer.py           # Tester för AI-sammanfattning
│
├── 📁 docs/                         # Dokumentation
│
├── 📁 .github/workflows/            # CI/CD
│   └── deploy.yml                   # GitHub Actions deployment
│
├── Dockerfile                       # Container-konfiguration
├── requirements.txt                 # Python-beroenden
├── mypy.ini                         # Type checking-konfiguration
└── README.md                        # Projektdokumentation












