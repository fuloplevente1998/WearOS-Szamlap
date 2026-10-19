# Fejlesztőkörnyezet

## Jules: környezet és tesztszintek

A **Jules Initial Setup** csak a függőségeket és az Android SDK-t telepítse,
majd legfeljebb a `./gradlew --version` parancsot futtassa. **Ne fusson benne**
a `bash scripts/verify.sh`: ez a Google változó `release` címkéjéről tölt
eszközöket, ezért egy külső kiadásváltozás blokkolná a Jules snapshot készítését.

A Jules feladatban, a kívánt fejlesztési ág checkoutja után:

```bash
# Csak WFF XML, erőforrások, panelvágás, ikonlogika és WFF 2 séma:
bash scripts/verify-fast.sh

# Kiadás előtti teljes ellenőrzés + a nem frissítéskompatibilis
# ideiglenes cloud/debug aláírás kötelező ellenőrzése:
bash scripts/verify-jules.sh
```

A helyi, megbízható tesztaláíró környezetben a teljes kapu továbbra is
`bash scripts/verify.sh`. A Jules semmilyen módon nem kaphatja meg a megtartott
tesztkulcsot vagy annak jelszavát, és nem publikálhat APK-t.

A Google WFF JAR-ok letöltése SHA-256 ellenőrzött: a kiadási címke
2026-10-16-án megváltozott, ezért a két érték frissítve lett a Google által
közzétett release-asset digest alapján. Ha a Google újra cseréli őket,
a letöltést szándékosan meg kell állítani és a forrást újra ellenőrizni;
a checksum-védelmet nem szabad kikapcsolni.

A GitHub Actions Node.js 20 deprecációs figyelmeztetéseinek és a rögzített
action-verzióknak a felülvizsgálata későbbi, külön feladat. A jelenlegi
CI Release gate változatlan maradt.


## APK és ellenőrzések

Szükséges: JDK 21, Python 3.11+, Node 24, Chromium/Chrome, Android SDK 36, Build Tools 36.0.0,
Platform Tools, valamint a projektben található Gradle 9.2.1 wrapper.
Az AGP verziója 9.0.0. A wrapper ellenőrzi a Gradle ZIP SHA-256 értékét.

```bash
sdkmanager 'platforms;android-36' 'build-tools;36.0.0' 'platform-tools'
npm ci --ignore-scripts
CHROMIUM_PATH=/a/chromium/vagy/chrome/utvonala bash scripts/verify.sh
```

A parancs letölti és SHA-256 alapján ellenőrzi a Google WFF-eszközeit,
generálja és ellenőrzi az XML-t, majd UI-geometria-/szövegellenőrzést, buildet, lintet, csomag-, ikon-, memória-,
aláírás- és igazításvizsgálatot futtat. A verziózott APK és a jelentések a
`dist/verify/` könyvtárba kerülnek. A Google `release` címkéje változhat;
az ismert SHA-tól eltérő eszközt a letöltő elutasítja. Frissítéskor a forrást
és a közzétett artifact-digestet is ellenőrizni kell.

## Meglévő Codex felhőkörnyezet

```bash
source /workspace/.wearos-setup/env.sh
CHROMIUM_PATH=/usr/bin/chromium GRADLE_OFFLINE=1 REQUIRE_TEST_CERTIFICATE=1 bash scripts/verify.sh
```

A WFF-eszközök első alkalommal hálózati letöltést igényelnek; utána a rögzített
hash alapján újrahasználhatók. A meglévő környezetet és checkoutot használjuk.
Munkafához nincs szükség új worktree-re. Az APK és az XML tesztelése nem
igényel futó szolgáltatást vagy APK-telepítést.

Ebben a felhőben nincs működő KVM-alapú Wear OS emulátor. A rajzolás és a natív
választó végső ellenőrzése a felhasználó Watch7 óráján történik. Nem szabad
egy böngészős képet Android-képernyőképként vagy a memória-becslést mért
fogyasztásként bemutatni.

## Grafika szerkesztése

A normál Gradle APK-build a repóban tárolt PNG-ket használja, Node nélkül is
futtatható. A teljes ellenőrzőkapu és a grafikai módosítások Playwright 1.62.1-et
és Chromiumot/Chrome-ot használnak; az npm-lockfile rögzíti a függőségeket:

```bash
python3 scripts/generate-watchface.py
CHROMIUM_PATH=/usr/bin/chromium node scripts/render-assets.cjs
```

A kanonikus geometria `scripts/hud_geometry.py`, a részletes ikonok
`scripts/hud_icons.py`, a névpárosítások `design/icon-pairings.json` fájlban vannak.
A 432/480 px, hosszú értékes, kikapcsolt mezős és ambient előnézetek illusztrációk.
A szövegmérés ugyanazzal a csomagolt fonttal történik.
A `CHECK_ONLY=1` ellenőrzőmód a csomagolt PNG-ket vizsgálja, és nem írja át őket.

## Ikoncsere tesztje

```bash
python3 scripts/icon_checks.py
python3 scripts/icon_checks.py dist/verify/SpartanNight-0.1.5-test.apk
```

A teszt a valódi XML konfigurációs és feltételágait értékeli ki. Megvizsgálja
az appnév változtatását, a cím elsőbbségét, a magyar/angol aliasokat, az ismeretlen
nevet és a kézi módot, illetve kizárja az Android-ikonok használatát. Ez nem
Wear OS futtatás; a forrás ténylegesen átadott nevét készüléken kell ellenőrizni.
