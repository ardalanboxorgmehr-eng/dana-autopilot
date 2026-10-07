#!/usr/bin/env python3
"""
Connect the YouTube channel to the Reply Desk. Run once on the Mac:

    python3 desk/yt_setup.py ~/Downloads/client_secret_XXXX.json

It opens Google's sign-in in your browser, you pick the channel and allow access,
and it stores three GitHub secrets (YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN)
with the gh command. Nothing is printed and nothing is written to disk.
"""
import json, os, secrets, subprocess, sys, threading, urllib.parse, urllib.request, webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
REPO = "ardalanboxorgmehr-eng/dana-autopilot"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    with open(os.path.expanduser(sys.argv[1])) as f:
        c = json.load(f)
    c = c.get("installed") or c.get("web") or c
    cid, sec = c["client_id"], c["client_secret"]
    state = secrets.token_urlsafe(16)
    got = {}

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if q.get("state", [""])[0] == state and "code" in q:
                got["code"] = q["code"][0]
                msg = "YouTube connected. You can close this tab and go back to Terminal."
            else:
                msg = "Something went wrong: " + q.get("error", ["no code"])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(("<p style='font:18px sans-serif;margin:40px'>%s</p>" % msg).encode())

    srv = HTTPServer(("127.0.0.1", 0), H)
    redirect = "http://127.0.0.1:%d/" % srv.server_address[1]
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
        "client_id": cid, "redirect_uri": redirect, "response_type": "code", "scope": SCOPE,
        "access_type": "offline", "prompt": "consent", "state": state})
    print("Opening Google sign-in. Pick the YouTube channel for دانستنی روز and press Allow.")
    webbrowser.open(url)
    while "code" not in got:
        srv.handle_request()
    body = urllib.parse.urlencode({"code": got["code"], "client_id": cid, "client_secret": sec,
                                   "redirect_uri": redirect, "grant_type": "authorization_code"}).encode()
    with urllib.request.urlopen("https://oauth2.googleapis.com/token", body, timeout=30) as r:
        tok = json.loads(r.read())
    if "refresh_token" not in tok:
        print("Google did not return a refresh token. Run this again.")
        return 1
    for name, val in (("YT_CLIENT_ID", cid), ("YT_CLIENT_SECRET", sec), ("YT_REFRESH_TOKEN", tok["refresh_token"])):
        r = subprocess.run(["gh", "secret", "set", name, "-R", REPO], input=val, text=True, capture_output=True)
        if r.returncode:
            print("Could not save %s: %s" % (name, r.stderr.strip()))
            return 1
    print("Done. The job will start reading YouTube comments within 15 minutes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
