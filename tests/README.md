# Tests

## Automated Tests

Run from the repository root:

```bash
python -m unittest -v tests/test_lms.py
```

## Current Automated Coverage

- Valid and invalid login
- Borrowing updates availability
- Returning restores availability
- Prevent deletion of a book with an open loan
- Search by title, author, and category
- Overdue-loan detection
- Member account linkage to its own Member record

## Result

The reference implementation was executed in the preparation environment and all 6 automated tests passed.

Additional manual acceptance checks are documented in:

`docs/testing/TEST_PLAN_AND_RESULTS.md`
