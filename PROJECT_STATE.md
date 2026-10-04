# Project State Tracking — Modular Platform Architecture (v2.2)

## Current Status
- **Current Milestone:** Infrastructure Stabilization & Step 4 Completed → Moving to Step 5 (Dynamic Schema Registry & Extensibility)
- **System Architecture:** Modular Multi-Tenant Document Intelligence Platform
- **Stability Status:** 100% Operational, Zero-Hallucination Verified, Fully Backward Compatible.

---

## Completed Milestones (v2.2 Platform Evolution):

### Phase 0–27 (Baseline MVP & Multimodal Core)
- پیاده‌سازی پایپ‌لاین RAG بدون فریم‌ورک‌های واسط (Framework-Free) با پایتون خالص، Google GenAI، ChromaDB و SQLite.
- پشتیبانی چندوجهی و چندفرمت: فایل‌های PDF دیجیتال و اسکن‌شده (PyMuPDF OCR)، اسناد Word (`.docx`)، تصاویر (Gemini Vision) و دفاتر کاری اکسل (`.xlsx`/`.xls`) با نگاشت ساختاریافته شیت‌ها و سطرها[cite: 1, 2].
- استخراج داده‌های ممیزی سیستم مدیریت زیست‌محیطی ISO 14001 و تولید گزارش‌های سازمانی اکسل و ورد با امضاهای پویا و متادیتای شرکت[cite: 1, 2].

### Step 1 — Modular Schema Registry
- انتقال کامل منطق دامنه به فایل‌های ساختاریافته در مسیر `schemas/*.json` (`iso_14001.json`, `fleet_fuel_expenses.json`, `general_documents.json`)[cite: 1, 2].
- پیاده‌سازی رجیستری پویا در `app/extraction/registry.py` همراه با اعتبارسنجی نوع داده‌ها و محاسبات ریاضی کاملاً قطعی (Whitelist Calculators) در `app/extraction/calculators.py`[cite: 1, 2].
- تبدیل `app/extraction/schemas.py` به یک Shim سازگار رو به عقب برای حفظ سلامت تست‌های قدیمی[cite: 1, 2].

### Step 2 — UI Module Switcher & Review Roundtrip
- افزودن انتخابگر دامنه‌های عملیاتی در نوار کناری رابط کاربری (`🧩 Modulo / Standard Operativo`)[cite: 1].
- پیاده‌سازی موتور چرخه بازبینی انسانی (`app/extraction/review.py`): ثبت ویرایش‌های دستی `st.data_editor` با وضعیت `EDITED` و محاسبه مجدد خودکار فرمول‌ها بدون ایجاد توهم[cite: 1, 2].
- فیلتر بازیابی معنایی بر اساس اسناد سشن فعال و اعمال پاک‌سازی زباله‌های برداری[cite: 1, 2].

### Step 3 — Scoped Exporters (Cross-Module Isolation)
- تفکیک قطعی ماژول‌ها در خروجی‌های رسمی اکسل و ورد از طریق `app/reporting/common.py` (`resolve_scope`)[cite: 1, 2].
- تضمین عدم نفوذ داده‌ها و شیت‌های ماژول‌های دیگر در گزارش نهایی (رفع آلودگی بین‌اسکیمایی)[cite: 1, 2].
- اعتبارسنجی ۱۰۰٪ موفق با تست اختصاصی `test_scoped_reports.py`[cite: 1, 2].

### Step 4 — Deadline Alerts Engine & Monitoring
- راه‌اندازی موتور قطعی استخراج سررسیدهای قانونی و ممیزی (`app/alerts/deadlines.py`) با شناسه‌های یکتای UUID5[cite: 1, 2].
- موتور اسکن زمان‌بندی‌شده و دسته‌بندی آستانه‌های بحرانی (`app/alerts/scanner.py`) بر اساس روزهای باقی‌مانده[cite: 1, 2].
- لایه پایداری SQLite (`app/alerts/store.py`) با سازوکار ضدهرزنامه و جلوگیری از ارسال تکراری (Deduplication)[cite: 1, 2].
- دیسپچر اعلان‌ها و کلاینت‌های استاندارد SMTP Email و Twilio SMS (`app/alerts/dispatcher.py`, `app/alerts/notifiers.py`)[cite: 1, 2].
- اضافه شدن تب «⏰ Scadenze & Monitoraggio» در UI و نقطه ورود CLI مستقل `app/alerts/run.py`[cite: 1, 2].

### Infrastructure & Architectural Bugfix Patches (Current Session)
1. **RAG Page Number & Provenance Patch:**
   - اصلاح قرارداد خروجی `app/rag/retriever.py` برای برگرداندن فیلدهای `page_number` و `document_name` در سطح ریشه دیکشنری و درون `metadata`[cite: 1, 2].
   - رفع باگ نمایش `N/A` برای شماره صفحات در `app/ai/prompts.py` و پاس شدن کامل `test_retriever.py`[cite: 1, 2].
2. **Database Unified Path & Signature Alignment Patch:**
   - یکپارچه‌سازی مسیر فایل پایگاه داده در `app/database/database.py` از طریق متغیر محیطی `ASSISTANT_DB_PATH` (پیش‌فرض: `assistant.db`)[cite: 1, 2].
   - افزودن پشتیبانی اختیاری از `document_id` در `create_conversation` و بازگرداندن کلید `id` در تاریخچه پیام‌ها جهت پاس شدن کامل `test_database.py`[cite: 1, 2].
3. **ChromaDB Session Concurrency & Entrypoint Patch:**
   - حذف دستور مخرب `clear_chroma_collection()` از راه‌اندازی سشن‌های جدید در `streamlit_app.py` برای محافظت از وکتورهای سایر نشست‌ها[cite: 1, 2].
   - پیاده‌سازی پاک‌سازی ایزوله بر اساس اسناد حذف‌شده و افزودن دکمه کنترل دستی بازنشانی وکتورها برای ادمین[cite: 1].
   - افزودن مسیردهی خودکار `sys.path` و فراخوانی صریح `render_ui()` در انتهای `streamlit_app.py` جهت اجرای بدون خطای وب‌اپلیکیشن[cite: 1].

---

## Next Milestone:
- **Step 5 — Dynamic Schema Registry Completion & Extensibility:**
  - پیکربندی پویای مدل‌ها و کلیدهای هوش مصنوعی بر اساس فایل‌های اسکیما بدون نیاز به دستکاری کدهای پایتون.
  - استانداردسازی و رفع ابهام در تبدیل اعداد اعشاری و هزارگان ایتالیایی در `normalize_number`[cite: 2].
  - یکپارچه‌سازی تست‌های اسکریپتی به یک فریم‌ورک تست جامع و خودکار (Pytest Suite)[cite: 2].