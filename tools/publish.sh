#!/usr/bin/env bash
# Rebuild the study hub, encrypt it with StaticCrypt, and write it to study-c3dfb61c4535/.
# Usage: STUDY_PASSWORD='...' tools/publish.sh   (password is never stored in the repo)
set -euo pipefail
cd "$(dirname "$0")/.."
: "${STUDY_PASSWORD:?set STUDY_PASSWORD}"
DEST="study-c3dfb61c4535"
rm -rf .tmp_build
STUDY_PUBLIC=1 STUDY_OUT=.tmp_build tools/.venv/bin/python tools/build_study.py --force "$@"
rm -rf "$DEST" && mkdir -p .tmp_enc
STATICRYPT_PASSWORD="$STUDY_PASSWORD" npx --yes staticrypt@3 .tmp_build -r -d .tmp_enc --short --remember 30 \
  --template-title "Study hub" --template-instructions "Enter the password to open the study hub." --config false
mv .tmp_enc/.tmp_build "$DEST" && rmdir .tmp_enc && rm -rf .tmp_build
find "$DEST" -name '*.html' -exec sed -i '' 's|<head>|<head><meta name="robots" content="noindex,nofollow">|' {} +
echo "Built $DEST. Review, then: git add -A && git commit && git push"
