# Data Dictionary — Library Management System

## 1. Role

| الحقل | النوع المنطقي | Null | مفتاح | القيود / الوصف |
|---|---|---:|---|---|
| id | Integer | No | PK | معرف فريد للدور |
| name | String(30) | No | UQ | Admin / Librarian / Member |

## 2. UserAccount

| الحقل | النوع المنطقي | Null | مفتاح | القيود / الوصف |
|---|---|---:|---|---|
| id | Integer | No | PK | معرف الحساب |
| username | String(100) | No | UQ | اسم دخول فريد |
| password_hash | String | No | — | Hash لكلمة المرور؛ لا تحفظ كنص صريح |
| salt | String | No | — | Salt لعملية Hash |
| role_id | Integer | No | FK | يشير إلى Role.id |
| active | Boolean | No | — | حالة تفعيل الحساب |
| failed_attempts | Integer | No | — | عدد المحاولات الفاشلة المتتالية |
| locked_until | DateTime | Yes | — | نهاية القفل المؤقت |
| created_at | DateTime | No | — | تاريخ إنشاء الحساب |

## 3. Member

| الحقل | النوع المنطقي | Null | مفتاح | القيود / الوصف |
|---|---|---:|---|---|
| id | Integer | No | PK | رقم العضو |
| full_name | String(150) | No | — | الاسم الكامل |
| phone | String(30) | No | — | رقم الهاتف |
| registration_date | Date | No | — | تاريخ التسجيل |
| status | Enum | No | — | Active / Inactive |
| user_id | Integer | Yes | FK,UQ | حساب Member المرتبط بالعضو |

## 4. Category

| الحقل | النوع المنطقي | Null | مفتاح | القيود / الوصف |
|---|---|---:|---|---|
| id | Integer | No | PK | معرف التصنيف |
| name | String(100) | No | UQ | اسم تصنيف فريد |
| description | String(500) | Yes | — | وصف اختياري |

## 5. Book

| الحقل | النوع المنطقي | Null | مفتاح | القيود / الوصف |
|---|---|---:|---|---|
| id | Integer | No | PK | معرف الكتاب |
| title | String(250) | No | — | عنوان الكتاب |
| author | String(200) | No | — | المؤلف |
| category_id | Integer | No | FK | يشير إلى Category.id |
| total_copies | Integer | No | — | عدد النسخ الكلي، >= 0 |
| available_copies | Integer | No | — | النسخ المتاحة، بين 0 و total_copies |

## 6. Loan

| الحقل | النوع المنطقي | Null | مفتاح | القيود / الوصف |
|---|---|---:|---|---|
| id | Integer | No | PK | رقم عملية الاستعارة |
| book_id | Integer | No | FK | يشير إلى Book.id |
| member_id | Integer | No | FK | يشير إلى Member.id |
| borrow_date | Date | No | — | تاريخ الاستعارة |
| due_date | Date | No | — | تاريخ الاستحقاق |
| return_date | Date | Yes | — | تاريخ الإرجاع الفعلي |
| status | Enum | No | — | Open / Returned |

## 7. عناصر مشتقة

| العنصر | قاعدة الاشتقاق |
|---|---|
| Book Availability | Available إذا كانت available_copies > 0 |
| Loan Overdue | return_date IS NULL AND due_date < CurrentDate |
| Borrowed Copies | total_copies - available_copies |

## 8. قواعد تحقق إدخال البيانات

- Username مطلوب وفريد.
- Password في التنفيذ المرجعي لا يقل عن 8 محارف.
- اسم الكتاب والمؤلف مطلوبان.
- اسم التصنيف مطلوب وفريد.
- اسم العضو ورقم الهاتف مطلوبان.
- Due Date لا يكون في الماضي عند تسجيل استعارة جديدة.
- لا يسمح بخفض Total Copies لأقل من عدد النسخ المستعارة حاليًا.
- Member Inactive لا يسمح له باستعارة جديدة.

## 9. تتبع المتطلبات

- UserAccount + Role: FR-01..FR-07.
- Book + Category: FR-08..FR-14 و FR-25..FR-29.
- Member: FR-15..FR-19.
- Loan: FR-20..FR-24 و FR-30..FR-34.
