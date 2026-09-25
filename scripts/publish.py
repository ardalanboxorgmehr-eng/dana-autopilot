#!/usr/bin/env python3
"""
Publish due دانستنی روز carousels to Instagram via the Content Publishing API.

Runs headless (GitHub Actions). Reads queue.json, finds posts whose London-local
publish time has arrived, uploads each slide as a carousel item, wraps them in a
carousel container, publishes, and records the result back into queue.json.

Env:
  IG_ACCESS_TOKEN  required, long-lived Instagram token
  IG_USER_ID       optional, overrides config.json
  DRY_RUN=1        do everything except the calls that change Instagram
"""
import json, os, sys, time, argparse, urllib.parse, urllib.request, urllib.error
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, "config.json")
QUEUE = os.path.join(ROOT, "queue.json")

# A post more than this many hours overdue is NOT published. Stops a burst of
# back-dated posts after the runner has been down for a while.
STALE_AFTER_HOURS = 6

CONTAINER_TIMEOUT_S = 300
CONTAINER_POLL_S = 5


class PublishError(RuntimeError):
    pass


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, path)


# ---------------------------------------------------------------- Graph API

class Graph:
    def __init__(self, ig_user_id, token, version, dry_run=False):
        self.ig = ig_user_id
        self.token = token
        self.base = f"https://graph.instagram.com/{version}"
        self.dry_run = dry_run
        self._fake = 0

    def _call(self, method, path, params):
        url = f"{self.base}{path}"
        params = dict(params, access_token=self.token)
        data = urllib.parse.urlencode(params).encode()
        if method == "GET":
            url = f"{url}?{urllib.parse.urlencode(params)}"
            data = None
        req = urllib.request.Request(url, data=data, method=method)
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")
            raise PublishError(f"{method} {path} -> HTTP {e.code}: {body}") from None
        except urllib.error.URLError as e:
            raise PublishError(f"{method} {path} -> {e.reason}") from None

    def create_item(self, image_url):
        """One carousel slide."""
        if self.dry_run:
            self._fake += 1
            return f"DRYRUN_ITEM_{self._fake}"
        r = self._call("POST", f"/{self.ig}/media",
                       {"image_url": image_url, "is_carousel_item": "true"})
        return r["id"]

    def create_carousel(self, children, caption):
        if self.dry_run:
            return "DRYRUN_CAROUSEL"
        r = self._call("POST", f"/{self.ig}/media",
                       {"media_type": "CAROUSEL",
                        "children": ",".join(children),
                        "caption": caption})
        return r["id"]

    def status(self, container_id):
        if self.dry_run:
            return "FINISHED"
        r = self._call("GET", f"/{container_id}", {"fields": "status_code"})
        return r.get("status_code", "UNKNOWN")

    def publish(self, container_id):
        if self.dry_run:
            return "DRYRUN_MEDIA"
        r = self._call("POST", f"/{self.ig}/media_publish",
                       {"creation_id": container_id})
        return r["id"]

    def identity(self):
        """Real call even in a dry run: this is how we prove the token works."""
        return self._call("GET", f"/{self.ig}", {"fields": "username,account_type"})

    def quota(self):
        # Deliberately NOT faked in dry-run mode. A dry run that never talks to
        # Meta cannot tell you the token is good, which is the main thing you
        # want to know before a real post is due.
        return self._call("GET", f"/{self.ig}/content_publishing_limit",
                          {"fields": "config,quota_usage"})

    def wait_ready(self, container_id, label):
        """Containers are built async. Poll until FINISHED or give up."""
        deadline = time.time() + CONTAINER_TIMEOUT_S
        last = None
        while time.time() < deadline:
            last = self.status(container_id)
            if last == "FINISHED":
                return
            if last in ("ERROR", "EXPIRED"):
                raise PublishError(f"{label} container {container_id} is {last}")
            time.sleep(CONTAINER_POLL_S)
        raise PublishError(
            f"{label} container {container_id} stuck at {last} after "
            f"{CONTAINER_TIMEOUT_S}s")


# ---------------------------------------------------------------- helpers

def slide_urls(cfg, post):
    base = cfg["site_base_url"].rstrip("/")
    return [f"{base}/slides/{post['id']}/slide-{i:02d}.jpg"
            for i in range(1, post["slides"] + 1)]


def check_reachable(urls):
    """Meta fetches these itself, so a broken URL fails deep inside their
    pipeline with a vague error. Check here instead, where the message is clear."""
    bad = []
    for u in urls:
        try:
            req = urllib.request.Request(u, method="HEAD")
            with urllib.request.urlopen(req, timeout=30) as r:
                ctype = (r.headers.get("Content-Type") or "").split(";")[0].strip()
                if ctype != "image/jpeg":
                    bad.append(f"{u} served as {ctype or 'no content-type'}, need image/jpeg")
        except Exception as e:
            bad.append(f"{u} unreachable ({e})")
    if bad:
        raise PublishError("slide images are not publishable:\n  " + "\n  ".join(bad))


