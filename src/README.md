# Source Code — LMS Reference Implementation

The implementation is intentionally lightweight for the academic submission and uses only the Python standard library.

## Technology

- Python 3.10+
- `http.server` for the web interface
- `sqlite3` for persistence
- PBKDF2-HMAC-SHA256 password hashing
- Cookie-based server-side sessions
- No third-party packages required

## Run

```bash
cd src
python app.py
```

Open:

`http://127.0.0.1:8080`

## Demo Accounts

- Admin: `admin / Admin@12345`
- Librarian: `librarian / Lib@12345`
- Member: `member / Member@12345`

These credentials are for academic demonstration only.

## Implemented Features

- Login/logout
- Role-based authorization
- Account activation/deactivation and role assignment
- Failed-login lockout after 5 attempts for 15 minutes
- 30-minute idle session timeout
- Books and categories
- Members
- Borrowing and returns
- Atomic availability updates
- Search by title, author, and category
- Current and overdue loans
- Member personal profile and own loan history
- SQLite persistence
- Backup and restore commands

## Backup

```bash
python app.py --backup
```

The command keeps the most recent 7 backup files.

## Restore

```bash
python app.py --restore data/backups/lms_backup_YYYYMMDD_HHMMSS.db
```

## Security Note

Passwords are hashed and salted. The implementation is an academic reference build, not a claim of production hardening.
