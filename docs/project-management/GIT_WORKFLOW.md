# Git Workflow and Branching Strategy

## 1. Purpose

This document defines the GitHub workflow for the Library Management System (LMS).
The workflow is intentionally lightweight for an individual academic project while still demonstrating professional source-control practices.

## 2. Permanent Branches

### `main`
Purpose:
- Stable and approved project baseline.
- Contains reviewed phase deliverables and release-ready code.
- Should not be used for day-to-day implementation work.

### `develop`
Purpose:
- Main integration branch for ongoing development.
- New feature and fix branches start from `develop`.
- Completed feature work is merged back into `develop`.

## 3. Temporary Branch Types

### Feature
Pattern:

```text
feature/us-XX-short-name
```

Examples:

```text
feature/us-01-authentication
feature/us-04-book-management
feature/us-10-borrow-book
```

Use for implementing a User Story or a coherent part of one.

### Fix
Pattern:

```text
fix/us-XX-short-name
```

Example:

```text
fix/us-12-search-validation
```

Use for defects discovered during Testing or Review.

### Documentation
Pattern:

```text
docs/short-description
```

Example:

```text
docs/update-srs-traceability
```

Use for documentation-only changes.

### Hotfix
Pattern:

```text
hotfix/short-description
```

Hotfix branches are created from `main` only when an approved stable version needs an urgent correction.

## 4. Branch Flow

Normal development flow:

```text
main
  └── develop
       ├── feature/us-XX-...
       ├── fix/us-XX-...
       └── docs/...
```

Feature/fix/documentation branches merge into `develop`.

When a phase or release is accepted:

```text
develop → main
```

## 5. User Story Workflow

For each User Story:

1. Confirm the Trello card is in **To Do**.
2. Create a branch from `develop`.
3. Move the Trello card to **In Progress**.
4. Implement the related Tasks.
5. Commit using the GitHub Issue number.
6. Push the branch.
7. Open a Pull Request to `develop`.
8. Verify tests and Acceptance Criteria.
9. Move the Trello card to **Testing**.
10. After successful testing, move it to **Review**.
11. Merge the Pull Request into `develop`.
12. When acceptance is complete, move the Trello card to **Done**.
13. Close the related GitHub Issue as completed.

## 6. Commit Convention

Use short imperative commit messages with a conventional prefix.

Recommended prefixes:

- `feat:` new functionality
- `fix:` defect correction
- `test:` test additions/changes
- `docs:` documentation only
- `refactor:` internal code improvement without behavior change
- `chore:` project/configuration maintenance

Examples:

```text
feat: implement login validation (#8)
feat: add book creation flow (#11)
fix: prevent deleting borrowed books (#12)
test: cover overdue loan rules (#22)
docs: update requirements traceability
```

## 7. Pull Request Rules

A Pull Request should:

- Target `develop` for feature, fix, test, and documentation branches.
- Link the related GitHub Issue.
- Include the matching Trello Card URL.
- Explain the change clearly.
- State how the change was tested.
- Confirm the Acceptance Criteria addressed.
- Avoid unrelated changes in the same PR.

Release/phase integration from `develop` to `main` should occur only after the planned work is reviewed.

## 8. Merge Strategy

Recommended merge method for this academic project:

- Feature/fix/docs → `develop`: **Squash merge** where practical, keeping history concise.
- `develop` → `main`: **Merge commit**, preserving the phase/release integration point.

## 9. Trello ↔ GitHub State Mapping

| Trello State | GitHub / Git State |
|---|---|
| Project Backlog | Approved story; no branch required |
| To Do | Ready; branch may be created |
| In Progress | Feature/fix branch active |
| Testing | Implementation complete; tests running |
| Review | Pull Request under final review/acceptance |
| Done | PR merged and GitHub Issue closed |

## 10. Traceability

The required traceability chain is:

```text
SRS Requirement
→ GitHub Epic
→ GitHub User Story / Issue
↔ Trello User Story Card
→ Trello Tasks
→ Git Branch
→ Commits
→ Pull Request
→ Tests / Acceptance Criteria
```

## 11. Example Commands

Start a User Story:

```bash
git switch develop
git pull
git switch -c feature/us-01-authentication
```

Save work:

```bash
git add .
git commit -m "feat: implement login validation (#8)"
git push -u origin feature/us-01-authentication
```

After the Pull Request is merged:

```bash
git switch develop
git pull
git branch -d feature/us-01-authentication
```

## 12. Current Repository State

- `main`: stable project baseline.
- `develop`: integration branch created and ready.
- Feature branches: created only when the corresponding User Story begins implementation.
