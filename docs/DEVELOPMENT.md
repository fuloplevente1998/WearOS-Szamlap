# Fejlesztőkörnyezet

## Projektarchitektúra és modulok

A repó több független Watch Face Format (WFF) 2 Gradle-modult tartalmaz:

| Téma | Gradle-modul | Csomagnév | Verzió |
| --- | --- | --- | --- |
| **HALO – Spartan Night** | `:watchface` | `hu.fuloplevente.spartannight` | `0.1.5-test` (code 6) |
| **Gyűrűk Ura – The One Ring** | `:lotr` | `hu.fuloplevente.onering` | `0.1.0-test` (code 1) |

Mindegyik számlap teljesen függetlenül építhető, ellenőrizhető és telepíthető.
A külön csomagnévnek köszönhetően a két számlap egyszerre is telepítve lehet a Galaxy Watch7-en.

## APK és ellenőrzések

Szükséges: JDK 21, Python 3.11+, Node 24, Chromium/Chrome, Android SDK 36, Build Tools 36.0.0,
Platform Tools, valamint a Gradle 9.2.1 wrapper (AGP 9.0.0).

```bash
sdkmanager 'platforms;android-36' 'build-tools;36.0.0' 'platform-tools'
npm ci --ignore-scripts
CHROMIUM_PATH=/usr/bin/google-chrome bash scripts/verify-fast.sh
CHROMIUM_PATH=/usr/bin/google-chrome bash scripts/verify.sh
```

A `verify-fast.sh` forrásalapú gyorsellenőrzést futtat (XML struktúra, WFF 2 séma mindkét modulra, ikonlogika).
A `verify.sh` mindkét modulra lefuttatja a teljes kaput:
- Eszközök letöltése/ellenőrzése (`wff-validator.jar`, `memory-footprint.jar`)
- Grafikák es XML generálása
- WFF 2 sémaellenőrzés (`:watchface` es `:lotr`)
- Gradle fordítás es lint (`:watchface:assembleDebug`, `:watchface:lintDebug`, `:lotr:assembleDebug`, `:lotr:lintDebug`)
- Csomagellenőrzés (`check-package.py` - APK struktúra, DEX hiánya, `Editable=true`)
- Memória-footprint becslés mindkét APK-ra

A lefordított APK-k helye:
- HALO: `watchface/build/outputs/apk/debug/watchface-debug.apk` (tesztcsomag: `dist/verify/SpartanNight-0.1.5-test.apk`)
- LOTR: `lotr/build/outputs/apk/debug/lotr-debug.apk`

## Egyedi modulok építése

```bash
./gradlew :watchface:assembleDebug  # Csak HALO
./gradlew :lotr:assembleDebug       # Csak LOTR
```

## Grafika szerkesztése és generálása

```bash
# HALO grafikák
python3 scripts/generate-watchface.py
CHROMIUM_PATH=/usr/bin/google-chrome node scripts/render-assets.cjs

# LOTR grafikák és előnézetek
CHROMIUM_PATH=/usr/bin/google-chrome node scripts/export-lotr-assets.cjs
CHROMIUM_PATH=/usr/bin/google-chrome node scripts/render-lotr-mockups.cjs
```

## Telepítés órára

Az APK-k egymás mellett telepíthetők ADB-n keresztül:

```bash
adb connect ORA_IP:PORT
adb install -r watchface/build/outputs/apk/debug/watchface-debug.apk
adb install -r lotr/build/outputs/apk/debug/lotr-debug.apk
```
