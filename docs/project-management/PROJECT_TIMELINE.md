# Project Timeline — Library Management System (LMS)

## 1. Timeline Objective

This timeline defines the execution order for the academic Library Management System project and the immediate submission-critical work. The project is implemented as an individual project, so activities are sequenced to avoid unnecessary parallel complexity.

## 2. Phase-Level Plan

| Phase | Main Deliverable | Dependency | Status |
|---|---|---|---|
| Phase 1 | Software Requirements Specification (SRS) | None | Completed |
| Phase 2 | GitHub/Trello Project Management Setup | Phase 1 | Completed |
| Phase 3 | System Analysis Diagrams | Phase 1 | Next |
| Phase 4 | Logical Data Design & Data Dictionary | Phase 3 | Pending |
| Phase 5 | Minimum Required Implementation | Phases 1–4 | Pending |
| Phase 6 | Testing & Acceptance Review | Phase 5 | Pending |
| Phase 7 | Final Documentation & Submission Package | Phases 1–6 | Pending |

## 3. Submission-Critical Schedule

> Submission window: morning of 20 September 2026. Exact clock time was not specified, so the plan prioritizes completion order rather than an invented submission hour.

### Critical Path

1. Close Phase 2 project-management evidence.
2. Complete all required analysis diagrams.
3. Complete logical data definitions and Data Dictionary.
4. Implement only the required core functions.
5. Execute minimum acceptance and functional tests.
6. Consolidate the final report and submission evidence.

## 4. Compressed Execution Plan

| Order | Work Package | Deliverable | Exit Condition |
|---:|---|---|---|
| 1 | Phase 2 Closure | Repository, Backlog, Trello, workflow, timeline, review | All 2.1–2.8 artifacts documented |
| 2 | Phase 3 — Use Case | Use Case model for Admin, Librarian, Member | All approved system functions represented |
| 3 | Phase 3 — DFD | Context Diagram + DFD Level 1 | External actors and major data flows consistent with SRS |
| 4 | Phase 3 — Activity | Activity diagrams for key workflows | Login, Borrow, Return, Search covered |
| 5 | Phase 3 — Sequence | Sequence diagrams for key interactions | Major request/response order documented |
| 6 | Phase 4 — Logical Data | Entities, attributes, relationship descriptions | Consistent with SRS and diagrams |
| 7 | Phase 4 — Data Dictionary | Formal dictionary for logical data elements | Main entities and fields documented |
| 8 | Phase 5 — Core Implementation | Minimum viable LMS implementation | Core Must requirements available |
| 9 | Phase 6 — Testing | Functional/acceptance evidence | Critical Must scenarios pass |
| 10 | Phase 7 — Final Package | Final report + evidence + repository | Submission package reviewed |

## 5. Implementation Priority

### Priority A — Must Complete
- Authentication and role-based access.
- Book management.
- Member management.
- Borrowing and returns.
- Search and availability.
- Current and overdue loan tracking.

### Priority B — Complete if time permits after Priority A
- Expanded usability refinements.
- Additional performance evidence.
- Extra documentation polish beyond required submission evidence.

## 6. Backlog Execution Waves

| Wave | Stories | Purpose |
|---|---|---|
| Wave 1 | US-01 to US-03 | Authentication and access foundation |
| Wave 2 | US-04 to US-09 | Books, categories, and members |
| Wave 3 | US-10 to US-11 | Borrowing and return |
| Wave 4 | US-12 to US-13 | Search and availability |
| Wave 5 | US-14 to US-16 | Loan monitoring and overdue tracking |
| Wave 6 | US-17 to US-22 | Quality verification and recovery |

## 7. Deadline Control Rules

Because the final submission is imminent:

- No new scope is added unless it is explicitly required by the academic specification.
- Out-of-Scope items remain excluded.
- Must requirements are completed before Should requirements.
- Documentation evidence is updated immediately after each phase.
- Visual polish is secondary to correctness, traceability, and required deliverables.
- Any optional automation or integration is deferred until required deliverables are complete.

## 8. Completion Check

Phase 2 is complete when:
- GitHub repository structure exists.
- Project Backlog is documented.
- Trello board is configured.
- Requirements are mapped to User Stories and Tasks.
- GitHub and Trello are cross-linked.
- Git workflow and branching strategy are documented.
- This timeline is documented.
- Phase 2 closure review is completed.
