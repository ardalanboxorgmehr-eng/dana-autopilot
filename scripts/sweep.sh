#!/usr/bin/env bash
# One comment-to-DM sweep, or a long run of them.
#
# Why this exists (9 Nov 2026). GitHub's cron is best effort and on this repo it
# mostly does not fire: between 8 Nov 20:20 and 9 Nov 05:54 only 2 of about 38
# due firings happened, so DMs sat unsent for up to 3.5 hours at a stretch. The
# usual answer is an outside pinger, which needs an account and a token.
# Instead, when cron DOES fire, that run stays alive and sweeps on its own clock
# for up to SWEEP_BUDGET_MIN. One firing then covers the next five and a half
# hours whether or not GitHub fires again.
#
# SWEEP_EVERY_MIN=0 (the default) means one sweep and out, which is what a
# manual dispatch wants.
set -uo pipefail

EVERY=${SWEEP_EVERY_MIN:-0}
BUDGET=${SWEEP_BUDGET_MIN:-330}
started=$SECONDS
alerted=0

record() {
  # Push this sweep's records. Never fatal: the next sweep merges and retries.
  if [ -z "$(git status --porcelain state/dm_sent.json state/yt_desk.json state/desk_inbox.enc)" ]; then
    echo "no new DMs"
    return 0
  fi
  git config user.name "dana-autopilot"
  git config user.email "actions@github.com"
  rm -rf /tmp/ours && mkdir -p /tmp/ours
  cp state/dm_sent.json /tmp/ours/ 2>/dev/null || true
  cp state/yt_desk.json /tmp/ours/ 2>/dev/null || true
  cp state/desk_inbox.enc /tmp/ours/ 2>/dev/null || true
  for try in 1 2 3 4 5; do
    git fetch origin "${GITHUB_REF_NAME}" || true
    git reset --hard FETCH_HEAD
    python scripts/merge_state.py /tmp/ours
    if [ -z "$(git status --porcelain state/)" ]; then
      echo "nothing new to record"
      return 0
    fi
    git add state/dm_sent.json
    [ -f state/yt_desk.json ] && git add state/yt_desk.json
    [ -f state/desk_inbox.enc ] && git add state/desk_inbox.enc
    git commit -m "dm: record sent messages"
    if git push; then
      return 0
    fi
    echo "push lost a race, merging again (attempt $try)"
    sleep $((try * 5))
  done
  echo "could not record this sweep's messages after 5 tries"
  return 1
}

sweep() {
  python scripts/dm_reply.py
  local rc=$?
  # Exit 1 is the health alert, not a crash. The push to his phone has already
  # gone out, and carrying on sweeping is what clears the backlog the alert is
  # about, so the loop keeps going and the job reports the alert at the end.
  [ $rc -eq 1 ] && alerted=1
  python scripts/yt_comments.py || echo "yt_comments failed, carrying on"
  record || true
  [ $rc -ge 2 ] && return $rc
  return 0
}

n=0
while :; do
  n=$((n + 1))
  echo "=== sweep $n, $(date -u +%H:%M:%S) UTC, $((($SECONDS - started) / 60)) min into this run ==="
  sweep
  rc=$?
  if [ $rc -ne 0 ]; then
    echo "Instagram connection failed (exit $rc), stopping this run"
    exit $rc
  fi
  [ "$EVERY" -eq 0 ] && break
  # Leave room for one more whole sweep inside the budget.
  elapsed=$((($SECONDS - started) / 60))
  if [ $((elapsed + EVERY)) -ge "$BUDGET" ]; then
    echo "budget of ${BUDGET} min used after $n sweeps; the next scheduled run takes over"
    break
  fi
  # Sleep to the next interval boundary rather than a flat interval, so the
  # sweeps do not drift later and later across five hours.
  target=$((n * EVERY * 60))
  nap=$((target - ($SECONDS - started)))
  [ $nap -lt 30 ] && nap=30
  echo "next sweep in $((nap / 60))m $((nap % 60))s"
  sleep $nap
done

[ $alerted -eq 1 ] && { echo "a health alert fired during this run"; exit 1; }
exit 0
