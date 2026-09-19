# GitHub ↔ Trello Workflow

## 1. Purpose

This document defines how GitHub and Trello are used together for the Library Management System (LMS).

The integration is intentionally lightweight and suitable for an individual academic project.

## 2. Tool Responsibilities

### GitHub
GitHub is the source of record for:
- Epics.
- User Stories.
- Requirement references (FR/NFR).
- Repository history.
- Commits.
- Branches.
- Pull Requests.
- Technical discussion.

### Trello
Trello is the source of record for:
- Execution status.
- Daily work planning.
- Task checklists.
- Progress through the workflow.

## 3. Two-Way Linking

Each Trello User Story card contains:
- The related GitHub Issue URL.
- Requirement identifiers.
- Priority.
- Acceptance Criteria.

Each GitHub User Story contains:
- The matching Trello Card URL.
- The Trello Board URL.

Each GitHub Epic contains:
- The Trello Board URL for execution tracking.

## 4. Workflow States

Trello states are interpreted as follows:

- Project Backlog: approved work not yet selected.
- To Do: ready to start.
- In Progress: implementation or active work has started.
- Testing: implementation completed and under verification.
- Review: acceptance criteria and documentation are being reviewed.
- Done: story accepted and completed.

## 5. Story Lifecycle

1. A requirement is approved in the SRS.
2. It is represented by a GitHub User Story.
3. The matching Trello card is selected from Project Backlog.
4. The card moves to To Do when ready.
5. It moves to In Progress when work begins.
6. When implementation is ready, it moves to Testing.
7. After successful testing, it moves to Review.
8. After Acceptance Criteria are satisfied, it moves to Done.
9. The matching GitHub Issue can then be closed as completed.

## 6. Commit and Pull Request Convention

When implementation begins, commits should include the related GitHub Issue number when appropriate.

Examples:

```text
feat: add user login validation (#8)
fix: prevent deleting borrowed books (#12)
test: add overdue loan acceptance tests (#22)
```

Pull Requests should reference or close the related GitHub Issue.

Examples:

```text
Closes #8
Closes #17
```

## 7. Completion Rule

A User Story is complete only when:
- All Trello checklist Tasks are complete.
- All Acceptance Criteria pass.
- The card is moved to Done.
- The related GitHub Issue is closed as completed.
- Required documentation is updated.

## 8. Current Integration Status

- 7 GitHub Epics linked to the Trello Board.
- 22 GitHub User Stories linked to 22 Trello cards.
- 22 Trello cards link back to their GitHub Issues.
- 97 Trello checklist Tasks are available for execution.
- The first execution wave, US-01 to US-03, is in To Do.
