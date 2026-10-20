#!/usr/bin/env python3
"""Build the private local study hub into ../study/ (git-ignored, never published).

Sources are read in place from the parent "AIML Lessons" folder. Nothing is copied
except rendered HTML . Re-run after adding notes or notebooks:

    tools/.venv/bin/python tools/build_study.py [--force]
"""
import html
import os
import re
import sys
from pathlib import Path

import markdown
import nbformat
from nbconvert import HTMLExporter

REPO = Path(__file__).resolve().parent.parent
ROOT = REPO.parent                      # "AIML Lessons"
OUT = Path(os.environ["STUDY_OUT"]) if os.environ.get("STUDY_OUT") else REPO / "study"
PUBLIC = bool(os.environ.get("STUDY_PUBLIC"))  # published build: notebooks are listed but not rendered or linked
NOTES = ROOT / "notes_md"
AIML = ROOT / "AIML"
FORCE = "--force" in sys.argv

SKIP_DIRS = {".venv", "venv", "site-packages", ".ipynb_checkpoints", "_raw", "__pycache__", "__MACOSX", ".git"}
SKIP_FILES = {"desktop.ini", ".DS_Store"}

# course -> modules. "key" matches note file prefix and the .docx name prefix.
COURSES = [
    {"id": "C6", "title": "Advanced Machine Learning", "dir": "C6 - Advanced Machine Learning", "modules": [
        {"key": "C6_M1", "folders": ["05-SVM-and-Naive-Bayes"]},
        {"key": "C6_M2", "folders": ["07-Regularisation-and-Hyperparameter-Tuning"]},
        {"key": "C6_Assignment_1", "folders": ["08-Model-Selection"]},
        {"key": "C6_M3", "folders": ["12-Time-Series"]},
        {"key": "C6_M4", "folders": ["13-Recommendation-Systems"]},
    ]},
    {"id": "C7", "title": "Deep Learning for Generative AI", "dir": "C7 - Deep Learning for Generative AI", "modules": [
        {"key": "C7_M1", "folders": ["14-Deep Learning for Generative AI"]},
        {"key": "C7_M2", "folders": []},
        {"key": "C7_M3", "folders": ["notebooks"]},
        {"key": "C7_M4", "folders": []},
        {"key": "C7_Assignment", "folders": []},
    ]},
    {"id": "C8", "title": "Designing GenAI Systems", "dir": "C8 - Designing GenAI Systems", "modules": [
        {"key": "C8_M1", "folders": []},
        {"key": "C8_M2", "folders": ["15-Module Downloads"]},
        {"key": "C8_M3", "folders": ["Material - Model Adaptation, Fine-Tuning and Evaluation", "QLoRA and DPO Notebooks"]},
        {"key": "C8_M4", "folders": ["Module Downloads", "Starter and Dataset RAG Legal"]},
    ]},
    {"id": "C9", "title": "Agentic AI Systems", "dir": "C9 - Agentic AI Systems", "locked": True, "modules": []},
]
PRE_C6 = ["01-Linear-Regression", "02-Logistic-Regression", "03-Decision-Trees", "04-Ensembles",
          "06-Clustering", "09-Neural-Networks", "10-CNN", "11-NLP"]


def esc(s):
    return html.escape(str(s), quote=True)


def rel(target: Path, from_dir: Path) -> str:
    return os.path.relpath(target, from_dir).replace(os.sep, "/")


def walk(folder: Path):
    for dp, dns, fns in os.walk(folder):
        dns[:] = sorted(d for d in dns if d not in SKIP_DIRS)
        for fn in sorted(fns):
            if fn not in SKIP_FILES:
                yield Path(dp) / fn


def fresh(src: Path, dst: Path) -> bool:
    return not FORCE and dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime


# ---------- pages ----------
def page(title, body, depth, extra_head="", bodyclass=""):
    up = "../" * depth
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>{esc(title)} · Study hub</title>
<link rel="stylesheet" href="{up}../styles.css">
<link rel="stylesheet" href="{up}study.css">{extra_head}
</head><body class="{bodyclass}">
<header class="sh-top"><a class="nav-brand" href="{up}index.html">Study hub</a>
<span class="sh-private">Private · local only · not published</span></header>
{body}
</body></html>"""


MD = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "sane_lists", "attr_list"],
                       extension_configs={"toc": {"toc_depth": "2-3", "permalink": False}})


def render_md(src: Path, dst: Path, title: str):
    if fresh(src, dst):
        return
    MD.reset()
    body = MD.convert(src.read_text(encoding="utf-8"))
    toc = MD.toc
    depth = len(dst.relative_to(OUT).parts) - 1
    up = "../" * depth
    html_ = page(title, f"""<div class="sh-note"><aside class="sh-toc"><a href="{up}index.html">&larr; Hub</a>{toc}</aside>
