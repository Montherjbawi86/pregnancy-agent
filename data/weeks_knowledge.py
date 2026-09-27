# معلومات الأسابيع — مصادر: WHO, ACOG, NHS
# للتثقيف الصحي فقط — ليست بديلاً عن الطبيب

TRIMESTERS = {
    (1, 13): {"ar": "الثلث الأول", "en": "First Trimester"},
    (14, 27): {"ar": "الثلث الثاني", "en": "Second Trimester"},
    (28, 40): {"ar": "الثلث الثالث", "en": "Third Trimester"},
}

WEEK_INFO = {
    4: {"size_ar": "حجم بذرة الخشخاش", "size_en": "Poppy seed", "len_cm": 0.1,
        "dev_ar": "انغراس البويضة في الرحم، بداية تكوّن المشيمة",
        "dev_en": "Implantation, placenta begins forming",
        "tip_ar": "ابدئي بحمض الفوليك 400 ميكروغرام يومياً", "tip_en": "Start folic acid 400 mcg daily"},
    6: {"size_ar": "حجم حبة العدس", "size_en": "Lentil", "len_cm": 0.6,
        "dev_ar": "بداية نبض القلب، تكوّن الأنبوب العصبي",
        "dev_en": "Heart starts beating, neural tube forms",
        "tip_ar": "تجنبي الكافيين الزائد والتدخين", "tip_en": "Avoid excess caffeine and smoking"},
    8: {"size_ar": "حجم حبة العنب", "size_en": "Grape", "len_cm": 1.6,
        "dev_ar": "تكوّن الأصابع، العينان، الأذنان",
        "dev_en": "Fingers, eyes, ears forming",
        "tip_ar": "الغثيان الصباحي طبيعي — كلي وجبات صغيرة متكررة", "tip_en": "Morning sickness normal — eat small frequent meals"},
    10: {"size_ar": "حجم حبة الفراولة", "size_en": "Strawberry", "len_cm": 3.1,
        "dev_ar": "اكتمال الأعضاء الحيوية الأساسية",
        "dev_en": "Vital organs complete",
        "tip_ar": "وقت جيد لأول تحليل شامل", "tip_en": "Good time for first comprehensive blood test"},
    12: {"size_ar": "حجم حبة الليمون", "size_en": "Lime", "len_cm": 5.4,
        "dev_ar": "الحركة تبدأ (قد لا تشعرين بعد)",
        "dev_en": "Movement begins (may not feel yet)",
        "tip_ar": "فحص الشفافية القفوية (NT scan) — من 11 إلى 14 أسبوعاً", "tip_en": "NT scan — weeks 11 to 14"},
    16: {"size_ar": "حجم حبة الأفوكادو", "size_en": "Avocado", "len_cm": 11.6,
        "dev_ar": "قد تشعرين بالحركة الأولى (Quickening)",
        "dev_en": "May feel first movement (Quickening)",
        "tip_ar": "تحليل السكر (Glucose test) قريباً", "tip_en": "Glucose test coming up"},
    20: {"size_ar": "حجم حبة الموز", "size_en": "Banana", "len_cm": 25.6,
        "dev_ar": "اكتمال نصف الحمل، الجنين يسمع الأصوات",
        "dev_en": "Halfway point, fetus hears sounds",
        "tip_ar": "فحص التشوهات (Anomaly scan) — أهم فحص في الحمل", "tip_en": "Anomaly scan — the most important scan"},
    24: {"size_ar": "حجم كوز ذرة", "size_en": "Corn", "len_cm": 30.0,
        "dev_ar": "الرئتان تتطوران، العينان تفتحان",
        "dev_en": "Lungs developing, eyes open",
        "tip_ar": "تحليل سكر الحمل ضروري الآن", "tip_en": "Gestational diabetes test essential now"},
    28: {"size_ar": "حجم حبة باذنجان", "size_en": "Eggplant", "len_cm": 37.6,
        "dev_ar": "الثلث الثالث — الجنين يزداد وزناً بسرعة",
        "dev_en": "Third trimester — rapid weight gain",
        "tip_ar": "ابدئي عدّ حركات الجنين يومياً", "tip_en": "Start counting fetal movements daily"},
    32: {"size_ar": "حجم حبة جوز الهند", "size_en": "Coconut", "len_cm": 42.4,
        "dev_ar": "الجنين يستعد للولادة، يتخذ وضعية الرأس",
        "dev_en": "Baby preparing for birth, head-down position",
        "tip_ar": "زيارات الطبيب كل أسبوعين", "tip_en": "Doctor visits every 2 weeks"},
    36: {"size_ar": "حجم رأس الخس", "size_en": "Romaine lettuce", "len_cm": 47.4,
        "dev_ar": "الرئتان مكتملتان تقريباً",
        "dev_en": "Lungs nearly mature",
        "tip_ar": "زيارات أسبوعية، جهزي حقيبة الولادة", "tip_en": "Weekly visits, prepare hospital bag"},
    40: {"size_ar": "حجم حبة بطيخ صغيرة", "size_en": "Small watermelon", "len_cm": 51.2,
        "dev_ar": "اكتمل الحمل — الوقت المتوقع للولادة",
        "dev_en": "Full term — expected due date",
        "tip_ar": "راقبي علامات المخاض: انقباضات منتظمة، نزول الماء", "tip_en": "Watch labor signs: regular contractions, water breaking"},
}

# أعراض تحدد مستوى الخطورة
SYMPTOMS_DB = {
    "emergency": {
        "ar": ["نزيف مهبلي غزير", "تشنجات", "ألم بطن حاد", "توقف حركة الجنين", "صداع شديد مع ضبابية الرؤية",
               "ضغط دم 140/90 أو أعلى", "ارتفاع حرارة فوق 39", "قيء مستمر لا يتوقف", "تسرب سائل من المهبل قبل الأسبوع 37"],
        "en": ["heavy vaginal bleeding", "seizures", "severe abdominal pain", "no fetal movement",
               "severe headache with blurred vision", "BP 140/90 or higher", "fever above 39C",
               "continuous vomiting", "water breaking before 37 weeks"],
        "action_ar": "🚨 اذهبي للطوارئ فوراً — هذا قد يكون حالة خطيرة",
        "action_en": "🚨 Go to ER immediately — this may be serious",
    },
    "urgent": {
        "ar": ["نزيف خفيف", "ألم بطن مستمر", "صداع مستمر", "تورم مفاجئ في اليدين والوجه",
               "حرقة بول", "إفرازات غير طبيعية", "انقباضات قبل الأسبوع 37"],
        "en": ["light bleeding", "persistent abdominal pain", "persistent headache",
               "sudden swelling of hands/face", "burning urination", "abnormal discharge",
               "contractions before 37 weeks"],
        "action_ar": "⚠️ اتصلي بطبيبك اليوم — لا تتأخري",
        "action_en": "⚠️ Call your doctor today — do not delay",
    },
}

DISCLAIMER_AR = "⚕️ *هذه معلومات تثقيفية فقط — ليست بديلاً عن استشارة الطبيب. راجعي طبيبك في كل قرار.*"
DISCLAIMER_EN = "⚕️ *Educational info only — not a substitute for medical advice. Consult your doctor for every decision.*"
