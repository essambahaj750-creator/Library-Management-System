# Submission & Demo Guide

## Run the LMS

From the repository root:

```bash
cd src
python app.py
```

Open:

`http://127.0.0.1:8080`

## Demo Accounts

| Role | Username | Password |
|---|---|---|
| Admin | admin | Admin@12345 |
| Librarian | librarian | Lib@12345 |
| Member | member | Member@12345 |

These are demonstration credentials only.

## Suggested Live Demo Order

1. Login as Admin.
2. Show Dashboard.
3. Open Users and explain roles.
4. Add or view a Category.
5. Add a Book.
6. Register or view a Member.
7. Register a Borrowing.
8. Show Current Loans.
9. Return the book.
10. Search for the book.
11. Login as Member.
12. Show My Profile and My Loans.
13. Explain overdue detection.
14. Show Trello board and GitHub repository.
15. Show Draw.io analysis diagrams.

## Key Talking Points

- Member does not self-borrow or self-return.
- Borrow and return update availability transactionally.
- Book deletion is rejected while an open loan exists.
- Passwords are hashed rather than stored as plaintext.
- Role checks restrict protected functions.
- Project artifacts are traceable from SRS → GitHub → Trello → code/tests.

## Links

GitHub:
https://github.com/essambahaj750-creator/Library-Management-System

Trello:
https://trello.com/b/rqznByBM/library-management-system
