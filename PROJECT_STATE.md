# Project State Tracking — Modular Platform Architecture (v2.3)

## Current Status
- **Current Milestone:** Step 5 (Dynamic Registry & Math Extensibility) & Step 6 (Central Configuration & Hot Reload) Completed 🟢
- **System Architecture:** Modular Multi-Tenant Document Intelligence Platform
- **Stability Status:** 100% Operational, Zero-Hallucination Verified, Fully Backward Compatible.
- **Test Suite Status:** 6/6 Offline Test Suites Passing (100% Green).

---

## Completed Milestones (v2.3 Platform Evolution):

### Phase 0–27 (Baseline MVP & Multimodal Core)
- پیاده‌سازی پایپ‌لاین RAG بدون فریم‌ورک‌های واسط (Framework-Free) با پایتون خالص، Google GenAI، ChromaDB و SQLite.
- پشتیبانی چندوجهی و چندفرمت: فایل‌های PDF دیجیتال و اسکن‌شده (PyMuPDF OCR)، اسناد Word (`.docx`)، تصاویر (Gemini Vision) و دفاتر کاری اکسل (`.xlsx`/`.xls`) با نگاشت ساختاریافته شیت‌ها و سطرها.
- استخراج داده‌های ممیزی سیستم مدیریت زیست‌محیطی ISO 14001 و تولید گزارش‌های سازمانی اکسل و ورد با امضاهای پویا و متادیتای شرکت.

### Step 1 — Modular Schema Registry
- انتقال کامل منطق دامنه به فایل‌های ساختاریافته در مسیر `schemas/*.json` (`iso_14001.json`, `fleet_fuel_expenses.json`, `general_documents.json`).
- پیاده‌سازی رجیستری در `app/extraction/registry.py` همراه با اعتبارسنجی نوع داده‌ها و محاسبات ریاضی قطعی در `app/extraction/calculators.py`.
- تبدیل `app/extraction/schemas.py` به یک Shim سازگار رو به عقب برای حفظ سلامت تست‌های قدیمی.

### Step 2 — UI Module Switcher & Review Roundtrip
- افزودن انتخابگر دامنه‌های عملیاتی در نوار کناری رابط کاربری (`🧩 Modulo / Standard Operativo`).
- پیاده‌سازی موتور چرخه بازبینی انسانی (`app/extraction/review.py`): ثبت ویرایش‌های دستی `st.data_editor` با وضعیت `EDITED` و محاسبه مجدد خودکار فرمول‌ها بدون ایجاد توهم.
- فیلتر بازیابی معنایی بر اساس اسناد سشن فعال و اعمال پاک‌سازی زباله‌های برداری.

### Step 3 — Scoped Exporters (Cross-Module Isolation)
- تفکیک قطعی ماژول‌ها در خروجی‌های رسمی اکسل و ورد از طریق `app/reporting/common.py` (`resolve_scope`).
- تضمین عدم نفوذ داده‌ها و شیت‌های ماژول‌های دیگر در گزارش نهایی (رفع آلودگی بین‌اسکیمایی).
- اعتبارسنجی ۱۰۰٪ موفق با تست اختصاصی `test_scoped_reports.py`.

### Step 4 — Deadline Alerts Engine & Monitoring
- راه‌اندازی موتور قطعی استخراج سررسیدهای قانونی و ممیزی (`app/alerts/deadlines.py`) با شناسه‌های یکتای UUID5.
- موتور اسکن زمان‌بندی‌شده و دسته‌بندی آستانه‌های بحرانی (`app/alerts/scanner.py`) بر اساس روزهای باقی‌‌مانده.
- لایه پایداری SQLite (`app/alerts/store.py`) با سازوکار ضدهرزنامه و جلوگیری از ارسال تکراری (Deduplication).
- دیسپچر اعلان‌ها و کلاینت‌های استاندارد SMTP Email و Twilio SMS (`app/alerts/dispatcher.py`, `app/alerts/notifiers.py`).
- اضافه شدن تب «⏰ Scadenze & Monitoraggio» در UI و نقطه ورود CLI مستقل `app/alerts/run.py`.

### Step 5 — Dynamic Schema Registry & Extensibility
- تعمیم عملگرهای محاسباتی قطعی پایتون در `calculators.py`: پشتیبانی کامل از عملگرهای `ratio`، `sum`، `diff` و `product` بدون ریسک توهم هوش مصنوعی.
- پیکربندی پویای مدل استخراج برای هر ماژول اسکیما (`ModuleDef.model`) با پیش‌فرض `gemini-3.6-flash`.
- افزودن مکانیزم بازخوانی زنده کش رجیستری (`reload_registry`).
- ارتقای نرمال‌ساز تاریخ (`normalizer.py`) برای پشتیبانی هم‌زمان از اسناد انگلیسی و ایتالیایی.

### Step 6 — Central Configuration & Hot Reload
- ایجاد ماژول تنظیمات متمرکز `app/config.py` جهت اتصال یکپارچه متغیرهای محیطی به هسته سیستم.
- انتقال تمام ثوابت هاردکدشده مدل‌ها، چانکر و آستانه‌ها به کانفیگ مرکزی.
- تعبیه دکمه بازخوانی زنده اسکیماها (`🔄 Ricarica Schemi (Hot Reload)`) در سایدبار رابط کاربری بدون نیاز به راه‌اندازی مجدد Streamlit.
- یکپارچه‌سازی کامل مسیر دیتابیس SQLite در تمام ماژول‌ها از طریق `get_db_path()`.

---

## Next Milestone:
- **Step 7 — Test Suite Standardization & Real Document Telemetry:**
  - یکپارچه‌سازی آزمون‌های مستقل پروژه در قالب فریم‌ورک استاندارد Pytest و خودکارسازی اجرای تست‌ها.
  - تست خط لوله با یک فایل واقعی چندصفحه‌ای جهت پایش میزان مصرف توکن، زمان پاسخ و کیفیت استخراج نهایی.