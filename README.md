# SecurePaper - Supabase Edition

## Features
- Supabase PostgreSQL database
- Password hashing with Werkzeug
- Role-based access control
- Encrypted question text and options using Fernet
- Approval/rejection workflow
- Approved-question-only paper generation
- Generated paper history
- Professional responsive CSS frontend

## Setup

1. Create the tables using the SQL supplied with this project.
2. Copy `.env.example` to `.env`.
3. Generate an encryption key:

```powershell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

4. Put that key in `QUESTION_ENCRYPTION_KEY`.
5. Install packages:

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

6. Run:

```powershell
python app.py
```

7. Open http://127.0.0.1:5000/register and create the first ADMIN account.

## Important security notes

- Keep `.env` private.
- Use the Supabase server-side secret key only in Flask.
- Do not upload `.env` to GitHub.
- Fernet encryption protects question content at rest.
- Passwords are hashed, not encrypted.
- In production, use HTTPS, set COOKIE_SECURE=true, rotate secrets safely, disable public registration, and use a production WSGI server.
