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


def clear_stale_locks(age=60):
    """Leftover .git/*.lock files (git interrupted, or another tool) block every
    push; remove any older than a minute before running git."""
    import glob
    for f in glob.glob(os.path.join(ROOT, ".git", "*.lock")):
        try:
            if time.time() - os.path.getmtime(f) > age:
                os.remove(f)
        except OSError:
            pass


def git(*args, timeout=90):
    clear_stale_locks()
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
            "auto_on": [g for g, v in auto["groups"].items() if v.get("on")],
            "badges": badges()}


def badges():
    out = {}
    try:
        out["failed"] = sum(1 for i in failed()["items"] if not i["handled"] and not i["queued"])
    except Exception:
        out["failed"] = 0
    try:
        out["inbox"] = len(inbox().get("items", []))
    except Exception:
        out["inbox"] = 0
    return out


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
        if l.get("dmkey") and l.get("outbox"):
            dc.write_sealed(dc.OUTBOX_ENC, l["dmkey"], {"items": l["outbox"][-200:]})
        files = ["reply_queue.json"] + [os.path.relpath(f, ROOT) for f in (dc.AUTO, dc.OUTBOX_ENC, dc.IDEAS_QUEUE)
                                        if os.path.exists(f)]
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


# ------------------------------------------------------------------ DM inbox, alerts, ideas, TikTok, weekly (7 Oct 2026)

INBOX_CACHE = os.path.join(HERE, "inbox_cache.json")
REPO = "ardalanboxorgmehr-eng/dana-autopilot"
TIKTOK = "danestani.ruzz"


def gh_secret(name, value):
    try:
        r = subprocess.run(["gh", "secret", "set", name, "-R", REPO], input=value, text=True,
                           capture_output=True, timeout=60)
        return r.returncode == 0, (r.stderr or r.stdout).strip()[-300:]
    except Exception as e:
        return False, str(e)


def connect_inbox():
    with LOCK:
        l = local()
        if not l.get("dmkey"):
            l["dmkey"] = secrets.token_urlsafe(32)
            save(LOCAL, l)
        ok, log = gh_secret("DESK_KEY", l["dmkey"])
        if ok:
            l["dm_connected"] = True
            save(LOCAL, l)
        return {"ok": ok, "log": "" if ok else log}


def inbox():
    l = local()
    if not l.get("dmkey"):
        return {"connected": False, "items": []}
    box = dc.read_sealed(dc.INBOX_ENC, l["dmkey"], None)
    if box is None:
        return {"connected": True, "waiting_for_job": True, "items": []}
    sent = {o["id"] for o in l.get("outbox", [])}
    drafts = load(DRAFTS, {})
    items = []
    for it in box.get("items", []):
        if it["id"] in sent:
            continue
        items.append(dict(it, draft=drafts.get(it["id"], ""), has_claude_draft=it["id"] in drafts))
    save(INBOX_CACHE, {"at": box.get("at"), "items": items})       # for Claude's drafting run (local only)
    return {"connected": True, "at": box.get("at", ""), "items": items}


def inbox_send(b):
    with LOCK:
        l = local()
        box = {i["id"]: i for i in dc.read_sealed(dc.INBOX_ENC, l.get("dmkey", ""), {"items": []}).get("items", [])}
        it = box.get(b.get("id"))
        text = (b.get("text") or "").strip()
        if not it or not text:
            return {"ok": False}
        l.setdefault("outbox", []).append({"id": it["id"], "uid": it["uid"], "text": text, "at": int(time.time())})
        l["outbox"] = l["outbox"][-300:]
        l["auto_dirty"] = True
        l["approved"][it["id"]] = int(time.time())
        save(LOCAL, l)
        draft = b.get("draft") or ""
        learn = load(LEARN, [])
        last = next((m["text"] for m in reversed(it.get("thread", [])) if not m.get("me")), "")
        learn.append({"id": it["id"], "platform": "dm", "group": "dm", "comment": last, "user": it.get("user", ""),
                      "draft": draft, "draft_kind": "dm", "final": text, "kind": "dm",
                      "edited": (not draft) or not same(draft, text), "wrote_own": not draft,
                      "at": datetime.now(timezone.utc).isoformat()})
        save(LEARN, learn[-3000:])
        return {"ok": True}


