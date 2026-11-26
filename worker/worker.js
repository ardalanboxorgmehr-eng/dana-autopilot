// Dana follow gate, 26 Nov 2026.
// Instagram calls this the moment someone taps a button in a Dana DM.
// SEND or FOLLOWED tap: check the follow, then send the post's content or ask to follow.
// Secrets (wrangler secret put): IG_ACCESS_TOKEN, APP_SECRET, VERIFY_TOKEN.

const API = "https://graph.instagram.com/v25.0";
const RAW = "https://raw.githubusercontent.com/ardalanboxorgmehr-eng/dana-autopilot/main";

const TXT = {
  follow: "تقریبا رسیدیم! 🙌\nاول پیج رو فالو کن، بعد دکمه‌ی زیر رو بزن تا برات بفرستم",
  again: "هنوز فالوت رو نمی‌بینم 🤔\nیه بار دیگه چک کن فالو شده باشه، بعد دوباره دکمه رو بزن",
  followed: "فالو کردم ✅",
  thanks: "مرسی که همراهمونی 💛\nاینم چیزی که قول داده بودم 👇\n\n",
};

export default {
  async fetch(req, env, ctx) {
    const url = new URL(req.url);
    if (req.method === "GET") {
      const ok = url.searchParams.get("hub.mode") === "subscribe" &&
        url.searchParams.get("hub.verify_token") === env.VERIFY_TOKEN;
      return new Response(ok ? url.searchParams.get("hub.challenge") : "forbidden", { status: ok ? 200 : 403 });
    }
    if (req.method !== "POST") return new Response("ok");
    const body = await req.text();
    if (!(await signed(body, req.headers.get("x-hub-signature-256") || "", env.APP_SECRET))) {
      return new Response("bad signature", { status: 401 });
    }
    // Answer Instagram at once; do the work after.
    ctx.waitUntil(handle(JSON.parse(body), env).catch((e) => console.log("error", e.message)));
    return new Response("EVENT_RECEIVED");
  },
};

async function handle(data, env) {
  for (const entry of data.entry || []) {
    for (const ev of entry.messaging || []) {
      if (ev.message && ev.message.is_echo) continue;
      const payload = (ev.postback && ev.postback.payload) ||
        (ev.message && ev.message.quick_reply && ev.message.quick_reply.payload) || "";
      const m = /^DANA:(SEND|FOLLOWED):(.+)$/.exec(payload);
      if (!m || !ev.sender) continue;
      await tap(env, ev.sender.id, m[1], m[2]);
    }
  }
}

async function tap(env, user, kind, rid) {
  const follows = await isFollower(env, user);
  if (follows === false) {
    return send(env, user, button(kind === "SEND" ? TXT.follow : TXT.again, TXT.followed, `DANA:FOLLOWED:${rid}`));
  }
  // true, or unknown (API error): never leave someone without the content.
  const content = await contentFor(rid);
  if (!content) return console.log("no content for", rid);
  const text = (TXT.thanks + content.replace(/^سلام![^\n]*\n+/, "")).slice(0, 1000);
  return send(env, user, { text });
}

async function isFollower(env, user) {
  try {
    const r = await fetch(`${API}/${user}?fields=is_user_follow_business&access_token=${env.IG_ACCESS_TOKEN}`);
    const j = await r.json();
    return typeof j.is_user_follow_business === "boolean" ? j.is_user_follow_business : null;
  } catch {
    return null;
  }
}

async function contentFor(rid) {
  const opt = { cf: { cacheTtl: 300 } };
  const r = await fetch(`${RAW}/content/${encodeURIComponent(rid)}/dm.json`, opt);
  if (r.ok) {
    const d = await r.json();
    if (d.dm_single) return d.dm_single;
  }
  const rules = await (await fetch(`${RAW}/dm_rules.json`, opt)).json();
  const hit = (rules.rules || []).find((x) => x.id === rid);
  return hit ? hit.message : null;
}

function button(text, title, payload) {
  return { attachment: { type: "template", payload: { template_type: "button", text,
    buttons: [{ type: "postback", title, payload }] } } };
}

async function send(env, user, message) {
  const r = await fetch(`${API}/me/messages?access_token=${env.IG_ACCESS_TOKEN}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ recipient: { id: user }, message }),
  });
  if (!r.ok) console.log("send failed", r.status, (await r.text()).slice(0, 300));
}

async function signed(body, header, secret) {
  if (!secret || !header.startsWith("sha256=")) return false;
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const mac = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(body));
  const hex = [...new Uint8Array(mac)].map((b) => b.toString(16).padStart(2, "0")).join("");
  return hex === header.slice(7);
}