<article class="sh-md">{body}</article></div>""", depth)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(html_, encoding="utf-8")


_exporter = HTMLExporter()
_exporter.exclude_input_prompt = False


def render_nb(src: Path, dst: Path):
    if fresh(src, dst):
        return True
    try:
        nb = nbformat.read(str(src), as_version=4)
        nb.metadata.pop("widgets", None)  # malformed widget state breaks nbconvert ('state' KeyError)
        body, _ = _exporter.from_notebook_node(nb, resources={"metadata": {"name": src.stem}})
    except Exception as e:  # unreadable/corrupt notebooks shouldn't break the hub
        print(f"  ! skipped {src.name}: {e}")
        return False
    bar = ('<div style="font:600 13px Archivo,system-ui;padding:8px 16px;background:#201e1d;color:#f3f2f2">'
           f'Study hub · rendered read-only copy of <code>{esc(src.relative_to(ROOT))}</code></div>')
    body = re.sub(r"(<body[^>]*>)", r"\1" + bar.replace("\\", "\\\\"), body, count=1)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(body, encoding="utf-8")
    return True


# ---------- hub ----------
def titleize(stem):
    return re.sub(r"\s+", " ", re.sub(r"[_]+", " ", stem)).strip()


def file_rows(folder: Path, hub_dir: Path):
    """Group a folder's notebooks / pdfs by sub-directory; returns html."""
    groups = {}
    for f in walk(folder):
        ext = f.suffix.lower()
        if ext not in (".ipynb", ".pdf", ".zip"):
            continue
        groups.setdefault(f.parent.relative_to(folder).as_posix(), []).append(f)
    out = []
    for sub, files in groups.items():
        items = []
        for f in files:
            ext = f.suffix.lower()
            mine = " <span class=\"tag tag-accent\">mine</span>" if "Hilay_Trivedi" in f.name else ""
            raw = rel(f, hub_dir)
            if ext == ".ipynb" and PUBLIC:
                items.append(f'<li class="sh-item" data-k="nb">{esc(f.stem)}{mine} <span class="tag tag-outline">local only</span></li>')
            elif ext == ".ipynb":
                dst = OUT / "nb" / f.relative_to(AIML).with_suffix(".html")
                ok = render_nb(f, dst)
                link = (f'<a href="{rel(dst, hub_dir)}">{esc(f.stem)}</a> '
                        f'<a class="sh-src" href="{raw}" title="open .ipynb in place">.ipynb</a>') if ok else esc(f.stem)
                items.append(f'<li class="sh-item" data-k="nb">{link}{mine}</li>')
            else:
                items.append(f'<li class="sh-item" data-k="{ext[1:]}"><a href="{raw}">{esc(f.name)}</a></li>')
        label = f'<div class="sh-sub">{esc(re.sub(r"^Notebooks - M\d/", "", sub))}</div>' if sub != "." else ""
        out.append(f'{label}<ul class="sh-list">{"".join(items)}</ul>')
    return "".join(out), sum(len(v) for v in groups.values())


def find_note(key):
    m = sorted(NOTES.glob(f"{key}*.md"))
    return m[0] if m else None


def find_docx(course_dir: Path, key):
    prefix = key.replace("_", " ")
    for f in sorted(course_dir.glob("*.docx")):
        if f.name.startswith(prefix):
            return f
    return None


def module_block(mod, course_dir: Path, hub_dir: Path):
    note = find_note(mod["key"])
    docx = find_docx(course_dir, mod["key"])
    title = titleize(note.stem[len(mod["key"]):]) if note else titleize(mod["key"])
    if "Assignment" in mod["key"]:
        title += " (assignment)"
    label = ""
    links = []
    if note:
        dst = OUT / "notes" / (note.stem + ".html")
        render_md(note, dst, title)
        links.append(f'<a class="btn btn-secondary" href="{rel(dst, hub_dir)}">Notes</a>')
    if docx:
        links.append(f'<a class="btn btn-ghost" href="{rel(docx, hub_dir)}">.docx</a>')
    mats, count = "", 0
    for fo in mod["folders"]:
        p = AIML / fo
        if p.is_dir():
            h, c = file_rows(p, hub_dir)
            mats += f'<div class="sh-folder">{esc(re.sub(r"^\d+-", "", fo))}</div>{h}'
            count += c
    det = (f'<details><summary>{count} notebooks / files</summary>{mats}</details>' if count
           else '<p class="sh-none">No loose notebooks or files (conceptual).</p>')
    search = esc(f"{title} {mods_text(mod)}".lower())
    return (f'<article class="card sh-mod" data-s="{search}">'
            f'<h3 class="card-title">{esc(title)}</h3><div class="sh-links">{"".join(links)}</div>{det}</article>')


