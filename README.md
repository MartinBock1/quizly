
# Quizly Backend

![Quizly Logo](https://img.shields.io/badge/Quizly-Backend-blue)

A modern Django backend for quiz generation from YouTube videos with AI support (Whisper, Gemini).

## Features
- User registration, login, logout (JWT, cookies)
- Quiz creation from YouTube links (audio extraction, transcription, AI questions)
- Dummy quiz fallback on errors
- Quiz management: list, detail, update, delete
- Modern REST API with CORS and CSRF protection
- Comprehensive tests

---

## Quickstart: Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/MartinBock1/quizly.git
cd quizly
```

### 2. Create Python environment
```bash
python -m venv env
```

### 3. Activate environment
- **Windows:**
  ```bash
  .\env\Scripts\activate
  ```
- **Linux/Mac:**
  ```bash
  source env/bin/activate
  ```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Create .env file
```env
SECRET_KEY=your-django-secret-key
GEMINI_API_KEY=your-gemini-api-key
```

### 6. Run migrations
```bash
python manage.py migrate
```

### 7. Start server
```bash
python manage.py runserver
```

---

## API Endpoints

### Authentication
- `POST /api/register/` – Register
- `POST /api/login/` – Login (JWT in cookie)
- `POST /api/logout/` – Logout

### Quiz Management
- `POST /api/createQuiz/` – Create quiz from YouTube video
- `GET /api/quizzes/` – List all quizzes of user
- `GET /api/quizzes/{id}/` – Get single quiz
- `PATCH /api/quizzes/{id}/` – Update quiz
- `DELETE /api/quizzes/{id}/` – Delete quiz

---

## Technology Stack
- Django 5
- Django REST Framework
- Simple JWT
- python-dotenv
- yt-dlp, Whisper, Gemini (Google Generative AI)

---

## Notes
- For local development: set `CORS_ALLOW_CREDENTIALS = True` in `settings.py`.
- Dummy quiz is automatically generated on AI/parsing errors.
- All endpoints are protected by token/cookie authentication.

---

## License
MIT

---

## Contact
Martin Bock – [GitHub](https://github.com/MartinBock1)
