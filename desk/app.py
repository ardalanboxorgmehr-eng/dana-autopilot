#!/usr/bin/env python3
"""
Reply Desk: one screen on the Mac for every unanswered comment on @danestani.ruzz
(Instagram) and its YouTube channel.

The 15-minute job writes unanswered comments into state/dm_sent.json ("_desk",
Instagram) and state/yt_desk.json (YouTube). This app pulls the repo, shows them
with a drafted reply, and when Ehsan approves, adds the replies to
reply_queue.json and pushes. The job posts them on its next runs.

Learning (7 Oct 2026): every approval is kept in desk/learn.json with the draft
and what he actually sent. Claude's scheduled drafting reads it, plus the rules
in desk/style.md, so drafts move toward how he writes. The Learned tab shows both.

Auto-send: once a group has STREAK_TO_UNLOCK unedited approvals in a row, a switch
appears. Switched-on groups are written to desk_auto.json and the job answers them
itself. Questions and spam never auto-send.

Phone: the app also listens on the Mac's Wi-Fi address. The Phone button shows a
QR code with a private key in the link; without the key nothing else on the
network can open it.

Local files (never pushed): desk/local.json, desk/drafts.json, desk/learn.json,
desk/style.md, desk/ideas.json

Run: double-click "desk/Reply Desk.command", or  python3 desk/app.py
"""
import json, os, secrets, socket, subprocess, sys, threading, time, urllib.parse, webbrowser
from collections import Counter
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import dm_reply as job  # noqa: E402
import desk_common as dc  # noqa: E402

STATE = os.path.join(ROOT, "state", "dm_sent.json")
YT = os.path.join(ROOT, "state", "yt_desk.json")
QUEUE = os.path.join(ROOT, "reply_queue.json")
LOCAL = os.path.join(HERE, "local.json")
DRAFTS = os.path.join(HERE, "drafts.json")
LEARN = os.path.join(HERE, "learn.json")
STYLE = os.path.join(HERE, "style.md")
IDEAS = os.path.join(HERE, "ideas.json")
PORT = int(os.environ.get("DESK_PORT", "8765"))
LOCK = threading.Lock()


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


def local():
    l = load(LOCAL, {})
    l.setdefault("skipped", {})
    l.setdefault("approved", {})
    if not l.get("key"):
        l["key"] = secrets.token_urlsafe(9)
        save(LOCAL, l)
    return l


def git(*args, timeout=90):
    try:
        r = subprocess.run(["git", "-C", ROOT] + list(args), capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout + r.stderr).strip()
    except Exception as e:
        return 1, str(e)


def same(a, b):
    return " ".join((a or "").split()) == " ".join((b or "").split())


# ------------------------------------------------------------------ learning

def learned_thanks():
    """His own thank-you lines, most used first; the defaults until he has some."""
    c = Counter(e["final"] for e in load(LEARN, []) if e.get("kind") == "thanks" and e.get("final"))
    mine = [t for t, _ in c.most_common(6)]
    return mine if len(mine) >= 2 else dc.THANKS


def stats():
    out = {}
    for e in load(LEARN, []):                      # oldest first
        if e.get("platform", "ig") != "ig":
            continue
        g = out.setdefault(e.get("group", "?"), {"approved": 0, "edited": 0, "streak": 0})
        g["approved"] += 1
        if e.get("edited"):
            g["edited"] += 1
            g["streak"] = 0
        else:
            g["streak"] += 1
    return out


def near(text, kw):
    return job.near_keyword(text, kw)


# ------------------------------------------------------------------ the list

def draft_for(it, group, post, drafts, thanks, n, platform):
    if it["id"] in drafts:
        return "answer", drafts[it["id"]]
    if platform == "yt":
        return ("thanks", thanks[n % len(thanks)]) if group == "chat" else ("answer", "")
    if group == "wants_dm":
        if post.get("message"):
            return "dm", post["message"]
        return "nudge", "یه دایرکت «%s» بهمون بده تا برات بفرستیم 📩" % post.get("keyword", "")
    if group == "chat":
        return "thanks", thanks[n % len(thanks)]
    return "answer", ""


