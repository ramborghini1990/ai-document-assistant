from typing import Dict, Any, List

# اسکیمای سررسیدها، الزامات قانونی و معاینات (Scadenziario ISO 14001)
SCADENZIARIO_SCHEMA = {
    "name": "scadenziario",
    "description": "Compliance deadlines, statutory obligations, medical visits, and audit schedules.",
    "fields": [
        "tema",           # موضوع یا حوزه (مثلاً ایمنی، محیط زیست، معاینات پزشکی)
        "adempimento",    # شرح الزام قانونی یا فعالیت
        "scadenza",       # تاریخ سررسید یا انقضا
        "preavviso",      # دوره پیش‌آگاهی یا تکرار
        "responsabile",   # شخص یا واحد مسئول
        "stato",          # وضعیت (مثلاً Programمتنوع, Concluso, In corso)
        "evidenza_note",  # مدارک اثباتی، شماره پروتکل یا توضیحات
        "allerta"         # هشدار یا درجه فوریت
    ]
}

# اسکیمای وسایل نقلیه و سوابق مصرف سوخت (Mezzi e Consumi Carburante)
VEHICLE_FUEL_SCHEMA = {
    "name": "vehicle_fuel",
    "description": "Vehicle fleet records, license plates, technical inspections, and fuel consumption.",
    "fields": [
        "targa",          # پلاک خودرو
        "modello",        # مدل یا نوع وسیله نقلیه
        "scadenza_revisione", # تاریخ انقضای معاینه فنی / بازرسی
        "periodo",        # دوره گزارش‌گیری (ماه/سال)
        "litri",          # حجم سوخت بر حسب لیتر
        "chilometri",     # مسافت پیموده شده بر حسب کیلومتر
        "consumo_l_100km" # نرخ مصرف در ۱۰۰ کیلومتر
    ]
}

# اسکیمای عمومی برای قراردادها، مجوزها و سایر اسناد اداری
GENERAL_SCHEMA = {
    "name": "general_document",
    "description": "General contracts, administrative authorizations, and company forms.",
    "fields": [
        "titolo_documento",
        "ente_emittente",
        "numero_protocollo",
        "data_emissione",
        "data_scadenza",
        "oggetto_sintesi"
    ]
}

AVAILABLE_SCHEMAS: Dict[str, Dict[str, Any]] = {
    "scadenziario": SCADENZIARIO_SCHEMA,
    "vehicle_fuel": VEHICLE_FUEL_SCHEMA,
    "general": GENERAL_SCHEMA
}