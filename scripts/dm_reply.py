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

MAX_SENDS_PER_RUN = 40
SEND_GAP_S = 3
MAX_ERROR_STREAK = 3          # this many failed sends in a row means throttling: stop the run
MAX_TRIES = 4                 # a comment whose DM fails this many runs gets the public "DM us the keyword" reply instead
QUEUE = os.path.join(ROOT, "reply_queue.json")
QUEUE_PER_RUN = 12            # hand-written threaded replies posted per run (~48/hour)
THANKS_PER_RUN = 5            # automatic thank-you replies to emoji-only comments per run
THANKS = ["مرسی از کامنتت 🙏", "مرسی که همراهمونی ✨", "ممنون که نظرت رو نوشتی 🙏", "مرسی ❤️"]
STALL_ALERT_H = 2             # keyword comments waiting and nothing sent for this long: alert
ALERT_REPEAT_H = 12           # do not email the same alert more often than this
CTA_MARKS = ("📩", "کامنت کن", "کامنت بذار")   # a caption with these asks for a DM keyword
RUN_BUDGET_S = 20 * 60       # stop starting new posts after 20 minutes; the next run carries on
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


_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def tokens(s):
    """Whole words of a comment, each normalised like norm(). ZWNJ, emoji and punctuation split words."""
    s = unicodedata.normalize("NFKC", s or "").translate(_DIGITS)
    return {norm(w) for w in re.split(r"[^\w]+|_", s) if norm(w)}


def hit(text, t, words, k):
    """Match rules, set 29 Sep 2026.
    A number keyword (the 7 Oct onward CTA) fires only when the comment IS that
    number, once digits are made Latin and spaces, emoji and punctuation are
    dropped: "5", "۵", "5 🙏" yes; "10/10", "۵ دقیقه" no.
    A keyword of 3 letters or fewer must be a whole word, so «ورد» no longer
    fires on «مورد», «متا» on «متاسفانه», «ویس» on «بنویس».
    Longer keywords keep the old contains-match, which catches misspellings."""
    nk = norm(k).translate(_DIGITS)
    if not nk:
        return False
    if nk.isdigit():
        bare = "".join(ch for ch in unicodedata.normalize("NFKC", text or "").translate(_DIGITS)
                       if ch.isalnum())
        return bare == nk
    if len(nk) <= 3:
        return nk in words
    if nk in t:
        return True
    # Misspellings (7 Oct 2026: «پرتمپت», «گیت آب», «جونای» never got their DM).
    # Only for short comments, so a long sentence never matches by accident.
    if len(t) <= len(nk) + 3:
        return edit_distance(t, nk) <= (1 if len(nk) <= 4 else 2)
    return False


