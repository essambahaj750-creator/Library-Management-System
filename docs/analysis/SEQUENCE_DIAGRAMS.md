# Sequence Diagrams

> المشاركون هنا مكونات منطقية للتحليل وليست فرضًا نهائيًا على تقنية التنفيذ.

## 1. Sequence — تسجيل الدخول

```mermaid
sequenceDiagram
    actor U as User
    participant UI as واجهة النظام
    participant AUTH as خدمة الوصول
    participant ACC as مخزن المستخدمين والأدوار

    U->>UI: إدخال بيانات الدخول
    UI->>AUTH: طلب تسجيل الدخول
    AUTH->>ACC: البحث عن الحساب والتحقق من حالته
    ACC-->>AUTH: بيانات الحساب والدور
    alt بيانات صحيحة وحساب فعال
        AUTH-->>UI: نجاح + صلاحيات الدور
        UI-->>U: فتح الواجهة المسموح بها
    else بيانات غير صحيحة أو حساب غير فعال
        AUTH-->>UI: رفض + سبب مناسب
        UI-->>U: عرض رسالة الخطأ
    end
```

## 2. Sequence — استعارة كتاب

```mermaid
sequenceDiagram
    actor L as Librarian/Admin
    participant UI as واجهة النظام
    participant MEM as إدارة الأعضاء
    participant BOOK as إدارة الكتب
    participant LOAN as إدارة الاستعارات
    participant DB as مخازن البيانات

    L->>UI: اختيار عضو وكتاب وموعد إرجاع
    UI->>MEM: تحقق من العضو
    MEM->>DB: قراءة بيانات العضو
    DB-->>MEM: حالة العضو
    MEM-->>UI: صالح/غير صالح
    UI->>BOOK: تحقق من التوفر
    BOOK->>DB: قراءة بيانات الكتاب
    DB-->>BOOK: النسخ المتاحة
    BOOK-->>UI: متاح/غير متاح
    alt العضو صالح والكتاب متاح والموعد صالح
        UI->>LOAN: إنشاء استعارة
        LOAN->>DB: حفظ Loan وتحديث التوفر
        DB-->>LOAN: نجاح
        LOAN-->>UI: تأكيد العملية
        UI-->>L: تم تسجيل الاستعارة
    else شرط غير متحقق
        UI-->>L: رفض العملية مع السبب
    end
```

## 3. Sequence — إرجاع كتاب

```mermaid
sequenceDiagram
    actor L as Librarian/Admin
    participant UI as واجهة النظام
    participant LOAN as إدارة الاستعارات
    participant BOOK as إدارة الكتب
    participant DB as مخازن البيانات

    L->>UI: تحديد الاستعارة المراد إرجاعها
    UI->>LOAN: طلب الإرجاع
    LOAN->>DB: التحقق من أن الاستعارة مفتوحة
    DB-->>LOAN: حالة الاستعارة
    alt الاستعارة مفتوحة
        LOAN->>DB: تسجيل الإرجاع وإغلاق Loan
        LOAN->>BOOK: طلب تحديث التوفر
        BOOK->>DB: زيادة النسخ المتاحة
        DB-->>BOOK: نجاح
        BOOK-->>LOAN: تم تحديث التوفر
        LOAN-->>UI: نجاح الإرجاع
        UI-->>L: تأكيد العملية
    else غير مفتوحة
        LOAN-->>UI: رفض
        UI-->>L: عرض سبب الرفض
    end
```

## 4. Sequence — البحث عن كتاب

```mermaid
sequenceDiagram
    actor U as Admin/Librarian/Member
    participant UI as واجهة النظام
    participant SEARCH as خدمة البحث
    participant BOOK as مخزن الكتب والتصنيفات

    U->>UI: إدخال معيار البحث
    UI->>SEARCH: بحث بالعنوان/المؤلف/التصنيف
    SEARCH->>BOOK: استعلام الكتب المطابقة
    BOOK-->>SEARCH: قائمة النتائج + بيانات التوفر
    SEARCH-->>UI: نتائج منظمة
    UI-->>U: عرض الكتب وحالة التوفر
```

## التغطية

| المخطط | المتطلبات |
|---|---|
| تسجيل الدخول | FR-01..FR-07 + NFR-03..NFR-06 |
| استعارة كتاب | FR-20, FR-21, FR-23 + NFR-09 |
| إرجاع كتاب | FR-22, FR-24 + NFR-09 |
| البحث عن كتاب | FR-25..FR-29 + NFR-01, NFR-07 |
