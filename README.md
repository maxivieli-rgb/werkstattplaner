# Werkstattplaner (iOS)

Eigenständige Version des Werkstattplaners als iPhone-App (Capacitor).

- `www/index.html` – die App (alle Daten lokal auf dem Gerät)
- `capacitor.config.json` – App-Name, Bundle-ID, Farben
- `codemagic.yaml` – Cloud-Build ohne Mac + Upload zu TestFlight
- `resources/` – App-Symbol und Startbild
- `docs/` – Hilfe- und Datenschutzseite (GitHub Pages)
- `store-screenshots/` – Screenshots für den App Store
- `ANLEITUNG.md` – Schritt für Schritt nur mit dem iPhone
- `STORE-TEXTE.md` – Texte für App Store Connect
- `build.py`, `shim.js` – erzeugen `www/index.html` aus der claude.ai-Version
