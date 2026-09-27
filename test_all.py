import json
from dotenv import load_dotenv
load_dotenv()

from src.tools import AVAILABLE_TOOLS
from src.rag import search_knowledge

print("=" * 50)
print("🧪 اختبار شامل")
print("=" * 50)

tests = [
    ("📅 حساب الأسبوع", lambda: AVAILABLE_TOOLS["calculate_pregnancy_week"](last_period="2026-06-01")),
    ("👶 معلومات الأسبوع", lambda: AVAILABLE_TOOLS["get_week_info"](week=20)),
    ("📅 تذكير الفحوصات", lambda: AVAILABLE_TOOLS["get_week_checklist"](week=22)),
    ("🩺 تقييم طوارئ", lambda: AVAILABLE_TOOLS["check_symptoms"](symptoms_text="نزيف غزير")),
    ("🩺 تقييم عادي", lambda: AVAILABLE_TOOLS["check_symptoms"](symptoms_text="غثيان خفيف")),
    ("⚖️ تسجيل قياس", lambda: AVAILABLE_TOOLS["log_measurement"](weight_kg=65, bp_systolic=120, bp_diastolic=80)),
    ("📋 عرض القياسات", lambda: AVAILABLE_TOOLS["get_measurements"]()),
    ("👶 بدء حركات", lambda: AVAILABLE_TOOLS["start_movement_session"]()),
    ("👶 تسجيل حركة", lambda: AVAILABLE_TOOLS["count_movement"]()),
    ("👶 ملخص حركات", lambda: AVAILABLE_TOOLS["get_movement_summary"]()),
    ("⏱️ بدء انقباض", lambda: AVAILABLE_TOOLS["start_contraction"]()),
    ("⏱️ انهاء انقباض", lambda: AVAILABLE_TOOLS["end_contraction"]()),
    ("📝 حفظ ملاحظة", lambda: AVAILABLE_TOOLS["save_note"](text="اختبار")),
    ("📝 قراءة ملاحظات", lambda: AVAILABLE_TOOLS["read_notes"]()),
    ("📚 بحث RAG", lambda: search_knowledge("الأطعمة الممنوعة في الحمل")),
    ("📚 بحث RAG 2", lambda: search_knowledge("تسمم الحمل")),
    ("📊 ملخص أسبوعي", lambda: AVAILABLE_TOOLS["get_weekly_summary"](last_period="2026-06-01")),
]

passed = 0
failed = 0

for name, fn in tests:
    try:
        result = fn()
        result_str = str(result)[:80]
        print(f"✅ {name}")
        print(f"   → {result_str}...")
        passed += 1
    except Exception as e:
        print(f"❌ {name}: {e}")
        failed += 1

print()
print("=" * 50)
print(f"✅ نجح: {passed}/{len(tests)}")
print(f"❌ فشل: {failed}/{len(tests)}")
print("=" * 50)
