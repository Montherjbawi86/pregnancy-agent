import json
from datetime import datetime, timedelta
import os

NOTES_DIR_FALLBACK = "notes"

def _load_json(filename, notes_dir=None):
    if notes_dir is None:
        try:
            from src.tools import get_user_dir
            notes_dir = get_user_dir()
        except Exception:
            notes_dir = NOTES_DIR_FALLBACK
    path = os.path.join(notes_dir, filename)
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _get_week_data(data, days=7):
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    result = {}
    for date in sorted(data.keys()):
        if date >= cutoff:
            result[date] = data[date]
    return result


def generate_weekly_summary(last_period: str = "") -> str:
    lines = []
    lines.append("📊 **ملخص الأسبوع الماضي**")
    lines.append("")
    lines.append(f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("")

    if last_period:
        try:
            from src.tools import calculate_pregnancy_week
            info = json.loads(calculate_pregnancy_week(last_period))
            lines.append("### 🤰 الحمل")
            lines.append(f"- **الأسبوع الحالي:** {info['display_ar']}")
            lines.append(f"- **المرحلة:** {info['trimester']}")
            lines.append(f"- **موعد الولادة:** {info['due_date']}")
            lines.append(f"- **باقي:** {info['days_remaining']} يوم")
            lines.append("")
        except Exception:
            pass

    measurements = _load_json("measurements.json")
    week_m = _get_week_data(measurements, 7)
    if week_m:
        all_weights = []
        all_sys = []
        for date, entries in week_m.items():
            for e in entries:
                if e.get("weight"):
                    all_weights.append(e["weight"])
                if e.get("bp") and "/" in e["bp"]:
                    try:
                        s, d = e["bp"].split("/")
                        all_sys.append(int(s))
                    except Exception:
                        pass
        lines.append(f"### ⚖️ القياسات ({len(week_m)} يوم)")
        if all_weights:
            lines.append(f"- **عدد القياسات:** {len(all_weights)}")
            lines.append(f"- **متوسط الوزن:** {sum(all_weights)/len(all_weights):.1f} kg")
            lines.append(f"- **آخر وزن:** {all_weights[-1]:.1f} kg")
        if all_sys:
            high = [s for s in all_sys if s >= 140]
            lines.append(f"- **متوسط الضغط الانقباضي:** {sum(all_sys)/len(all_sys):.0f}")
            if high:
                lines.append(f"- ⚠️ **قياسات ضغط مرتفع:** {len(high)}")
        lines.append("")
    else:
        lines.append("### ⚖️ القياسات")
        lines.append("- لا قياسات هذا الأسبوع")
        lines.append("")

    movements = _load_json("movements.json")
    week_mov = _get_week_data(movements, 7)
    if week_mov:
        total_sessions = 0
        completed = 0
        for date, sessions in week_mov.items():
            for s in sessions:
                total_sessions += 1
                if s.get("count", 0) >= 10:
                    completed += 1
        lines.append("### 👶 حركات الجنين")
        lines.append(f"- **عدد الجلسات:** {total_sessions}")
        lines.append(f"- **جلسات مكتملة (10+):** {completed}")
        if completed < total_sessions:
            lines.append(f"- ⚠️ {total_sessions - completed} جلسة غير مكتملة")
        lines.append("")
    else:
        lines.append("### 👶 حركات الجنين")
        lines.append("- لا جلسات هذا الأسبوع")
        lines.append("")

    contractions = _load_json("contractions.json")
    week_c = _get_week_data(contractions, 7)
    if week_c:
        total = sum(len(v) for v in week_c.values())
        lines.append("### ⏱️ الانقباضات")
        lines.append(f"- **إجمالي الانقباضات:** {total}")
        lines.append("")
    else:
        lines.append("### ⏱️ الانقباضات")
        lines.append("- لا انقباضات هذا الأسبوع")
        lines.append("")

    try:
        from src.tools import get_user_dir
        notes_path = os.path.join(get_user_dir(), "notes.txt")
    except Exception:
        notes_path = os.path.join(NOTES_DIR_FALLBACK, "notes.txt")

    if os.path.exists(notes_path):
        with open(notes_path, "r", encoding="utf-8") as f:
            notes = f.read().strip()
        if notes:
            week_notes = []
            cutoff_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            for line in notes.split("\n"):
                if line.strip() and line.split(" — ")[0].strip() >= cutoff_date:
                    week_notes.append(line)
            if week_notes:
                lines.append(f"### 📝 الملاحظات ({len(week_notes)})")
                for n in week_notes[-5:]:
                    lines.append(f"- {n}")
                lines.append("")

    lines.append("### 💡 توصيات")
    lines.append("- راجعي طبيبك إذا لاحظتِ أي تغير غير طبيعي")
    lines.append("- اشربي ماء كافياً (3 لتر)")
    lines.append("- نامي على الجانب الأيسر")
    lines.append("- مارسي رياضة معتدلة")
    lines.append("")
    lines.append("⚕️ *هذا الملخص تثقيفي — استشيري طبيبك*")

    return "\n".join(lines)