def setup_alerts():
    with LOCK:
        l = local()
        if not l.get("ntfy"):
            l["ntfy"] = "dana-desk-" + secrets.token_hex(6)
            save(LOCAL, l)
        ok, log = gh_secret("NTFY_TOPIC", l["ntfy"])
        if ok:
            l["alerts_on"] = True
            save(LOCAL, l)
        return {"ok": ok, "log": "" if ok else log, "topic": l["ntfy"], "url": "https://ntfy.sh/" + l["ntfy"]}


def queue_idea(b):
    with LOCK:
        topic, post = (b.get("topic") or "").strip(), (b.get("post") or "").strip()
        if not topic:
            return {"ok": False}
        q = load(dc.IDEAS_QUEUE, {"_note": "Ideas Ehsan sent from Reply Desk. Dana's daily run uses the oldest 'new' one first, then marks it used.", "items": []})
        if not any(i["topic"] == topic for i in q["items"]):
            q["items"].append({"topic": topic, "post": post, "count": b.get("count", 0), "status": "new",
                               "added": datetime.now(timezone.utc).strftime("%Y-%m-%d")})
            save(dc.IDEAS_QUEUE, q)
        ideas = load(IDEAS, {"ideas": []})
        for d in ideas.get("ideas", []):
            if d.get("topic") == topic:
                d["status"] = "queued"
        save(IDEAS, ideas)
        l = local()
        l["auto_dirty"] = True
        save(LOCAL, l)
        return {"ok": True}


def first_line(path):
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    return line.strip()[:90]
    except OSError:
        pass
    return ""


def tiktok():
    from zoneinfo import ZoneInfo
    now = datetime.now(ZoneInfo("Europe/London")).strftime("%Y-%m-%d-%H%M")
    base = os.path.join(ROOT, "content")
    posts = []
    for d in sorted(os.listdir(base) if os.path.isdir(base) else [], reverse=True):
        if not d[:4].isdigit() or d > now:
            continue
        title = first_line(os.path.join(base, d, "caption-tiktok.txt")) or first_line(os.path.join(base, d, "caption.txt"))
        posts.append({"id": d, "title": title})
        if len(posts) >= 14:
            break
    return {"handle": TIKTOK, "profile": "https://www.tiktok.com/@" + TIKTOK,
            "studio": "https://www.tiktok.com/tiktokstudio/comment", "posts": posts}


def weekly():
    now = datetime.now(timezone.utc)
    cut = (now.timestamp() - 7 * 86400)

    def recent(v):
        try:
            return datetime.fromisoformat(v["at"]).timestamp() >= cut and "failed" not in v and "skipped" not in v
        except (KeyError, ValueError, TypeError):
            return False
    st = load(STATE, {})
    rules = st.get("_media_rules", {})
    old_rules = {r["id"]: r.get("caption_starts", "") for r in load(os.path.join(ROOT, "dm_rules.json"), {}).get("rules", [])}
    per_post = []
    kw_total = 0
    for k, recs in st.items():
        if k.startswith("_") or not isinstance(recs, dict):
            continue
        n = sum(1 for v in recs.values() if recent(v))
        kw_total += n
        if n:
            rid = rules.get(k, "")
            title = first_line(os.path.join(ROOT, "content", rid, "caption.txt")) if rid else ""
            per_post.append({"post": rid, "title": title or old_rules.get(rid, ""), "dms": n})
    per_post.sort(key=lambda x: -x["dms"])
    q = [v for v in st.get("_queue", {}).values() if recent(v)]
    yt = load(YT, {})
    learn = [e for e in load(LEARN, []) if recent(e)]
    ideas = load(IDEAS, {"ideas": []}).get("ideas", [])[:5]
    return {"since": datetime.fromtimestamp(cut, timezone.utc).strftime("%d %b"),
            "keyword_dms": kw_total,
            "keyword_dms_inbox": sum(1 for v in st.get("_inbox", {}).values() if recent(v)),
            "replies_desk": sum(1 for v in q if v.get("via", "desk") == "desk"),
            "replies_auto": sum(1 for v in q if v.get("via") == "auto"),
            "thanks_emoji": sum(1 for v in st.get("_thanked", {}).values() if recent(v)),
            "dm_replies": sum(1 for v in st.get("_inbox_sent", {}).values() if recent(v)),
            "yt_replies": sum(1 for v in yt.get("done", {}).values() if recent(v)),
            "edited_pct": round(100 * sum(1 for e in learn if e.get("edited")) / len(learn)) if learn else 0,
            "approved": len(learn), "top_posts": per_post[:6], "top_questions": ideas,
            "summary": load(os.path.join(HERE, "weekly.json"), {}).get("summary", "")}


