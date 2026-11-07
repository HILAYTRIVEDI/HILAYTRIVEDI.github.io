#!/usr/bin/env python3
"""Blog tool: posts are structured JSON files in blog/posts/<slug>.json, committed to git.

No database. Git is the persistence layer: a post exists once its JSON is committed and pushed,
and GitHub Pages serves it as a static file. This script keeps the derived files in sync.

Commands (stdlib only, run from anywhere):
  python3 tools/blog.py new "Post title" [--tags a,b]   create blog/posts/<slug>.json as a draft
  python3 tools/blog.py import path/to/post.md          convert Markdown (+ front matter) to a post JSON
  python3 tools/blog.py build [--drafts]                validate every post, write blog/index.json + blog/feed.xml

Typical flow: new/import -> edit the JSON -> set "draft": false -> build -> git add/commit/push.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape as xesc

ROOT = Path(__file__).resolve().parent.parent
BLOG = ROOT / "blog"
POSTS = BLOG / "posts"
SITE = "https://hilaytrivedi.github.io"
AUTHOR = "Hilay Trivedi"
SCHEMA_VERSION = 1

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
BLOCK_FIELDS = {
    "p": {"text"},
    "h2": {"text"},
    "h3": {"text"},
    "list": {"items"},
    "code": {"code"},
    "quote": {"text"},
    "callout": {"text"},
    "image": {"src", "alt"},
    "hr": set(),
}


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:80] or "post"


def words_in(blocks: list[dict]) -> int:
    n = 0
    for b in blocks:
        for k in ("text", "code", "caption"):
            if isinstance(b.get(k), str):
                n += len(b[k].split())
        for it in b.get("items", []) or []:
            n += len(str(it).split())
    return n


# ---------- validation ----------
def validate(post: dict, fname: str) -> list[str]:
    errs = []
    req = {"slug": str, "title": str, "date": str, "summary": str, "tags": list, "blocks": list}
    for k, t in req.items():
        if not isinstance(post.get(k), t):
            errs.append(f"'{k}' missing or not a {t.__name__}")
    if errs:
        return errs
    if not SLUG_RE.match(post["slug"]):
        errs.append("slug must be lowercase-kebab-case")
    if post["slug"] + ".json" != fname:
        errs.append(f"filename must be {post['slug']}.json")
    for k in ("date", "updated"):
        if k in post and not (isinstance(post[k], str) and DATE_RE.match(post[k])):
            errs.append(f"'{k}' must be YYYY-MM-DD")
    if not all(isinstance(t, str) and t for t in post["tags"]):
        errs.append("tags must be non-empty strings")
    if "draft" in post and not isinstance(post["draft"], bool):
        errs.append("'draft' must be true/false")
    for i, b in enumerate(post["blocks"]):
        typ = b.get("type") if isinstance(b, dict) else None
        if typ not in BLOCK_FIELDS:
            errs.append(f"blocks[{i}]: unknown type {typ!r} (allowed: {', '.join(BLOCK_FIELDS)})")
            continue
        missing = BLOCK_FIELDS[typ] - b.keys()
        if missing:
            errs.append(f"blocks[{i}] ({typ}): missing {', '.join(sorted(missing))}")
        if typ == "list" and not (isinstance(b.get("items"), list) and b["items"]):
            errs.append(f"blocks[{i}] (list): 'items' must be a non-empty array")
    return errs


def load_posts() -> tuple[list[dict], list[str]]:
    posts, problems = [], []
    for f in sorted(POSTS.glob("*.json")):
        try:
            post = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            problems.append(f"{f.name}: invalid JSON ({e})")
            continue
        errs = validate(post, f.name)
        problems += [f"{f.name}: {e}" for e in errs]
        if not errs:
            posts.append(post)
    return posts, problems


# ---------- build ----------
def cmd_build(args) -> int:
    POSTS.mkdir(parents=True, exist_ok=True)
    posts, problems = load_posts()
    if problems:
        print("Fix these before building:\n  " + "\n  ".join(problems), file=sys.stderr)
        return 1
    live = [p for p in posts if args.drafts or not p.get("draft", False)]
    live.sort(key=lambda p: (p["date"], p["slug"]), reverse=True)
    entries = [{
        "slug": p["slug"], "title": p["title"], "date": p["date"], "updated": p.get("updated"),
        "summary": p["summary"], "tags": p["tags"],
        "readingMinutes": max(1, round(words_in(p["blocks"]) / 220)),
        **({"draft": True} if p.get("draft") else {}),
    } for p in live]
    for e in entries:
        if e["updated"] is None:
            del e["updated"]
    manifest = {"schema": SCHEMA_VERSION, "posts": entries}
    (BLOG / "index.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_feed([e for e in entries if not e.get("draft")])
    drafts = sum(1 for p in posts if p.get("draft"))
    print(f"Built blog/index.json + blog/feed.xml: {len(entries)} listed, {drafts} draft(s) total"
          + (" (drafts INCLUDED, rebuild without --drafts before committing)" if args.drafts else ""))
    return 0


def write_feed(entries: list[dict]) -> None:
    def rfc822(d: str) -> str:
        return format_datetime(dt.datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc))
    items = "".join(
        f"""
  <item>
    <title>{xesc(e['title'])}</title>
    <link>{SITE}/blog/post.html?p={e['slug']}</link>
    <guid isPermaLink="false">{e['slug']}</guid>
    <pubDate>{rfc822(e['date'])}</pubDate>
    <description>{xesc(e['summary'])}</description>{''.join(f'''
    <category>{xesc(t)}</category>''' for t in e['tags'])}
  </item>""" for e in entries[:30])
    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>{AUTHOR}: Writing</title>
  <link>{SITE}/blog/</link>
  <description>Notes on AI systems, agents and WordPress engineering.</description>
  <language>en</language>{items}
</channel>
</rss>
"""
    (BLOG / "feed.xml").write_text(feed, encoding="utf-8")


