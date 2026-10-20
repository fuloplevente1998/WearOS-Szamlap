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

- The map is a stylized illustration and the bezel uses decorative motifs; the first visual review below identifies remaining fidelity work.
- No Galaxy Watch7 test is recorded. Date rollover, live health sources, empty states, provider selection, app launching and AOD readability remain unverified on device.
- CI uses a temporary debug certificate; update compatibility with an installed APK is not guaranteed. A retained LOTR signing strategy needs separate agreement.
- Keep the package ID/version unchanged. Main merge and final release require separate user approval.

Follow the [Watch7 checklist](MIDDLE-EARTH.md#galaxy-watch7-próba--ha-az-óra-fel-van-töltve) for device evidence.

## First visual review – 2026-10-20

Generated and visually inspected all four 432/480 px active/ambient illustrations
against `references/one-ring.jpg`. Local rasterization used Chromium 153.0.8010.0;
the installed fallback font differs from CI, so the existing text check exposed
an overflow that the previous CI did not catch. No physical watch was used.

- **Fixed:** `NYITÁS` was 38.70 px wide in a 36.48 px available text area at 432 px. Reduced only that caption from 10 to 9 logical units in both workout renderers (`SHORT_TEXT` and `LONG_TEXT`); the slot bounds, IDs, provider and tap behavior are unchanged. Existing text checks now pass at both sizes.
- **Active:** all five fields stay inside the bezel. The sparse repeated terrain symbols, dashed region shapes and large map labels differ substantially from the reference's dense ink cartography. The four repeated bezel glyph shapes also need more flowing engraving detail.
- **Ambient illustration:** the map, data fields and second hand are absent; the two main hands remain distinguishable in these generated images. This is not a native rendering or power-use result.
- **Preview fidelity to audit:** the preview draws hands after the fields, whereas the WFF lists the slots after the clock. Its hard-coded bezel alpha also needs comparison with native WFF semantics before treating the ambient illustration as representative.

Next visual step: improve one artwork layer at a time, starting with the bezel
engraving, while keeping the native scaffold and the five existing slots.

## Bezel engraving refinement – 2026-10-20

- Replaced the four repeating angular motifs with twelve curved calligraphic path forms, arranged as 58 marks in four spaced phrases. These are decorative Elvish-inspired marks, **not a verified transcription of the Ring inscription**.
- Added a dark engraved cut, warm gold infill and a fine edge highlight. Paths are font-independent and rasterized once; there is no runtime animation or additional WFF layer.
- Preserved the existing ring geometry, metal gradients, map, hands and native complication implementation. Package ID and version are unchanged.
- Regenerated and visually inspected 432/480 active and ambient illustrations. Existing 20 text bounds checks and the native slot checks pass locally.
- Pixel comparison with the preceding revision confirms that changes in all four illustrations are confined to the engraving band (logical radius 194–216). The inner map, fields and hands are unchanged.
- The result is a finer decorative treatment; authentic inscription fidelity, detailed map artwork, preview/native layer order and AOD semantics still need further work. Watch7 rendering and power use remain untested.

Next step: refine the parchment map toward the reference's denser cartography.

## Parchment map detail pass – 2026-10-20

- Refined the existing mountain/tree symbols and added smaller ridgelines, clustered woodland, river branches, contour/coast hatching and settlement marks. The existing map layer and parchment treatment remain in use.
- Reduced the opacity and weight of the large region shapes and removed their dashed outlines, so they no longer dominate the ink details.
- Repositioned and reduced the main place names to avoid the five complication rectangles; added small Mirkwood, Erebor and northern-region labels. All 11 map label bounds were measured with local Chromium and avoid the native slot bounds.
- This remains a stylized Middle-earth illustration, not an exact geographic or artistic reproduction of the reference.
- Regenerated and visually inspected all four 432/480 active/ambient illustrations. Existing 20 complication text checks and native slot checks pass locally.
- Pixel comparison confirms active changes stay within the map circle (logical radius below 191); both ambient illustrations are pixel-identical to the preceding revision. The bezel, WFF, package ID, version and HALO sources are unchanged.

Next step: audit preview/native drawing order and ambient alpha semantics before
further visual decisions. Device rendering and live complication behavior remain
pending Galaxy Watch7 testing.

## Native/preview order and ambient fix – 2026-10-20

- Confirmed [WFF scene traversal order](https://developer.android.com/training/wearables/wff/effects) and the [integer 0–255 PartImage alpha scale](https://developer.android.com/reference/wear-os/wff/group/part/image/part-image) against Android's documentation.
- Moved the existing native clock and hub after the five slots. Opaque complication backgrounds can no longer draw over the hands; the hub remains last. Slot IDs, bounds and provider policies are unchanged.
- Corrected the native ambient bezel alpha from `0.35` (not 35% on this scale) to `89`, approximately 35% opacity. Map, fields and second hand remain hidden in ambient.
- The limited illustration renderer now traverses the XML scene order and reads mode alpha, scene background, preview time, hand geometry/pivots and hub geometry from WFF. Unknown scene elements fail explicitly. Complication samples and their simplified text/frame rendering are still illustrative, not a complete Wear OS renderer.
- Added per-size active/ambient drawing traces to `layout-report.json`; ambient traces contain only the bezel, hour/minute hands and hub.
- Extended static checks for integer alpha, hidden ambient elements, centered pivots and foreground hand/hub order. Six temporary regression mutations (fractional alpha, visible map/slot/seconds, wrong clock order and offset pivot) were all rejected.
- Regenerated and visually inspected all four 432/480 illustrations; all 20 existing text checks pass locally. HALO sources, artwork, package ID and version are unchanged.

Next step: audit native complication data types and fallbacks, especially
textless ranged battery data and date/app shortcut compatibility. Live data,
tap behavior, native rendering and power use still require Galaxy Watch7 tests.
