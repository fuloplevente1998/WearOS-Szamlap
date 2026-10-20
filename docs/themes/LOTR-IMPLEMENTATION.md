# One Ring Classic – implementation log

Development branch: `feat/lotr-one-ring`; module: `:lotrwatchface`; package: `hu.fuloplevente.oneringwatchface`.

## Stage 1 – native analog scaffold

- Distinct resource-only Watch Face Format 2 APK from HALO / Spartan Night.
- 450 × 450 coordinate space, round face, dark bronze and antique golden ring up to physical display boundary.
- Independent resource-backed hour, minute and second hands (seconds hidden in ambient).
- Separate existing reference mockup used only as temporary watch-face picker preview, **not** the runtime background (it contains static clock hands).

## Pending

- Extract/create clean Middle-earth parchment map layer without baked hands.
- Detailed golden elvish inscription, replace simple gradient-like circles.
- Five editable native complications: battery (12), pulse (9), steps (3), date (6), workout shortcut (4:30).
- Ambient simplified map/ring, 432/480 preview, Google WFF validation, CI build, physical Watch7 testing.

No build or validation result is claimed for stage 1. The HALO release gate is unchanged.
