# Phase 6 — Test Plan and Results

## 1. هدف الاختبار

التحقق من أن النسخة المرجعية من نظام إدارة المكتبة تنفذ قواعد العمل الأساسية ومتطلبات القبول الحرجة قبل التسليم.

## 2. بيئة الاختبار

- Python 3.13
- SQLite
- Localhost HTTP
- اختبارات آلية باستخدام `unittest`
- بيانات أداء اصطناعية عند حدود الحجم المستهدف

## 3. نتائج الاختبارات الآلية

تم تشغيل:

```bash
python -m unittest -v test_lms.py
```

النتيجة:

- 6 Tests executed
- 6 Passed
- 0 Failed

### السيناريوهات المغطاة

| ID | السيناريو | النتيجة |
|---|---|---|
| T-01 | تسجيل دخول صحيح وخاطئ | PASS |
| T-02 | الاستعارة تخفض النسخ المتاحة | PASS |
| T-03 | الإرجاع يعيد النسخ المتاحة ويغلق Loan | PASS |
| T-04 | منع حذف كتاب عليه Loan مفتوح | PASS |
| T-05 | البحث بالعنوان والمؤلف والتصنيف | PASS |
| T-06 | اكتشاف الاستعارة المتأخرة | PASS |
| T-07 | ربط حساب Member بسجل Member الخاص به | PASS |

> ملاحظة: T-02 وT-03 جزء من اختبار آلي واحد؛ لذلك عدد حالات الاختبار الموثقة 7 بينما عدد دوال الاختبار الآلية المنفذة 6.

## 4. HTTP Smoke Tests

تم تشغيل التطبيق محليًا والتحقق من المسارات الحرجة:

| الفحص | النتيجة |
|---|---|
| GET /login | HTTP 200 |
| Admin login | HTTP 303 Redirect إلى النظام |
| Admin dashboard | HTTP 200 |
| Member login | HTTP 303 Redirect |
| Member access to /users | HTTP 403 |

هذا يؤكد أن التطبيق يبدأ ويخدم الصفحة وأن Role Authorization يعمل في سيناريو منع واضح.

## 5. Performance / Scalability Check

تم توليد بيانات اصطناعية بالحجم التالي:

- 10,000 Books
- 5,000 Members
- 50,000 Loans

تم تكرار كل قياس 20 مرة محليًا:

| العملية | Average | Max |
|---|---:|---:|
| Search by title | 1.235 ms | 2.664 ms |
| Search by author | 1.912 ms | 2.717 ms |
| List open loans | 3.136 ms | 6.098 ms |

النتائج المحلية أقل بكثير من أهداف NFR-01 وNFR-02، مع التنبيه أن هذا قياس بيئة محلية وليس Benchmark إنتاجيًا.

## 6. Backup / Restore Check

| العملية | الزمن المقاس |
|---|---:|
| Backup | 0.709 ms |
| Restore | 0.165 ms |

تم التحقق من إنشاء قاعدة البيانات المستعادة بنجاح.

## 7. NFR Verification Status

| NFR | الحالة | الدليل |
|---|---|---|
| NFR-01 | Verified locally | Search benchmark |
| NFR-02 | Verified locally | Basic query benchmark |
| NFR-03 | Partially verified | HTTP 403 + role checks in code |
| NFR-04 | Verified by implementation | Salted PBKDF2 hash; no plaintext storage |
| NFR-05 | Implemented | 5 failures / 15-min lock |
| NFR-06 | Implemented | 30-min idle session expiration |
| NFR-07 | Supported | Direct search screen |
| NFR-08 | Supported | Validation error pages/messages |
| NFR-09 | Verified by tests | Explicit DB transactions for Borrow/Return |
| NFR-10 | Design target only | 99% availability cannot be established from a short local test |
| NFR-11 | Verified locally | 10k/5k/50k dataset |
| NFR-12 | Documented | Modules/business rules in repository docs |
| NFR-13 | Supported | Zero third-party dependencies; simple run command |
| NFR-14 | Implemented | Backup command |
| NFR-15 | Implemented | Retains latest 7 backups |
| NFR-16 | Verified locally | Restore operation completes far below 30 min |

## 8. Conclusion

Core Must scenarios passed in the academic test environment. The only target not independently measurable before submission is long-duration availability (NFR-10), which remains an operational target rather than a claimed measured result.
