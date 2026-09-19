# المرحلة الرابعة — التصميم المنطقي للبيانات وقاموس البيانات

تم تصميم نموذج البيانات بالاعتماد على خط الأساس المعتمد في SRS ومخططات المرحلة الثالثة.

## المخرجات

- `LOGICAL_DATA_MODEL.md` — وصف الكيانات والعلاقات وقواعد التكامل.
- `DATA_DICTIONARY.md` — قاموس البيانات التفصيلي.
- `ERD.drawio` — مخطط ERD قابل للتعديل في diagrams.net / Draw.io.
- `PHASE4_REVIEW.md` — مراجعة إغلاق المرحلة.

## الكيانات

1. Role
2. UserAccount
3. Member
4. Category
5. Book
6. Loan

## العلاقات

- Role 1:N UserAccount
- UserAccount 1:0..1 Member
- Category 1:N Book
- Member 1:N Loan
- Book 1:N Loan

## قواعد رئيسية

- `available_copies <= total_copies`.
- لا يمكن حذف كتاب عليه Loan مفتوح.
- Loan يعتبر متأخرًا عندما يتجاوز `due_date` ولا يوجد `return_date`.
- Member يرى بيانات Member المرتبطة بحسابه فقط.
- لا يوجد Fine أو Reservation أو E-Book أو Multi-Branch ضمن النموذج الحالي.
