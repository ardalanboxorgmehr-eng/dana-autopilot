#!/usr/bin/env python3
"""
Reply Desk: one screen on the Mac for every unanswered comment on @danestani.ruzz.

The comment-to-DM job (scripts/dm_reply.py, every 15 minutes on GitHub) writes the
unanswered comments into state/dm_sent.json under "_desk". This app pulls the repo,
shows them with a drafted reply, and when Ehsan approves, adds the replies to
reply_queue.json and pushes. The job then posts them on its next run.

No Instagram token on the Mac: sending is done by the job, with the token in
GitHub secrets. Push uses the Mac's own git login.

Local files (never pushed):
  desk/local.json    skipped and approved ids
  desk/drafts.json   drafts Claude writes for questions: {"<comment id>": "text"}

Run: double-click "desk/Reply Desk.command", or  python3 desk/app.py
"""
import json, os, re, subprocess, sys, threading, time, webbrowser
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import dm_reply as job  # noqa: E402  (shared text matching and rules)

STATE = os.path.join(ROOT, "state", "dm_sent.json")
QUEUE = os.path.join(ROOT, "reply_queue.json")
LOCAL = os.path.join(HERE, "local.json")
DRAFTS = os.path.join(HERE, "drafts.json")
PORT = int(os.environ.get("DESK_PORT", "8765"))
LOCK = threading.Lock()

THANKS = ["مرسی از کامنتت 🙏", "مرسی که نظرت رو نوشتی 🙏", "ممنون که همراهمونی ✨", "مرسی ❤️"]
QUESTION_WORDS = ["چطور", "چجوری", "چطوری", "کجا", "چرا", "چیه", "چی ", "میشه", "می‌شه", "رایگان", "پولی",
                  "قیمت", "کار نمیکنه", "کار نمی‌کنه", "باز نمیشه", "باز نمی‌شه", "کدوم", "نمیشه", "نمی‌شه",
                  "how", "where", "free", "price", "why"]
WANTS_DM = ["دایرکت", "بفرست", "بفرستید", "لینک", "ارسال", "پیوی", "پی وی", "send", "link", "dm"]
SPAM = ["http", "www.", ".com", "فالوور", "فالو کن", "فالوم", "پیجم", "پیج ما", "تبلیغ", "سفارش", "خرید",
        "follow", "promo", "crypto", "کریپتو", "سرمایه گذاری", "سرمایه‌گذاری"]


# ------------------------------------------------------------------ files

