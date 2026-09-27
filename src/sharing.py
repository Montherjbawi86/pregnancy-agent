"""نظام مشاركة بيانات الحمل مع الزوج/العائلة"""
import os
import json
import hashlib
from datetime import datetime

SHARE_DB = "notes/sharing_db.json"


def _load_shares():
    """يحمّل قاعدة بيانات المشاركات"""
    if not os.path.exists(SHARE_DB):
        return {}
    with open(SHARE_DB, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_shares(data):
    """يحفظ قاعدة البيانات"""
    os.makedirs("notes", exist_ok=True)
    with open(SHARE_DB, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def generate_share_code(username: str) -> str:
    """يولّد رمز فريد للمستخدمة"""
    code = hashlib.md5(username.encode()).hexdigest()[:8].upper()
    return code


def enable_sharing(username: str, partner_name: str = "", permissions: dict = None) -> str:
    """يفعّل المشاركة ويعيد الرمز"""
    if permissions is None:
        permissions = {
            "week": True,
            "due_date": True,
            "trimester": True,
            "measurements": False,
            "journal": False,
            "letters": False,
            "ultrasounds": False,
            "movements": False,
        }

    code = generate_share_code(username)
    shares = _load_shares()
    shares[code] = {
        "username": username,
        "partner_name": partner_name,
        "enabled": True,
        "permissions": permissions,
        "created": datetime.now().isoformat(),
        "views": [],  # سجل المشاهدات
    }
    _save_shares(shares)
    return code


def disable_sharing(code: str):
    """يعطّل المشاركة"""
    shares = _load_shares()
    if code in shares:
        shares[code]["enabled"] = False
        _save_shares(shares)
        return True
    return False


def update_permissions(code: str, permissions: dict):
    """يحدّث الصلاحيات"""
    shares = _load_shares()
    if code in shares:
        shares[code]["permissions"] = permissions
        _save_shares(shares)
        return True
    return False


def get_share_by_code(code: str) -> dict:
    """يجد مشاركة بالرمز"""
    shares = _load_shares()
    return shares.get(code.upper())


def log_view(code: str, viewer_name: str = "زائر"):
    """يسجّل مشاهدة"""
    shares = _load_shares()
    if code in shares:
        shares[code]["views"].append({
            "viewer": viewer_name,
            "time": datetime.now().isoformat(),
        })
        # احتفظ بآخر 50 مشاهدة فقط
        shares[code]["views"] = shares[code]["views"][-50:]
        _save_shares(shares)


def get_views(code: str) -> list:
    """يعيد سجل المشاهدات"""
    share = get_share_by_code(code)
    if share:
        return share.get("views", [])
    return []


def get_partner_data(username: str, permissions: dict) -> dict:
    """يجمع بيانات الزوجة حسب الصلاحيات"""
    data = {}
    user_dir = f"notes/users/{username}"

    # أسبوع الحمل
    if permissions.get("week") or permissions.get("due_date") or permissions.get("trimester"):
        try:
            from src.tools import calculate_pregnancy_week
            settings_file = os.path.join(user_dir, "share_settings.json")
            lmp = "2026-06-01"
            if os.path.exists(settings_file):
                with open(settings_file) as f:
                    s = json.load(f)
                lmp = s.get("lmp_date", lmp)
            info = json.loads(calculate_pregnancy_week(lmp))
            data["week_info"] = {
                "weeks": info.get("weeks"),
                "days": info.get("days"),
                "due_date": info.get("due_date"),
                "days_remaining": info.get("days_remaining"),
                "trimester": info.get("trimester"),
            }
        except Exception:
            pass

    # القياسات
    if permissions.get("measurements"):
        try:
            from src.tools import _load_json
            data["measurements"] = _load_json("measurements.json")
        except Exception:
            pass

    # اليوميات
    if permissions.get("journal"):
        try:
            journal_file = os.path.join(user_dir, "journal", "entries.json")
            if os.path.exists(journal_file):
                with open(journal_file, "r", encoding="utf-8") as f:
                    data["journal"] = json.load(f)
        except Exception:
            pass

    # الرسائل
    if permissions.get("letters"):
        try:
            letters_file = os.path.join(user_dir, "letters", "letters.json")
            if os.path.exists(letters_file):
                with open(letters_file, "r", encoding="utf-8") as f:
                    data["letters"] = json.load(f)
        except Exception:
            pass

    # صور السونار
    if permissions.get("ultrasounds"):
        try:
            us_dir = os.path.join(user_dir, "ultrasounds")
            if os.path.exists(us_dir):
                imgs = [f for f in os.listdir(us_dir) if f.lower().endswith(("jpg", "jpeg", "png", "webp"))]
                data["ultrasounds"] = imgs
        except Exception:
            pass

    return data
