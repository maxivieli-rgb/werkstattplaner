# Werkstattplaner in den App Store – nur mit dem iPhone

Du brauchst: dein iPhone, Safari, 99 € für Apple, ca. 2 Stunden verteilt auf ein paar Tage.
Kosten danach: 99 €/Jahr an Apple. GitHub und Codemagic sind kostenlos (Codemagic: 500 Build-Minuten im Monat gratis, ein Build dauert ca. 15 Minuten).

Tipp: Wenn eine Seite in Safari zu klein oder abgeschnitten ist: unten links auf **„aA“** → **„Desktop-Website anfordern“**.

---

## Schritt 1 – Apple-Entwicklerkonto (einmalig, 1–2 Tage Wartezeit)
1. App **„Apple Developer“** aus dem App Store laden.
2. Mit deiner Apple-ID anmelden → **Konto** → **Jetzt registrieren**.
3. Als **Einzelperson** registrieren, 99 € bezahlen.
4. Warten, bis die Mail „Welcome to the Apple Developer Program“ kommt.

## Schritt 2 – GitHub (Ablage für die App-Dateien)
1. In Safari **github.com** öffnen → **Sign up** → Konto anlegen.
2. Oben rechts **+** → **New repository** → Name: `werkstattplaner` → **Private** → **Create repository**.
3. **Dateien hochladen – am einfachsten mache ich das für dich:**
   Verbinde GitHub mit Claude (claude.ai → Einstellungen → Konnektoren → GitHub) und schreib mir „Repo ist da“. Ich lade dann alles hoch.
   *(Selbst hochladen geht auch: ZIP in der Dateien-App entpacken, auf GitHub „Add file → Upload files“. Achtung: Ordner müssen dabei erhalten bleiben – vom Handy ist das fummelig.)*

## Schritt 3 – Bundle-ID bei Apple anlegen
1. Safari: **developer.apple.com/account** → anmelden → **Certificates, IDs & Profiles** → **Identifiers** → **+**.
2. **App IDs** → **App** → Weiter.
3. Description: `Werkstattplaner`, Bundle ID **Explicit**: `de.werkstattplaner.meister` → **Register**.

## Schritt 4 – App in App Store Connect anlegen
1. Safari: **appstoreconnect.apple.com** (oder App „App Store Connect“) → **Apps** → **+** → **Neue App**.
2. Plattform **iOS**, Name **Werkstattplaner – Kfz** (siehe `STORE-TEXTE.md`, falls vergeben), Sprache **Deutsch**, Bundle-ID `de.werkstattplaner.meister`, SKU `werkstattplaner1`, Zugriff **Voll**.
3. Danach unter **App-Informationen** die **Apple-ID** notieren (eine lange Zahl, z. B. 6745123456). Die brauchst du in Schritt 6.

## Schritt 5 – API-Schlüssel für Codemagic
1. App Store Connect → **Benutzer und Zugriff** → **Integrationen** → **App Store Connect API** → **Team-Schlüssel** → **+**.
2. Name `Codemagic`, Zugriff **App-Manager** → **Generieren**.
3. **Schlüssel herunterladen** (geht nur EIN Mal! Datei `AuthKey_XXXX.p8` landet in der Dateien-App).
4. **Issuer-ID** und **Schlüssel-ID** notieren.

## Schritt 6 – Codemagic einrichten
1. Safari: **codemagic.io** → **Sign up with GitHub**.
2. **Add application** → GitHub → Repo `werkstattplaner` → Projekttyp **Other / codemagic.yaml**.
3. Oben **Teams** → dein Team → **Integrations** → **Developer Portal** → **Connect**:
   - Name: **`werkstatt_asc`** (genau so!)
   - Issuer ID, Key ID eintragen, `.p8`-Datei hochladen → **Save**.
4. In der App → **Environment variables**:
   - Variable `APP_STORE_APPLE_ID` = die Zahl aus Schritt 4, Gruppe **`appstore`** → **Add**.

## Schritt 7 – App bauen
1. Codemagic → deine App → **Start new build** → Workflow **Werkstattplaner iOS** → **Start**.
2. Nach ca. 15 Minuten ist die App bei Apple in **TestFlight**.
3. App **„TestFlight“** aufs iPhone laden → die App installieren und ausprobieren.
4. Klappt etwas nicht: Schick mir einen Screenshot vom roten Fehler in Codemagic.

## Schritt 8 – Store-Eintrag und Prüfung
1. Datenschutzseite online stellen: GitHub → Repo → **Settings** → **Pages** → Branch `main`, Ordner **`/docs`** → Save.
   Vorher in `docs/datenschutz.html` und `docs/index.html` **deinen Namen, Adresse und E-Mail** eintragen (Pflicht!).
2. App Store Connect → deine App → **App-Datenschutz** → „Daten werden nicht erfasst“.
3. Version 1.0: Texte aus `STORE-TEXTE.md` einfügen, Screenshots aus `store-screenshots` hochladen (6,9"-Display).
4. **Build** auswählen (der aus TestFlight), Altersfreigabe ausfüllen, Preis **Kostenlos**.
5. **Zur Prüfung einreichen**. Apple prüft meist in 1–3 Tagen.

## Später: neue Version
Ich ändere die App, lade sie auf GitHub, du tippst in Codemagic auf **Start new build** und reichst die neue Version in App Store Connect ein.

---

### Was in der Store-Version drin ist – und was nicht
**Drin:** Aufträge, Arbeiten mit Paketen, Teile mit EK/VK, Lager, Planer, Kunden, Kalkulator, Kostenvoranschlag und Rechnung als PDF, WhatsApp/Mail, Übersicht, Datensicherung.
**Nicht drin** (läuft nur in claude.ai): Jarvis, Kontroll-Bot, KI-Fehlersuche, Öl-/Drehmoment-Suche, automatische Wochenplanung, Gmail-Bestellungen, Garantie-Ordner.
Deine echten Kundendaten sind **nicht** in der Store-App – jeder Nutzer startet leer.
