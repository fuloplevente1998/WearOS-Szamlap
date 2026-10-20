#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
validation_tools_dir="${WFF_TOOLS_DIR:-$PWD/.tools/wff}"
mkdir -p dist/verify
python3 -c "from pathlib import Path; Path('dist/verify/report.json').unlink(missing_ok=True)"
python3 scripts/fetch-validation-tools.py --output "$validation_tools_dir"
python3 scripts/generate-watchface.py
node scripts/export-lotr-assets.cjs
if git rev-parse --verify HEAD >/dev/null 2>&1; then
  git diff --exit-code -- design/ watchface/src/main/res/ lotr/src/main/res/
fi
CHECK_ONLY=1 node scripts/render-assets.cjs > dist/verify/ui-halo.txt 2>&1
node scripts/render-lotr-mockups.cjs > dist/verify/ui-lotr.txt 2>&1

java -jar "$validation_tools_dir/wff-validator.jar" 2 --stop-on-fail watchface/src/main/res/raw/watchface.xml > dist/verify/schema-halo.txt 2>&1
java -jar "$validation_tools_dir/wff-validator.jar" 2 --stop-on-fail lotr/src/main/res/raw/watchface.xml > dist/verify/schema-lotr.txt 2>&1
cat dist/verify/schema-halo.txt dist/verify/schema-lotr.txt > dist/verify/schema.txt

gradle_command="${GRADLE_COMMAND:-./gradlew}"
gradle_flags=(--no-daemon --console plain)
if [[ "${GRADLE_OFFLINE:-0}" == 1 ]]; then gradle_flags+=(--offline); fi
"$gradle_command" "${gradle_flags[@]}" :watchface:assembleDebug :watchface:lintDebug :lotr:assembleDebug :lotr:lintDebug > dist/verify/build.txt 2>&1

python3 scripts/check-package.py > dist/verify/package.txt
python3 scripts/icon_checks.py watchface/build/outputs/apk/debug/watchface-debug.apk > dist/verify/icons.txt

java -Xmx3g -jar "$validation_tools_dir/memory-footprint.jar" \
  --watch-face watchface/build/outputs/apk/debug/watchface-debug.apk --schema-version 2 \
  --ambient-limit-mb 10 --active-limit-mb 100 --apply-v1-offload-limitations \
  --estimate-optimization --greedy-after-iterations 1000 > dist/verify/memory-halo.txt 2>&1

java -Xmx3g -jar "$validation_tools_dir/memory-footprint.jar" \
  --watch-face lotr/build/outputs/apk/debug/lotr-debug.apk --schema-version 2 \
  --ambient-limit-mb 10 --active-limit-mb 100 --apply-v1-offload-limitations \
  --estimate-optimization --greedy-after-iterations 1000 > dist/verify/memory-lotr.txt 2>&1

cat dist/verify/memory-halo.txt dist/verify/memory-lotr.txt > dist/verify/memory.txt

python3 scripts/package-test-build.py
echo 'PASS: HALO & LOTR WFF schemas, build, lint, package checks, HALO icon pairing, memory footprint, APK signatures and alignment.'
