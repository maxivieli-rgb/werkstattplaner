---
name: anrufen
description: Ruft den Nutzer per Telefon (Bland-API) an, um eine Entscheidung, Freigabe oder Antwort einzuholen, oder um zu melden, dass eine längere Aufgabe fertig ist. Verwenden, wenn der Nutzer "ruf mich an" sagt, wenn eine Session ausdrücklich mit Anruf-Rückfragen gestartet wurde, oder wenn eine Entscheidung nötig ist und der Nutzer gesagt hat, er sei unterwegs.
---

# Anrufen

Ruft den Nutzer an und liefert Zusammenfassung und Transkript des Gesprächs zurück.

## Wann anrufen

- Nur bei echten Entscheidungen, Freigaben oder einer Fertig-Meldung, nicht für Kleinigkeiten,
  die du mit einem vernünftigen Standard selbst lösen kannst.
- Höchstens ein Anruf pro offener Frage. Mehrere Fragen in einem Anruf bündeln.
- Keine Geheimnisse, Passwörter oder Kundendaten am Telefon vorlesen lassen.

## Ablauf

1. Formuliere das Anliegen kurz und am Telefon verständlich, idealerweise mit klaren
   Optionen ("A: … oder B: …?"). Keine Dateipfade oder Code vorlesen lassen.
2. Starte den Anruf (blockiert, bis das Gespräch vorbei ist, max. ~10 Minuten):

   ```bash
   python3 .claude/skills/anrufen/anruf.py "Soll der Kalender A: die Woche oder B: den Monat zuerst anzeigen?"
   ```

   Lange Wartezeit: das Bash-Timeout auf 660000 ms setzen.
3. Lies Zusammenfassung **und** Transkript. Arbeite mit der Antwort weiter und erwähne in
   deiner nächsten Nachricht, was am Telefon entschieden wurde.
4. Exit-Code 2 (nicht erreicht, Mailbox, Zeitlimit): nicht sofort erneut anrufen. Stelle die
   Frage stattdessen im Chat und arbeite an etwas anderem weiter, das nicht davon abhängt.

## Voraussetzungen

- `BLAND_TO_NUMBER` ist gesetzt (E.164, z. B. `+4917612345678`).
- Der Bland-API-Key ist als Netzwerk-Secret für `api.bland.ai` in der Cloud-Umgebung
  hinterlegt (der Proxy setzt ihn ein) oder lokal als `BLAND_API_KEY` exportiert.
- Fehler 401: Key fehlt/falsch. Fehler wegen Guthaben: Anrufe nach Deutschland brauchen
  bei Bland mindestens 5 $ gekauftes Guthaben.
