# Agent instructions — WearOS-Szamlap

Applies to Jules, Codex and other automated coding agents working in this repository.

## Project identity and compatibility
- This is **Spartan Night**, an Android resource-only **Watch Face Format (WFF) 2** watch face for Wear OS 5+ / Galaxy Watch7.
- Its Gradle scripts are Kotlin DSL, but the watch face is **not a Kotlin or Java app**. `android:hasCode="false"` must remain true and the APK must contain no DEX.
- Runtime implementation is `watchface/src/main/res/raw/watchface.xml`; editable inputs and artwork are under `design/` and `scripts/`.
- JDK 21, Gradle wrapper 9.2.1, Android Gradle Plugin 9.0.0, Android SDK 36, Build Tools 36.0.0; Node 24 / Playwright 1.62.1 / Chromium for visual checks.
- Keep the 8 native complication slots and their stable IDs, supported LONG_TEXT app shortcuts, WFF 2 schema, EMPTY states and always-on restrictions.

## Change and validation policy
- For small XML, layout or HUD icon/alias changes, run `bash scripts/verify-fast.sh` first. It validates XML source structure, cropping, provider/icon switch logic and Google's WFF 2 schema. It does not build an APK or run device tests.
- Generated XML and SVG assets must agree with `scripts/generate-watchface.py`. Regenerate deliberately when editing their canonical source; do not blindly overwrite hand edits. For bitmap/artwork changes, also run the Playwright visual checks.
- Before merging, creating an APK intended for testers, or publishing any release, run the complete `bash scripts/verify.sh` gate in a properly provisioned environment. In Jules use `bash scripts/verify-jules.sh`, which performs the full gate and asserts that the resulting signing certificate **cannot update** the existing Watch7 installation.
- Full validation covers deterministic resource generation, 432/480 px visual geometry, Google schema, Gradle assemble/lint, packaged resources, icon switching, memory estimate, APK signature and alignment.
- Report CI results separately from checks actually run in the current environment. A Chromium preview is not a native watch screenshot; memory estimate is not measured battery usage. Final rendering and provider choice require a real Watch7.

## Versions, compatibility and pull requests
- Do not change `versionCode` (currently 6), `versionName` (currently `0.1.5-test`), `applicationId`, namespace, minSdk/targetSdk, or signing identity without explicit owner approval.
- Avoid changes to existing editor configuration IDs, complication slot IDs and saved user settings unless explicitly requested with migration planning.
- Work on a separate feature branch. Do not merge into `main`, create a PR, publish a release or upload an APK without explicit instruction.

## Signing / private-key boundaries
- Jules and other untrusted cloud coding agents may build **debug APKs signed only with their own disposable debug key**. They must never access, import, stage, request, decode, upload or reproduce the owner's retained test signing key, keystore password or production key.
- An APK signed with a fresh debug key **cannot be installed as an update** over the existing Watch7 Spartan Night installation. Never claim otherwise, and do not suggest uninstalling the installed face to bypass a signature mismatch.
- The retained test signing certificate is pinned in `scripts/package-test-build.py`; locally signed prereleases must pass `REQUIRE_TEST_CERTIFICATE=1` on the trusted signing environment, following `docs/RELEASES.md`.
- Do not invoke `scripts/publish-test-release.py`, stage signed release artifacts or set `REQUIRE_TEST_CERTIFICATE=1` in Jules. A successful cloud build is validation only, not a publishable/updatable APK.
- Existing `.gitignore` excludes keystores, `local.properties`, build outputs and tool downloads. Never commit credentials or binary signing material.

## External tools and CI upkeep
- `design/validation-tools.json` pins publisher-observed SHA-256 digests for Google's WFF validator and memory-footprint tool. The upstream `release` tag is mutable; hashes may change. Never remove checksum verification or blindly adopt downloaded bytes. Verify updated digests against the publisher's release asset metadata before changing the manifest.
- The original full GitHub Actions release gate in `.github/workflows/checks.yml` remains required. Node.js 20 deprecation warnings in pinned actions need a **separate future review**, with compatible action revisions and an independently passing full gate; do not bulk-upgrade them incidentally.