def items():
    state = load(STATE, {})
    desk = state.get("_desk", {})
    yt = load(YT, {})
    l = local()
    drafts = load(DRAFTS, {})
    queued = {i["id"] for i in load(QUEUE, {"items": []}).get("items", [])}
    auto = dc.load_auto()
    skip = set(l["skipped"]) | set(auto["skip"])
    thanks = learned_thanks()
    try:
        rules, _ = job.load_rules()
        msgs = {r[3]: (r[1], r[2]) for r in rules}
    except Exception:
        msgs = {}
    posts = desk.get("posts", {})
    out = []
    for n, it in enumerate(desk.get("items", [])):
        if it["id"] in queued or it["id"] in skip or it["id"] in state.get("_queue", {}):
            continue
        post = dict(posts.get(it["media"], {}))
        kws, msg = msgs.get(it.get("rule"), ([post.get("keyword", "")], ""))
        post["message"] = msg
        post["keyword"] = post.get("keyword") or (kws[0] if kws else "")
        g = dc.group_of(it["text"], post["keyword"], near)
        if auto["groups"].get(g, {}).get("on"):
            continue                                   # the job answers these itself
        kind, text = draft_for(it, g, post, drafts, thanks, n, "ig")
        try:
            age_days = (datetime.now(timezone.utc) - job.ts(it["at"])).days
        except (KeyError, ValueError):
            age_days = 0
        if kind == "dm" and age_days >= 7:
            kind, text = "nudge", "یه دایرکت «%s» بهمون بده تا برات بفرستیم 📩" % post["keyword"]
        out.append(dict(it, platform="ig", group=g, kind=kind, draft=text, caption=post.get("caption", ""),
                        keyword=post["keyword"], has_claude_draft=it["id"] in drafts))
    for n, it in enumerate(yt.get("items", [])):
        if it["id"] in queued or it["id"] in skip:
            continue
        g = dc.group_of(it["text"])
        if g == "wants_dm":
            g = "question"
        kind, text = draft_for(it, g, {}, drafts, thanks, n, "yt")
        out.append(dict(it, platform="yt", group=g, kind=kind, draft=text, caption=it.get("title", ""),
                        keyword="", has_claude_draft=it["id"] in drafts))
    out.sort(key=lambda i: i.get("at", ""), reverse=True)
    return {"at": desk.get("at", ""), "yt_at": yt.get("at", ""), "yt_connected": bool(yt.get("channel")),
            "yt_error": yt.get("error", ""), "items": out,
            "pending_push": len(l["approved"]) + (1 if l.get("auto_dirty") else 0),
            "queue_left": (state.get("_health", {}).get("queue_left") or 0) + (yt.get("queue_left") or 0),
            "auto_on": [g for g, v in auto["groups"].items() if v.get("on")]}


def sources():
    s = {i["id"]: dict(i, platform="ig") for i in load(STATE, {}).get("_desk", {}).get("items", [])}
    s.update({i["id"]: dict(i, platform="yt") for i in load(YT, {}).get("items", [])})
    return s


def approve(batch):
    """batch: [{id, kind, text, draft, draft_kind, group}] -> reply_queue.json + learn.json (not pushed yet)."""
    with LOCK:
        src_by = sources()
        q = load(QUEUE, {"items": []})
        have = {i["id"] for i in q["items"]}
        l = local()
        learn = load(LEARN, [])
        added = 0
        for b in batch:
            src = src_by.get(b.get("id"))
            text = (b.get("text") or "").strip()
            if not src or not text or src["id"] in have:
                continue
            yt = src["platform"] == "yt"
            allowed = ("answer", "thanks") if yt else ("answer", "thanks", "nudge", "dm")
            kind = b.get("kind") if b.get("kind") in allowed else "answer"
            item = {"id": src["id"], "media": src["media"], "user": src["user"], "kind": kind, "text": text,
                    "at": int(job.ts(src["at"]).timestamp()) if src.get("at") and not yt else 0, "via": "desk"}
            if yt:
                item["platform"] = "yt"
            q["items"].append(item)
            l["approved"][src["id"]] = int(time.time())
            draft = b.get("draft") or ""
            dkind = b.get("draft_kind") or kind
            edited = (not draft) or (not same(draft, text)) or kind != dkind
            learn.append({"id": src["id"], "platform": src["platform"], "group": b.get("group", ""),
                          "comment": src.get("text", ""), "user": src.get("user", ""),
                          "draft": draft, "draft_kind": dkind, "final": text, "kind": kind, "edited": edited,
                          "wrote_own": not draft, "at": datetime.now(timezone.utc).isoformat()})
            added += 1
        q["made"] = datetime.now(timezone.utc).isoformat()
        save(QUEUE, q)
        save(LOCAL, l)
        save(LEARN, learn[-3000:])
        return added


def skip(ids):
    with LOCK:
        l = local()
        auto = dc.load_auto()
        for i in ids:
            l["skipped"][i] = int(time.time())
            if i not in auto["skip"]:
                auto["skip"].append(i)
        auto["skip"] = auto["skip"][-3000:]
        dc.save_auto(auto)
        l["auto_dirty"] = True
        save(LOCAL, l)
        return len(ids)


