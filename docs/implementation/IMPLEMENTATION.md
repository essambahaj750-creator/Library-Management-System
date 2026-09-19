# Phase 5 — Implementation

## Implementation Strategy

Because the submission deadline is immediate, the project uses a compact reference implementation that can run without package installation.

## Technology

- Python 3 standard library
- Built-in HTTP server
- SQLite database
- Server-side sessions
- PBKDF2-HMAC-SHA256 password hashing

## Implemented Functional Areas

| Area | Implemented |
|---|---|
| Authentication | Yes |
| Role-based permissions | Yes |
| User accounts / roles | Yes |
| Books | Yes |
| Categories | Yes |
| Members | Yes |
| Borrowing | Yes |
| Returns | Yes |
| Search | Yes |
| Availability | Yes |
| Current loans | Yes |
| Overdue loans | Yes |
| Member own profile | Yes |
| Member own loan history | Yes |
| Backup / restore command | Yes |

## Requirement Alignment

- FR-01..FR-07: authentication, accounts, roles, permission checks.
- FR-08..FR-14: books and categories.
- FR-15..FR-19: members and personal access.
- FR-20..FR-24: borrowing, return, availability updates.
- FR-25..FR-29: search and availability.
- FR-30..FR-34: current and overdue loan monitoring.

## Relevant NFR Evidence

- NFR-03: server-side role checks reject unauthorized functions.
- NFR-04: passwords stored as salted PBKDF2 hashes.
- NFR-05: lockout after 5 failed attempts for 15 minutes.
- NFR-06: sessions expire after 30 minutes of inactivity.
- NFR-09: borrow/return database updates use explicit transactions.
- NFR-14/NFR-15: backup command retains the latest 7 backups.

## Run

```bash
cd src
python app.py
```

## Verification Performed

- Automated unit/business-rule test suite: 6/6 passed.
- HTTP smoke test: `GET /login` returned HTTP 200.
