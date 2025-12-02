# AI-Assistant Light – Teknisk Rapport

## 1. Projektöversikt

AI-Assistant Light är en webbaserad applikation som automatiskt sammanfattar användarens dag genom att hämta data från Gmail och Google Calendar. Applikationen använder OpenAI:s GPT-4o-mini för att generera intelligenta sammanfattningar på svenska.

### 1.1 Syfte
Att skapa en personlig AI-assistent som ger användaren en snabb överblick över dagens e-post och schemalagda händelser, presenterat i en lättläst sammanfattning.

### 1.2 Teknisk Stack
| Komponent | Teknologi |
|-----------|-----------|
| Backend | Python 3.13, FastAPI |
| Frontend | HTML, CSS, Jinja2 Templates |
| AI/ML | OpenAI GPT-4o-mini |
| Autentisering | Google OAuth 2.0 |
| Databas | Google Cloud Firestore |
| Deployment | Google Cloud Run, Docker |
| CI/CD | GitHub Actions |

---

## 2. Arkitektur

### 2.1 Projektstruktur
```
AI-Assistant-Light/
├── src/
│   ├── config.py              # Konfiguration
│   ├── services/
│   │   ├── gmail.py           # Gmail-integration
│   │   ├── calendar.py        # Calendar-integration
│   │   ├── summarizer.py      # AI-sammanfattning
│   │   └── storage.py         # Credential-lagring
│   └── web/
│       ├── app.py             # FastAPI-applikation
│       ├── static/style.css
│       └── templates/
├── tests/                     # Enhetstester
├── .github/workflows/         # CI/CD
└── Dockerfile
```

### 2.2 Komponentdiagram
```
┌─────────────────────────────────────────────────────────────────┐
│                         Användare                                │
└─────────────────────────────┬───────────────────────────────────┘
                              │ HTTPS
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Google Cloud Run                              │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    FastAPI (app.py)                        │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────┐   │  │
│  │  │ /       │  │ /login  │  │/callback│  │  /logout    │   │  │
│  │  └────┬────┘  └────┬────┘  └────┬────┘  └─────────────┘   │  │
│  └───────┼────────────┼────────────┼─────────────────────────┘  │
│          │            │            │                             │
│  ┌───────▼────────────▼────────────▼─────────────────────────┐  │
│  │                    Services Layer                          │  │
│  │  ┌──────────┐  ┌──────────┐  ┌────────────┐  ┌─────────┐  │  │
│  │  │gmail.py  │  │calendar  │  │summarizer  │  │storage  │  │  │
│  │  │          │  │.py       │  │.py         │  │.py      │  │  │
│  │  └────┬─────┘  └────┬─────┘  └─────┬──────┘  └────┬────┘  │  │
│  └───────┼─────────────┼──────────────┼──────────────┼───────┘  │
└──────────┼─────────────┼──────────────┼──────────────┼──────────┘
           │             │              │              │
           ▼             ▼              ▼              ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐
    │Gmail API │  │Calendar  │  │ OpenAI   │  │  Firestore   │
    │          │  │API       │  │ API      │  │              │
    └──────────┘  └──────────┘  └──────────┘  └──────────────┘
```

---

## 3. Komponenter i Detalj

### 3.1 config.py – Konfigurationshantering
Centraliserad hantering av alla miljövariabler och konfigurationer.

**Ansvar:**
- Ladda miljövariabler från systemet
- Definiera OAuth-scopes för Google API:er
- Hantera krypteringsnycklar för credential-lagring

**Nyckelvariabler:**
```python
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly"
]
GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI
OPENAI_API_KEY, CREDENTIAL_ENC_KEY, SESSION_SECRET_KEY
```

### 3.2 gmail.py – Gmail-integration
Hämtar olästa e-postmeddelanden från användarens Gmail-konto.

**Funktion:** `fetch_unread_emails(credentials) -> list[dict]`

**Flöde:**
1. Bygger Gmail API-tjänst med användarens credentials
2. Söker efter olästa meddelanden (max 10 st)
3. Hämtar metadata: avsändare, ämne, datum, utdrag
4. Returnerar lista med e-postdata

### 3.3 calendar.py – Google Calendar-integration
Hämtar dagens kalenderhändelser.

**Funktion:** `fetch_todays_events(credentials) -> list[dict]`

**Flöde:**
1. Beräknar dagens start- och sluttid (UTC)
2. Hämtar händelser inom tidsintervallet
3. Extraherar: titel, start/sluttid, plats
4. Hanterar heldagshändelser separat

### 3.4 summarizer.py – AI-sammanfattning
Genererar intelligenta sammanfattningar med OpenAI.

**Funktioner:**
- `summarize_day(emails, events) -> str` – Huvudfunktion
- `fallback_summary(emails, events) -> str` – Backup utan AI

**Flöde:**
1. Formaterar e-post och händelser till text
2. Skickar prompt till GPT-4o-mini
3. Vid fel: använder fallback-sammanfattning
4. Returnerar HTML-formaterad sammanfattning

**Prompt-strategi:**
```
Du är en personlig AI-assistent. Sammanfatta användarens dag 
baserat på e-post och kalenderhändelser. Svara på svenska.
Använd HTML-formatering för läsbarhet.
```

### 3.5 storage.py – Credential-lagring
Säker lagring av OAuth-tokens i Firestore med kryptering.

**Funktioner:**
- `save_credentials(user_id, credentials)` – Krypterar och sparar
- `load_credentials(user_id) -> Credentials` – Hämtar och dekrypterar