def set_auto(group, on):
    with LOCK:
        if group not in dc.AUTO_GROUPS:
            return {"ok": False, "log": "this group always waits for you"}
        st = stats().get(group, {})
        if on and st.get("streak", 0) < dc.STREAK_TO_UNLOCK:
            return {"ok": False, "log": "needs %d unedited approvals in a row first" % dc.STREAK_TO_UNLOCK}
        auto = dc.load_auto()
        auto["groups"][group] = {"on": bool(on), "since": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+0000")}
        auto["thanks"] = learned_thanks()
        dc.save_auto(auto)
        l = local()
        l["auto_dirty"] = True
        save(LOCAL, l)
        return {"ok": True}


def learned():
    learn = load(LEARN, [])
    edits = [e for e in learn if e.get("edited") and e.get("draft")][-40:][::-1]
    auto = dc.load_auto()
    try:
        style = open(STYLE, encoding="utf-8").read()
    except OSError:
        style = ""
    return {"style": style, "edits": edits, "stats": stats(), "total": len(learn),
            "unlock": dc.STREAK_TO_UNLOCK, "auto_groups": list(dc.AUTO_GROUPS),
            "auto": auto["groups"], "thanks": learned_thanks()}


def save_style(text):
    with open(STYLE, "w", encoding="utf-8") as f:
        f.write(text.strip() + "\n")
    return {"ok": True}


def refresh():
    with LOCK:
        code, out = git("pull", "--rebase", "--autostash")
        return {"ok": code == 0, "log": out[-600:]}


def push():
    with LOCK:
        l = local()
        n = len(l["approved"])
        if not n and not l.get("auto_dirty"):
            return {"ok": True, "log": "nothing to send"}
        log = []
        files = ["reply_queue.json"] + (["desk_auto.json"] if os.path.exists(dc.AUTO) else [])
        code, out = git("add", *files); log.append(out)
        msg = "desk: %d approved replies" % n if n else "desk: auto-send settings"
        code, out = git("commit", "-m", msg); log.append(out)
        code, out = git("pull", "--rebase", "--autostash"); log.append(out)
        if code != 0:
            git("rebase", "--abort")
            return {"ok": False, "log": "\n".join(log)[-800:]}
        code, out = git("push", timeout=120); log.append(out)
        if code == 0:
            l["approved"] = {}
            l["auto_dirty"] = False
            save(LOCAL, l)
        return {"ok": code == 0, "log": "\n".join(x for x in log if x)[-800:]}


def lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return ""


# ------------------------------------------------------------------ web

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, code, body, ctype="application/json; charset=utf-8", extra=None):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def allowed(self, key):
        if self.client_address[0] in ("127.0.0.1", "::1"):
            return True
        ck = self.headers.get("Cookie") or ""
        return ("dk=" + key) in [c.strip() for c in ck.split(";")]

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        key = local()["key"]
        if u.path == "/":
            extra = None
            if urllib.parse.parse_qs(u.query).get("k", [""])[0] == key:
                extra = {"Set-Cookie": "dk=%s; Max-Age=31536000; Path=/; SameSite=Strict; HttpOnly" % key}
            elif not self.allowed(key):
                return self.send(403, b"Open the Phone link from the Mac first.", "text/plain; charset=utf-8")
            with open(os.path.join(HERE, "desk.html"), "rb") as f:
                return self.send(200, f.read(), "text/html; charset=utf-8", extra)
        if not self.allowed(key):
            return self.send(403, {"error": "forbidden"})
        if u.path == "/api/items":
            return self.send(200, items())
        if u.path == "/api/learned":
            return self.send(200, learned())
        if u.path == "/api/ideas":
            return self.send(200, load(IDEAS, {"ideas": []}))
        if u.path == "/api/phone":
            ip = lan_ip()
            return self.send(200, {"url": "http://%s:%d/?k=%s" % (ip, PORT, key) if ip else ""})
        self.send(404, {"error": "not found"})

    def do_POST(self):
        if self.headers.get("X-Desk") != "1" or not self.allowed(local()["key"]):
            return self.send(403, {"error": "forbidden"})
        n = int(self.headers.get("Content-Length") or 0)
        body = json.loads(self.rfile.read(n) or b"{}")
        if self.path == "/api/approve":
            return self.send(200, {"added": approve(body.get("items", []))})
        if self.path == "/api/skip":
            return self.send(200, {"skipped": skip(body.get("ids", []))})
        if self.path == "/api/auto":
            return self.send(200, set_auto(body.get("group"), body.get("on")))
        if self.path == "/api/style":
            return self.send(200, save_style(body.get("text", "")))
        if self.path == "/api/refresh":
            return self.send(200, refresh())
        if self.path == "/api/push":
            return self.send(200, push())
        self.send(404, {"error": "not found"})


def main():
    local()
    srv = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    url = "http://127.0.0.1:%d/" % PORT
    print("Reply Desk running at " + url + "  (close this window to stop)")
    print("On your iPhone (same Wi-Fi): press Phone in the app and scan the code.")
    if "--no-browser" not in sys.argv:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