def read_caption(post):
    path = os.path.join(ROOT, "content", post["id"], "caption.txt")
    if not os.path.exists(path):
        raise PublishError(f"no caption at content/{post['id']}/caption.txt")
    text = open(path, encoding="utf-8").read().strip()
    if not text:
        raise PublishError(f"caption for {post['id']} is empty")
    if len(text) > 2200:
        raise PublishError(f"caption for {post['id']} is {len(text)} chars, max 2200")
    return text


def due_posts(queue, now_london):
    """Pending posts whose time has come and which are not stale."""
    due, stale = [], []
    for p in queue["posts"]:
        if p.get("status") != "pending":
            continue
        when = datetime.fromisoformat(p["publish_at"]).replace(
            tzinfo=ZoneInfo("Europe/London"))
        if when > now_london:
            continue
        if now_london - when > timedelta(hours=STALE_AFTER_HOURS):
            stale.append((p, when))
        else:
            due.append((p, when))
    due.sort(key=lambda x: x[1])
    return due, stale


# ---------------------------------------------------------------- main

def publish_one(g, cfg, post):
    caption = read_caption(post)
    urls = slide_urls(cfg, post)
    check_reachable(urls)

    # Resume a half-finished run rather than rebuilding every container.
    carousel_id = post.get("carousel_id")
    if not carousel_id:
        children = []
        for i, u in enumerate(urls, 1):
            cid = g.create_item(u)
            children.append(cid)
            print(f"    slide {i}/{len(urls)} -> {cid}", flush=True)
        for i, cid in enumerate(children, 1):
            g.wait_ready(cid, f"slide {i}")
        carousel_id = g.create_carousel(children, caption)
        post["carousel_id"] = carousel_id
        print(f"    carousel -> {carousel_id}", flush=True)
    else:
        print(f"    resuming carousel {carousel_id}", flush=True)

    g.wait_ready(carousel_id, "carousel")
    media_id = g.publish(carousel_id)

    post["status"] = "published"
    post["media_id"] = media_id
    post["published_at"] = datetime.now(ZoneInfo("Europe/London")).isoformat(timespec="seconds")
    post.pop("carousel_id", None)
    post.pop("error", None)
    return media_id


def health_check(g):
    """Prove the token, the account and the quota endpoint all work."""
    me = g.identity()
    print(f"connected to @{me.get('username','?')} "
          f"({me.get('account_type','?')}, id {me.get('id', g.ig)})")
    q = g.quota()
    used = q.get("quota_usage", 0)
    total = (q.get("config") or {}).get("quota_total", 100)
    print(f"publishing quota: {used}/{total} used in the last 24h")
    return used, total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="resolve everything, change nothing on Instagram")
    args = ap.parse_args()
    dry = args.dry_run or os.environ.get("DRY_RUN") == "1"

    cfg = load(CONFIG)
    queue = load(QUEUE)

    token = os.environ.get("IG_ACCESS_TOKEN", "")
    ig_user_id = os.environ.get("IG_USER_ID") or cfg.get("ig_user_id", "")
    if not dry:
        if not token:
            print("IG_ACCESS_TOKEN is not set", file=sys.stderr)
            return 2
        if not ig_user_id:
            print("IG_USER_ID is not set (config.json or env)", file=sys.stderr)
            return 2

    now = datetime.now(ZoneInfo("Europe/London"))
    print(f"now (London): {now:%Y-%m-%d %H:%M %Z}")

    # Build the client either way: a dry run with no token still exercises the
    # whole flow offline, which is what scripts/selftest.py relies on.
    g = Graph(ig_user_id, token, cfg.get("api_version", "v25.0"), dry_run=dry)
    used = total = None
    if token and ig_user_id:
        try:
            used, total = health_check(g)
        except PublishError as e:
            print(f"CANNOT REACH INSTAGRAM: {e}", file=sys.stderr)
            return 2
    else:
        print("no token set, skipping the Instagram connection check")

    due, stale = due_posts(queue, now)

    changed = False
    for p, when in stale:
        p["status"] = "missed"
        p["error"] = (f"more than {STALE_AFTER_HOURS}h overdue "
                      f"(was due {when:%Y-%m-%d %H:%M}), not published")
        changed = True
        print(f"MISSED {p['id']}: {p['error']}", file=sys.stderr)

    if not due:
        print("nothing due")
        if changed:
            save(QUEUE, queue)
        return 1 if stale else 0

    if used is not None and used + len(due) > total:
        print("would exceed the 24h publishing quota, stopping", file=sys.stderr)
        return 2

    failures = 0
    for p, when in due:
        print(f"\n>>> {p['id']}  due {when:%Y-%m-%d %H:%M}  "
              f"{p.get('notes','')}", flush=True)
        try:
            media_id = publish_one(g, cfg, p)
            print(f"    PUBLISHED as {media_id}")
        except PublishError as e:
            failures += 1
            p["status"] = "error"
            p["error"] = str(e)[:500]
            print(f"    FAILED: {e}", file=sys.stderr)
        finally:
            changed = True
            save(QUEUE, queue)

    if changed:
        save(QUEUE, queue)
    return 1 if (failures or stale) else 0


if __name__ == "__main__":
    sys.exit(main())
