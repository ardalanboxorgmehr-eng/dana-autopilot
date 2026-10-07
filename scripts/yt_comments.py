#!/usr/bin/env python3
"""
YouTube comments for the Reply Desk (added 7 Oct 2026).

Runs inside the comment-to-DM job. Does nothing until the three secrets
YT_CLIENT_ID, YT_CLIENT_SECRET and YT_REFRESH_TOKEN exist (set once with
desk/yt_setup.py on the Mac; the token never leaves the Mac except into GitHub).

  read  (about once an hour): newest uploads, their comment threads, and keeps the
        ones the channel has not answered in state/yt_desk.json for the app
  send  (every run): reply_queue.json items with "platform": "yt", up to 10 a run

YouTube has no DMs, so the only reply type is a threaded reply.
Quota: reading costs ~1 unit per video, each reply 50; the free 10,000 a day is plenty.
"""
import json, os, sys, time, urllib.parse, urllib.request, urllib.error
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state", "yt_desk.json")
QUEUE = os.path.join(ROOT, "reply_queue.json")
API = "https://www.googleapis.com/youtube/v3"
READ_EVERY_MIN = 55
VIDEOS = 30
KEEP = 300
SEND_PER_RUN = 10


def load(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def save(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, path)


def http(method, url, params=None, body=None, token=None, form=False):
    if params:
        url += "?" + urllib.parse.urlencode(params)
    headers = {}
    data = None
    if token:
        headers["Authorization"] = "Bearer " + token
    if body is not None:
        if form:
            data = urllib.parse.urlencode(body).encode()
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        else:
            data = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read()[:300].decode('utf-8', 'replace')}")


def access_token():
    cid, sec, ref = (os.environ.get(k, "").strip() for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"))
    if not (cid and sec and ref):
        return None
    r = http("POST", "https://oauth2.googleapis.com/token",
             body={"client_id": cid, "client_secret": sec, "refresh_token": ref, "grant_type": "refresh_token"}, form=True)
    return r["access_token"]


def read(tok, st, now):
    ch = http("GET", API + "/channels", {"part": "id,contentDetails,snippet", "mine": "true"}, token=tok)["items"][0]
    me = ch["id"]
    st["channel"] = {"id": me, "title": ch["snippet"]["title"]}
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    vids = http("GET", API + "/playlistItems", {"part": "contentDetails,snippet", "playlistId": uploads,
                                                "maxResults": VIDEOS}, token=tok).get("items", [])
    done = st.setdefault("done", {})
    items = []
    for v in vids:
        vid = v["contentDetails"]["videoId"]
        title = v["snippet"]["title"][:80]
        try:
            th = http("GET", API + "/commentThreads", {"part": "snippet,replies", "videoId": vid, "maxResults": 100,
                                                       "order": "time", "textFormat": "plainText"}, token=tok)
        except RuntimeError as e:
            if "commentsDisabled" in str(e):
                continue
            raise
        for t in th.get("items", []):
            top = t["snippet"]["topLevelComment"]
            s = top["snippet"]
            if (s.get("authorChannelId") or {}).get("value") == me or top["id"] in done:
                continue
            replies = (t.get("replies") or {}).get("comments", [])
            if any((r["snippet"].get("authorChannelId") or {}).get("value") == me for r in replies):
                continue
            items.append({"id": top["id"], "media": vid, "title": title, "user": s.get("authorDisplayName", ""),
                          "text": (s.get("textDisplay") or "")[:500], "at": s.get("publishedAt", ""),
                          "url": f"https://www.youtube.com/shorts/{vid}"})
    items.sort(key=lambda i: i["at"], reverse=True)
    st["items"] = items[:KEEP]
    st["at"] = now.isoformat()


def send(tok, st, now, log):
    done = st.setdefault("done", {})
    todo = [i for i in load(QUEUE, {"items": []}).get("items", [])
            if i.get("platform") == "yt" and i.get("text") and i["id"] not in done]
    sent = 0
    for it in todo[:SEND_PER_RUN]:
        try:
            http("POST", API + "/comments", {"part": "snippet"},
                 body={"snippet": {"parentId": it["id"], "textOriginal": it["text"]}}, token=tok)
            done[it["id"]] = {"at": now.isoformat(), "kind": it.get("kind")}
            sent += 1
        except RuntimeError as e:
            log(f"youtube reply failed {it['id']}: {e}")
            if "HTTP 404" in str(e):
                done[it["id"]] = {"at": now.isoformat(), "failed": str(e)[:200]}
            elif "HTTP 403" in str(e):
                break
        time.sleep(2)
    st["items"] = [i for i in st.get("items", []) if i["id"] not in done]
    st["queue_left"] = len(todo) - sent
    if todo:
        log(f"youtube: {sent} replies posted, {len(todo) - sent} left")


def main():
    now = datetime.now(timezone.utc)
    tok = access_token()
    if not tok:
        print("youtube: not connected yet (no YT_ secrets), skipping")
        return 0
    st = load(STATE, {})
    try:
        send(tok, st, now, print)
        last = st.get("at")
        if not last or datetime.fromisoformat(last) < now - timedelta(minutes=READ_EVERY_MIN):
            read(tok, st, now)
            print(f"youtube: {len(st['items'])} unanswered comments")
        st.pop("error", None)
    except Exception as e:  # never break the Instagram job
        st["error"] = f"{now.isoformat()} {str(e)[:300]}"
        print("youtube error:", e)
    cut = (now - timedelta(days=120)).isoformat()
    st["done"] = {k: v for k, v in st.get("done", {}).items() if v.get("at", "") >= cut}
    save(STATE, st)
    return 0


if __name__ == "__main__":
    sys.exit(main())
