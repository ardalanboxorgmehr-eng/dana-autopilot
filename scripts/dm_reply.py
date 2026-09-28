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

Exit codes: 0 fine, 1 some sends failed, 2 the Instagram connection is broken
(so GitHub emails the owner the same hour instead of DMs silently stopping).

Env: IG_ACCESS_TOKEN (required). DM_MODE overrides config ("dry_run"/"live").
     DM_LOOKBACK_HOURS (test runs only) looks back that many hours instead of start_at.
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


def ts(s):
    return datetime.strptime(s.replace("Z", "+0000"), "%Y-%m-%dT%H:%M:%S%z")


# ------------------------------------------------------------------ main

def run(ig, cfg, state, now, log=print):
    dmcfg = cfg.get("dm", {})
    mode = os.environ.get("DM_MODE") or dmcfg.get("mode", "dry_run")
    start_at = ts(dmcfg["start_at"]) if dmcfg.get("start_at") else now
    look = os.environ.get("DM_LOOKBACK_HOURS")
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

    sends = errors = 0
    for m in ig.recent_media():
        if ts(m["timestamp"]) < now - timedelta(days=WINDOW_DAYS + 1):
            continue
        rule = rule_for(m.get("caption", ""), rules)
        if not rule:
            continue
        _, kws, msg, rid = rule
        done = state.setdefault(m["id"], {})
        users_done = {v.get("user") for v in done.values()}
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
            if user in users_done:
                done[c["id"]] = {"user": user, "at": now.isoformat(), "skipped": "already sent to this person"}
                continue
            if sends >= MAX_SENDS_PER_RUN:
                log("send limit for this run reached, the rest go next run")
                return (1 if errors else 0), sends
            if mode != "live":
                log(f"[dry run] {rid}: would DM @{user} for «{c.get('text','')[:30]}»")
                continue
            try:
                ig.private_reply(c["id"], msg)
            except IGError as e:
                errors += 1
                log(f"DM FAILED {rid} @{user}: {e}")
                continue
            done[c["id"]] = {"user": user, "at": now.isoformat()}
            users_done.add(user)
            sends += 1
            log(f"DM sent {rid} @{user}")
            try:
                ig.public_reply(c["id"], random.choice(PUBLIC_REPLIES))
            except IGError as e:
                log(f"public reply failed {rid} @{user}: {e}")
            time.sleep(SEND_GAP_S)
    log(f"done: {sends} sent, {errors} failed")
    return (1 if errors else 0), sends


def main():
    token = os.environ.get("IG_ACCESS_TOKEN", "").strip()
    if not token:
        print("CONNECTION BROKEN: IG_ACCESS_TOKEN is empty")
        return 2
    cfg = load(CONFIG, {})
    state = load(STATE, {})
    ig = IG(token, cfg.get("api_version", "v25.0"))
    code, _ = run(ig, cfg, state, datetime.now(timezone.utc))
    save(STATE, state)
    return code


if __name__ == "__main__":
    sys.exit(main())
