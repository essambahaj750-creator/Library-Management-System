# Use Case Diagram — Library Management System

## الهدف

تمثيل التفاعل بين الممثلين الثلاثة ووظائف النظام الرئيسية وفق المتطلبات المعتمدة.

```mermaid
flowchart LR
    Admin([Administrator])
    Librarian([Librarian])
    Member([Member])

    subgraph LMS["Library Management System (LMS)"]
        UC01((تسجيل الدخول والخروج))
        UC02((إدارة الحسابات والأدوار))
        UC03((إدارة الكتب))
        UC04((إدارة التصنيفات))
        UC05((إدارة الأعضاء))
        UC06((تسجيل الاستعارة))
        UC07((تسجيل الإرجاع))
        UC08((البحث عن الكتب))
        UC09((عرض حالة التوفر))
        UC10((عرض الاستعارات الحالية))
        UC11((متابعة الاستعارات المتأخرة))
        UC12((عرض الملف الشخصي))
        UC13((عرض سجل الاستعارات))
    end

    Admin --- UC01
    Admin --- UC02
    Admin --- UC03
    Admin --- UC04
    Admin --- UC05
    Admin --- UC06
    Admin --- UC07
    Admin --- UC08
    Admin --- UC09
    Admin --- UC10
    Admin --- UC11
    Admin --- UC13

    Librarian --- UC01
    Librarian --- UC03
    Librarian --- UC04
    Librarian --- UC05
    Librarian --- UC06
    Librarian --- UC07
    Librarian --- UC08
    Librarian --- UC09
    Librarian --- UC10
    Librarian --- UC11
    Librarian --- UC13

    Member --- UC01
    Member --- UC08
    Member --- UC09
    Member --- UC10
    Member --- UC11
    Member --- UC12
    Member --- UC13
```

## وصف الممثلين

### Administrator
يمتلك صلاحيات Librarian بالإضافة إلى إدارة حسابات المستخدمين والأدوار والصلاحيات.

### Librarian
يدير الكتب والتصنيفات والأعضاء، ويسجل الاستعارات والإرجاعات، ويتابع الاستعارات الحالية والمتأخرة.

### Member
يسجل الدخول إلى حسابه الشخصي، ويبحث عن الكتب ويعرض التوفر وبياناته واستعاراته وسجله الشخصي فقط.

## تغطية المتطلبات

| Use Case | المتطلبات |
|---|---|
| تسجيل الدخول والخروج | FR-01..FR-03 |
| إدارة الحسابات والأدوار | FR-04..FR-07 |
| إدارة الكتب | FR-08..FR-11 |
| إدارة التصنيفات | FR-12..FR-14 |
| إدارة الأعضاء | FR-15..FR-19 |
| تسجيل الاستعارة | FR-20, FR-21, FR-23 |
| تسجيل الإرجاع | FR-22, FR-24 |
| البحث وعرض التوفر | FR-25..FR-29 |
| الاستعارات الحالية والمتأخرة | FR-30..FR-34 |
