# Requirements Verification Matrix

| Requirement Group | Implementation / Evidence | Status |
|---|---|---|
| FR-01..FR-03 | Login/logout, credential validation | Verified |
| FR-04..FR-06 | Admin account create/activate/role assignment | Implemented |
| FR-07 | Role checks on protected functions | Verified by HTTP 403 scenario |
| FR-08..FR-11 | Add/edit/view/delete book with open-loan guard | Implemented + tested deletion rule |
| FR-12..FR-14 | Add/view categories; category deletion excluded | Implemented |
| FR-15..FR-19 | Register/edit/view member and Member self linkage | Implemented + tested account linkage |
| FR-20..FR-24 | Borrow/return and availability updates | Verified by automated tests |
| FR-25..FR-29 | Search title/author/category + availability | Verified by automated tests |
| FR-30..FR-34 | Current/overdue loans and Member own loans | Implemented + overdue tested |
| NFR-01..02 | Local timing checks | Verified locally |
| NFR-03..06 | Authorization, password hashing, lockout, idle timeout | Implemented |
| NFR-07..08 | Direct search flow and clear validation errors | Implemented |
| NFR-09 | Transactional borrow/return | Verified |
| NFR-10 | Availability target | Not measurable in short local run |
| NFR-11 | 10k/5k/50k synthetic dataset | Verified locally |
| NFR-12..13 | Documentation and portable standard-library runtime | Implemented |
| NFR-14..16 | Backup retention / restore | Implemented and locally checked |
