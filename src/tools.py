import os
import json
from datetime import datetime, timedelta

_DEFAULT_NOTES_DIR = "notes"
os.makedirs(_DEFAULT_NOTES_DIR, exist_ok=True)

# مجلد المستخدمة الحالية — قابل للتغيير من app.py
_current_user_dir = _DEFAULT_NOTES_DIR


def set_user_dir(user_dir):
    """يحدد مجلد بيانات المستخدمة"""
    global _current_user_dir
    _current_user_dir = user_dir
    os.makedirs(user_dir, exist_ok=True)
    return user_dir


def get_user_dir():
    return _current_user_dir


# للتوافق مع الكود القديم
class _NotesDirProxy:
    def __fspath__(self):
        return _current_user_dir
    def __str__(self):
        return _current_user_dir

NOTES_DIR = _NotesDirProxy()


def _load_json(filename):
    path = os.path.join(_current_user_dir, filename)
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_json(filename, data):
    path = os.path.join(_current_user_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ============ حساب الأسبوع ============
def calculate_pregnancy_week(last_period: str) -> str:
    """يحسب أسبوع الحمل من تاريخ آخر دورة (YYYY-MM-DD)"""
    try:
        lmp = datetime.strptime(last_period, "%Y-%m-%d")
    except ValueError:
        return "خطأ: الصيغة يجب أن تكون YYYY-MM-DD (مثال: 2025-06-15)"
    today = datetime.now()
    days = (today - lmp).days
    if days < 0:
        return "خطأ: تاريخ آخر دورة في المستقبل؟"
    weeks = days // 7
    extra_days = days % 7
    if weeks > 42:
        return "الأسبوع تجاوز 42 — راجعي الطبيب فوراً"
    # موعد الولادة = آخر دورة + 280 يوم
    due = lmp + timedelta(days=280)
    days_left = (due - today).days
    return json.dumps({
        "weeks": weeks, "days": extra_days,
        "display_ar": f"الأسبوع {weeks} + {extra_days} أيام",
        "display_en": f"Week {weeks} + {extra_days} days",
        "due_date": due.strftime("%Y-%m-%d"),
        "days_remaining": days_left,
        "trimester": "الثلث الأول" if weeks <= 13 else ("الثلث الثاني" if weeks <= 27 else "الثلث الثالث"),
    }, ensure_ascii=False)

# ============ معلومات الأسبوع ============
def get_week_info(week: int) -> str:
    """يجيب بمعلومات الأسبوع من قاعدة المعرفة"""
    import sys
    sys.path.insert(0, ".")
    from data.weeks_knowledge import WEEK_INFO
    # ابحث عن أقرب أسبوع
    available = sorted(WEEK_INFO.keys())
    closest = min(available, key=lambda w: abs(w - week))
    info = WEEK_INFO[closest]
    return json.dumps({"week": closest, **info}, ensure_ascii=False)

# ============ تقييم الأعراض ============
def check_symptoms(symptoms_text: str) -> str:
    """يقيّم الأعراض ويعيد مستوى الخطورة"""
    import sys
    sys.path.insert(0, ".")
    from data.weeks_knowledge import SYMPTOMS_DB
    text = symptoms_text.lower()
    for level in ["emergency", "urgent"]:
        for symptom in SYMPTOMS_DB[level]["ar"] + SYMPTOMS_DB[level]["en"]:
            if symptom.lower() in text:
                return json.dumps({
                    "level": level,
                    "action_ar": SYMPTOMS_DB[level]["action_ar"],
                    "action_en": SYMPTOMS_DB[level]["action_en"],
                    "matched": symptom,
                }, ensure_ascii=False)
    return json.dumps({
        "level": "normal",
        "action_ar": "الأعراض تبدو ضمن الطبيعي — راقبيها، وإذا استمرت راجعي طبيبك",
        "action_en": "Symptoms seem normal — monitor, consult doctor if persistent",
    }, ensure_ascii=False)

# ============ تتبع الوزن والضغط ============
def log_measurement(weight_kg: float = None, bp_systolic: int = None, bp_diastolic: int = None, note: str = "") -> str:
    """يسجل قياسات الوزن والضغط"""
    records = _load_json("measurements.json")
    date = datetime.now().strftime("%Y-%m-%d")
    if date not in records:
        records[date] = []
    entry = {"time": datetime.now().strftime("%H:%M"), "weight": weight_kg,
             "bp": f"{bp_systolic}/{bp_diastolic}" if bp_systolic else None, "note": note}
    records[date].append(entry)
    _save_json("measurements.json", records)
    # تنبيه إذا الضغط مرتفع
    warning = ""
    if bp_systolic and bp_systolic >= 140:
        warning = " ⚠️ ضغط مرتفع! اتصلي بطبيبك"
    elif bp_systolic and bp_systolic >= 130:
        warning = " ⚠️ ضغط مرتفع قليلاً — راقبي"
    return f"✅ تم التسجيل: {date} {entry['time']}{warning}"

def get_measurements() -> str:
    """يعرض آخر القياسات"""
    records = _load_json("measurements.json")
    if not records:
        return "لا قياسات مسجلة بعد"
    lines = []
    for date in sorted(records.keys(), reverse=True)[:7]:  # آخر 7 أيام
        for entry in records[date]:
            w = f"وزن: {entry['weight']}kg" if entry.get("weight") else ""
            bp = f"ضغط: {entry['bp']}" if entry.get("bp") else ""
            lines.append(f"{date} {entry['time']} — {w} {bp}")
    return "📊 آخر القياسات:\n" + "\n".join(lines)

# ============ حفظ ملاحظات ============
def save_note(text: str) -> str:
    with open(os.path.join(NOTES_DIR, "notes.txt"), "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M')} — {text}\n")
    return f"✅ تم حفظ الملاحظة"

def read_notes() -> str:
    path = os.path.join(NOTES_DIR, "notes.txt")
    if not os.path.exists(path):
        return "لا ملاحظات محفوظة"
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip() or "الملف فارغ"


# ============ تذكير الفحوصات ============
def get_week_checklist(week: int) -> str:
    """يرجع فحوصات وتوصيات الأسبوع"""
    import sys
    sys.path.insert(0, ".")
    from data.checklists import get_checklist
    data = get_checklist(week)
    return json.dumps(data, ensure_ascii=False)


# ============ عدّاد حركات الجنين ============
def start_movement_session() -> str:
    """يبدأ جلسة عدّ حركات الجنين"""
    from datetime import datetime
    sessions = _load_json("movements.json")
    today = datetime.now().strftime("%Y-%m-%d")
    if today not in sessions:
        sessions[today] = []
    session = {
        "start": datetime.now().strftime("%H:%M:%S"),
        "end": None,
        "count": 0,
        "movements": [],
    }
    sessions[today].append(session)
    _save_json("movements.json", sessions)
    return f"✅ بدأت جلسة العدّ الساعة {session['start']}. اضغطي على 'سجّلي حركة' عند كل حركة."

def count_movement() -> str:
    """يسجل حركة واحدة"""
    from datetime import datetime
    sessions = _load_json("movements.json")
    today = datetime.now().strftime("%Y-%m-%d")
    if today not in sessions or not sessions[today]:
        return "⚠️ لا توجد جلسة نشطة. ابدئي جلسة أولاً."
    current = sessions[today][-1]
    if current["end"]:
        return "⚠️ الجلسة منتهية. ابدئي جلسة جديدة."
    current["count"] += 1
    current["movements"].append(datetime.now().strftime("%H:%M:%S"))
    # إذا وصلت 10 حركات، أغلق الجلسة
    if current["count"] >= 10:
        current["end"] = datetime.now().strftime("%H:%M:%S")
        _save_json("movements.json", sessions)
        # احسب المدة
        start = datetime.strptime(current["start"], "%H:%M:%S")
        end = datetime.strptime(current["end"], "%H:%M:%S")
        duration_min = int((end - start).total_seconds() / 60)
        return f"🎉 أكملتِ 10 حركات في {duration_min} دقيقة! هذا ممتاز — استمري بهذه المتابعة."
    _save_json("movements.json", sessions)
    remaining = 10 - current["count"]
    return f"✅ حركة #{current['count']}. باقي {remaining} حركات."

def end_movement_session() -> str:
    """ينهي الجلسة يدوياً"""
    from datetime import datetime
    sessions = _load_json("movements.json")
    today = datetime.now().strftime("%Y-%m-%d")
    if today not in sessions or not sessions[today]:
        return "⚠️ لا توجد جلسة"
    current = sessions[today][-1]
    if current["end"]:
        return "⚠️ الجلسة منتهية بالفعل"
    current["end"] = datetime.now().strftime("%H:%M:%S")
    _save_json("movements.json", sessions)
    count = current["count"]
    start = datetime.strptime(current["start"], "%H:%M:%S")
    end = datetime.strptime(current["end"], "%H:%M:%S")
    duration = int((end - start).total_seconds() / 60)
    if count < 10 and duration > 120:
        return f"🚨 سجلتِ {count} حركات فقط في {duration} دقيقة. هذا أقل من المطلوب. اتصلي بطبيبك فوراً."
    elif count < 10:
        return f"⚠️ سجلتِ {count} حركات في {duration} دقيقة. إذا لم تشعري بحركة الجنين بشكل طبيعي، اتصلي بطبيبك."
    return f"✅ أنهيتِ الجلسة: {count} حركات في {duration} دقيقة"

def get_movement_summary() -> str:
    """يعرض ملخص جلست الحركة"""
    from datetime import datetime
    sessions = _load_json("movements.json")
    if not sessions:
        return "لا توجد جلسات مسجلة بعد. ابدئي جلسة عدّ الحركات."
    lines = ["📊 ملخص جلسات حركة الجنين:"]
    for date in sorted(sessions.keys(), reverse=True)[:5]:
        for s in sessions[date]:
            end = s.get("end") or "جارية"
            lines.append(f"  {date}: {s['count']} حركات ({s['start']} - {end})")
    return "\n".join(lines)


# ============ عدّاد انقباضات المخاض ============
def start_contraction() -> str:
    """يبدأ تسجيل انقباضة"""
    from datetime import datetime
    data = _load_json("contractions.json")
    today = datetime.now().strftime("%Y-%m-%d")
    if today not in data:
        data[today] = []
    contraction = {
        "start": datetime.now().strftime("%H:%M:%S"),
        "end": None,
        "duration_sec": 0,
        "gap_from_previous_sec": 0,
    }
    if data[today]:
        last = data[today][-1]
        if last.get("end"):
            prev_end = datetime.strptime(last["end"], "%H:%M:%S")
            now = datetime.now()
            gap = int((now - prev_end).total_seconds())
            contraction["gap_from_previous_sec"] = gap
    data[today].append(contraction)
    _save_json("contractions.json", data)
    return f"⏱️ بدأت انقباضة الساعة {contraction['start']}. قولي 'انتهت الانقباضة' عند توقفها."

def end_contraction() -> str:
    """ينهي انقباضة"""
    from datetime import datetime
    data = _load_json("contractions.json")
    today = datetime.now().strftime("%Y-%m-%d")
    if today not in data or not data[today]:
        return "⚠️ لا انقباضة نشطة"
    current = data[today][-1]
    if current.get("end"):
        return "⚠️ الانقباضة منتهية"
    current["end"] = datetime.now().strftime("%H:%M:%S")
    start = datetime.strptime(current["start"], "%H:%M:%S")
    end = datetime.strptime(current["end"], "%H:%M:%S")
    duration = int((end - start).total_seconds())
    current["duration_sec"] = duration
    _save_json("contractions.json", data)
    # تحليل
    gap = current.get("gap_from_previous_sec", 0)
    msg = f"✅ انتهت الانقباضة. المدة: {duration} ثانية."
    if gap > 0:
        msg += f" التباعد عن السابقة: {gap // 60} دقيقة."
    return msg

def analyze_contractions() -> str:
    """يحلل نمط الانقباضات ويعطي توصية"""
    from datetime import datetime
    data = _load_json("contractions.json")
    today = datetime.now().strftime("%Y-%m-%d")
    if today not in data or len(data[today]) < 3:
        return "ℹ️ نحتاج 3 انقباضات على الأقل لتحليل النمط"
    recent = [c for c in data[today] if c.get("end")][-6:]
    if len(recent) < 3:
        return "ℹ️ نحتاج 3 انقباضات منتهية على الأقل"
    durations = [c["duration_sec"] for c in recent]
    gaps = [c["gap_from_previous_sec"] for c in recent if c["gap_from_previous_sec"] > 0]
    avg_dur = sum(durations) // len(durations)
    avg_gap = sum(gaps) // len(gaps) if gaps else 0

    result = {
        "count": len(recent),
        "avg_duration_sec": avg_dur,
        "avg_duration_display": f"{avg_dur // 60} د {avg_dur % 60} ث",
        "avg_gap_min": avg_gap // 60 if avg_gap else 0,
        "contractions": [{"start": c["start"], "end": c["end"], "duration": c["duration_sec"], "gap_min": c["gap_from_previous_sec"] // 60} for c in recent],
    }

    # قاعدة 5-1-1
    if avg_gap and avg_gap <= 300 and avg_dur >= 60:
        result["recommendation"] = "🚨 الانقباضات منتظمة (كل 5 دقائق أو أقل) وتستمر أكثر من دقيقة → اذهبي للمستشفى الآن!"
    elif avg_gap and avg_gap <= 600:
        result["recommendation"] = "⚠️ الانقباضات تقترب. استعدي، واتصلي بطبيبك."
    else:
        result["recommendation"] = "✅ الانقباضات متباعدة. راقبي وارتاحي."

    return json.dumps(result, ensure_ascii=False)

def get_contractions_summary() -> str:
    """ملخص انقباضات اليوم"""
    data = _load_json("contractions.json")
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    if today not in data or not data[today]:
        return "لا انقباضات مسجلة اليوم"
    lines = [f"📊 انقباضات اليوم ({len(data[today])}):"]
    for c in data[today]:
        end = c.get("end") or "جارية"
        lines.append(f"  {c['start']} - {end} ({c['duration_sec']} ث)")
    return "\n".join(lines)


# ============ تقرير PDF ============
def export_pdf_report(patient_name: str = "", last_period: str = "") -> str:
    """يولّد تقرير PDF"""
    import sys
    sys.path.insert(0, ".")
    from src.report import generate_report
    return generate_report(patient_name, last_period)


# ============ الملخص الأسبوعي ============
def get_weekly_summary(last_period: str = "") -> str:
    import sys
    sys.path.insert(0, ".")
    from src.weekly_summary import generate_weekly_summary
    return generate_weekly_summary(last_period)

# ============ سجل الأدوات ============
TOOLS_DEFINITIONS = [
    {"type": "function", "function": {"name": "calculate_pregnancy_week", "description": "يحسب أسبوع الحمل وموعد الولادة من تاريخ آخر دورة (YYYY-MM-DD)", "parameters": {"type": "object", "properties": {"last_period": {"type": "string"}}, "required": ["last_period"]}}},
    {"type": "function", "function": {"name": "get_week_info", "description": "يعطي معلومات مفصلة عن أسبوع حمل معين (حجم الجنين، التطور، نصائح)", "parameters": {"type": "object", "properties": {"week": {"type": "integer"}}, "required": ["week"]}}},
    {"type": "function", "function": {"name": "check_symptoms", "description": "يقيّم الأعراض ويخبر إن كانت طبيعية أو تستدعي طبيباً أو طوارئ", "parameters": {"type": "object", "properties": {"symptoms_text": {"type": "string"}}, "required": ["symptoms_text"]}}},
    {"type": "function", "function": {"name": "log_measurement", "description": "يسجل الوزن والضغط", "parameters": {"type": "object", "properties": {"weight_kg": {"type": "number"}, "bp_systolic": {"type": "integer"}, "bp_diastolic": {"type": "integer"}, "note": {"type": "string"}}}}},
    {"type": "function", "function": {"name": "get_measurements", "description": "يعرض آخر القياسات المسجلة", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "save_note", "description": "يحفظ ملاحظة", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "read_notes", "description": "يقرأ الملاحظات", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "search_knowledge", "description": "يبحث في قاعدة المعرفة الطبية الموثوقة (WHO/ACOG/NHS) عن معلومات حول: التغذية، الرياضة، الفحوصات، علامات الخطر، تطور الجنين. استخدمها قبل الإجابة على أي سؤال طبي.", "parameters": {"type": "object", "properties": {"query": {"type": "string", "description": "السؤال أو الموضوع"}}, "required": ["query"]}}},
    {"type": "function", "function": {"name": "get_week_checklist", "description": "يرجع فحوصات وتوصيات وعلامات خطر الأسبوع الحالي من الحمل. استخدمها دائماً عندما تعرف أسبوع المستخدمة.", "parameters": {"type": "object", "properties": {"week": {"type": "integer", "description": "أسبوع الحمل (1-42)"}}, "required": ["week"]}}},
    {"type": "function", "function": {"name": "start_movement_session", "description": "يبدأ جلسة عدّ حركات الجنين. استخدميه عندما تطلب المستخدمة البدء بعدّ الحركات", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "count_movement", "description": "يسجل حركة واحدة للجنين. استخدميه عند كل طلب 'سجلي حركة'", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "end_movement_session", "description": "ينهي جلسة عدّ الحركات ويعطي النتيجة", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_movement_summary", "description": "يعرض ملخص جلسات عدّ حركات الجنين", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "start_contraction", "description": "يبدأ تسجيل انقباضة مخاض", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "end_contraction", "description": "ينهي انقباضة", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "analyze_contractions", "description": "يحلل نمط الانقباضات ويعطي توصية (اذهبي للمستشفى أم لا)", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_contractions_summary", "description": "ملخص انقباضات اليوم", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "export_pdf_report", "description": "يولّد تقرير PDF للطبيب يحتوي أسبوع الحمل والقياسات وحركات الجنين والانقباضات والملاحظات. استخدميه عندما تطلب المستخدمة تقريراً أو ملخصاً للطبيب", "parameters": {"type": "object", "properties": {"patient_name": {"type": "string", "description": "اسم المستخدمة (اختياري)"}, "last_period": {"type": "string", "description": "تاريخ آخر دورة YYYY-MM-DD (اختياري)"}}}}},
    {"type": "function", "function": {"name": "get_weekly_summary", "description": "يولّد ملخصاً أسبوعياً شاملاً لكل بيانات المستخدمة (القياسات، الحركات، الانقباضات، الملاحظات). استخدميه عندما تطلب المستخدمة ملخصاً.", "parameters": {"type": "object", "properties": {"last_period": {"type": "string", "description": "تاريخ آخر دورة YYYY-MM-DD (اختياري)"}}}}},
]

AVAILABLE_TOOLS = {
    "calculate_pregnancy_week": calculate_pregnancy_week,
    "get_week_info": get_week_info,
    "check_symptoms": check_symptoms,
    "log_measurement": log_measurement,
    "get_measurements": get_measurements,
    "save_note": save_note,
    "read_notes": read_notes,
    "get_week_checklist": get_week_checklist,
    "get_weekly_summary": get_weekly_summary,
    "start_movement_session": start_movement_session,
    "count_movement": count_movement,
    "end_movement_session": end_movement_session,
    "get_movement_summary": get_movement_summary,
    "start_contraction": start_contraction,
    "end_contraction": end_contraction,
    "analyze_contractions": analyze_contractions,
    "get_contractions_summary": get_contractions_summary,
    "export_pdf_report": export_pdf_report,
}
