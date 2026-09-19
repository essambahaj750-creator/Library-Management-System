# Project Backlog — Library Management System (LMS)

## 1. Purpose

هذا الملف يمثل الـ **Project Backlog** المعتمد للمشروع، وتم اشتقاقه مباشرة من وثيقة المتطلبات الأساسية (SRS) للمرحلة الأولى.

- Functional Requirements: FR-01 إلى FR-34
- Non-Functional Requirements: NFR-01 إلى NFR-16
- Actors: Admin, Librarian, Member
- Scope: مكتبة عامة واحدة، كتب مادية فقط

كل User Story على GitHub تحتوي على:
1. المتطلبات المرتبطة.
2. الأولوية.
3. User Story / Quality Story.
4. Acceptance Criteria.
5. قائمة Tasks قابلة للتنفيذ.

---

## 2. Backlog Hierarchy

**Epic → User Story → Tasks → Acceptance Criteria**

عدد عناصر الـBacklog الحالية:

- **7 Epics**
- **22 User Stories**
- **97 Tasks**
- تغطية **34 Functional Requirements**
- تغطية **16 Non-Functional Requirements**

---

## 3. Epics

| Epic | GitHub Issue | Scope |
|---|---:|---|
| E1 — Authentication & Access Control | #1 | FR-01..FR-07 |
| E2 — Books & Categories Management | #2 | FR-08..FR-14 |
| E3 — Member Management | #3 | FR-15..FR-19 |
| E4 — Borrowing & Returns | #4 | FR-20..FR-24 |
| E5 — Search & Availability | #5 | FR-25..FR-29 |
| E6 — Loan Monitoring & Overdue Tracking | #6 | FR-30..FR-34 |
| E7 — Quality Attributes & Acceptance | #7 | NFR-01..NFR-16 |

---

## 4. User Stories

### E1 — Authentication & Access Control

| Story | Issue | Requirements | Priority |
|---|---:|---|---|
| US-01 — Sign in and sign out | #8 | FR-01, FR-02, FR-03 | Must |
| US-02 — Manage user accounts and roles | #9 | FR-04, FR-05, FR-06 | Must |
| US-03 — Enforce role-based permissions | #10 | FR-07 | Must |

### E2 — Books & Categories Management

| Story | Issue | Requirements | Priority |
|---|---:|---|---|
| US-04 — Add, edit, and view books | #11 | FR-08, FR-09, FR-11 | Must |
| US-05 — Safely delete a book | #12 | FR-10 | Must |
| US-06 — Manage book categories | #13 | FR-12, FR-13, FR-14 | Should |

### E3 — Member Management

| Story | Issue | Requirements | Priority |
|---|---:|---|---|
| US-07 — Register and update members | #14 | FR-15, FR-16 | Must |
| US-08 — View member details and personal profile | #15 | FR-17, FR-18 | Must |
| US-09 — View member loan history | #16 | FR-19 | Must |

### E4 — Borrowing & Returns

| Story | Issue | Requirements | Priority |
|---|---:|---|---|
| US-10 — Borrow an available book | #17 | FR-20, FR-21, FR-23 | Must |
| US-11 — Return a borrowed book | #18 | FR-22, FR-24 | Must |

### E5 — Search & Availability

| Story | Issue | Requirements | Priority |
|---|---:|---|---|
| US-12 — Search books by title, author, and category | #19 | FR-25, FR-26, FR-27 | Must / Should |
| US-13 — Display organized search results and availability | #20 | FR-28, FR-29 | Must |

### E6 — Loan Monitoring & Overdue Tracking

| Story | Issue | Requirements | Priority |
|---|---:|---|---|
| US-14 — View current open loans | #21 | FR-30 | Must |
| US-15 — Detect and review overdue loans | #22 | FR-31, FR-32 | Must |
| US-16 — Member views current loans and overdue status | #23 | FR-33, FR-34 | Must |

### E7 — Quality Attributes & Acceptance

| Story | Issue | Requirements | Priority |
|---|---:|---|---|
| US-17 — Performance and scalability | #24 | NFR-01, NFR-02, NFR-11 | Must |
| US-18 — Security controls | #25 | NFR-03..NFR-06 | Must |
| US-19 — Usability targets | #26 | NFR-07, NFR-08 | Should |
| US-20 — Reliability and availability | #27 | NFR-09, NFR-10 | Must |
| US-21 — Maintainability and portability | #30 | NFR-12, NFR-13 | Should |
| US-22 — Backup and recovery | #31 | NFR-14, NFR-15, NFR-16 | Must |

> Issues #28 و #29 مغلقتان كنسخ مكررة ولا تعتبران جزءًا من الـBacklog الفعال.

---

## 5. Recommended Execution Order

### Wave 1 — Access Foundation
US-01 → US-02 → US-03

### Wave 2 — Core Library Data
US-06 → US-04 → US-05 → US-07 → US-08

### Wave 3 — Circulation
US-10 → US-11 → US-09

### Wave 4 — Search
US-12 → US-13

### Wave 5 — Monitoring
US-14 → US-15 → US-16

### Wave 6 — Quality Verification
US-17 → US-18 → US-19 → US-20 → US-21 → US-22

---

## 6. Definition of Ready (DoR)

تعد User Story جاهزة للعمل عندما:

- تكون مرتبطة بـ Epic واضح.
- تكون مرتبطة بمتطلب FR أو NFR معتمد.
- تكون صياغة الهدف واضحة.
- تحتوي Acceptance Criteria قابلة للاختبار.
- تكون Dependencies معروفة عند وجودها.
- تكون Tasks محددة بما يكفي للبدء بالتنفيذ.

---

## 7. Definition of Done (DoD)

تعد User Story مكتملة عندما:

- تكتمل جميع Tasks الخاصة بها.
- تتحقق جميع Acceptance Criteria.
- لا تخالف صلاحيات Actors أو حدود Scope.
- تمر اختبارات القبول المرتبطة بالـFR/NFR.
- يتم تحديث التوثيق عند الحاجة.
- لا تترك حالة بيانات غير متسقة أو وظيفة جزئية.

---

## 8. Backlog Governance

- **Must:** وظيفة أساسية لا يمكن قبول النسخة الأكاديمية بدونها.
- **Should:** مهمة مهمة ولكن يمكن تأجيلها مؤقتًا عند الضرورة.
- أي وظيفة جديدة خارج SRS لا تضاف مباشرة؛ يجب مراجعة أثرها على Scope وTraceability.
- لا يتم إغلاق Epic حتى تكتمل جميع User Stories المرتبطة به.
- يتم تحديث حالة Tasks من داخل User Story المعنية.


---

## 9. Trello Execution Mapping

The approved backlog has been transferred to Trello for execution tracking.

- Board: https://trello.com/b/rqznByBM/library-management-system
- 22 User Stories are represented as Trello cards.
- 97 executable Tasks are represented as Trello checklist items.
- GitHub Issue links are embedded in Trello card descriptions.
- The first execution wave (US-01 to US-03) is placed in To Do.
