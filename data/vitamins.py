# جدول الفيتامينات اليومية
VITAMINS = [
    {"name": "حمض الفوليك", "emoji": "🌿", "dose": "400 mcg", "when": "قبل الأكل صباحاً",
     "why": "يقلل تشوهات الأنبوب العصبي", "trimesters": [1, 2, 3]},
    {"name": "الحديد", "emoji": "🩸", "dose": "27 mg", "when": "مع فيتامين C على معدة فارغة",
     "why": "يمنع فقر الدم", "trimesters": [2, 3]},
    {"name": "الكالسيوم", "emoji": "🦴", "dose": "1000 mg", "when": "مع الطعام، ليس مع الحديد",
     "why": "لعظام الجنين", "trimesters": [2, 3]},
    {"name": "فيتامين D", "emoji": "☀️", "dose": "600-800 IU", "when": "مع وجبة دهنية",
     "why": "امتصاص الكالسيوم والمناعة", "trimesters": [1, 2, 3]},
    {"name": "أوميغا 3 (DHA)", "emoji": "🐟", "dose": "200-300 mg", "when": "مع الطعام",
     "why": "تطور دماغ الجنين", "trimesters": [1, 2, 3]},
    {"name": "فيتامين B12", "emoji": "💊", "dose": "2.6 mcg", "when": "مع الطعام",
     "why": "الأعصاب وتكوين الدم", "trimesters": [1, 2, 3]},
]


def get_vitamins_for_week(week: int) -> list:
    """يرجع الفيتامينات المناسبة للأسبوع"""
    if week <= 13:
        trimester = 1
    elif week <= 27:
        trimester = 2
    else:
        trimester = 3
    return [v for v in VITAMINS if trimester in v["trimesters"]]
