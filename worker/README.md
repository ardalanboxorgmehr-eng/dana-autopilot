# dana-gate: follow gate for Dana DMs (26 Nov 2026)

Flow: comment > DM with button (dm_reply.py) > tap > Worker checks the follow >
not following: "follow then tap" button > following: the post's dm_single text.
If Instagram will not say whether they follow, the content is sent anyway.

## Turn it on (once, from Terminal in ~/Desktop/dana-autopilot/worker)

1. npx wrangler login                (free Cloudflare account)
2. npx wrangler deploy               (prints the URL, https://dana-gate.<name>.workers.dev)
3. npx wrangler secret put IG_ACCESS_TOKEN   (same token as the GitHub secret)
   npx wrangler secret put APP_SECRET        (Meta app > App settings > Basic > App secret)
   npx wrangler secret put VERIFY_TOKEN      (any word you choose)
4. Meta app "Dana Autopilot" > Instagram > Webhooks: callback URL = the Worker URL,
   verify token = the same word, subscribe to messaging_postbacks.
5. config.json: dm.gate = true, commit, push.

When the Instagram token is renewed, run step 3's IG_ACCESS_TOKEN line again.
Telegram later: add a second button to the content message in worker.js.
