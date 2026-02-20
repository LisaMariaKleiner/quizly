# Quizly Backend

Django REST Framework Backend für die Quizly-Anwendung. Erstellt Quiz basierend auf YouTube-Videos durch Transkription mit Whisper AI und Quiz-Generierung mit Gemini API.

## Features

- **User Authentication**: Registrierung, Login/Logout, JWT Token Refresh
- **Quiz Management**: Erstellen, Abrufen, Bearbeiten von Quizzen
- **YouTube Integration**: Videos via `yt-dlp` herunterladen
- **Transkription**: Automatische Audio-Transkription mit Whisper AI
- **KI-Generierung**: Quiz-Erstellung mit Google Gemini API

## Voraussetzungen

- Python 3.10+
- pip oder conda
- API Keys:
  - Google Gemini API Key
  - (Optional: YouTube API Key)

## Installation

### 1. Virtuelle Umgebung erstellen

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. Dependencies installieren

```bash
pip install -r requirements.txt
```

### 3. Environment-Variablen setzen

```bash
# .env Datei erstellen
cp .env.example .env

# API Keys in .env eintragen
```

### 4. Datenbank initialisieren

```bash
python manage.py migrate
```

### 5. Superuser erstellen (optional)

```bash
python manage.py createsuperuser
```

## Entwicklungsserver starten

```bash
python manage.py runserver
```

Server läuft unter: `http://localhost:8000`

## API Endpoints

### Authentication

- `POST /api/register/` - Neuen Benutzer registrieren
- `POST /api/login/` - Benutzer anmelden
- `POST /api/logout/` - Benutzer abmelden
- `POST /api/token/refresh/` - Access Token erneuern

### Quiz Management (In Entwicklung)

- `GET /api/quiz/` - Alle Quizze abrufen
- `POST /api/quiz/` - Neues Quiz erstellen
- `GET /api/quiz/{id}/` - Quiz-Details
- `PUT /api/quiz/{id}/` - Quiz bearbeiten
- `DELETE /api/quiz/{id}/` - Quiz löschen

## Projektstruktur

```
quizly_backend/
├── core/                  # Django Core Settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── auth_app/             # Authentication App
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── ...
├── quiz_app/             # Quiz Management App
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── ...
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Dependencies

- **Django 4.2.7** - Web Framework
- **djangorestframework 3.14.0** - REST API
- **djangorestframework-simplejwt 5.3.2** - JWT Authentication
- **whisper-ai 3.1** - Audio Transkription
- **yt-dlp 2024.1.1** - YouTube Video Download
- **google-generativeai 0.3.0** - Gemini API
- **corsheaders 4.3.1** - CORS Support
- **python-decouple 3.8** - Environment Config

## Environment Variablen

Siehe `.env.example` für alle notwendigen Variablen.

## Hinweise für Entwicklung

1. **Nie** `.env` mit echten API Keys auf GitHub pushen
2. `.env.example` immer aktuell halten
3. Database-Migrationen vor Commit testen
4. API-Tests vor Production-Deployment durchführen

## Lizenz

MIT