def edit_distance(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def matches(text, keywords, exclude):
    t = norm(text)
    words = tokens(text)
    if any(hit(text, t, words, x) for x in exclude):
        return False
    return any(hit(text, t, words, k) for k in keywords)


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


GREETING = "سلام! مرسی که کامنت گذاشتی 😊"
GREETINGS = [GREETING, "سلام! ممنون از کامنتت 😊", "سلام 👋 مرسی که کامنت گذاشتی!",
             "سلام! خوشحالم که کامنت گذاشتی 🌱", "سلام! مرسی از کامنتت ✨"]


def vary(msg):
    """Swap the stock greeting for one of a few (8 Oct 2026): hundreds of identical
    private replies in a row is what Meta throttles with HTTP 500 code 1."""
    if msg.startswith(GREETING):
        return random.choice(GREETINGS) + msg[len(GREETING):]
    return msg


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

    def recent_media(self, limit=1000):
        """Every post on the page, newest first. Pages through all of them (fixed
        7 Oct 2026: only the newest 60 were read, so a comment on an older post
        that went viral later was never seen)."""
        out = []
        r = self._call("GET", "/me/media", {"fields": "id,caption,timestamp", "limit": 100})
        while True:
            out += r.get("data", [])
            nxt = r.get("paging", {}).get("next")
            if not nxt or len(out) >= limit:
                return out
            r = self._call("GET", nxt)

    def comments(self, media_id, since=None):
        """All comments, or, when the API returns them newest first, stop paging
        once a whole page is older than `since` (fixed 7 Oct 2026: re-reading
        5,000 comments on the big posts every run made runs take 45 minutes)."""
        out = []
        try:
            r = self._call("GET", f"/{media_id}/comments", {"fields": "id,text,timestamp,from,username,replies{username,from}", "limit": 50})
        except IGError:   # older API versions without nested replies
            r = self._call("GET", f"/{media_id}/comments", {"fields": "id,text,timestamp,from,username", "limit": 50})
        while True:
            page = r.get("data", [])
            out += page
            nxt = r.get("paging", {}).get("next")
            if not nxt or len(out) > 6000:
                return out
            if since is not None and page:
                stamps = [ts(c["timestamp"]) for c in page if c.get("timestamp")]
                newest_first = all(a >= b for a, b in zip(stamps, stamps[1:]))
                if newest_first and stamps and stamps[-1] < since:
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

def run(ig, cfg, state, now, log=print, checkpoint=None):
    dmcfg = cfg.get("dm", {})
    mode = os.environ.get("DM_MODE") or dmcfg.get("mode", "dry_run")
    start_at = ts(dmcfg["start_at"]) if dmcfg.get("start_at") else now
    look = os.environ.get("DM_LOOKBACK_HOURS") or dmcfg.get("dry_run_lookback_hours")
    if look and mode != "live":          # test runs only: look further back
        start_at = now - timedelta(hours=float(look))
    window_start = max(start_at, now - timedelta(days=WINDOW_DAYS))
    rules, exclude = load_rules()
    forget_retryable(state)

    try:
        who = ig.me()
    except IGError as e:
        log(f"CONNECTION BROKEN: {e}")
        return 2, 0
    own = {str(who.get("user_id", "")), who.get("username", "")}
    log(f"connected to @{who.get('username')} · mode={mode} · handling comments after {window_start.isoformat()}")

    started = time.monotonic()
    sends = errors = skipped = bounced = streak = posts_read = thanked = 0
    waiting = {}
    failures = []
    active = []                      # (media, rule) for every recent post with a rule, newest first
    pins = state.setdefault("_media_rules", {})     # media id -> rule id, fixed 7 Oct 2026
    by_id = {r[3]: r for r in rules}
    unmatched = []
    desk_seen = []                   # (media, rule, comments in the window) for the Reply Desk
    for m in ig.recent_media():
        rule = by_id.get(pins.get(m["id"])) or rule_for(m.get("caption", ""), rules)
        if rule:
            # Once a post has matched, remember it by its id: editing the caption
            # later (it happened to the Opus 5.5 and iOS 27 posts) cannot break it.
            pins[m["id"]] = rule[3]
            active.append((m, rule))
        elif any(k in (m.get("caption") or "") for k in CTA_MARKS) and \
                ts(m["timestamp"]) >= now - timedelta(days=WINDOW_DAYS):
            unmatched.append({"id": m["id"], "caption": (m.get("caption") or "")[:60]})
    for u in unmatched:
        log(f"NO DM RULE for a post that asks for a keyword: {u['caption']}")
    for m, rule in active:
        # No cut-off on the POST's age (fixed 7 Oct 2026): Instagram's 7-day limit
        # is on the COMMENT, and old posts (Claude slides, Gemini, Photoshop) keep
        # pulling keyword comments. window_start already limits comments to 7 days.
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
        if time.monotonic() - started > RUN_BUDGET_S:
            log("time budget for this run used, the rest go next run")
            break
        try:
            comments = ig.comments(m["id"], since=window_start)
        except IGError as e:
            # One unreadable post must not stop the others (fixed 7 Oct 2026).
            err = str(e)[:300]
            failures.append({"post": rid, "user": "", "error": "read: " + err})
            log(f"READ FAILED {rid}: {err}")
            continue
        fresh = [c for c in comments if ts(c["timestamp"]) >= window_start]
        desk_seen.append((m, rule, fresh))
        posts_read += 1
        log(f"post {rid}: {len(comments)} comments read, {len(fresh)} in the window")
        # Oldest first (8 Oct 2026): Instagram returns newest first, so with a
        # backlog the oldest comments ran out of their 7-day DM window unsent.
        for c in sorted(comments, key=lambda c: c.get("timestamp", "")):
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
            if sends + errors >= MAX_SENDS_PER_RUN:
                log("send limit for this run reached, the rest go next run")
                break
            if streak >= MAX_ERROR_STREAK:
                log(f"{streak} failures in a row, Instagram is throttling: stopping, the rest go next run")
                break
            if mode != "live":
                log(f"[dry run] {rid}: would DM @{user} for «{c.get('text','')[:30]}»")
                continue
            try:
                ig.private_reply(c["id"], vary(msg))
            except IGError as e:
                errors += 1
                streak += 1
                err = str(e)[:300]
                failures.append({"post": rid, "user": user, "error": err})
                log(f"DM FAILED {rid} @{user}: {err}")
                # Fixed 7 Oct 2026: a burst of failures is Instagram throttling,
                # not hundreds of closed inboxes. Only a lone closed-inbox error
                # is final; everything else is retried on a later run.
                tries = state.setdefault("_tries", {})
                tries[c["id"]] = tries.get(c["id"], 0) + 1
                if (BOUNCE_CODE in err and streak == 1) or tries[c["id"]] >= MAX_TRIES:
                    # Final: a closed inbox, or a comment Instagram keeps refusing
                    # (same HTTP 500 run after run). Leave the public reply asking
                    # them to DM the keyword, so nobody is left without an answer.
                    done[c["id"]] = {"user": user, "at": now.isoformat(), "failed": err, "tries": tries.pop(c["id"]),
                                     "c_at": c.get("timestamp", ""), "text": (c.get("text") or "")[:120]}
                    bounce(ig, c["id"], done[c["id"]], kws[0], now, log, rid)
                time.sleep(SEND_GAP_S * 3)
                continue
            streak = 0
            done[c["id"]] = {"user": user, "at": now.isoformat()}
            users_done.add(user)
            sends += 1
            if checkpoint:
                checkpoint()
            log(f"DM sent {rid} @{user}")
            try:
                ig.public_reply(c["id"], random.choice(PUBLIC_REPLIES))
            except IGError as e:
                done[c["id"]]["public_failed"] = str(e)[:200]
                log(f"public reply failed {rid} @{user}: {e}")
            time.sleep(SEND_GAP_S)
        if mode == "live" and thanked < THANKS_PER_RUN:
            thanked += thank_emoji(ig, fresh, state, own, now, log, THANKS_PER_RUN - thanked)
        left = count_waiting(fresh, done, own, kws, exclude)
        if left:
            waiting[rid] = left
        if sends + errors >= MAX_SENDS_PER_RUN or streak >= MAX_ERROR_STREAK:
            break
    queue_sent = run_queue(ig, state, own, mode, now, log, extra=auto_items(state, now, log)) if mode == "live" else 0
    desk_snapshot(state, desk_seen, own, exclude, now)
    try:
        desk_inbox(ig, state, own, mode, now, log)
    except Exception as e:                       # never break the comment job
        log(f"desk inbox skipped: {e}")
    try:
        phone_alerts(state, now, log)
    except Exception as e:
        log(f"phone alert skipped: {e}")
    inbox_sent = 0
    if dmcfg.get("inbox", True) and sends < MAX_SENDS_PER_RUN:
        inbox_sent = answer_inbox(ig, state, active, own, exclude, mode, max(start_at, now - timedelta(hours=INBOX_HOURS)),
                                  now, MAX_SENDS_PER_RUN - sends, log)
    state["_report"] = {"at": now.isoformat(), "mode": mode, "sent": sends, "failed": errors,
                        "skipped": skipped, "inbox_sent": inbox_sent, "bounce_backlog": bounced,
                        "queue_replies": queue_sent, "thanks": thanked,
                        "failures": failures[:20]}
    log(f"done: {sends} sent, {errors} failed, {skipped} skipped, {inbox_sent} answered from the inbox")
    alert = health(state, now, mode, sends + inbox_sent, waiting, unmatched,
                   posts_read, len(active), log)
    # Fail the job (GitHub then emails the owner) when sending is broken
    # outright, or when health() raises an alert.
    return (1 if (errors and not sends) or alert else 0), sends


def has_our_reply(c, own):
    replies = (c.get("replies") or {}).get("data", [])
    return any((r.get("username") in own) or (str((r.get("from") or {}).get("id", "")) in own) for r in replies)


def thank_emoji(ig, comments, state, own, now, log, budget):
    """Comments that are only emoji or hearts get a short threaded thank-you
    (Ehsan, 7 Oct 2026: never leave a comment without the right response)."""
    log_ = state.setdefault("_thanked", {})
    n = 0
    for c in comments:
        if n >= budget:
            break
        frm = c.get("from") or {}
        user = frm.get("username") or c.get("username", "")
        if c["id"] in log_ or user in own or str(frm.get("id", "")) in own or has_our_reply(c, own):
            continue
        if any(ch.isalnum() for ch in (c.get("text") or "")):
            continue
        try:
            ig.public_reply(c["id"], THANKS[len(log_) % len(THANKS)])
            log_[c["id"]] = {"user": user, "at": now.isoformat()}
            n += 1
            time.sleep(SEND_GAP_S)
        except IGError as e:
            log(f"thank-you reply failed @{user}: {e}")
            break
    return n


def near_keyword(text, keyword):
    k = norm(keyword)
    return bool(k) and any(edit_distance(w, k) <= 2 for w in tokens(text) if len(w) >= 3)


def auto_items(state, now, log):
    """Reply Desk auto-send (added 7 Oct 2026). Groups Ehsan switched on in the
    app (desk_auto.json) are answered here without waiting for approval, using
    the last desk snapshot. Only "chat" (a thank-you) and "wants_dm" (the post's
    DM) can ever be switched on; questions and spam always wait for him."""
    import desk_common
    auto = desk_common.load_auto()
    on = {g: v for g, v in auto["groups"].items() if g in desk_common.AUTO_GROUPS and v.get("on")}
    if not on:
        return []
    desk = state.get("_desk", {})
    done = state.get("_queue", {})
    skip = set(auto["skip"])
    try:
        rules, _ = load_rules()
        msgs = {r[3]: (r[1], r[2]) for r in rules}
    except Exception:
        msgs = {}
    thanks = auto["thanks"] or desk_common.THANKS
    out = []
    for it in desk.get("items", []):
        if it["id"] in done or it["id"] in skip:
            continue
        post = desk.get("posts", {}).get(it["media"], {})
        kws, msg = msgs.get(it.get("rule"), ([post.get("keyword", "")], ""))
        kw = post.get("keyword") or (kws[0] if kws else "")
        g = desk_common.group_of(it["text"], kw, near_keyword)
        if g not in on:
            continue
        try:
            at = ts(it["at"])
            since = ts(on[g].get("since", "2000-01-01T00:00:00+0000"))
        except (KeyError, ValueError):
            continue
        if at < since:
            continue
        if g == "chat":
            kind, text = "thanks", thanks[len(out) % len(thanks)]
        elif msg and now - at < timedelta(days=7):
            kind, text = "dm", msg
        else:
            kind, text = "nudge", "یه دایرکت «%s» بهمون بده تا برات بفرستیم 📩" % kw
        out.append({"id": it["id"], "media": it["media"], "user": it["user"], "kind": kind, "text": text,
                    "at": int(at.timestamp()), "via": "auto"})
    if out:
        log(f"auto-send: {len(out)} replies from switched-on groups ({', '.join(on)})")
    return out


def run_queue(ig, state, own, mode, now, log, extra=()):
    """Post the hand-written threaded replies in reply_queue.json, a few per run.
    Answers first, then thank-yous, then the 'DM us the keyword' replies.
    YouTube items (platform "yt") are left for scripts/yt_comments.py."""
    q = [i for i in load(QUEUE, {"items": []}).get("items", []) if i.get("platform", "ig") == "ig"]
    have = {i["id"] for i in q}
    q += [i for i in extra if i["id"] not in have]
    done = state.setdefault("_queue", {})
    order = {"dm": 0, "answer": 0, "thanks": 1, "nudge": 2}
    todo = [i for i in q if i.get("text") and i["id"] not in done]
    todo.sort(key=lambda i: (order.get(i.get("kind"), 3), -int(i.get("at") or 0)))
    sent = fails = 0
    for item in todo:
        if sent >= QUEUE_PER_RUN or fails >= MAX_ERROR_STREAK:
            break
        cid = item["id"]
        try:
            c = ig._call("GET", f"/{cid}", {"fields": "id,replies{username,from}"})
            # A retry from the Failed DMs tab: our "DM us the keyword" reply is
            # already under the comment, so do not treat that as answered.
            if has_our_reply(c, own) and not item.get("retry"):
                done[cid] = {"at": now.isoformat(), "skipped": "already answered"}
                continue
            if item.get("kind") == "dm":
                # Reply Desk: the post's DM, sent as Instagram's one private reply
                # to this comment (allowed within 7 days of the comment).
                ig.private_reply(cid, item["text"])
                if item.get("media"):
                    state.setdefault(item["media"], {})[cid] = {"user": item.get("user", ""), "at": now.isoformat(), "via": "desk"}
                try:
                    ig.public_reply(cid, random.choice(PUBLIC_REPLIES))
                except IGError:
                    pass
            else:
                ig.public_reply(cid, item["text"])
            done[cid] = {"at": now.isoformat(), "kind": item.get("kind"), "via": item.get("via", "desk")}
            sent += 1
            fails = 0
        except IGError as e:
            err = str(e)[:200]
            log(f"queue reply failed {cid} @{item.get('user')}: {err}")
            if ("HTTP 400" in err and ("does not exist" in err or "Unsupported" in err)) or item.get("retry"):
                done[cid] = {"at": now.isoformat(), "failed": err}   # comment deleted, or a one-shot retry
            else:
                fails += 1
        time.sleep(SEND_GAP_S)
    left = len([i for i in q if i.get("text") and i["id"] not in done])
    if q:
        log(f"reply queue: {sent} posted this run, {left} left")
    state.setdefault("_health", {})["queue_left"] = left
    return sent


DESK_MAX = 400                # newest unanswered comments kept for the Reply Desk


def desk_snapshot(state, seen, own, exclude, now):
    """Unanswered comments for the Reply Desk app (desk/app.py), added 7 Oct 2026.
    Public comments only: the repo is public, so DMs are never written here.
    Leaves out our own comments, anything we already replied to, DM'd,
    thanked or queued, and keyword comments the job is about to DM."""
    handled = set(state.get("_thanked", {})) | set(state.get("_queue", {}))
    items = []
    for m, (_, kws, msg, rid), comments in seen:
        done = state.get(m["id"], {})
        for c in comments:
            frm = c.get("from") or {}
            user = frm.get("username") or c.get("username", "")
            if c["id"] in done or c["id"] in handled or user in own or str(frm.get("id", "")) in own:
                continue
            if has_our_reply(c, own) or matches(c.get("text", ""), kws, exclude):
                continue
            if not any(ch.isalnum() for ch in (c.get("text") or "")):
                continue                     # emoji-only: the job thanks those itself
            items.append({"id": c["id"], "media": m["id"], "rule": rid, "user": user,
                          "text": (c.get("text") or "")[:500], "at": c.get("timestamp", "")})
    items.sort(key=lambda i: i["at"], reverse=True)
    posts = {}
    for m, (_, kws, msg, rid), _c in seen:
        posts[m["id"]] = {"rule": rid, "keyword": kws[0] if kws else "",
                          "caption": (m.get("caption") or "").split("\n")[0][:80]}
    state["_desk"] = {"at": now.isoformat(), "items": items[:DESK_MAX],
                      "posts": {k: v for k, v in posts.items() if any(i["media"] == k for i in items[:DESK_MAX])}}


def desk_inbox(ig, state, own, mode, now, log):
    """Reply Desk DM inbox (added 7 Oct 2026). Conversations whose last message
    is theirs and inside Instagram's 24-hour reply window are written to
    state/desk_inbox.enc, sealed with DESK_KEY so DM text never sits in the
    public repo. Replies Ehsan approves arrive sealed in desk_out.enc and are
    sent here. Keyword DMs are still answered by answer_inbox()."""
    import desk_common
    key = os.environ.get("DESK_KEY", "").strip()
    if not key:
        return
    done = state.setdefault("_inbox_sent", {})
    out = desk_common.read_sealed(desk_common.OUTBOX_ENC, key, {"items": []})
    sent = 0
    if mode == "live":
        for it in out.get("items", []):
            if it.get("id") in done or not it.get("uid") or not it.get("text"):
                continue
            if sent >= 10:
                break
            try:
                ig.send_to_user(it["uid"], it["text"])
                done[it["id"]] = {"at": now.isoformat()}
                sent += 1
            except IGError as e:
                done[it["id"]] = {"at": now.isoformat(), "failed": str(e)[:200]}
                log(f"desk DM failed: {e}")
            time.sleep(SEND_GAP_S)
    convs = ig.conversations()
    keyword = {k for k in state.get("_inbox", {})}
    items = []
    for conv in convs:
        msgs = sorted((conv.get("messages") or {}).get("data", []), key=lambda x: x.get("created_time", ""))
        if not msgs:
            continue
        last = msgs[-1]
        frm = last.get("from") or {}
        uid, user = str(frm.get("id", "")), frm.get("username", "")
        if not uid or uid in own or user in own or last.get("id") in keyword or last.get("id") in done:
            continue
        try:
            if now - ts(last["created_time"]) > timedelta(hours=23):
                continue
        except (KeyError, ValueError):
            continue
        thread = [{"me": (str((m.get("from") or {}).get("id", "")) in own or (m.get("from") or {}).get("username") in own),
                   "text": (m.get("message") or "")[:600], "at": m.get("created_time", "")} for m in msgs[-6:]]
        items.append({"id": last["id"], "uid": uid, "user": user, "at": last.get("created_time", ""), "thread": thread})
    import hashlib
    digest = hashlib.sha256(json.dumps(items, sort_keys=True).encode()).hexdigest()[:16]
    if digest != state.get("_inbox_hash") or not os.path.exists(os.path.join(ROOT, "state", "desk_inbox.enc")):
        desk_common.write_sealed(os.path.join(ROOT, "state", "desk_inbox.enc"), key, {"at": now.isoformat(), "items": items})
        state["_inbox_hash"] = digest
    state.setdefault("_health", {})["inbox_waiting"] = len(items)
    if sent:
        log(f"desk inbox: {sent} DMs sent")


def phone_alerts(state, now, log):
    """Push to Ehsan's phone through ntfy (added 7 Oct 2026): questions or DMs
    waiting more than 2 hours, once each, never 23:00-08:00 London; and a
    Monday-morning nudge that the weekly summary is ready. Counts only, no
    comment text, because ntfy topics are not private."""
    import desk_common
    from zoneinfo import ZoneInfo
    topic = os.environ.get("NTFY_TOPIC", "").strip()
    if not topic:
        return
    local = now.astimezone(ZoneInfo("Europe/London"))
    if local.hour < 8 or local.hour >= 23:
        return
    seen = state.setdefault("_alerted", {})
    old = now - timedelta(hours=2)
    new_q = []
    desk = state.get("_desk", {})
    for it in desk.get("items", []):
        if it["id"] in seen or it["id"] in state.get("_queue", {}):
            continue
        kw = desk.get("posts", {}).get(it["media"], {}).get("keyword", "")
        try:
            late = ts(it["at"]) < old and ts(it["at"]) > now - timedelta(days=3)
        except (KeyError, ValueError):
            continue
        if late and desk_common.group_of(it["text"], kw, near_keyword) == "question":
            new_q.append(it["id"])
    dms = state.get("_health", {}).get("inbox_waiting", 0)
    seen_fail = state.setdefault("_alerted_fail", {})
    new_fail = []
    for k, recs in state.items():
        if k.startswith("_") or not isinstance(recs, dict):
            continue
        for cid, r in recs.items():
            if r.get("failed") and cid not in seen_fail:
                try:
                    if datetime.fromisoformat(r["at"]) > now - timedelta(days=1):
                        new_fail.append(cid)
                except (KeyError, ValueError):
                    pass
    lines = []
    if new_q:
        lines.append(f"{len(new_q)} question{'s' if len(new_q) > 1 else ''} waiting over 2 hours")
    last_dm = state.get("_alerted_dm", "")
    if dms and (not last_dm or datetime.fromisoformat(last_dm) < now - timedelta(hours=3)):
        lines.append(f"{dms} DM{'s' if dms > 1 else ''} waiting for a reply")
        state["_alerted_dm"] = now.isoformat()
    if new_fail:
        lines.append(f"{len(new_fail)} keyword DM{'s' if len(new_fail) > 1 else ''} failed, see the Failed DMs tab")
    week = local.strftime("%G-W%V")
    if local.weekday() == 0 and state.get("_weekly_push") != week:
        lines.append("Weekly summary is ready in the Weekly tab")
        state["_weekly_push"] = week
    if not lines:
        return
    req = urllib.request.Request("https://ntfy.sh/" + urllib.parse.quote(topic), data="\n".join(lines).encode(),
                                 headers={"Title": "Reply Desk", "Tags": "speech_balloon"}, method="POST")
    urllib.request.urlopen(req, timeout=20).read()
    for i in new_q:
        seen[i] = now.isoformat()
    for i in new_fail:
        seen_fail[i] = now.isoformat()
    state["_alerted_fail"] = {k: v for k, v in seen_fail.items() if v >= (now - timedelta(days=10)).isoformat()}
    cut = (now - timedelta(days=10)).isoformat()
    state["_alerted"] = {k: v for k, v in seen.items() if v >= cut}
    log("phone alert: " + "; ".join(lines))


def count_waiting(comments, done, own, kws, exclude):
    """Keyword comments in the window that still have no DM and no reply from us."""
    users = {v.get("user") for v in done.values() if "failed" not in v}
    n = 0
    for c in comments:
        frm = c.get("from") or {}
        user = frm.get("username") or c.get("username", "")
        if c["id"] in done or user in own or str(frm.get("id", "")) in own or user in users:
            continue
        if not matches(c.get("text", ""), kws, exclude):
            continue
        replies = (c.get("replies") or {}).get("data", [])
        if any((r.get("username") in own) or (str((r.get("from") or {}).get("id", "")) in own) for r in replies):
            continue
        n += 1
    return n


def health(state, now, mode, sent, waiting, unmatched, posts_read, posts_total, log):
    """Write state['_health'] every run and decide whether to alert (added 7 Oct 2026,
    after a bug left ~800 people without their DM for days unnoticed)."""
    h = state.setdefault("_health", {})
    if sent:
        h["last_sent_at"] = now.isoformat()
    h.update({"at": now.isoformat(), "mode": mode, "waiting": waiting,
              "waiting_total": sum(waiting.values()), "unmatched_posts": unmatched,
              "posts_read": posts_read, "posts_with_rule": posts_total})
    problems = []
    last = h.get("last_sent_at")
    if mode == "live" and h["waiting_total"] and \
            (not last or datetime.fromisoformat(last) < now - timedelta(hours=STALL_ALERT_H)):
        problems.append(f"{h['waiting_total']} keyword comments waiting and nothing sent for "
                        f"{STALL_ALERT_H}+ hours: {waiting}")
    if unmatched:
        problems.append(f"{len(unmatched)} post(s) ask for a keyword but have no DM rule: "
                        + "; ".join(u["caption"] for u in unmatched))
    h["problems"] = problems
    if not problems:
        h.pop("alerted_at", None)
        return False
    for p in problems:
        log("ALERT: " + p)
    last_alert = h.get("alerted_at")
    if last_alert and datetime.fromisoformat(last_alert) > now - timedelta(hours=ALERT_REPEAT_H):
        return False                       # already emailed for this, stay quiet
    h["alerted_at"] = now.isoformat()
    return True


def forget_retryable(state):
    """Drop failure records that were not final, so those comments are tried again:
    Instagram 500s, and closed-inbox errors whose public reply also failed (the
    7 Oct 2026 throttling burst). Real closed inboxes keep their record."""
    for mid, recs in state.items():
        if mid.startswith("_") or not isinstance(recs, dict):
            continue
        for cid in list(recs):
            r = recs[cid]
            f = r.get("failed", "")
            if f and ("bounce_failed" in r or ("HTTP 500" in f and not r.get("tries"))):
                del recs[cid]


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
        if mid.startswith("_") and mid not in ("_inbox", "_inbox_sent"):
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
    # Save after every send and on any crash, so a run that dies half way
    # (7 Oct 2026: two runs died after sending and recorded nothing) keeps
    # its record and nobody is messaged twice.
    try:
        code, _ = run(ig, cfg, state, now, checkpoint=lambda: save(STATE, state))
    finally:
        prune(state, now)
        save(STATE, state)
    return code


if __name__ == "__main__":
    sys.exit(main())
