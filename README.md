# Library Management System (LMS)

Academic project for a public library management system.

## Project Scope

The system is designed for one public library and physical books only. It covers:

- User authentication and role-based access
- Books and categories management
- Members management
- Borrowing and returns
- Book search and availability
- Current and overdue loans monitoring

## Actors

- Administrator (Admin)
- Librarian
- Member

## Requirements Baseline

Phase 1 — Software Requirements Specification (SRS) has been completed and approved.

- 6 documented problems (P-01 to P-06)
- 8 project objectives (OBJ-01 to OBJ-08)
- 30 system functions (FN-01 to FN-30)
- 34 functional requirements (FR-01 to FR-34)
- 16 non-functional requirements (NFR-01 to NFR-16)

## Project Backlog

Phase 2.2 — Project Backlog has been structured and linked to the approved requirements.

- 7 Epics
- 22 User Stories
- 97 executable Tasks
- Functional and non-functional requirements mapped to GitHub Issues
- Definition of Ready (DoR) and Definition of Done (DoD) documented

Backlog document:

`docs/project-management/PROJECT_BACKLOG.md`

## Repository Structure

```text
Library-Management-System/
├── README.md
├── docs/
│   ├── SRS/
│   ├── analysis/
│   │   ├── README.md
│   │   ├── USE_CASE_DIAGRAM.md
│   │   ├── DFD_DIAGRAMS.md
│   │   ├── ACTIVITY_DIAGRAMS.md
│   │   ├── SEQUENCE_DIAGRAMS.md
│   │   └── PHASE3_REVIEW.md
│   └── project-management/
│       ├── PROJECT_BACKLOG.md
│       ├── TRELLO_MAPPING.md
│       ├── GITHUB_TRELLO_WORKFLOW.md
│       ├── GIT_WORKFLOW.md
│       ├── PROJECT_TIMELINE.md
│       └── PHASE2_REVIEW.md
├── src/
└── tests/
```

## Project Status

- Phase 1: Requirements Analysis — Completed
- Phase 2.1: GitHub Repository Setup — Completed
- Phase 2.2: Project Backlog — Completed
- Phase 2.3: Trello Board — Completed
- Phase 2.4: Requirements-to-Tasks Mapping — Completed
- Phase 2.5: GitHub ↔ Trello Linking — Completed
- Phase 2.6: Git Workflow & Branching Strategy — Completed
- Phase 2.7: Project Timeline — Completed
- Phase 2.8: Phase Closure Review — Completed
- Phase 2: Project Management & Repository Setup — Completed
- Phase 3: System Analysis Diagrams — Completed
- Phase 4: Logical Data Design & Data Dictionary — Completed
- Phase 5: Implementation — Completed
- Phase 6: Testing & Review — Completed
- Phase 7: Final Documentation & Submission — Completed
- Phase 4: Logical Data Design & Data Dictionary — Not Started
- Phase 5: Implementation — Not Started
- Phase 6: Testing & Review — Not Started
- Phase 7: Final Documentation & Submission — Not Started

## Project Tracking

- GitHub Issues: source of requirement/work-item references.
- Trello Board: source of execution status.
- Trello Board: https://trello.com/b/rqznByBM/library-management-system
- Every Trello User Story links to its GitHub Issue.
- Every GitHub User Story links back to its Trello Card.

Integration workflow document:

`docs/project-management/GITHUB_TRELLO_WORKFLOW.md`

## Out of Scope

The current academic version does not include financial fines, book reservations, SMS/email notifications, e-books, multiple library branches, payroll, suppliers, or home delivery.


## System Analysis Diagrams

Phase 3 is documented under:

`docs/analysis/`

It includes Use Case, DFD Context/Level 1, Activity, and Sequence diagrams, all traceable to the approved SRS baseline.


## Data Design

Phase 4 data-design artifacts are available under:

`docs/data-design/`

They include the logical data model, detailed Data Dictionary, an editable Draw.io ERD, and the Phase 4 closure review.



## Premium Interface Update

The LMS interface has been upgraded with a modern role-aware design:

- Professional fixed sidebar with SVG navigation icons
- Premium login screen without exposing account credentials
- Role-specific dashboards for Admin, Librarian, and Member
- Member dashboard shows only the member's own loan information
- Dashboard search bar, quick actions, KPI cards, recent circulation, and responsive layouts
- Improved profile presentation and mobile behavior

## Reference Implementation

A runnable academic implementation is available under:

`src/app.py`

Run with Python 3:

```bash
cd src
python app.py
```

Automated tests are located under `tests/`.


## Verification

Testing evidence is documented under:

`docs/testing/`

The reference build passed 6/6 automated tests, HTTP smoke checks, local scale checks at 10,000 books / 5,000 members / 50,000 loans, and backup/restore checks.


## Final Status

**PROJECT READY FOR ACADEMIC SUBMISSION**

Final status, checklist, and demo guide are available under:

`docs/final/`

GitHub: https://github.com/essambahaj750-creator/Library-Management-System

Trello: https://trello.com/b/rqznByBM/library-management-system
