"""نظام تسجيل دخول بسيط بكلمات سر"""
import os
import json
import hashlib

USERS_FILE = "notes/users_db.json"


def _load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_users(data):
    os.makedirs("notes", exist_ok=True)
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _hash(password):
    """تشفير كلمة السر"""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def register_user(username: str, password: str) -> dict:
    """تسجيل مستخدمة جديدة"""
    if not username or not password:
        return {"ok": False, "error": "الاسم وكلمة السر مطلوبان"}
    if len(username) < 2:
        return {"ok": False, "error": "الاسم قصير جداً"}
    if len(password) < 4:
        return {"ok": False, "error": "كلمة السر يجب أن تكون 4 أحرف على الأقل"}

    clean = username.strip().replace("/", "_").replace(" ", "_")
    users = _load_users()

    if clean in users:
        return {"ok": False, "error": "الاسم مستخدم بالفعل"}

    users[clean] = {
        "password_hash": _hash(password),
        "created": __import__("datetime").datetime.now().isoformat(),
    }
    _save_users(users)

    # أنشئ مجلدها
    os.makedirs(f"notes/users/{clean}", exist_ok=True)

    return {"ok": True, "username": clean}


def login_user(username: str, password: str) -> dict:
    """تسجيل دخول"""
    if not username or not password:
        return {"ok": False, "error": "أدخلي الاسم وكلمة السر"}

    clean = username.strip().replace("/", "_").replace(" ", "_")
    users = _load_users()

    if clean not in users:
        return {"ok": False, "error": "الاسم أو كلمة السر خطأ"}

    if users[clean]["password_hash"] != _hash(password):
        return {"ok": False, "error": "الاسم أو كلمة السر خطأ"}

    return {"ok": True, "username": clean}


def change_password(username: str, old_password: str, new_password: str) -> dict:
    """تغيير كلمة السر"""
    check = login_user(username, old_password)
    if not check["ok"]:
        return check
    if len(new_password) < 4:
        return {"ok": False, "error": "كلمة السر الجديدة قصيرة"}

    clean = username.strip().replace("/", "_").replace(" ", "_")
    users = _load_users()
    users[clean]["password_hash"] = _hash(new_password)
    _save_users(users)
    return {"ok": True}


def list_users() -> list:
    """قائمة المستخدمات المسجلات"""
    return sorted(_load_users().keys())
