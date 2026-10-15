# Fejlesztési irány

A HALO / Spartan Night az első működő számlap. A többi téma a felhasználó
döntése alapján most terv és referenciaanyag; megvalósításuk külön lépés.

## 1. A HALO készülékes lezárása

- Galaxy Watch7-en ellenőrizni az új APK-t: 432 és 480 px elrendezés,
  olvasható felső címek, teljes lépésszám és akkumulátorérték, hosszú appnév.
- Mind a nyolc mezőben forrás- és alkalmazáscsere a natív szerkesztővel.
  Health → szív, akkumulátor → akkujel, lépések → cipő, TrainPilot → futó.
- Rögzíteni a Watch7 által ténylegesen átadott magyar/angol címeket és neveket;
  ezekkel bővíteni az explicit ikonpárosításokat. A WFF nem ad appcsomag-azonosítót.
- Név nélküli forrásnál a kézi HALO-jel megtartása. Nem következtetünk az
  adat fajtájára pusztán egy számból vagy százalékból.
- A Nincs / None minden mezőből eltünteti a keretet, ikont és szöveget.
- Koppintási műveletek, jogosultság nélkül/hiányzó adatokkal való megjelenés,
  beállítások megmaradása újraindítás és számlapváltás után.
- Aktív és always-on képernyőkép, majd valós fogyasztáspróba. A felhőben
  futó memóriabecslés nem helyettesít akkumulátorüzemidő-mérést.

## 2. HALO-dizájn finomítása

Zöld idő és külső gyűrű; jégcián értékek és alsó ikonok; körívet követő,
áttetsző panelek; egymáshoz illesztett töréspontok; digitális grafit lunetta.
Minden változtatást olvashatósági ellenőrzés kövessen. A fizikai tok és a
csavarozott külső lunetta a referenciafotó része, a kijelző csak digitális
keretet rajzolhat. Az óra és az adatok élők, nem képre égetett feliratok.

## 3. Közös témarendszer előkészítése

Az adatmezők, szerkesztés, ikonfelismerés, ambient nézet és ellenőrzések közös
alapot kapjanak. A témák geometriája, ikonja, betűkészlete és háttere külön
erőforrás legyen. A több téma hozzáadása előtt kell eldönteni, melyik legyen
külön APK/csomagnév; a már telepített HALO csomagneve és aláírása maradjon meg.

A közös követelmény legfeljebb nyolc natív mező, cserélhető adatforrás,
teljesen eltűnő kikapcsolt panelek és takarékos always-on nézet. Az analóg
Egy Gyűrű-változat használhat kevesebb mezőt, hogy a térkép olvasható maradjon.

## 4. Következő témák

| Téma | Vizuális cél | Első megvalósítandó rész |
| --- | --- | --- |
| God of War / Kratos | Jeges kék, bronz, rúna, balta vagy Kratos-motívum | Rúna- és ikonlap, körhöz illesztett panelek |
| Egy Gyűrű | Arany peremgyűrű, pergamentérkép, analóg mutatók | Valódi mutatók és külön gyűrű-/térképréteg |
| Középfölde HUD | Kékes térkép, bronz keretek, kalandos panelek | Digitális adatmezős változat |
| Star Wars | Kék/vörös oldalak, fénykardok, sötét űrháttér | Kétoldalas színkiosztás, saját tematikus ikonok |

A tervek nem működő számlapok. A következő téma megvalósítási sorrendjét a HALO
készülékes visszajelzése után érdemes véglegesíteni.

## 5. Kiadás

A [kiadási kapuk](RELEASES.md) kötelező automatizált ellenőrzéseket írnak le.
A jelenlegi kiadások fejlesztői tesztkulcsos prerelease-ek. Végleges kiadáshoz
készülékes jegyzőkönyv és külön kezelt éles aláírás szükséges; a jelenlegi
feltöltőszkript kizárólag `-test` verziót, prerelease-ként publikál.
