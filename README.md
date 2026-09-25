# dana-autopilot

Posts the دانستنی روز carousels to @danestani.ruzz on its own, with no browser
and no Mac involved. Slides are built from a spec, hosted on GitHub Pages, and
published through Instagram's Content Publishing API on a schedule.

New here? Read **SETUP.md** first.

---

## How it works

```
content/<post-id>/          the source of truth for one post
  spec.json                 slide layout for the builder
  art.py                    optional, draws the artwork the slides use
  caption.txt               the Instagram caption, exactly as posted
  dm.json                   comment keywords and DM text

        │  build workflow (on push, and nightly)
        ▼
docs/slides/<post-id>/      1080x1350 JPEGs, served by GitHub Pages
        │
        │  publish workflow (every 15 minutes)
        ▼
queue.json                  what goes out when, and what happened
        │
        ▼
   Instagram
```

Nothing publishes because a clock struck a time. The publish job wakes up every
15 minutes, reads `queue.json`, and acts on anything that is due. That is what
makes it survive a late runner, a missed cycle, or the BST/GMT change without
anyone editing a cron line.

---

## queue.json

```json
{
  "posts": [
    {
      "id": "2026-10-02-0600",
      "publish_at": "2026-10-02T06:00",
      "slides": 7,
      "keyword": "کشف",
      "notes": "short description for humans",
      "status": "pending"
    }
  ]
}
```

`publish_at` is **London local time**, written plainly with no timezone on the
end. The code applies Europe/London, so 06:00 is 06:00 to you in both summer and
winter.

`status` is the whole state machine:

| status | meaning |
|---|---|
| `pending` | will publish when its time comes |
| `published` | done, `media_id` and `published_at` recorded |
| `error` | tried and failed, reason in `error`, will not retry on its own |
| `missed` | more than 6 hours overdue, deliberately skipped |
| `external` | scheduled somewhere else, autopilot must not touch it |

To retry a failed post: fix the cause, set `status` back to `pending`, adjust
`publish_at` if the moment has passed.

---

## Adding a post

1. Make `content/<post-id>/` with a spec, caption, and dm.json.
2. Add the entry to `queue.json` with `"status": "pending"`.
3. Push. The build workflow renders the slides and publishes them to Pages.
4. The publish workflow takes it from there.

Post ids are `YYYY-MM-DD-HHMM` so the folder sorts by time and matches the slot.

---

## Running things by hand

```bash
pip install Pillow

python scripts/build_all.py                  # build what changed
python scripts/build_all.py --force          # rebuild everything
python scripts/build_all.py --only 2026-10-02-0600

python scripts/selftest.py                   # prove the publish logic, touches nothing

IG_ACCESS_TOKEN=... IG_USER_ID=... python scripts/publish.py --dry-run
```

`selftest.py` runs the real publisher against a local web server and a fake
Graph API, covering due, not-yet-due, already-published, stale, missing slides
and missing caption. Run it after changing `publish.py`.

---

## Deliberate choices

**Stale posts are skipped, not published.** If the runner is down for a day, a
06:00 post does not go out at 19:00 to a sleeping audience, and a backlog does
not dump all at once. It is marked `missed` and the run fails so you hear about
it.

**The publisher checks the slide URLs itself** before calling Meta. Meta fetches
those images on its own servers, so a bad URL otherwise surfaces as a vague
error deep in their pipeline instead of "this file 404s".

**A half-finished post resumes.** The carousel container id is saved before
publishing, so a crash between building and publishing does not rebuild
everything.

**Secrets are never printed.** The token refresh script will not log a token
even on failure.

---

## Limits worth knowing

- 100 API posts per 24 hours. A carousel counts as one. We use two a day.
- JPEG only. No PNG, no WebP.
- Every slide is cropped to match the first slide's aspect ratio. Keep them all
  1080x1350.
- Up to 10 slides per carousel.
- Captions max 2200 characters. The publisher refuses anything longer rather
  than letting Instagram truncate it.
