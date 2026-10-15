#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
validation_tools_dir="${WFF_TOOLS_DIR:-$PWD/.tools/wff}"
mkdir -p dist/verify
python3 -c "from pathlib import Path; Path('dist/verify/report.json').unlink(missing_ok=True)"
python3 scripts/fetch-validation-tools.py --output "$validation_tools_dir"
python3 scripts/generate-watchface.py
# Generated XML, layouts and strings must already match the committed sources.
if git rev-parse --verify HEAD >/dev/null 2>&1; then
  git diff --exit-code -- design/ watchface/src/main/res/
fi
CHECK_ONLY=1 node scripts/render-assets.cjs > dist/verify/ui.txt 2>&1
java -jar "$validation_tools_dir/wff-validator.jar" 2 --stop-on-fail watchface/src/main/res/raw/watchface.xml > dist/verify/schema.txt 2>&1
gradle_command="${GRADLE_COMMAND:-./gradlew}"
gradle_flags=(--no-daemon --console plain)
if [[ "${GRADLE_OFFLINE:-0}" == 1 ]]; then gradle_flags+=(--offline); fi
"$gradle_command" "${gradle_flags[@]}" :watchface:assembleDebug :watchface:lintDebug > dist/verify/build.txt 2>&1
python3 scripts/check-package.py > dist/verify/package.txt
python3 scripts/icon_checks.py watchface/build/outputs/apk/debug/watchface-debug.apk > dist/verify/icons.txt
java -Xmx3g -jar "$validation_tools_dir/memory-footprint.jar" \
  --watch-face watchface/build/outputs/apk/debug/watchface-debug.apk --schema-version 2 \
  --ambient-limit-mb 10 --active-limit-mb 100 --apply-v1-offload-limitations \
  --estimate-optimization --greedy-after-iterations 1000 > dist/verify/memory.txt 2>&1
python3 scripts/package-test-build.py
echo 'PASS: UI geometry/text, WFF schema, build, lint, package, HALO icon pairing, memory, APK signature and alignment.'
