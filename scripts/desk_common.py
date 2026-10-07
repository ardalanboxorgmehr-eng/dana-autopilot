"""Shared by the Reply Desk app (desk/app.py) and the 15-minute job (scripts/dm_reply.py):
how a comment is grouped, and the auto-send settings file.

desk_auto.json (in the repo, pushed by the app) decides which easy groups the job
answers on its own. Questions and spam are never auto-sent.
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUTO = os.path.join(ROOT, "desk_auto.json")
AUTO_GROUPS = ("chat", "wants_dm")       # the only groups that may ever send on their own
STREAK_TO_UNLOCK = 20                    # unedited approvals in a row before the switch appears

THANKS = ["مرسی از کامنتت 🙏", "مرسی که نظرت رو نوشتی 🙏", "ممنون که همراهمونی ✨", "مرسی ❤️"]
QUESTION_WORDS = ["چطور", "چجوری", "چطوری", "کجا", "چرا", "چیه", "چی ", "میشه", "می‌شه", "رایگان", "پولی",
                  "قیمت", "کار نمیکنه", "کار نمی‌کنه", "باز نمیشه", "باز نمی‌شه", "کدوم", "نمیشه", "نمی‌شه",
                  "how", "where", "free", "price", "why"]
WANTS_DM = ["دایرکت", "بفرست", "بفرستید", "لینک", "ارسال", "پیوی", "پی وی", "send", "link", "dm",
            "دریافت نشد", "نرسید", "نیومد", "نیامد"]
SPAM = ["http", "www.", ".com", ".app", ".io", "فالوور", "فالو کن", "فالوم", "پیجم", "پیج ما", "تبلیغ", "سفارش",
        "خرید", "follow", "promo", "crypto", "کریپتو", "سرمایه گذاری", "سرمایه‌گذاری"]


def group_of(text, keyword="", near=None):
    """near(text, keyword) -> True when a word is a misspelling of the keyword."""
    t = (text or "").lower()
    if any(w in t for w in SPAM) or t.count("@") >= 2:
        return "spam"
    if (keyword and near and near(text, keyword)) or any(w in t for w in WANTS_DM):
        return "wants_dm"
    if "?" in t or "؟" in t or any(w in t for w in QUESTION_WORDS):
        return "question"
    return "chat"


def load_auto():
    try:
        with open(AUTO, encoding="utf-8") as f:
            a = json.load(f)
    except (OSError, ValueError):
        a = {}
    a.setdefault("groups", {})
    a.setdefault("thanks", [])
    a.setdefault("skip", [])
    return a


def save_auto(a):
    tmp = AUTO + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(a, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, AUTO)
