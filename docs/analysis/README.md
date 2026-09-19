# المرحلة الثالثة — تحليل النظام والمخططات

## الهدف

توثيق التحليل السلوكي والوظيفي لنظام **Library Management System (LMS)** بالاعتماد على خط الأساس المعتمد في وثيقة SRS.

## المخططات المنفذة

1. **Use Case Diagram**
   - يوضح المستخدمين الرئيسيين ووظائف النظام.
   - الملف: `USE_CASE_DIAGRAM.md`

2. **Data Flow Diagrams (DFD)**
   - Context Diagram / Level 0.
   - DFD Level 1.
   - الملف: `DFD_DIAGRAMS.md`

3. **Activity Diagrams**
   - تسجيل الدخول.
   - استعارة كتاب.
   - إرجاع كتاب.
   - البحث عن كتاب.
   - الملف: `ACTIVITY_DIAGRAMS.md`

4. **Sequence Diagrams**
   - تسجيل الدخول.
   - استعارة كتاب.
   - إرجاع كتاب.
   - البحث عن كتاب.
   - الملف: `SEQUENCE_DIAGRAMS.md`

5. **Phase 3 Closure Review**
   - مراجعة التغطية والاتساق.
   - الملف: `PHASE3_REVIEW.md`

## المستخدمون المعتمدون

- Administrator (Admin)
- Librarian
- Member

## قواعد النطاق المؤثرة على التحليل

- Librarian أو Admin فقط يسجلان الاستعارة والإرجاع.
- Member يملك تسجيل دخول شخصيًا.
- Member يرى بياناته واستعاراته فقط.
- حذف الكتاب مسموح فقط إذا لم توجد استعارة مفتوحة عليه.
- لا توجد غرامات أو حجوزات أو فروع متعددة أو كتب إلكترونية ضمن النطاق الحالي.

## منهجية التتبع

المخططات مرتبطة مباشرة بمتطلبات SRS:

```text
Problem → Objective → Function → FR/NFR → User Story → Analysis Diagram
```

## تنسيق المخططات

تم استخدام **Mermaid** داخل ملفات Markdown حتى:
- تبقى المخططات قابلة للتعديل.
- تظهر مباشرة داخل GitHub.
- يمكن لاحقًا تصديرها كصور للتقرير النهائي.
