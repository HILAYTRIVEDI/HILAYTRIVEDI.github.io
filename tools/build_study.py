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

# Topic plan, in learning order. Each topic: title, optional one-line blurb, links and notebook folders.
# A link is (label, source, anchor-prefix): source is a notes_md key (e.g. "C6_M1") or "ext:<name>" for
# tools/topic_notes/<name>.md. The anchor prefix is matched against that note's heading ids ("14-" -> "14-why-svms"),
# so split cards deep-link into one note file without renaming it.
EXT = REPO / "tools" / "topic_notes"
EXT_TAG = "Extra reading, not from the course"
GROUPS = [
    ("Foundations", "foundations", [
        {"t": "Linear Regression", "f": ["01-Linear-Regression"]},
        {"t": "Logistic Regression", "f": ["02-Logistic-Regression"]},
        {"t": "Decision Trees", "f": ["03-Decision-Trees"]},
        {"t": "Ensembles", "f": ["04-Ensembles"]},
        {"t": "Gradient Boosting and XGBoost", "n": [("Notes", "ext:gradient-boosting", "")], "x": 1},
        {"t": "Clustering", "f": ["06-Clustering"]},
        {"t": "PCA and Dimensionality Reduction", "n": [("Notes", "ext:pca-dimensionality-reduction", "")], "x": 1},
        {"t": "Neural Networks", "f": ["09-Neural-Networks"]},
        {"t": "Backprop and Optimisers", "n": [("Notes", "ext:backprop-and-optimisers", "")], "x": 1},
        {"t": "CNN", "f": ["10-CNN"]},
        {"t": "NLP Basics", "f": ["11-NLP"]},
    ]),
    ("Classical ML", "classical", [
        {"t": "Bias, Variance and Overfitting", "n": [("Notes", "C6_M1", "11-")]},
        {"t": "Regularisation (L1 and L2)", "n": [("Notes", "ext:regularisation", "")], "x": 1},
        {"t": "SVM", "n": [("Notes", "C6_M1", "14-")], "f": ["05-SVM-and-Naive-Bayes"]},
        {"t": "Kernels", "n": [("Notes", "C6_M1", "21-")]},
        {"t": "Naive Bayes", "n": [("Notes", "C6_M1", "31-")]},
        {"t": "Evaluation Metrics", "n": [("Notes", "ext:evaluation-metrics", "")], "x": 1},
        {"t": "Model Selection and Tuning", "n": [("Notes", "C6_M2", "11-")], "f": ["07-Regularisation-and-Hyperparameter-Tuning"]},
        {"t": "Feature Selection", "n": [("Notes", "C6_M2", "18-")]},
        {"t": "Class Imbalance", "n": [("Notes", "C6_M2", "28-")]},
        {"t": "Model Selection in Practice: Cardio Risk", "n": [("Notes", "C6_Assignment_1", "")], "f": ["08-Model-Selection"]},
        {"t": "Association Rules", "n": [("Notes", "C6_M2", "31-")]},
        {"t": "Explainable AI", "n": [("Notes", "C6_M2", "41-")]},
        {"t": "Time Series", "n": [("Notes", "C6_M3", "11-")], "f": ["12-Time-Series"]},
        {"t": "Recommendation Systems", "n": [("Notes", "C6_M4", "11-")], "f": ["13-Recommendation-Systems"]},
    ]),
    ("Computer Vision", "vision", [
        {"t": "Image Processing", "n": [("Notes", "C7_M1", "11-")], "f": ["14-Deep Learning for Generative AI"]},
        {"t": "Object Detection", "n": [("Notes", "C7_M1", "21-")]},
        {"t": "Transfer Learning", "n": [("Notes", "C7_M1", "31-")]},
        {"t": "Transfer Learning in Practice: Surface Defects", "n": [("Notes", "C7_Assignment", "")]},
        {"t": "Encoder-Decoder and U-Net", "n": [("Notes", "C7_M1", "41-")]},
    ]),
    ("Language Models", "language", [
        {"t": "RNN, LSTM and GRU", "n": [("Notes", "ext:rnn-lstm-gru", "")], "x": 1},
        {"t": "Embeddings and Search Basics", "n": [("Notes", "C7_M2", "11-"), ("Search", "C8_M4", "01-")]},
        {"t": "Seq2Seq and Attention", "n": [("Notes", "C7_M2", "13-")]},
        {"t": "Transformers", "n": [("Notes", "C7_M2", "21-")]},
        {"t": "Transformer Variants: BERT, T5, SBERT", "n": [("Notes", "C7_M2", "31-")]},
    ]),
    ("Generative Models", "generative", [
        {"t": "Variational Autoencoders", "n": [("Notes", "C7_M3", "11-")], "f": ["notebooks"]},
        {"t": "GANs and CycleGAN", "n": [("Notes", "C7_M3", "21-")]},
        {"t": "Diffusion Models", "n": [("Notes", "C7_M3", "31-")]},
        {"t": "Multimodal Models: CLIP and VLMs", "n": [("Notes", "C7_M3", "41-")]},
        {"t": "Vision Transformers", "n": [("Notes", "C7_M3", "51-")]},
    ]),
    ("GenAI Systems", "systems", [
        {"t": "GenAI Landscape", "n": [("Notes", "C8_M1", "11-")]},
        {"t": "Prompt Engineering", "n": [("Full guide", "ext:prompt-engineering", ""),
                                          ("System prompting", "C8_M1", "21-"), ("Multimodal prompting", "C8_M1", "31-")], "x": 1},
        {"t": "LLM APIs and Tool Calling", "n": [("Notes", "C8_M2", "11-")], "f": ["15-Module Downloads"]},
        {"t": "LangChain and Frameworks", "n": [("Notes", "C8_M2", "21-")]},
        {"t": "Fine-Tuning: LoRA and QLoRA", "n": [("Notes", "C8_M3", "11-")], "f": ["Material - Model Adaptation, Fine-Tuning and Evaluation"]},
        {"t": "Alignment: RLHF and DPO", "n": [("Notes", "C8_M3", "21-")], "f": ["QLoRA and DPO Notebooks"]},
        {"t": "RAG Foundations", "n": [("Notes", "C8_M4", "11-")], "f": ["Module Downloads"]},
        {"t": "LlamaIndex and Advanced RAG", "n": [("LlamaIndex", "C8_M4", "31-"), ("Advanced RAG", "C8_M4", "41-")], "f": ["Starter and Dataset RAG Legal"]},
        {"t": "LLM Evaluation, Reliability and Observability", "n": [("Notes", "C8_M3", "41-"), ("Red-teaming", "C8_M1", "41-")]},
    ]),
    ("Responsible AI", "responsible", [
        {"t": "Hallucination", "n": [("Notes", "C7_M4", "21-")]},
        {"t": "Prompt Injection and Jailbreaks", "n": [("Notes", "C7_M4", "31-")]},
        {"t": "Responsible AI Metrics", "n": [("Notes", "C7_M4", "11-")]},
    ]),
    ("Agentic AI", "agentic", [
        {"t": "Agentic AI", "locked": True},
    ]),
]


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
    if key.startswith("ext:"):
        f = EXT / (key[4:] + ".md")
        return f if f.exists() else None
    m = sorted(NOTES.glob(f"{key}*.md"))
    return m[0] if m else None


