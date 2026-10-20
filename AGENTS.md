# Agent instructions — WearOS-Szamlap

Applies to Jules, Codex and other automated coding agents working in this repository.

## Project architecture and modules
This repository contains multiple Watch Face Format (WFF) 2 watch face Gradle modules:
- **`:watchface`**: **SpartanNight** (HALO theme) — Package: `hu.fuloplevente.spartannight` (versionCode 6, versionName `0.1.5-test`).
- **`:lotr`**: **The One Ring** (Lord of the Rings theme) — Package: `hu.fuloplevente.onering` (versionCode 1, versionName `0.1.0-test`).
- Gradle scripts use Kotlin DSL, but watch faces are resource-only WFF 2 apps without DEX (`android:hasCode="false"`).
- Runtime implementations live in `<module>/src/main/res/raw/watchface.xml`.
- Requirements: JDK 21, Gradle wrapper 9.2.1, AGP 9.0.0, Android SDK 36, Build Tools 36.0.0, Node 24 / Playwright 1.62.1 / Chromium.

## Change and validation policy
- For small XML, layout or icon changes, run `bash scripts/verify-fast.sh` first. It validates XML source structures, resources, slot counts, provider/icon logic and Google's WFF 2 schemas for all modules.
- Generated XML and SVG assets must agree with canonical generator scripts (`scripts/generate-watchface.py` for HALO, `scripts/export-lotr-assets.cjs` and `scripts/render-lotr-mockups.cjs` for LOTR).
- Before merging or creating test APKs, run `bash scripts/verify.sh` (or `bash scripts/verify-jules.sh` in Jules), which performs full verification across both modules (schema, Gradle build, lint, package checks, memory footprint estimates).
- Full validation covers deterministic resource generation, visual geometry/mockups, Google schema, Gradle assemble/lint, packaged resources, icon switching, memory estimates, APK signatures and alignment.
- Report CI results separately from checks actually run in current environment. A Chromium preview is not a native watch screenshot; memory estimate is not measured battery usage.

## Versions, compatibility and pull requests
- Do not change HALO `versionCode` (6) or `versionName` (`0.1.5-test`), `applicationId`, namespace, minSdk/targetSdk, or HALO signing identity without explicit owner approval.
- LOTR operates independently under package `hu.fuloplevente.onering`, allowing side-by-side installation on Galaxy Watch7 alongside HALO.
- Work on a separate feature branch. Do not merge into `main`, create a PR, publish a release or upload an APK without explicit instruction.

## Signing / private-key boundaries
- Cloud agents must use disposable debug keys (`REQUIRE_TEST_CERTIFICATE=0`).
- Agents must never access, import, stage, request, decode, upload or reproduce the owner's retained HALO test signing key.
- The retained test signing certificate applies only to HALO prereleases in trusted signing environments (`REQUIRE_TEST_CERTIFICATE=1`), following `docs/RELEASES.md`.

## External tools and CI upkeep
- `design/validation-tools.json` pins publisher-observed SHA-256 digests for Google's WFF validator and memory-footprint tool. Never bypass checksum verification.
- `.github/workflows/checks.yml` handles CI validation and artifact publishing (`halo-watchface-${{ github.sha }}` and `lotr-watchface-${{ github.sha }}`).