def settings():
    l = local()
    return {"dm_connected": bool(l.get("dm_connected")), "alerts_on": bool(l.get("alerts_on")),
            "ntfy": ("https://ntfy.sh/" + l["ntfy"]) if l.get("ntfy") else ""}


# ------------------------------------------------------------------ failed keyword DMs (7 Oct 2026)

def reason_of(err):
    e = err or ""
    if job.BOUNCE_CODE in e:
        return "Their inbox does not take messages from pages"
    if "HTTP 500" in e:
        return "Instagram server error"
    if "HTTP 400" in e and ("does not exist" in e or "Unsupported" in e):
        return "Comment was deleted"
    if "HTTP 4" in e:
        return "Instagram refused it"
    return e[:80] or "Unknown"


def failed():
    st = load(STATE, {})
    l = local()
    gone = set(l.get("failed_dismissed", {}))
    queued = {i["id"] for i in load(QUEUE, {"items": []}).get("items", [])}
    try:
        rules, _ = job.load_rules()
        msgs = {r[3]: (r[1], r[2]) for r in rules}
    except Exception:
        msgs = {}
    old_rules = {r["id"]: r.get("caption_starts", "") for r in load(os.path.join(ROOT, "dm_rules.json"), {}).get("rules", [])}
    pins = st.get("_media_rules", {})
    later = {(v.get("user"), v.get("rule")) for v in st.get("_inbox", {}).values() if "failed" not in v and "skipped" not in v}
    now = datetime.now(timezone.utc)
    out = []
    for mid, recs in st.items():
        if mid.startswith("_") or not isinstance(recs, dict):
            continue
        rid = pins.get(mid, "")
        kws, msg = msgs.get(rid, ([""], ""))
        title = first_line(os.path.join(ROOT, "content", rid, "caption.txt")) if rid else ""
        for cid, r in recs.items():
            if not r.get("failed") or cid in gone:
                continue
            got_later = (r.get("user"), rid) in later
            when = r.get("c_at") or r.get("at", "")
            try:
                t = job.ts(when) if "+0000" in when or when.endswith("Z") else datetime.fromisoformat(when)
                age_days = (now - t).total_seconds() / 86400
            except (ValueError, TypeError):
                age_days = 99
            out.append({"id": cid, "media": mid, "post": rid, "title": title or old_rules.get(rid, ""),
                        "keyword": kws[0] if kws else "", "message": msg, "user": r.get("user", ""),
                        "text": r.get("text", ""), "at": r.get("at", ""), "reason": reason_of(r["failed"]),
                        "bounced": bool(r.get("bounced")), "can_dm": age_days < 6.8 and bool(msg),
                        "got_later": got_later, "queued": cid in queued,
                        "closed": job.BOUNCE_CODE in r["failed"],
                        "handled": got_later or (bool(r.get("bounced")) and job.BOUNCE_CODE in r["failed"])})
    out.sort(key=lambda i: i["at"], reverse=True)
    return {"items": out, "retrying": len(st.get("_tries", {}))}


