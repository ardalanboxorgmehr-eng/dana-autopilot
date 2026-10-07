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


# ------------------------------------------------------------------ sealed files (added 7 Oct 2026)
# The repo is public, so Instagram DMs never go into it in plain text. The job
# writes state/desk_inbox.enc and the Mac writes desk_out.enc, both sealed with
# DESK_KEY (a GitHub secret, and desk/local.json "dmkey" on the Mac).
# Construction: keystream = HMAC-SHA256(enc_key, nonce || counter), tag =
# HMAC-SHA256(mac_key, nonce || ciphertext). Stdlib only.
import base64 as _b64, hashlib as _hl, hmac as _hm, secrets as _sec

INBOX_ENC = os.path.join(ROOT, "state", "desk_inbox.enc")
OUTBOX_ENC = os.path.join(ROOT, "desk_out.enc")
IDEAS_QUEUE = os.path.join(ROOT, "ideas_queue.json")


def _keys(key):
    k = key.encode() if isinstance(key, str) else key
    return (_hm.new(k, b"desk-enc", _hl.sha256).digest(), _hm.new(k, b"desk-mac", _hl.sha256).digest())


def _stream(ek, nonce, n):
    out, i = bytearray(), 0
    while len(out) < n:
        out += _hm.new(ek, nonce + i.to_bytes(8, "big"), _hl.sha256).digest()
        i += 1
    return bytes(out[:n])


def seal(key, obj):
    ek, mk = _keys(key)
    data = json.dumps(obj, ensure_ascii=False).encode()
    nonce = _sec.token_bytes(16)
    ct = bytes(a ^ b for a, b in zip(data, _stream(ek, nonce, len(data))))
    tag = _hm.new(mk, nonce + ct, _hl.sha256).digest()
    return _b64.b64encode(b"D1" + nonce + tag + ct).decode()


def unseal(key, text):
    raw = _b64.b64decode(text)
    if raw[:2] != b"D1":
        raise ValueError("unknown format")
    nonce, tag, ct = raw[2:18], raw[18:50], raw[50:]
    ek, mk = _keys(key)
    if not _hm.compare_digest(tag, _hm.new(mk, nonce + ct, _hl.sha256).digest()):
        raise ValueError("wrong key or damaged file")
    return json.loads(bytes(a ^ b for a, b in zip(ct, _stream(ek, nonce, len(ct)))))


def read_sealed(path, key, default):
    try:
        with open(path, encoding="utf-8") as f:
            return unseal(key, f.read().strip())
    except (OSError, ValueError):
        return default


def write_sealed(path, key, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(seal(key, obj) + "\n")
    os.replace(tmp, path)
