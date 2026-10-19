#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# Jules must never use the owner's retained signing certificate.
if [[ "${REQUIRE_TEST_CERTIFICATE:-0}" != 0 ]]; then
  echo 'ERROR: Do not request the retained test signing key in Jules.' >&2
  exit 1
fi

# Only the repo's default debug signing is allowed here. Never publish from Jules.
REQUIRE_TEST_CERTIFICATE=0 bash scripts/verify.sh

python3 - <<'PY'
import json
from pathlib import Path

report = json.loads(Path('dist/verify/report.json').read_text())
if report.get('updateCompatibleWithExistingWatch7') is not False:
    raise SystemExit('FAIL: Cloud signing matches the retained Watch7 certificate; do not distribute this APK.')
print('PASS: full validation; temporary debug-signed APK is NOT update-compatible with the existing Watch7 installation.')
print('No release publishing or signed-APK upload has been requested.')
PY