def mods_text(mod):
    out = []
    for fo in mod["folders"]:
        p = AIML / fo
        if p.is_dir():
            out += [f.stem for f in walk(p) if f.suffix.lower() in (".ipynb", ".pdf")]
    return " ".join(out)


def build():
    OUT.mkdir(exist_ok=True)
    hub_dir = OUT
    (OUT / "study.css").write_text((REPO / "tools" / "study.css").read_text(encoding="utf-8"), encoding="utf-8")

    quick = []
    for name, src in (("Combined cheat sheet", ROOT / "COMBINED_CHEATSHEET.md"), ("Master index", ROOT / "MASTER_INDEX.md")):
        if src.exists():
            dst = OUT / "notes" / (src.stem + ".html")
            render_md(src, dst, name)
            quick.append(f'<a class="btn btn-primary" href="{rel(dst, hub_dir)}">{name}</a>')
    # remaining notes not covered by a module (safety net)
    for n in sorted(NOTES.glob("*.md")):
        render_md(n, OUT / "notes" / (n.stem + ".html"), titleize(re.sub(r"^C\d_(M\d_|Assignment_?\d*_?)?", "", n.stem)))

    def sect(sid, cid, title, cards, tag=""):
        return (f'<section class="sh-course" id="{sid}"><div class="sh-chead"><h2>{esc(title)}</h2>{tag}</div><div class="sh-grid">{"".join(cards)}</div></section>')

    sections, navl = [], []
    for c in COURSES:
        cdir = ROOT / c["dir"]
        cards = [module_block(m, cdir, hub_dir) for m in c["modules"]]
        if c.get("locked") and not any(walk(cdir)):
            cards = ['<p class="sh-none">Locked. No materials yet. Re-run the build once this course opens.</p>']
            tag = '<span class="tag tag-outline">Locked</span>'
        else:
            tag = '<span class="tag tag-accent">Complete</span>'
        sections.append(sect(c["id"], c["id"], c["title"], cards, tag))
        navl.append((c["id"], c["title"]))
    pre = []
    for fo in PRE_C6:
        p = AIML / fo
        if not p.is_dir():
            continue
        h, n = file_rows(p, hub_dir)
        name = titleize(re.sub(r"^\d+-", "", fo))
        s_ = esc(f"{name} {mods_text({'folders': [fo]})}".lower())
        pre.append(f'<article class="card sh-mod" data-s="{s_}"><h3 class="card-title">{esc(name)}</h3>'
                   f'<details><summary>{n} notebooks / files</summary>{h}</details></article>')
    sections.append(sect("pre", "Pre", "Earlier topics: notebooks only", pre, '<span class="tag tag-neutral">No refined notes</span>'))
    navl.append(("pre", "Earlier topics"))
    nav = "".join(f'<a href="#{i}">{l}</a>' for i, l in navl)
    body = f"""<main class="sh-main"><div class="sh-hero"><h1>My AIML study hub</h1>
<div class="sh-links">{"".join(quick)}</div>
<div class="sh-bar"><input id="q" class="input" type="search" placeholder="Filter modules and notebooks…" aria-label="Filter"><nav>{nav}</nav></div></div>
{"".join(sections)}</main>
<script>
const q=document.getElementById('q');
q.addEventListener('input',()=>{{const t=q.value.trim().toLowerCase();
document.querySelectorAll('.sh-mod').forEach(m=>{{m.hidden=t&&!m.dataset.s.includes(t);if(t&&!m.hidden)m.querySelector('details')?.setAttribute('open','')}});
document.querySelectorAll('.sh-course').forEach(c=>{{c.hidden=t&&![...c.querySelectorAll('.sh-mod')].some(m=>!m.hidden)}});}});
</script>"""
    (OUT / "index.html").write_text(page("My AIML study hub", body, 0), encoding="utf-8")
    print(f"Built {OUT / 'index.html'}")


if __name__ == "__main__":
    build()
