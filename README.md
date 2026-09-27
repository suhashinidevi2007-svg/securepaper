# Deployment link 
https://securepaper-9jp9sff49-suhashini-s.vercel.app/

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


   screenshots:
<img width="1917" height="445" alt="image" src="https://github.com/user-attachments/assets/7ee93723-8f59-4b50-b3ab-c37696092e92" />

<img width="1823" height="970" alt="image" src="https://github.com/user-attachments/assets/a4f63eda-6967-43c7-984c-5963c7769aec" />

<img width="1488" height="613" alt="image" src="https://github.com/user-attachments/assets/7665b994-e8bc-41e0-9d56-920d3125957d" />

<img width="1493" height="756" alt="image" src="https://github.com/user-attachments/assets/b1fdd3be-6608-41ea-a74f-88bbc485a98d" />

<img width="1460" height="717" alt="image" src="https://github.com/user-attachments/assets/bf4fd090-92fa-47c6-a924-34e755525ff8" />
 <img width="1243" height="557" alt="image" src="https://github.com/user-attachments/assets/e287aa8f-54b1-4e6e-a25c-76ceaa07db80" />
<img width="1493" height="491" alt="image" src="https://github.com/user-attachments/assets/9128586b-5662-4b77-b165-b312276fbb45" />
<img width="580" height="636" alt="image" src="https://github.com/user-attachments/assets/0fdd42b3-c747-4420-8800-9737545c0aad" />

filtering:<img width="1507" height="581" alt="image" src="https://github.com/user-attachments/assets/156b9ccd-d3ce-42a0-960c-8bdedf6477c2" />
acess denied to generate question for custodian role:
<img width="936" height="837" alt="image" src="https://github.com/user-attachments/assets/b6d25097-3585-4acc-b922-1f6be4ce0c5b" />

<img width="825" height="802" alt="image" src="https://github.com/user-attachments/assets/2fde5d88-015b-4985-9664-60229788bb84" />

