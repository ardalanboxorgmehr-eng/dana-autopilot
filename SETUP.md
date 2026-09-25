# Setup

Everything here is a one-off. After this the system runs without your Mac,
your phone, or any browser being open.

There are three parts: GitHub, Meta, and the first test post. Budget about
40 minutes, most of it waiting for pages to load.

---

## Part 1: GitHub (10 minutes)

**1. Create the repository**

A free account at github.com is enough. Make a new repository called
`dana-autopilot`.

Make it **public**. Two reasons: GitHub Pages on a private repo needs a paid
plan, and Meta has to be able to fetch the slide images anyway. Nothing secret
lives in the repo. The access token goes in Secrets, which stay private even on
a public repo.

The only real consequence is that someone could see next week's posts before
they go out. If that bothers you, say so and I will move image hosting to a
private bucket instead.

**2. Push this folder**

```bash
cd dana-autopilot
git init
git add .
git commit -m "dana autopilot"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/dana-autopilot.git
git push -u origin main
```

**3. Turn on Pages**

Repository → Settings → Pages → Source: **GitHub Actions**.

Your slides will be served from
`https://YOUR-USERNAME.github.io/dana-autopilot/slides/...`

**4. Set the site URL**

Edit `config.json` and replace `site_base_url` with that address, no trailing
slash:

```json
"site_base_url": "https://YOUR-USERNAME.github.io/dana-autopilot"
```

---

## Part 2: Meta (20 minutes)

The good news: because you are publishing to **your own** account, you do
**not** need App Review or Business Verification. Meta's Standard Access covers
an account that has a role on your own app. That is the part that usually takes
weeks, and it does not apply to you.

**5. Create the app**

1. Go to developers.facebook.com and log in with the account that manages
   @danestani.ruzz.
2. My Apps → Create App.
3. When asked what you are building, pick the option for **Instagram**. If it
   asks for an app type, choose **Business**.
4. In the app dashboard, add the **Instagram** product, then open
   **API setup with Instagram business login**.

**6. Generate the token**

In that same panel:

1. Add your Instagram account (@danestani.ruzz) to the app.
2. Under permissions make sure both of these are on:
   - `instagram_business_basic`
   - `instagram_business_content_publish`
3. Generate an access token and copy it.
4. On the same screen you will see your **Instagram user ID**, a long number
   starting 178414... Copy that too.

Keep the token somewhere safe for the next 5 minutes. Do not paste it into
chat, an email, or a file in the repo.

**7. Put them into GitHub**

Repository → Settings → Secrets and variables → Actions → New repository secret.

| Name | Value |
|---|---|
| `IG_ACCESS_TOKEN` | the token from step 6 |
| `IG_USER_ID` | the Instagram user ID from step 6 |

**8. Optional: hands-off token renewal**

Instagram tokens expire after 60 days. Without this, the system emails you when
it is running out and you redo step 6. With this, it renews itself.

Create a fine-grained personal access token (Settings → Developer settings →
Personal access tokens → Fine-grained), scoped to **this repository only**, with
**Secrets: Read and write**. Add it as a secret called `GH_PAT`.

Skip this if you would rather not have a token that can write secrets sitting in
the repo. Six manual renewals a year is not much.

---

## Part 3: First test post

**9. Dry run**

Actions → **publish due posts** → Run workflow → tick **dry run** → Run.

This resolves everything and changes nothing on Instagram. It proves the token
works, the slides are reachable, and the captions are valid. Read the log.

**10. A real one**

Put a single post in `queue.json` with a `publish_at` a few minutes ahead and
`"status": "pending"`. Wait for the schedule to pick it up, or run the workflow
by hand without the dry run box ticked.

Check the post on Instagram: slide order, the 4:5 crop, Farsi text not cut off,
caption and hashtags intact.

**The one thing to watch on the first real post:** Meta crops every slide in a
carousel to match the first one. All our slides are 1080x1350, so they should
all pass through untouched, but confirm it with your own eyes once before
trusting it.

---

## What still needs your Mac

Nothing, for posting.

Comment-to-DM is still ReplyRush or ManyChat for now. Doing that through the API
needs `instagram_manage_comments` plus `pages_messaging` and Advanced Access,
which does mean App Review. That is a separate project, worth doing once
publishing has been running cleanly for a couple of weeks.

---

## If something breaks

Every failed run emails you. The queue records the reason against the post.

- **Slide images unreachable** — the build workflow did not run, or Pages is not
  turned on, or `site_base_url` is wrong.
- **Post marked `missed`** — it was more than 6 hours late, so it was skipped
  rather than posted at the wrong time of day. Deliberate. Move the date and set
  it back to `pending` if you still want it out.
- **Token errors** — regenerate at step 6 and update the secret.
