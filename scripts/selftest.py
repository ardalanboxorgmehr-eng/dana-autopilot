#!/usr/bin/env python3
"""
Prove the publish logic end to end without touching Instagram.

Serves docs/ over a local HTTP server so the slide-URL checks are real, points
config at it, and runs publish.py --dry-run against a queue covering every case:
due, not yet due, already published, stale, missing caption, missing slide.

Run: python scripts/selftest.py
"""
import json, os, shutil, subprocess, sys, tempfile, threading, functools, http.server, socketserver
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LONDON = ZoneInfo("Europe/London")
FAILED = []


def check(name, cond, detail=""):
    print(("  PASS  " if cond else "  FAIL  ") + name + (f"   {detail}" if detail and not cond else ""))
    if not cond:
        FAILED.append(name)


def serve(directory):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=directory)
    handler.log_message = lambda *a, **k: None
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, httpd.server_address[1]


def main():
    work = tempfile.mkdtemp(prefix="dana-selftest-")
    repo = os.path.join(work, "repo")
    shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns(".git", "__pycache__"))

    httpd, port = serve(os.path.join(repo, "docs"))
    base = f"http://127.0.0.1:{port}"

    cfg = json.load(open(os.path.join(repo, "config.json"), encoding="utf-8"))
    cfg["site_base_url"] = base
    cfg["ig_user_id"] = "17841400000000000"
    json.dump(cfg, open(os.path.join(repo, "config.json"), "w"), indent=2)

    now = datetime.now(LONDON)
    real = "2026-10-01-0600"          # exists with 7 slides and a caption
    other = "2026-10-01-1530"

    # a post whose slides do not exist on the server
    ghost_dir = os.path.join(repo, "content", "ghost-post")
    os.makedirs(ghost_dir, exist_ok=True)
    open(os.path.join(ghost_dir, "caption.txt"), "w").write("ghost\n")

    # a post with slides but no caption file
    nocap = os.path.join(repo, "docs", "slides", "nocap-post")
    shutil.copytree(os.path.join(repo, "docs", "slides", real), nocap)

    queue = {"posts": [
        {"id": real, "publish_at": (now - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M"),
         "slides": 7, "status": "pending", "notes": "due now"},
        {"id": other, "publish_at": (now + timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M"),
         "slides": 7, "status": "pending", "notes": "not yet due"},
        {"id": "already-done", "publish_at": (now - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M"),
         "slides": 7, "status": "published", "notes": "must be left alone"},
        {"id": "stale-post", "publish_at": (now - timedelta(hours=20)).strftime("%Y-%m-%dT%H:%M"),
         "slides": 7, "status": "pending", "notes": "far too late"},
        {"id": "ghost-post", "publish_at": (now - timedelta(minutes=2)).strftime("%Y-%m-%dT%H:%M"),
         "slides": 3, "status": "pending", "notes": "slides not on the server"},
        {"id": "nocap-post", "publish_at": (now - timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M"),
         "slides": 7, "status": "pending", "notes": "no caption file"},
    ]}
    json.dump(queue, open(os.path.join(repo, "queue.json"), "w"), ensure_ascii=False, indent=2)

    print("running publish.py --dry-run\n")
    r = subprocess.run([sys.executable, os.path.join(repo, "scripts", "publish.py"), "--dry-run"],
                       capture_output=True, text=True)
    print(r.stdout)
    if r.stderr:
        print("stderr:\n" + r.stderr)

    q = {p["id"]: p for p in json.load(open(os.path.join(repo, "queue.json"), encoding="utf-8"))["posts"]}

    print("results:")
    check("due post is published", q[real]["status"] == "published", q[real].get("status"))
    check("published post got a media id", bool(q[real].get("media_id")))
    check("future post untouched", q[other]["status"] == "pending", q[other].get("status"))
    check("already published left alone", q["already-done"]["status"] == "published")
    check("stale post marked missed, not published", q["stale-post"]["status"] == "missed",
          q["stale-post"].get("status"))
    check("missing slides -> error not publish", q["ghost-post"]["status"] == "error",
          q["ghost-post"].get("status"))
    check("missing slides error names the URL", "unreachable" in q["ghost-post"].get("error", ""))
    check("missing caption -> error not publish", q["nocap-post"]["status"] == "error",
          q["nocap-post"].get("status"))
    check("missing caption error is clear", "caption" in q["nocap-post"].get("error", "").lower())
    check("exit code flags the failures", r.returncode == 1, f"got {r.returncode}")
    check("no carousel id left behind on success", "carousel_id" not in q[real])

    # second run must not republish
    print("\nre-running to check it does not double post")
    r2 = subprocess.run([sys.executable, os.path.join(repo, "scripts", "publish.py"), "--dry-run"],
                        capture_output=True, text=True)
    q2 = {p["id"]: p for p in json.load(open(os.path.join(repo, "queue.json"), encoding="utf-8"))["posts"]}
    check("published post not republished", q2[real]["published_at"] == q[real]["published_at"])
    check("second run publishes nothing new",
          "nothing due" in r2.stdout or ">>>" not in r2.stdout, r2.stdout[-200:])

    httpd.shutdown()
    shutil.rmtree(work, ignore_errors=True)

    print()
    if FAILED:
        print(f"{len(FAILED)} check(s) failed: {', '.join(FAILED)}")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
