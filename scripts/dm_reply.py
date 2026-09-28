#!/usr/bin/env python3
"""
Comment-to-DM for @danestani.ruzz, run headless every 15 minutes.

For each recent post it finds the post's DM rule (keywords + message), reads
the comments, and for every NEW comment that contains a keyword it sends the
commenter one private reply (Instagram's "private reply" to a comment), then
leaves a short threaded public reply under the comment.

Rules come from two places:
  content/<post-id>/dm.json   autopilot posts, matched by caption.txt
  dm_rules.json               older posts, matched by the caption's first words

Safety:
  * config.json "dm.mode" must be "live" to send anything. "dry_run" only logs.
  * Comments older than config.json "dm.start_at" are never touched, so turning
    this on does not mass-message an old backlog.
  * One DM per comment and one per person per post (state/dm_sent.json).
  * Instagram only allows a private reply within 7 days of the comment.
  * At most MAX_SENDS_PER_RUN sends a run, a few seconds apart.

When a DM bounces because the person's inbox is closed to pages (Instagram
error 2534001), it leaves a threaded public reply asking them to DM the keyword
instead. Keyword DMs that people send the page are answered from the inbox
(Instagram allows a reply within 24 hours of their message).

Exit codes: 0 fine, 1 some sends failed, 2 the Instagram connection is broken
(so GitHub emails the owner the same hour instead of DMs silently stopping).

Env: IG_ACCESS_TOKEN (required). DM_MODE overrides config ("dry_run"/"live").
     DM_LOOKBACK_HOURS or config dm.dry_run_lookback_hours (test runs only) looks back
     that many hours instead of start_at. Ignored in live mode.
Config dm.bounce_backlog: true also leaves the bounce reply on comments whose DM
     bounced before this feature existed (each once). Off by default.
Config dm.inbox: false turns off answering keyword DMs. On by default.
"""
import glob, json, os, random, re, sys, time, unicodedata
import urllib.parse, urllib.request, urllib.error
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, "config.json")
RULES = os.path.join(ROOT, "dm_rules.json")
STATE = os.path.join(ROOT, "state", "dm_sent.json")
CONTENT = os.path.join(ROOT, "content")

MAX_SENDS_PER_RUN = 80
SEND_GAP_S = 3
WINDOW_DAYS = 7
PUBLIC_REPLIES = [
    "برات فرستادم، دایرکتت رو چک کن 📩",
    "فرستادم تو دایرکت 🌱",
    "دایرکتت رو ببین، اونجاست ✨",
    "تو دایرکت منتظرته 📩",
]
BOUNCE_CODE = "2534001"      # inbox closed to pages / thread deleted: retrying never helps
INBOX_HOURS = 24             # Instagram's reply window for a message they sent us


def bounce_text(keyword):
    return f"نشد برات بفرستم، دایرکتت برای پیج‌ها بسته‌ست 🙏 یه دایرکت «{keyword}» بهمون بده تا برات بفرستیم"


class IGError(RuntimeError):
    pass


# ------------------------------------------------------------------ text

_TRANS = str.maketrans({"ي": "ی", "ى": "ی", "ك": "ک", "ة": "ه", "ۀ": "ه", "أ": "ا", "إ": "ا", "آ": "ا"})

def norm(s):
    """Lower-case, Persian letter forms unified, no ZWNJ, tatweel, marks or spaces."""
    s = unicodedata.normalize("NFKC", s or "").translate(_TRANS).lower()
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return re.sub(r"[\s‌‍ـ]+", "", s)


def matches(text, keywords, exclude):
    t = norm(text)
    if any(norm(x) and norm(x) in t for x in exclude):
        return False
    return any(norm(k) and norm(k) in t for k in keywords)


# ------------------------------------------------------------------ io

def load(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, path)