# ---------- new ----------
def cmd_new(args) -> int:
    slug = args.slug or slugify(args.title)
    path = POSTS / f"{slug}.json"
    if path.exists():
        print(f"{path.relative_to(ROOT)} already exists", file=sys.stderr)
        return 1
    POSTS.mkdir(parents=True, exist_ok=True)
    post = {
        "slug": slug, "title": args.title, "date": dt.date.today().isoformat(),
        "summary": "One or two sentences shown on the blog index.",
        "tags": [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else [],
        "draft": True,
        "blocks": [
            {"type": "p", "text": "Opening paragraph. Inline **bold**, *italic*, `code` and [links](https://example.com) work."},
            {"type": "h2", "text": "A section heading"},
            {"type": "list", "ordered": False, "items": ["First point", "Second point"]},
            {"type": "code", "lang": "python", "code": "print('hello')"},
        ],
    }
    path.write_text(json.dumps(post, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Created {path.relative_to(ROOT)} (draft). Edit it, set \"draft\": false, then run build.")
    return 0


# ---------- import from Markdown ----------
def md_to_blocks(md: str) -> list[dict]:
    lines = md.replace("\r\n", "\n").split("\n")
    blocks, para, i = [], [], 0

    def flush():
        if para:
            blocks.append({"type": "p", "text": " ".join(s.strip() for s in para)})
            para.clear()

    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if s.startswith("```"):
            flush()
            lang, code = s[3:].strip(), []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            blk = {"type": "code", "code": "\n".join(code)}
            if lang:
                blk["lang"] = lang
            blocks.append(blk)
        elif not s:
            flush()
        elif m := re.match(r"^(#{1,3})\s+(.*)$", s):
            flush()
            blocks.append({"type": "h2" if len(m.group(1)) <= 2 else "h3", "text": m.group(2)})
        elif re.match(r"^(-{3,}|\*{3,})$", s):
            flush()
            blocks.append({"type": "hr"})
        elif m := re.match(r"^!\[([^\]]*)\]\(([^)\s]+)(?:\s+\"([^\"]*)\")?\)$", s):
            flush()
            blk = {"type": "image", "src": m.group(2), "alt": m.group(1)}
            if m.group(3):
                blk["caption"] = m.group(3)
            blocks.append(blk)
        elif s.startswith(">"):
            flush()
            q = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                q.append(lines[i].strip()[1:].strip())
                i += 1
            text = " ".join(q)
            if text.upper().startswith("[!NOTE]"):
                blocks.append({"type": "callout", "text": text[7:].strip()})
            else:
                blocks.append({"type": "quote", "text": text})
            continue
        elif re.match(r"^([-*+]|\d+[.)])\s+", s):
            flush()
            ordered = bool(re.match(r"^\d", s))
            items = []
            while i < len(lines) and re.match(r"^\s*([-*+]|\d+[.)])\s+", lines[i]):
                items.append(re.sub(r"^\s*([-*+]|\d+[.)])\s+", "", lines[i]).strip())
                i += 1
            blocks.append({"type": "list", "ordered": ordered, "items": items})
            continue
        else:
            para.append(ln)
        i += 1
    flush()
    return blocks


def parse_front_matter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    meta = {}
    for ln in text[3:end].strip().splitlines():
        if ":" in ln:
            k, v = ln.split(":", 1)
            v = v.strip().strip('"').strip("'")
            if v.startswith("[") and v.endswith("]"):
                v = [x.strip().strip('"').strip("'") for x in v[1:-1].split(",") if x.strip()]
            elif v.lower() in ("true", "false"):
                v = v.lower() == "true"
            meta[k.strip()] = v
    return meta, text[end + 4:]


def cmd_import(args) -> int:
    src = Path(args.file)
    meta, body = parse_front_matter(src.read_text(encoding="utf-8"))
    blocks = md_to_blocks(body)
    title = meta.get("title")
    if not title and blocks and blocks[0]["type"] in ("h2", "h3"):
        title = blocks.pop(0)["text"]
    title = title or src.stem.replace("-", " ").title()
    tags = meta.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    first_p = next((b["text"] for b in blocks if b["type"] == "p"), "")
    post = {
        "slug": meta.get("slug") or slugify(title),
        "title": title,
        "date": meta.get("date") or dt.date.today().isoformat(),
        "summary": meta.get("summary") or (first_p[:200] + ("…" if len(first_p) > 200 else "")),
        "tags": tags,
        "draft": meta.get("draft", True),
        "blocks": blocks,
    }
    if meta.get("updated"):
        post["updated"] = meta["updated"]
    path = POSTS / f"{post['slug']}.json"
    if path.exists() and not args.force:
        print(f"{path.relative_to(ROOT)} exists; pass --force to overwrite", file=sys.stderr)
        return 1
    errs = validate(post, path.name)
    if errs:
        print("Converted post is invalid:\n  " + "\n  ".join(errs), file=sys.stderr)
        return 1
    POSTS.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(post, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {path.relative_to(ROOT)} ({len(blocks)} blocks, draft={post['draft']}). Run build next.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new", help="create a draft post")
    n.add_argument("title")
    n.add_argument("--slug")
    n.add_argument("--tags", help="comma-separated")
    n.set_defaults(fn=cmd_new)
    im = sub.add_parser("import", help="convert a Markdown file to a post")
    im.add_argument("file")
    im.add_argument("--force", action="store_true")
    im.set_defaults(fn=cmd_import)
    b = sub.add_parser("build", help="validate posts, write index.json + feed.xml")
    b.add_argument("--drafts", action="store_true", help="also list drafts (local preview only)")
    b.set_defaults(fn=cmd_build)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