def failed_action(b):
    with LOCK:
        f = {i["id"]: i for i in failed()["items"]}
        l = local()
        q = load(QUEUE, {"items": []})
        have = {i["id"] for i in q["items"]}
        n = 0
        for cid in b.get("ids", []):
            it = f.get(cid)
            if not it:
                continue
            if b.get("action") == "dismiss":
                l.setdefault("failed_dismissed", {})[cid] = int(time.time())
                n += 1
                continue
            if cid in have:
                continue
            if b.get("action") == "dm" and it["can_dm"]:
                item = {"id": cid, "media": it["media"], "user": it["user"], "kind": "dm", "text": it["message"],
                        "at": int(time.time()), "via": "desk", "retry": True}
            elif b.get("action") == "nudge" and not it["bounced"]:
                item = {"id": cid, "media": it["media"], "user": it["user"], "kind": "nudge",
                        "text": job.bounce_text(it["keyword"]), "at": int(time.time()), "via": "desk"}
            else:
                continue
            q["items"].append(item)
            l["approved"][cid] = int(time.time())
            n += 1
        save(QUEUE, q)
        save(LOCAL, l)
        return {"ok": True, "done": n}


# ------------------------------------------------------------------ review before send (8 Oct 2026)

def pending():
    """Everything approved on this Mac but not pushed yet, for the Review screen."""
    l = local()
    ids = set(l["approved"])
    learn = {e["id"]: e for e in load(LEARN, [])}
    src = sources()
    fail = {}
    if ids:
        try:
            fail = {i["id"]: i for i in failed()["items"]}
        except Exception:
            fail = {}
    out = []
    for it in load(QUEUE, {"items": []}).get("items", []):
        if it["id"] not in ids:
            continue
        s = src.get(it["id"], {})
        f = fail.get(it["id"], {})
        out.append({"id": it["id"], "kind": it.get("kind"), "text": it.get("text", ""), "user": it.get("user", ""),
                    "platform": it.get("platform", "ig"), "retry": bool(it.get("retry")),
                    "comment": s.get("text") or learn.get(it["id"], {}).get("comment") or f.get("text", ""),
                    "where": "failed" if f else "comments"})
    for o in l.get("outbox", []):
        if o["id"] in ids:
            out.append({"id": o["id"], "kind": "inbox", "text": o["text"], "user": learn.get(o["id"], {}).get("user", ""),
                        "platform": "dm", "comment": learn.get(o["id"], {}).get("comment", ""), "where": "dms"})
    other = []
    if l.get("auto_dirty"):
        auto = dc.load_auto()
        on = [g for g, v in auto["groups"].items() if v.get("on")]
        other.append("Auto-send settings" + (": on for " + ", ".join(on) if on else ": all off"))
        q = [i for i in load(dc.IDEAS_QUEUE, {"items": []}).get("items", []) if i.get("status") == "new"]
        if q:
            other.append("%d idea%s in the carousel queue" % (len(q), "s" if len(q) > 1 else ""))
    return {"items": out, "other": other}


def unapprove(ids):
    with LOCK:
        ids = set(ids)
        l = local()
        mine = ids & set(l["approved"])           # only things not pushed yet
        q = load(QUEUE, {"items": []})
        q["items"] = [i for i in q["items"] if i["id"] not in mine]
        save(QUEUE, q)
        l["outbox"] = [o for o in l.get("outbox", []) if o["id"] not in mine]
        for i in mine:
            l["approved"].pop(i, None)
        save(LOCAL, l)
        learn = load(LEARN, [])
        save(LEARN, [e for e in learn if e["id"] not in mine])
        return {"ok": True, "removed": len(mine)}


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
        if u.path == "/api/pending":
            return self.send(200, pending())
        if u.path == "/api/failed":
            return self.send(200, failed())
        if u.path == "/api/inbox":
            return self.send(200, inbox())
        if u.path == "/api/tiktok":
            return self.send(200, tiktok())
        if u.path == "/api/weekly":
            return self.send(200, weekly())
        if u.path == "/api/settings":
            return self.send(200, settings())
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
        if self.path == "/api/unapprove":
            return self.send(200, unapprove(body.get("ids", [])))
        if self.path == "/api/failed_action":
            return self.send(200, failed_action(body))
        if self.path == "/api/inbox_send":
            return self.send(200, inbox_send(body))
        if self.path == "/api/connect_inbox":
            return self.send(200, connect_inbox())
        if self.path == "/api/alerts":
            return self.send(200, setup_alerts())
        if self.path == "/api/idea_queue":
            return self.send(200, queue_idea(body))
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