def load(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def save(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1 if path == QUEUE else 2)
        f.write("\n")
    os.replace(tmp, path)


def git(*args, timeout=90):
    try:
        r = subprocess.run(["git", "-C", ROOT] + list(args), capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout + r.stderr).strip()
    except Exception as e:  # git missing, timeout
        return 1, str(e)


# ------------------------------------------------------------------ sorting and drafts

def group_of(text, keyword):
    t = (text or "").lower()
    if any(w in t for w in SPAM) or t.count("@") >= 2:
        return "spam"
    words = job.tokens(text)
    near = keyword and any(job.edit_distance(w, job.norm(keyword)) <= 2 for w in words if len(w) >= 3)
    if near or any(w in t for w in WANTS_DM):
        return "wants_dm"
    if "?" in t or "؟" in t or any(w in t for w in QUESTION_WORDS):
        return "question"
    return "chat"


def draft_for(item, group, post, drafts, n):
    if item["id"] in drafts:
        return "answer", drafts[item["id"]]
    if group == "wants_dm":
        msg = post.get("message")
        if msg:
            return "dm", msg
        return "nudge", "یه دایرکت «%s» بهمون بده تا برات بفرستیم 📩" % post.get("keyword", "")
    if group == "chat":
        return "thanks", THANKS[n % len(THANKS)]
    return "answer", ""


def items():
    state = load(STATE, {})
    desk = state.get("_desk", {})
    local = load(LOCAL, {"skipped": {}, "approved": {}})
    drafts = load(DRAFTS, {})
    queued = {i["id"] for i in load(QUEUE, {"items": []}).get("items", [])}
    rules, _ = job.load_rules()
    msgs = {r[3]: (r[1], r[2]) for r in rules}
    posts = desk.get("posts", {})
    out = []
    for n, it in enumerate(desk.get("items", [])):
        if it["id"] in queued or it["id"] in local["skipped"]:
            continue
        post = dict(posts.get(it["media"], {}))
        kws, msg = msgs.get(it.get("rule"), ([post.get("keyword", "")], ""))
        post["message"] = msg
        post["keyword"] = post.get("keyword") or (kws[0] if kws else "")
        g = group_of(it["text"], post["keyword"])
        kind, text = draft_for(it, g, post, drafts, n)
        try:
            age_days = (datetime.now(timezone.utc) - job.ts(it["at"])).days
        except (KeyError, ValueError):
            age_days = 0
        if kind == "dm" and age_days >= 7:      # Instagram: private reply only within 7 days
            kind, text = "nudge", "یه دایرکت «%s» بهمون بده تا برات بفرستیم 📩" % post["keyword"]
        out.append(dict(it, group=g, kind=kind, draft=text, caption=post.get("caption", ""),
                        keyword=post["keyword"], has_claude_draft=it["id"] in drafts))
    return {"at": desk.get("at", ""), "items": out,
            "pending_push": len(local.get("approved", {})),
            "queue_left": state.get("_health", {}).get("queue_left")}


def approve(batch):
    """batch: [{id, kind, text}] -> appended to reply_queue.json (not pushed yet)."""
    with LOCK:
        state = load(STATE, {})
        by_id = {i["id"]: i for i in state.get("_desk", {}).get("items", [])}
        q = load(QUEUE, {"items": []})
        have = {i["id"] for i in q["items"]}
        local = load(LOCAL, {"skipped": {}, "approved": {}})
        added = 0
        for b in batch:
            src = by_id.get(b.get("id"))
            text = (b.get("text") or "").strip()
            kind = b.get("kind") if b.get("kind") in ("answer", "thanks", "nudge", "dm") else "answer"
            if not src or not text or src["id"] in have:
                continue
            item = {"id": src["id"], "media": src["media"], "user": src["user"], "kind": kind, "text": text,
                    "at": int(job.ts(src["at"]).timestamp()) if src.get("at") else 0, "via": "desk"}
            q["items"].append(item)
            local["approved"][src["id"]] = int(time.time())
            added += 1
        q["made"] = datetime.now(timezone.utc).isoformat()
        save(QUEUE, q)
        save(LOCAL, local)
        return added


def skip(ids):
    with LOCK:
        local = load(LOCAL, {"skipped": {}, "approved": {}})
        for i in ids:
            local["skipped"][i] = int(time.time())
        save(LOCAL, local)
        return len(ids)


def refresh():
    with LOCK:
        code, out = git("pull", "--rebase", "--autostash")
        return {"ok": code == 0, "log": out[-600:]}


def push():
    with LOCK:
        local = load(LOCAL, {"skipped": {}, "approved": {}})
        n = len(local.get("approved", {}))
        if not n:
            return {"ok": True, "log": "nothing to send"}
        log = []
        code, out = git("add", "reply_queue.json"); log.append(out)
        code, out = git("commit", "-m", "desk: %d approved replies" % n); log.append(out)
        code, out = git("pull", "--rebase", "--autostash"); log.append(out)
        if code != 0:
            git("rebase", "--abort")
            return {"ok": False, "log": "\n".join(log)[-800:]}
        code, out = git("push", timeout=120); log.append(out)
        if code == 0:
            local["approved"] = {}
            save(LOCAL, local)
        return {"ok": code == 0, "log": "\n".join(x for x in log if x)[-800:]}


# ------------------------------------------------------------------ web

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, code, body, ctype="application/json; charset=utf-8"):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/":
            with open(os.path.join(HERE, "desk.html"), "rb") as f:
                return self.send(200, f.read(), "text/html; charset=utf-8")
        if self.path == "/api/items":
            return self.send(200, items())
        self.send(404, {"error": "not found"})

    def do_POST(self):
        # Only this page may call the API (stops other web pages posting to localhost).
        if self.headers.get("X-Desk") != "1":
            return self.send(403, {"error": "forbidden"})
        n = int(self.headers.get("Content-Length") or 0)
        body = json.loads(self.rfile.read(n) or b"{}")
        if self.path == "/api/approve":
            return self.send(200, {"added": approve(body.get("items", []))})
        if self.path == "/api/skip":
            return self.send(200, {"skipped": skip(body.get("ids", []))})
        if self.path == "/api/refresh":
            return self.send(200, refresh())
        if self.path == "/api/push":
            return self.send(200, push())
        self.send(404, {"error": "not found"})


def main():
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = "http://127.0.0.1:%d/" % PORT
    print("Reply Desk running at " + url + "  (close this window to stop)")
    if "--no-browser" not in sys.argv:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
