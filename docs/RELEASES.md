# Kiadási kapuk és aláírás

## Kötelező automatizált kapu

A `Wear OS checks` workflow `Release gate` nevű jobja minden main pushnál,
PR-nél és kézi indításnál fut. A job akkor sikeres, ha az alábbiak mind átmentek:

1. A generált WFF XML, SVG és metaadat egyezik a forrással; UI-geometria és
   szövegilleszkedés 432/480 px méreten, az APK telepítése nélkül.
2. Google WFF 2 sémavizsgálat, `--stop-on-fail` kapcsolóval.
3. APK-build és Android lint; lint-hiba nem megengedett.
4. Nyolc szerkeszthető mező, teljes rajzolási határok, rejtett EMPTY panelek,
   csomagolt font és erőforrások, `Editable=true`, DEX nélküli APK.
5. Saját HALO-ikonok névpárosítása és váltása; nincs Android-ikon.
6. Google aktív/ambient memóriabecslés: 100/10 MB korlát.
7. APK-aláírás és igazítás ellenőrzése.

A workflow és a Gradle letöltései rögzített verziót/commitot és ellenőrzőösszeget
használnak. A CI az APK-t és jelentéseket 14 napig artifactként tárolja.

## Frissíthető tesztkiadás

A publikus prerelease a megtartott **helyi tesztkulccsal** aláírt APK-t tartalmazza.
A kulcs és jelszava nem kerül a repóba vagy artifactba. A mostani GitHub-kapcsolat
nem engedi a Secrets-kezelést; ezért a CI ideiglenes debugkulccsal épít, és a
CI-snapshot nem frissíti a felhasználónál lévő APK-t. A release-feltöltő ezt az
eltérő tanúsítványt elutasítja. A CI-snapshot telepítése helyett a Releases
oldalról kell letölteni a frissíthető APK-t.

Teszt-tanúsítvány SHA-256:
`4e014742bb0b3aee16dcb2cb6fb97cf91a784233e84bf230429ad5dd83bd8f84`

Munkamenet a helyi, megtartott tesztkulccsal:

```bash
git switch main
# Minden forrásváltoztatás commitolása és push után:
source /workspace/.wearos-setup/env.sh
CHROMIUM_PATH=/usr/bin/chromium GRADLE_OFFLINE=1 REQUIRE_TEST_CERTIFICATE=1 bash scripts/verify.sh
# A GitHub Release gate sikeres befejezése után:
python3 scripts/publish-test-release.py
```

A feltöltő csak tiszta main ágról, a távoli main aktuális commitjához tartozó
helyi jelentéssel és sikeres GitHub-kapuval publikál. Ellenőrzi az APK hashét,
a tesztaláírás folytonosságát és a `-test` verziót. Mindig prerelease-t készít,
SHA-256 fájllal és jelentéssel. Meglévő kiadást nem cserél le: új verzió szükséges.

A felhő GitHub-kapcsolata az `uploads.github.com` végponton nem biztosít
hitelesítést. Ezért a script csak a már aláírt APK-t, SHA-fájlt, jelentést és
kiadási szöveget teszi egy külön, átmeneti `codex/release-assets-…` ágra; a main
nem tartalmaz APK-binárisokat. Az ág pontos commitjával kézi GitHub-workflow-t
indít. A workflow újra lefuttatja a Release gate-et, majd az aláírás és a csomag
újbóli ellenőrzése után, saját GitHub-tokenjével feltölti a release asseteket.
A kulcs nem hagyja el a helyi környezetet. Sikeres publikálás után kizárólag
az adott kiadáshoz létrehozott átmeneti ág törölhető.

## Készülékes kapu és végleges kiadás

A teszt-prerelease közli, hogy az új verzió Watch7-es ellenőrzése még hátravan.
Végleges kiadáshoz rögzíteni kell a rendszerverziót, kijelzőméretet, aktív/AOD
képeket, nyolc mező forráscseréjét, Nincs állapotát, koppintásait, az ikonok
felismerését, az újraindítás utáni beállításokat és fogyasztáspróbát.

A jelenlegi script nem tud stabil/Play-kiadást publikálni. Az éles aláírás és
annak védett tárolása külön beállítás, a készülékes jegyzőkönyv pedig külön
stabil kiadási kapu lesz. A tématervekhez addig nincs APK, amíg natív
implementációjuk és saját ellenőrzési eredményük el nem készül.
