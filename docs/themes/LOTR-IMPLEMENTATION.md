# One Ring Classic – implementation log

Development branch: `feat/lotr-one-ring`; module: `:lotrwatchface`; package: `hu.fuloplevente.oneringwatchface`.

## Verified baseline – 2026-10-20

- Source commit: `d7ce6ec1c9790c1fab966146e7f1f7246f6cb9da`.
- [PR #4](https://github.com/fuloplevente1998/WearOS-Szamlap/pull/4) is open and draft; no merge or release is authorized.
- [Wear OS checks #18](https://github.com/fuloplevente1998/WearOS-Szamlap/actions/runs/39387216044) completed successfully on that source commit.
- Distinct resource-only WFF2 APK, `0.1.0-test` / version code `1`; HALO remains a separate module and package.
- 450 × 450 logical canvas; separate SVG-derived parchment map and gold bezel, with independent native hour, minute and second hands.
- Five editable native complication slots exist: battery (12), heart rate (9), steps (3), date (6), app shortcut (4:30). Each has an empty renderer; provider selection and tap actions still require device testing.
- The battery slot supports `RANGED_VALUE`, but currently displays provider text only; textless ranged data needs a targeted audit.
- Ambient variants hide the map, second hand and complication slots and reduce bezel alpha. Readability and power consumption are not device-verified.
- The picker uses generated `lotr_preview.png`, not the original reference. The preview contains illustrative values, never runtime health data.

## Validation and build prerequisites

The successful baseline CI ran the HALO release gate, LOTR static slot checks,
432/480 active/ambient preview generation and text bounds checks, Google WFF2
validation, LOTR debug assembly and Android lint. These are automated checks,
not evidence of Wear OS runtime behavior.

Map, bezel and picker PNGs are generated during CI and are not tracked in git.
A clean checkout needs `npm ci --ignore-scripts`,
`node scripts/render-lotr-assets.cjs` and
`node scripts/render-lotr-previews.cjs` before the LOTR Gradle build.
Set `CHROMIUM_PATH` if using a system Chromium/Chrome executable. See
[development setup](../DEVELOPMENT.md) for SDK/JDK requirements.

## Small-step priorities

1. Correct stale implementation/PR status against the existing code and CI.
2. Compare the 432/480 active and ambient illustrations with `references/one-ring.jpg`; record differences before changing artwork.
3. Refine the bezel engraving and parchment map toward the reference without replacing the working native scaffold.
4. Audit all five slot types, missing data, date formatting, long values and app shortcut behavior; extend checks where needed.
5. Audit ambient contrast and preview fidelity; keep HALO regression gates passing.
6. Produce a successful feature-branch test build and retain its APK/report artifact links.
7. Obtain Galaxy Watch7 feedback for data updates, native picker, taps, actual rendering and battery use.

## Remaining release blockers

- The map is a stylized illustration and the bezel uses decorative motifs; visual fidelity still needs review.
- No Galaxy Watch7 test is recorded. Date rollover, live health sources, empty states, provider selection, app launching and AOD readability remain unverified on device.
- CI uses a temporary debug certificate; update compatibility with an installed APK is not guaranteed. A retained LOTR signing strategy needs separate agreement.
- Keep the package ID/version unchanged. Main merge and final release require separate user approval.

Follow the [Watch7 checklist](MIDDLE-EARTH.md#galaxy-watch7-próba--ha-az-óra-fel-van-töltve) for device evidence.
