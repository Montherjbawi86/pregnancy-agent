import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

NOTES_DIR = "notes"
REPORT_DIR = "reports"
os.makedirs(REPORT_DIR, exist_ok=True)

# حاول تسجيل خط عربي إن وُجد
ARABIC_FONT = "Helvetica"
for candidate in [
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/Library/Fonts/Arial Unicode.ttf",
    "/System/Library/Fonts/ArialHB.ttc",
]:
    if os.path.exists(candidate):
        try:
            pdfmetrics.registerFont(TTFont("Arabic", candidate))
            ARABIC_FONT = "Arabic"
            break
        except Exception:
            continue


def _load_json(filename):
    path = os.path.join(NOTES_DIR, filename)
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _read_notes():
    path = os.path.join(NOTES_DIR, "notes.txt")
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def generate_report(patient_name: str = "", last_period: str = "") -> str:
    """يولّد PDF يحتوي كل بيانات المستخدمة"""
    from src.tools import calculate_pregnancy_week

    filename = f"تقرير-{datetime.now().strftime('%Y%m%d-%H%M')}.pdf"
    path = os.path.join(REPORT_DIR, filename)

    doc = SimpleDocTemplate(path, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("title", parent=styles["Title"], fontName=ARABIC_FONT, fontSize=20, alignment=2)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontName=ARABIC_FONT, fontSize=14, alignment=2, textColor=colors.HexColor("#1f77b4"))
    normal = ParagraphStyle("normal", parent=styles["Normal"], fontName=ARABIC_FONT, fontSize=11, alignment=2, leading=16)

    story = []
    story.append(Paragraph("🤰 تقرير متابعة الحمل", title_style))
    story.append(Paragraph(f"التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}", normal))
    if patient_name:
        story.append(Paragraph(f"الاسم: {patient_name}", normal))
    story.append(Spacer(1, 0.5*cm))

    # معلومات الحمل
    if last_period:
        story.append(Paragraph("📅 معلومات الحمل", h2))
        week_info = calculate_pregnancy_week(last_period)
        try:
            info = json.loads(week_info)
            story.append(Paragraph(f"آخر دورة: {last_period}", normal))
            story.append(Paragraph(f"الأسبوع الحالي: {info['display_ar']}", normal))
            story.append(Paragraph(f"موعد الولادة المتوقع: {info['due_date']}", normal))
            story.append(Paragraph(f"الأيام المتبقية: {info['days_remaining']}", normal))
            story.append(Paragraph(f"المرحلة: {info['trimester']}", normal))
        except Exception:
            story.append(Paragraph(week_info, normal))
        story.append(Spacer(1, 0.5*cm))

    # القياسات
    measurements = _load_json("measurements.json")
    if measurements:
        story.append(Paragraph("⚖️ القياسات (آخر 10)", h2))
        rows = [["التاريخ", "الوقت", "الوزن (kg)", "الضغط", "ملاحظة"]]
        count = 0
        for date in sorted(measurements.keys(), reverse=True):
            for entry in measurements[date]:
                if count >= 10:
                    break
                rows.append([date, entry.get("time", ""), str(entry.get("weight") or "-"),
                             str(entry.get("bp") or "-"), entry.get("note", "")[:30]])
                count += 1
            if count >= 10:
                break
        t = Table(rows, colWidths=[2.5*cm, 1.8*cm, 2.2*cm, 2.5*cm, 5*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f77b4")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, -1), ARABIC_FONT),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.5*cm))

    # حركات الجنين
    movements = _load_json("movements.json")
    if movements:
        story.append(Paragraph("👶 حركات الجنين (آخر 5 جلسات)", h2))
        rows = [["التاريخ", "البداية", "النهاية", "عدد الحركات"]]
        count = 0
        for date in sorted(movements.keys(), reverse=True):
            for s in movements[date]:
                if count >= 5:
                    break
                rows.append([date, s["start"], s.get("end") or "جارية", str(s["count"])])
                count += 1
            if count >= 5:
                break
        t = Table(rows, colWidths=[3*cm, 3*cm, 3*cm, 3*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2ca02c")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, -1), ARABIC_FONT),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.5*cm))

    # الانقباضات
    contractions = _load_json("contractions.json")
    if contractions:
        story.append(Paragraph("⏱️ انقباضات المخاض (آخر جلسة)", h2))
        last_date = sorted(contractions.keys())[-1]
        rows = [["البداية", "النهاية", "المدة (ث)"]]
        for c in contractions[last_date][-10:]:
            rows.append([c["start"], c.get("end") or "جارية", str(c["duration_sec"])])
        t = Table(rows, colWidths=[3*cm, 3*cm, 3*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d62728")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, -1), ARABIC_FONT),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.5*cm))

    # الملاحظات
    notes = _read_notes()
    if notes:
        story.append(Paragraph("📝 الملاحظات", h2))
        for line in notes.split("\n")[-15:]:
            story.append(Paragraph(line, normal))
        story.append(Spacer(1, 0.5*cm))

    # تذييل
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("⚕️ هذا التقرير تثقيفي — ليس بديلاً عن الفحص الطبي", ParagraphStyle("foot", parent=normal, textColor=colors.grey, fontSize=9)))

    doc.build(story)
    return f"✅ تم إنشاء التقرير: {path}"
