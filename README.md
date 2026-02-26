# Quizly Backend 🎯

Django REST API Backend für die Quizly-Anwendung. Erstellt automatisch **10 Quizfragen** aus YouTube-Videos durch:

1. 📹 Audio-Download mit `yt-dlp`
2. 📝 Transkription mit **Whisper AI**
3. 🧠 Quiz-Generierung mit **Google Gemini 2.5 Flash API**

---

## 📋 Table of Contents

- [Features](#features)
- [Systemanforderungen](#systemanforderungen)
- [Installation](#installation)
  - [FFmpeg Setup](#ffmpeg-setup)
  - [Python Virtual Environment](#python-virtual-environment)
  - [Dependencies](#dependencies)
  - [Environment Variables](#environment-variables)
  - [Datenbank](#datenbank)
- [Server starten](#server-starten)
- [API Endpoints](#api-endpoints)
- [Projektstruktur](#projektstruktur)

---

## ✨ Features

- ✅ **JWT Authentifizierung** - Token-based Authentication
- ✅ **YouTube Integration** - Videos direkt von URL verarbeiten
- ✅ **Automatische Transkription** - Whisper AI (unterstützt Deutsch)
- ✅ **AI Quiz-Generierung** - Google Gemini 2.5 Flash API generiert intelligente Fragen (schnell & kostengünstig)
- ✅ **10 Fragen pro Video** - Mit je 4 Antwortmöglichkeiten
- ✅ **Quiz Management** - CRUD Operations für Quizze

---

## 🔧 Systemanforderungen

### Erforderlich (Must-Have) ✅

| Komponente  | Anforderung        | Details                                                                             |
| ----------- | ------------------ | ----------------------------------------------------------------------------------- |
| **Python**  | 3.9 - 3.12         | ⚠️ **NICHT Python 3.13+** (Kompatibilitätsprobleme mit `yt-dlp` & `openai-whisper`) |
| **FFmpeg**  | Aktuellste Version | [Installation weiter unten](#ffmpeg-setup)                                          |
| **API Key** | Google Gemini      | Kostenlos von [Google AI Studio](https://ai.google.dev/gemini-api/docs/api-key)     |

### Vor dem Start - Prüf-Checkliste ✓

````bash
# 1. Python Version prüfen
python --version
# ✅ Sollte 3.9 - 3.12 sein (z.B. 3.12.7)
# ❌ NICHT 3.13 oder höher!

# 2. pip vorhanden?
pip --version
# ✅ Sollte Version anzeigen

# 3. FFmpeg installiert?
ffmpeg -version
# ✅ Sollte Version + Info anzeigen
# ❌ Falls die Fehlschlägt → Siehe FFmpeg-Setup


## ⚙️ Installation

### FFmpeg Setup

**FFmpeg ist ERFORDERLICH** für Audio-Extraktion. Ohne FFmpeg funktioniert die Transkription nicht!

#### Windows

**Option 1: Chocolatey** (empfohlen)

```powershell
choco install ffmpeg
````

**Option 2: Scoop**

```powershell
scoop install ffmpeg
```

**Option 3: Manual Download**

- Download von [ffmpeg.org](https://ffmpeg.org/download.html)
- ZIP extrahieren zu `C:\ffmpeg`
- Zu System PATH hinzufügen (Windows + X → Umgebungsvariablen)

**Überprüfung:**

```powershell
ffmpeg -version
# Sollte Versionsnummer anzeigen
```

#### macOS

```bash
# Mit Homebrew (empfohlen)
brew install ffmpeg

# Überprüfung
ffmpeg -version
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install ffmpeg

# Überprüfung
ffmpeg -version
```

#### Linux (Fedora/RHEL)

```bash
sudo dnf install ffmpeg

# Überprüfung
ffmpeg -version
```

### Python Virtual Environment

#### Windows (PowerShell)

```powershell
# Virtual Environment erstellen
python -m venv venv

# Aktivieren
.\venv\Scripts\Activate.ps1

# ✅ Prompt sollte mit "(venv)" starten
```

#### Windows (Command Prompt)

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

#### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate

# ✅ Prompt sollte mit "(venv)" starten
```

### Dependencies installieren

```bash
pip install -r requirements.txt
```

**Erste Installation? Das dauert etwas** (Whisper Model wird heruntergeladen ~140MB)

#### ⚠️ Häufige Fehler & Lösungen

**Problem: `No module named 'pkg_resources'` bei der Installation**

Dies passiert mit Python 3.13/3.14 bei `openai-whisper` oder `yt-dlp`.

**Lösung:**

```bash
# Cache löschen
pip cache purge

# Mit --no-cache-dir neu installieren
pip install -r requirements.txt --no-cache-dir

# Falls immer noch Fehler: Build Tools aktualisieren
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt --no-cache-dir
```

**Wenn gar nichts hilft:** Downgrade auf Python 3.12

```bash
# Python 3.12 von https://www.python.org/downloads/ installieren
# Dann venv neu erstellen und nochmal versuchen
```

### Environment Variables

Erstelle eine `.env` Datei im Root-Verzeichnis:

```bash
# .env Datei erstellen
GEMINI_API_KEY=AIza_YOUR_API_KEY_HERE
```

**Wo bekommst du den API Key?**

1. Gehe zu [Google AI Studio](https://ai.google.dev/gemini-api/docs/api-key)
2. Klick "API Key erstellen"
3. Kopiere den Key
4. Füge ihn in `.env` ein

**⚠️ Wichtig:**

- `.env` DARF NICHT auf GitHub hochgeladen werden
- `.gitignore` enthält bereits `.env` (nicht editieren!)
- Nutze `.env.example` als Template für andere Developer

### Datenbank

Datenbank-Migrationen durchführen:

```bash
python manage.py migrate
```

**Optional: Superuser erstellen**

```bash
python manage.py createsuperuser

# Interaktives Setup:
# Username: admin
# Email: admin@example.com
# Password: (sicheres Passwort)
```

Admin-Panel dann unter: `http://localhost:8000/admin`

---

## 🚀 Server starten

```bash
# Virtual Environment aktivieren (falls noch nicht aktiv)
# Windows: .\venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

python manage.py runserver
```

**Server läuft unter:**

- API: `http://localhost:8000/api/`
- Admin: `http://localhost:8000/admin/`

---

## 📡 API Endpoints

### Authentication

| Methode | Endpoint              | Beschreibung            |
| ------- | --------------------- | ----------------------- |
| POST    | `/api/register/`      | Neuen User registrieren |
| POST    | `/api/login/`         | Login (JWT Token)       |
| POST    | `/api/logout/`        | Logout                  |
| POST    | `/api/token/refresh/` | Access Token erneuern   |

### Quiz Management

| Methode  | Endpoint             | Beschreibung                            |
| -------- | -------------------- | --------------------------------------- |
| **POST** | `/api/quizzes/`      | 🌟 **Neues Quiz von YouTube URL**       |
| GET      | `/api/quizzes/`      | Alle Quizze des Users                   |
| GET      | `/api/quizzes/{id}/` | Quiz-Details                            |
| PATCH    | `/api/quizzes/{id}/` | Quiz aktualisieren (Titel/Beschreibung) |
| DELETE   | `/api/quizzes/{id}/` | Quiz löschen                            |

### POST /api/quizzes/ - Quiz von YouTube erstellen

**Authentifizierung:** Erforderlich (JWT Token)

**Request:**

```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

**Was passiert intern:**

```
1️⃣  Audio Download (yt-dlp)
    ├─ Lädt bestes Audio vom Video
    └─ Konvertiert zu MP3

2️⃣  Transkription (Whisper AI)
    ├─ Wandelt Audio in Text um
    └─ Deutsche Sprache erkannt

3️⃣  Quiz-Generierung (Gemini Flash)
    ├─ Generiert 10 intelligente Fragen
    ├─ Jede Frage mit 4 Antwortmöglichkeiten
    └─ Basierend auf Transkript-Inhalt

4️⃣  Speicherung
    └─ Quiz + Fragen + Antworten in DB
```

**Response (201 Created):**

```json
{
  "id": 42,
  "title": "Video Title",
  "description": "Video description...",
  "video_url": "https://www.youtube.com/watch?v=...",
  "created_at": "2026-02-23T12:00:00Z",
  "updated_at": "2026-02-23T12:00:00Z",
  "questions": [
    {
      "id": 101,
      "question_title": "Worum geht es im Video?",
      "question_options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "Option A",
      "created_at": "2026-02-23T12:00:00Z",
      "updated_at": "2026-02-23T12:00:00Z"
    }
    // ... 9 weitere Fragen
  ]
}
```

**Fehlerbehandlung:**

- ❌ Keine `.env` / API Key: **500 Server Error**
- ❌ YouTube URL ungültig: **400 Bad Request**
- ❌ Audio Download fehlgeschlagen: **500 Server Error**
- ❌ Transkription leer: **500 Server Error**
- ❌ Gemini Fehler: **500 Server Error**

⚠️ **Hinweis:** Es gibt **KEINEN Fallback-Modus** - wenn AI ausfällt, gibt es einen 500er Error (gewünscht für strikte Fehlerbehandlung)

---

## 📁 Projektstruktur

```
quizly_backend/
├── core/                      # Django Settings
│   ├── settings.py           # Konfiguration
│   ├── urls.py               # URL Router
│   ├── wsgi.py               # WSGI Config
│   └── asgi.py               # ASGI Config
│
├── auth_app/                 # Authentication
│   ├── models.py             # User Model
│   ├── serializers.py        # API Serializer
│   ├── views.py              # Login/Register Endpoints
│   ├── urls.py               # Auth URLs
│   └── migrations/           # DB Migrationen
│
├── quiz_app/                 # Quiz Management
│   ├── models.py             # Quiz, Question, Answer Models
│   ├── serializers.py        # Quiz Serializer
│   ├── views.py              # Quiz CRUD + AI Integration
│   ├── urls.py               # Quiz URLs
│   └── migrations/           # DB Migrationen
│
├── manage.py                 # Django CLI
├── requirements.txt          # Python Dependencies
├── .env                      # ⚠️ Environment Variablen (GitIgnored)
├── .env.example              # Template für .env
├── .gitignore                # Git Settings
├── README.md                 # Diese Datei
└── db.sqlite3                # SQLite Datenbank (Dev only)
```

---

## 📦 Dependencies

```
Django==4.2.7                          # Web Framework
djangorestframework==3.14.0            # REST API
djangorestframework-simplejwt==5.3.1   # JWT Auth
yt-dlp==2026.2.4                       # YouTube Download
openai-whisper==20231117               # Audio Transkription
google-genai                           # Google Gemini API
python-dotenv                          # .env Datei laden
Pillow==10.1.0                         # Bild-Processing
corsheaders==4.3.1                     # CORS Support
psycopg2-binary==2.9.9                 # PostgreSQL (optional)
```

---

## 🐛 Troubleshooting

### ❌ "FFmpeg not found"

**Symptom:** Fehler bei Audio-Extraktion

**Lösung:**

```bash
# Windows
ffmpeg -version

# Wenn nicht erkannt: FFmpeg installieren (siehe FFmpeg Setup oben)
```

### ❌ "ModuleNotFoundError: No module named 'google'"

**Symptom:** Google Gemini API nicht verfügbar

**Lösung:**

```bash
# Virtual Environment aktivieren
pip install google-genai
```

### ❌ "GEMINI_API_KEY not set"

**Symptom:** 500 Error bei Quiz-Erstellung

**Lösung:**

```bash
# 1. Erstelle .env für real:
echo GEMINI_API_KEY=your_key_here > .env

# 2. Oder bearbeite .env manuell mit Editor
# 3. Server neustarten
```

### ❌ Quiz-Erstellung dauert sehr lange

**Normal:** Erste Erstellung dauert länger (Whisper Model wird heruntergeladen)

**Erste Erstellung:** ~30-60 Sekunden
**Weitere Erstellungen:** ~10-30 Sekunden

### ❌ "Invalid YouTube URL"

**Symptom:** 400 Bad Request

**Lösung:**

- Nutze volle YouTube URL: `https://www.youtube.com/watch?v=VIDEO_ID`
- Nicht: `youtu.be/VIDEO_ID` oder `youtube.com/watch?v=...` (ohne https)

### macOS: "No module named 'whisper'"

**Symptom:** ImportError bei Whisper

**Lösung:**

```bash
# Optional: Nutze python3 explizit
python3 -m venv venv
source venv/bin/activate
pip install openai-whisper
```

---

**Made with ❤️ for Quizly**