**Säkerhetsmekanismer:**
- Fernet-kryptering (AES-128-CBC)
- Credentials lagras aldrig i klartext
- Automatisk token-refresh vid behov

### 3.6 app.py – FastAPI-applikation
Webbapplikationens huvudfil med alla HTTP-routes.

**Endpoints:**

| Route | Metod | Beskrivning |
|-------|-------|-------------|
| `/` | GET | Huvudsida med sammanfattning |
| `/auth/login` | GET | Startar OAuth-flöde |
| `/auth/callback` | GET | Hanterar OAuth-callback |
| `/logout` | GET | Loggar ut användaren |
| `/health` | GET | Hälsokontroll för Cloud Run |

**OAuth-flöde:**
```
1. Användare → /auth/login
2. Redirect → Google OAuth consent screen
3. Google → /auth/callback?code=xxx
4. App: Utbyter code mot tokens
5. App: Krypterar och sparar tokens i Firestore
6. Redirect → / (huvudsida)
```

---

## 4. Dataflöde

### 4.1 Autentiseringsflöde
```
┌──────────┐     ┌─────────┐     ┌────────┐     ┌───────────┐
│Användare │────▶│ /login  │────▶│ Google │────▶│ /callback │
└──────────┘     └─────────┘     │ OAuth  │     └─────┬─────┘
                                 └────────┘           │
                                                      ▼
                                              ┌───────────────┐
                                              │   Firestore   │
                                              │ (krypterade   │
                                              │  credentials) │
                                              └───────────────┘
```

### 4.2 Sammanfattningsflöde
```
┌──────────┐     ┌─────────┐     ┌────────────────────────────┐
│Användare │────▶│   /     │────▶│ 1. Hämta credentials       │
└──────────┘     └─────────┘     │ 2. fetch_unread_emails()   │
                                 │ 3. fetch_todays_events()   │
                                 │ 4. summarize_day()         │
                                 │ 5. Rendera template        │
                                 └────────────────────────────┘
```

---

## 5. Säkerhet

### 5.1 Implementerade säkerhetsåtgärder
| Åtgärd | Implementation |
|--------|----------------|
| OAuth 2.0 | Google-autentisering, inga lösenord lagras |
| Credential-kryptering | Fernet (AES-128-CBC) |
| Session-hantering | Signerade cookies med itsdangerous |
| HTTPS | Tvingat via Cloud Run |
| Miljövariabler | Känslig data i GitHub Secrets |

### 5.2 Datahantering
- Credentials krypteras innan lagring i Firestore
- Access tokens har begränsad livslängd
- Refresh tokens används för förnyelse
- Användare kan radera data via `/logout`

---

## 6. CI/CD Pipeline

### 6.1 GitHub Actions Workflow
```yaml
Trigger: Push till 'dev' branch

Steg:
1. Checkout kod
2. Installera Python 3.11
3. Installera beroenden
4. Kör Ruff (linting)
5. Kör Pytest (enhetstester)
6. Autentisera mot Google Cloud
7. Bygg Docker-image
8. Deploya till Cloud Run
```

### 6.2 Kvalitetskontroller
- **Ruff:** Statisk kodanalys och linting
- **Pytest:** 16 enhetstester med mocking
- **Type hints:** Genomgående i kodbasen

---

## 7. Testning

### 7.1 Teststrategi
| Testtyp | Verktyg | Omfattning |
|---------|---------|------------|
| Enhetstester | Pytest | Services, Endpoints |
| Mocking | unittest.mock | Externa API:er |
| Linting | Ruff | Kodkvalitet |

### 7.2 Testfall
```
tests/
├── test_app.py          # 4 tester (endpoints)
├── test_gmail.py        # 2 tester (e-posthämtning)
├── test_calendar.py     # 3 tester (kalenderhändelser)
└── test_summarizer.py   # 7 tester (AI-sammanfattning)
```

**Totalt: 16 enhetstester**

---

## 8. Deployment

### 8.1 Docker-konfiguration
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV PYTHONPATH=/app
CMD ["uvicorn", "src.web.app:app", "--host", "0.0.0.0", "--port", "8080"]
```

### 8.2 Cloud Run-konfiguration
| Parameter | Värde |
|-----------|-------|
| Region | europe-north1 (Finland) |
| Memory | 512 MB |
| CPU | 1 |
| Min instances | 0 |
| Max instances | 10 |
| Timeout | 300s |

---

## 9. Framtida Förbättringar

1. **Notifikationer:** Push-notiser för viktiga e-post
2. **Schemaläggning:** Daglig sammanfattning via e-post
3. **Fler datakällor:** Microsoft Outlook, Slack
4. **Personalisering:** Användarprofiler med preferenser
5. **Caching:** Redis för snabbare responstider

---

## 10. Slutsats

AI-Assistant Light demonstrerar en modern molnbaserad arkitektur med:
- **Clean Code-principer:** Separata moduler med tydligt ansvar
- **Säker autentisering:** OAuth 2.0 med krypterad credential-lagring
- **CI/CD:** Automatisk deployment vid kodändringar
- **Testning:** Omfattande enhetstester med mocking
- **Skalbarhet:** Containeriserad deployment på Cloud Run

Applikationen visar hur AI kan integreras i vardagliga verktyg för att spara tid och ge användaren värdefulla insikter.

---

*Rapport genererad: December 2025*
