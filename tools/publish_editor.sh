#!/usr/bin/env bash
# Bundle the blog editor (editor/, gitignored) into one page, encrypt it with StaticCrypt, and write it
# to editor-c1a83dcf32c6/. Same protection as the study hub: unguessable path + password + noindex.
# Usage: EDITOR_PASSWORD='...' tools/publish_editor.sh   (password is never stored in the repo)
set -euo pipefail
cd "$(dirname "$0")/.."
: "${EDITOR_PASSWORD:?set EDITOR_PASSWORD}"
DEST="editor-c1a83dcf32c6"
TMP=".tmp_editor"
rm -rf "$TMP" && mkdir -p "$TMP/src" "$TMP/enc"

# Inline admin.css + admin.js so the whole editor sits inside the encrypted payload, and allow
# exactly that inline script through the page's CSP by hash.
python3 - "$TMP/src/index.html" <<'PY'
import base64, hashlib, re, sys
from pathlib import Path
src = Path("editor")
html = (src / "index.html").read_text(encoding="utf-8")
css = (src / "admin.css").read_text(encoding="utf-8")
js = (src / "admin.js").read_text(encoding="utf-8")
html = html.replace('<link rel="stylesheet" href="admin.css">', f"<style>\n{css}</style>")
html = html.replace('<script src="admin.js"></script>', f"<script>\n{js}</script>")
digest = base64.b64encode(hashlib.sha256(f"\n{js}".encode()).digest()).decode()
html, n = re.subn(r"script-src 'self'", f"script-src 'self' 'sha256-{digest}'", html)
assert n == 1 and "admin.js" not in html and "admin.css" not in html, "inlining failed"
Path(sys.argv[1]).write_text(html, encoding="utf-8")
PY

STATICRYPT_PASSWORD="$EDITOR_PASSWORD" npx --yes staticrypt@3 "$TMP/src/index.html" -d "$TMP/enc" --short --remember 30 \
  --template-title "Blog editor" --template-instructions "Enter the password to open the blog editor." --config false
rm -rf "$DEST" && mkdir -p "$DEST"
mv "$TMP/enc/index.html" "$DEST/index.html" && rm -rf "$TMP"
sed -i '' 's|<head>|<head><meta name="robots" content="noindex,nofollow">|' "$DEST/index.html"
echo "Built $DEST/index.html. Review, then: git add -A && git commit && git push"
