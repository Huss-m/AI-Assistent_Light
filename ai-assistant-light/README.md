# AI-Assistant Light

En personlig assistent som integrerar Gmail och Google Calendar.

## Struktur

```
src/
├── config.py           # Konfiguration
├── services/
│   ├── gmail.py        # Gmail-integration
│   ├── calendar.py     # Calendar-integration
│   ├── summarizer.py   # AI-sammanfattning
│   └── storage.py      # Firestore-lagring
└── web/
    ├── app.py          # FastAPI-app
    ├── static/
    └── templates/
```

## Kör lokalt

```bash
uvicorn src.web.app:app --reload
```