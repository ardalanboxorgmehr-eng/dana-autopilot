#!/usr/bin/env python3
"""
Build slides for every post in content/ into docs/slides/<id>/.

Each content/<id>/ folder holds:
  spec.json    the slide spec for build/dana_ai.py
  art.py       optional, generates the source art (s1.png, d*.png) first
  caption.txt  the Instagram caption
  dm.json      keywords and DM text for the comment-to-DM tool

Only rebuilds when the output is missing or older than the inputs, unless --force.
"""
import os, sys, json, shutil, subprocess, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")
SLIDES = os.path.join(ROOT, "docs", "slides")
BUILDER = os.path.join(ROOT, "build", "dana_ai.py")


def newest(paths):
    times = [os.path.getmtime(p) for p in paths if os.path.exists(p)]
    return max(times) if times else 0


def needs_build(folder, out_dir, force):
    if force or not os.path.isdir(out_dir):
        return True
    outs = [os.path.join(out_dir, f) for f in os.listdir(out_dir) if f.endswith(".jpg")]
    if not outs:
        return True
    ins = [os.path.join(folder, f) for f in os.listdir(folder)]
    ins.append(BUILDER)
    return newest(ins) > newest(outs)


def build(post_id, force):
    folder = os.path.join(CONTENT, post_id)
    spec = os.path.join(folder, "spec.json")
    if not os.path.exists(spec):
        print(f"  {post_id}: no spec.json, skipping")
        return None
    out_dir = os.path.join(SLIDES, post_id)
    if not needs_build(folder, out_dir, force):
        n = len([f for f in os.listdir(out_dir) if f.endswith(".jpg")])
        print(f"  {post_id}: up to date ({n} slides)")
        return n

    art = os.path.join(folder, "art.py")
    if os.path.exists(art):
        subprocess.run([sys.executable, art], check=True, cwd=folder)

    subprocess.run([sys.executable, BUILDER, "spec.json"], check=True, cwd=folder)

    src = os.path.join(folder, "out")
    os.makedirs(out_dir, exist_ok=True)
    for f in os.listdir(out_dir):
        if f.endswith(".jpg"):
            os.remove(os.path.join(out_dir, f))
    n = 0
    for f in sorted(os.listdir(src)):
        if f.endswith(".jpg"):
            shutil.copy(os.path.join(src, f), out_dir)
            n += 1
    print(f"  {post_id}: built {n} slides")
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--only", help="build just this post id")
    args = ap.parse_args()

    ids = sorted(os.listdir(CONTENT)) if os.path.isdir(CONTENT) else []
    if args.only:
        ids = [args.only]

    print(f"building {len(ids)} post(s)")
    counts = {}
    for pid in ids:
        if not os.path.isdir(os.path.join(CONTENT, pid)):
            continue
        n = build(pid, args.force)
        if n:
            counts[pid] = n

    # keep queue.json's slide counts honest
    qpath = os.path.join(ROOT, "queue.json")
    if os.path.exists(qpath):
        q = json.load(open(qpath, encoding="utf-8"))
        changed = False
        for p in q["posts"]:
            if p["id"] in counts and p.get("slides") != counts[p["id"]]:
                print(f"  queue: {p['id']} slides {p.get('slides')} -> {counts[p['id']]}")
                p["slides"] = counts[p["id"]]
                changed = True
        if changed:
            with open(qpath, "w", encoding="utf-8") as f:
                json.dump(q, f, ensure_ascii=False, indent=2)
                f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