def load_rules():
    """[(caption_prefix, keywords, message, rule_id)] from both sources."""
    out = []
    old = load(RULES, {"rules": [], "exclude": []})
    exclude = old.get("exclude", [])
    for r in old.get("rules", []):
        out.append((r["caption_starts"], r["keywords"], r["message"], r["id"]))
    for d in sorted(glob.glob(os.path.join(CONTENT, "*", "dm.json"))):
        folder = os.path.dirname(d)
        cap_path = os.path.join(folder, "caption.txt")
        if not os.path.exists(cap_path):
            continue
        dm = load(d)
        with open(cap_path, encoding="utf-8") as f:
            first = f.read().strip().split("\n")[0]
        if dm.get("dm_single") and dm.get("keywords"):
            out.append((first[:40], dm["keywords"], dm["dm_single"], os.path.basename(folder)))
    return out, exclude


def rule_for(caption, rules):
    c = norm(caption)
    best = None
    for prefix, kws, msg, rid in rules:
        p = norm(prefix)
        if p and c.startswith(p) and (best is None or len(p) > len(norm(best[0]))):
            best = (prefix, kws, msg, rid)
    return best


# ------------------------------------------------------------------ api

class IG:
    def __init__(self, token, version):
        self.token = token
        self.base = f"https://graph.instagram.com/{version}"

    def _call(self, method, path, params=None, body=None):
        if path.startswith("http"):          # a paging "next" link, already signed
            url = path
        else:
            params = dict(params or {}, access_token=self.token)
            url = f"{self.base}{path}?{urllib.parse.urlencode(params)}"
        data, headers = None, {}
        if body is not None:
            data = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
        elif method == "POST":
            data = b""
        req = urllib.request.Request(url, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            raise IGError(f"{method} {path[:60]} -> HTTP {e.code}: {e.read().decode(errors='replace')[:400]}") from None
        except urllib.error.URLError as e:
            raise IGError(f"{method} {path[:60]} -> {e.reason}") from None

    def me(self):
        return self._call("GET", "/me", {"fields": "user_id,username"})

    def recent_media(self, limit=30):
        return self._call("GET", "/me/media", {"fields": "id,caption,timestamp", "limit": limit}).get("data", [])

    def comments(self, media_id):
        out = []
        try:
            r = self._call("GET", f"/{media_id}/comments", {"fields": "id,text,timestamp,from,username,replies{username,from}", "limit": 50})
        except IGError:   # older API versions without nested replies
            r = self._call("GET", f"/{media_id}/comments", {"fields": "id,text,timestamp,from,username", "limit": 50})
        while True:
            out += r.get("data", [])
            nxt = r.get("paging", {}).get("next")
            if not nxt or len(out) > 2000:
                return out
            r = self._call("GET", nxt)

    def private_reply(self, comment_id, text):
        return self._call("POST", "/me/messages", body={"recipient": {"comment_id": comment_id}, "message": {"text": text}})

    def public_reply(self, comment_id, text):
        return self._call("POST", f"/{comment_id}/replies", {"message": text})

    def conversations(self):
        return self._call("GET", "/me/conversations", {
            "platform": "instagram", "limit": 50,
            "fields": "updated_time,messages.limit(10){id,created_time,from,message}"}).get("data", [])

    def send_to_user(self, user_id, text):
        return self._call("POST", "/me/messages", body={"recipient": {"id": user_id}, "message": {"text": text}})


def ts(s):
    return datetime.strptime(s.replace("Z", "+0000"), "%Y-%m-%dT%H:%M:%S%z")


# ------------------------------------------------------------------ main

def run(ig, cfg, state, now, log=print):
    dmcfg = cfg.get("dm", {})
    mode = os.environ.get("DM_MODE") or dmcfg.get("mode", "dry_run")
    start_at = ts(dmcfg["start_at"]) if dmcfg.get("start_at") else now
    look = os.environ.get("DM_LOOKBACK_HOURS") or dmcfg.get("dry_run_lookback_hours")
    if look and mode != "live":          # test runs only: look further back
        start_at = now - timedelta(hours=float(look))
    window_start = max(start_at, now - timedelta(days=WINDOW_DAYS))
    rules, exclude = load_rules()

    try:
        who = ig.me()
    except IGError as e:
        log(f"CONNECTION BROKEN: {e}")
        return 2, 0
    own = {str(who.get("user_id", "")), who.get("username", "")}
    log(f"connected to @{who.get('username')} · mode={mode} · handling comments after {window_start.isoformat()}")

    sends = errors = skipped = bounced = 0
    failures = []
    active = []                      # (media, rule) for every recent post with a rule, newest first
    for m in ig.recent_media():
        rule = rule_for(m.get("caption", ""), rules)
        if rule:
            active.append((m, rule))
    for m, rule in active:
        if ts(m["timestamp"]) < now - timedelta(days=WINDOW_DAYS + 1):
            continue
        _, kws, msg, rid = rule
        done = state.setdefault(m["id"], {})
        users_done = {v.get("user") for v in done.values() if "failed" not in v}
        if dmcfg.get("bounce_backlog") and mode == "live":
            for cid, rec in done.items():
                if BOUNCE_CODE in rec.get("failed", "") and "bounced" not in rec and "bounce_failed" not in rec:
                    if bounced >= MAX_SENDS_PER_RUN:
                        break
                    bounce(ig, cid, rec, kws[0], now, log, rid)
                    bounced += 1
                    time.sleep(SEND_GAP_S)
        comments = ig.comments(m["id"])
        fresh = [c for c in comments if ts(c["timestamp"]) >= window_start]
        log(f"post {rid}: {len(comments)} comments read, {len(fresh)} in the window")
        for c in comments:
            if c["id"] in done or ts(c["timestamp"]) < window_start:
                continue
            frm = c.get("from") or {}
            user = frm.get("username") or c.get("username", "")
            if str(frm.get("id", "")) in own or user in own:
                continue
            if not matches(c.get("text", ""), kws, exclude):
                continue
            replies = (c.get("replies") or {}).get("data", [])
            if any((r.get("username") in own) or (str((r.get("from") or {}).get("id", "")) in own) for r in replies):
                if mode == "live":
                    done[c["id"]] = {"user": user, "at": now.isoformat(), "skipped": "we already replied"}
                skipped += 1
                continue
            if user in users_done:
                if mode == "live":
                    done[c["id"]] = {"user": user, "at": now.isoformat(), "skipped": "already sent to this person"}
                skipped += 1
                continue
            if sends >= MAX_SENDS_PER_RUN:
                log("send limit for this run reached, the rest go next run")
                break
            if mode != "live":
                log(f"[dry run] {rid}: would DM @{user} for «{c.get('text','')[:30]}»")
                continue
            try:
                ig.private_reply(c["id"], msg)
            except IGError as e:
                errors += 1
                err = str(e)[:300]
                done[c["id"]] = {"user": user, "at": now.isoformat(), "failed": err}
                failures.append({"post": rid, "user": user, "error": err})
                log(f"DM FAILED {rid} @{user}: {err}")
                if BOUNCE_CODE in err:
                    bounce(ig, c["id"], done[c["id"]], kws[0], now, log, rid)
                time.sleep(SEND_GAP_S)
                continue
            done[c["id"]] = {"user": user, "at": now.isoformat()}
            users_done.add(user)
            sends += 1
            log(f"DM sent {rid} @{user}")
            try:
                ig.public_reply(c["id"], random.choice(PUBLIC_REPLIES))
            except IGError as e:
                done[c["id"]]["public_failed"] = str(e)[:200]
                log(f"public reply failed {rid} @{user}: {e}")
            time.sleep(SEND_GAP_S)
        if sends >= MAX_SENDS_PER_RUN:
            break
    inbox_sent = 0
    if dmcfg.get("inbox", True) and sends < MAX_SENDS_PER_RUN:
        inbox_sent = answer_inbox(ig, state, active, own, exclude, mode, max(start_at, now - timedelta(hours=INBOX_HOURS)),
                                  now, MAX_SENDS_PER_RUN - sends, log)
    state["_report"] = {"at": now.isoformat(), "mode": mode, "sent": sends, "failed": errors,
                        "skipped": skipped, "inbox_sent": inbox_sent, "bounce_backlog": bounced,
                        "failures": failures[:20]}
    log(f"done: {sends} sent, {errors} failed, {skipped} skipped, {inbox_sent} answered from the inbox")
    # A failed send is recorded and not retried. Only fail the job (and email
    # the owner) when sending is broken outright: errors and nothing went out.
    return (1 if errors and not sends else 0), sends


def bounce(ig, comment_id, rec, keyword, now, log, rid):
    """Public threaded reply when the DM could not be delivered. Once per comment."""
    try:
        ig.public_reply(comment_id, bounce_text(keyword))
        rec["bounced"] = now.isoformat()
        log(f"bounce reply left {rid} @{rec.get('user')}")
    except IGError as e:
        rec["bounce_failed"] = str(e)[:200]
        log(f"bounce reply failed {rid} @{rec.get('user')}: {e}")


def answer_inbox(ig, state, active, own, exclude, mode, since, now, budget, log):
    """Send the post's DM to people who messaged the page one of its keywords."""
    try:
        convs = ig.conversations()
    except IGError as e:
        log(f"inbox not readable, skipped this run: {e}")
        return 0
    box = state.setdefault("_inbox", {})
    got = {}                                         # media id -> usernames already sent by comment
    sent = 0
    for conv in convs:
        msgs = (conv.get("messages") or {}).get("data", [])
        for mm in sorted(msgs, key=lambda x: x.get("created_time", "")):
            if sent >= budget:
                return sent
            frm = mm.get("from") or {}
            uid, user = str(frm.get("id", "")), frm.get("username", "")
            if not uid or uid in own or user in own or mm.get("id") in box:
                continue
            try:
                if ts(mm["created_time"]) < since:
                    continue
            except (KeyError, ValueError):
                continue
            hit = None
            for m, (_, kws, msg, rid) in active:     # newest post first
                if matches(mm.get("message", ""), kws, exclude):
                    hit = (m, kws, msg, rid)
                    break
            if not hit:
                continue
            m, kws, msg, rid = hit
            if m["id"] not in got:
                got[m["id"]] = {v.get("user") for v in state.get(m["id"], {}).values() if "failed" not in v}
            if user in got[m["id"]] or any(v.get("uid") == uid and v.get("rule") == rid and "failed" not in v
                                          for v in box.values()):
                if mode == "live":
                    box[mm["id"]] = {"user": user, "uid": uid, "rule": rid, "at": now.isoformat(), "skipped": "already has it"}
                continue
            if mode != "live":
                log(f"[dry run] inbox {rid}: would DM @{user} for «{mm.get('message','')[:30]}»")
                continue
            try:
                ig.send_to_user(uid, msg)
            except IGError as e:
                box[mm["id"]] = {"user": user, "uid": uid, "rule": rid, "at": now.isoformat(), "failed": str(e)[:300]}
                log(f"inbox DM FAILED {rid} @{user}: {e}")
                continue
            box[mm["id"]] = {"user": user, "uid": uid, "rule": rid, "at": now.isoformat()}
            got[m["id"]].add(user)
            sent += 1
            log(f"inbox DM sent {rid} @{user}")
            time.sleep(SEND_GAP_S)
    return sent


def prune(state, now, days=90):
    """Forget sent-message records older than the privacy policy allows."""
    cutoff = now - timedelta(days=days)
    for mid in list(state):
        if mid.startswith("_") and mid != "_inbox":
            continue
        recs = state[mid]
        for cid in list(recs):
            try:
                if datetime.fromisoformat(recs[cid]["at"]) < cutoff:
                    del recs[cid]
            except (KeyError, ValueError):
                pass
        if not recs:
            del state[mid]


def main():
    token = os.environ.get("IG_ACCESS_TOKEN", "").strip()
    if not token:
        print("CONNECTION BROKEN: IG_ACCESS_TOKEN is empty")
        return 2
    cfg = load(CONFIG, {})
    state = load(STATE, {})
    ig = IG(token, cfg.get("api_version", "v25.0"))
    now = datetime.now(timezone.utc)
    code, _ = run(ig, cfg, state, now)
    prune(state, now)
    save(STATE, state)
    return code


if __name__ == "__main__":
    sys.exit(main())