def note_href(key, prefix, title, hub_dir: Path):
    """Render the note (if needed) and return its href, deep-linked to the first heading id starting with prefix."""
    note = find_note(key)
    if not note:
        return None
    dst = OUT / "notes" / (note.stem + ".html")
    render_md(note, dst, title)
    href = rel(dst, hub_dir)
    if prefix:
        m = re.search(r'id="(%s[^"]*)"' % re.escape(prefix), dst.read_text(encoding="utf-8"))
        if m:
            href += "#" + m.group(1)
    return href


def topic_block(t, hub_dir: Path):
    title = t["t"]
    if t.get("locked"):
        return (f'<article class="card sh-mod" data-s="{esc(title.lower())}"><h3 class="card-title">{esc(title)}</h3>'
                '<p class="sh-none">Coming soon.</p></article>')
    links = []
    for label, key, prefix in t.get("n", []):
        href = note_href(key, prefix, title, hub_dir)
        if href:
            links.append(f'<a class="btn btn-secondary" href="{href}">{esc(label)}</a>')
    mats, count = "", 0
    for fo in t.get("f", []):
        p = AIML / fo
        if p.is_dir():
            h, c = file_rows(p, hub_dir)
            mats += f'<div class="sh-folder">{esc(re.sub(r"^\d+-", "", fo))}</div>{h}'
            count += c
    if count:
        det = f'<details><summary>{count} notebooks / files</summary>{mats}</details>'
    elif not links:
        det = '<p class="sh-none">Coming soon.</p>'
    else:
        det = ""
    tag = f'<span class="tag tag-outline">{EXT_TAG}</span>' if t.get("x") else ""
    search = esc(f"{title} {mods_text(t)}".lower())
    return (f'<article class="card sh-mod" data-s="{search}">'
            f'<h3 class="card-title">{esc(title)}</h3>{tag}<div class="sh-links">{"".join(links)}</div>{det}</article>')


def mods_text(t):
    out = []
    for fo in t.get("f", []):
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
    # every course note is rendered, since topic cards deep-link into them
    for n in sorted(NOTES.glob("*.md")):
        render_md(n, OUT / "notes" / (n.stem + ".html"), titleize(re.sub(r"^C\d_(M\d_|Assignment_?\d*_?)?", "", n.stem)))

    sections, navl = [], []
    for title, sid, topics in GROUPS:
        cards = [topic_block(t, hub_dir) for t in topics]
        tag = '<span class="tag tag-outline">Coming soon</span>' if all(t.get("locked") for t in topics) else ""
        sections.append(f'<section class="sh-course" id="{sid}"><div class="sh-chead"><h2>{esc(title)}</h2>{tag}</div>'
                        f'<div class="sh-grid">{"".join(cards)}</div></section>')
        navl.append((sid, title))
    nav = "".join(f'<a href="#{i}">{l}</a>' for i, l in navl)
    body = f"""<main class="sh-main"><div class="sh-hero"><h1>My AIML study hub</h1>
<div class="sh-links">{"".join(quick)}</div>
<div class="sh-bar"><input id="q" class="input" type="search" placeholder="Filter topics and notebooks…" aria-label="Filter"><nav>{nav}</nav></div></div>
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
