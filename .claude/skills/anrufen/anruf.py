#!/usr/bin/env python3
"""Ruft den Nutzer über die Bland-API an und gibt das Gesprächsergebnis aus.

Aufruf:
    python3 anruf.py "Frage oder Info, die am Telefon besprochen werden soll"

Umgebungsvariablen:
    BLAND_TO_NUMBER   Zielnummer im E.164-Format, z. B. +4917612345678 (Pflicht)
    BLAND_API_KEY     API-Key. In Claude-Code-Cloud-Sessions setzt der Netzwerk-Proxy
                      den echten Key ein; dann reicht der Platzhalter.
    BLAND_VOICE       Optional: Stimme (Standard: Bland-Default)
    BLAND_MAX_WAIT    Optional: maximale Wartezeit in Sekunden (Standard: 600)

Exit-Codes: 0 = Gespräch geführt, 2 = nicht erreicht/abgebrochen, 1 = Fehler.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = "https://api.bland.ai/v1/calls"
KEY = os.environ.get("BLAND_API_KEY", "platzhalter-wird-vom-proxy-ersetzt")


def request(method, url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {KEY}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        sys.exit(f"Bland-API-Fehler {e.code}: {e.read().decode(errors='replace')}")


def main():
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        sys.exit("Bitte die Frage/Nachricht als Argument übergeben.")
    nummer = os.environ.get("BLAND_TO_NUMBER")
    if not nummer:
        sys.exit("BLAND_TO_NUMBER ist nicht gesetzt (Format +49...).")
    anliegen = sys.argv[1].strip()

    task = (
        "Du bist der Assistent eines Softwareprojekts (Werkstattplaner) und rufst "
        "den Entwickler an, weil der KI-Coding-Agent eine Entscheidung oder Info braucht. "
        "Sprich ausschließlich Deutsch, freundlich und knapp. "
        f"Anliegen: {anliegen}\n"
        "Erkläre das Anliegen in ein bis zwei Sätzen, stelle die Frage und höre die Antwort an. "
        "WICHTIG: Fragt zuerst eine automatische Anrufprüfung (z. B. iPhone-Anruffilter) "
        "nach Name und Grund des Anrufs, dann ist das KEINE Mailbox. Antworte darauf genau: "
        "'Hier ist Claude, der KI-Assistent vom Werkstattplaner, mit einer kurzen Rückfrage.' "
        "Lege dann NICHT auf, sondern warte still, bis die Person selbst rangeht, und "
        "beginne erst dann mit dem Anliegen. "
        "Wenn die Antwort unklar ist, frage einmal nach. Wiederhole die Entscheidung zum Schluss "
        "kurz zur Bestätigung, bedanke dich und beende das Gespräch. Erfinde keine Details."
    )
    body = {
        "phone_number": nummer,
        "task": task,
        "language": "de",
        "first_sentence": "Hallo, hier ist Claude, dein KI-Assistent vom Werkstattplaner.",
        "wait_for_greeting": True,
        "max_duration": 5,
        "summary_prompt": (
            "Fasse auf Deutsch in einem Satz zusammen, welche Entscheidung oder Antwort "
            "der Angerufene gegeben hat. Wenn keine klare Antwort kam, schreibe das."
        ),
    }
    if os.environ.get("BLAND_VOICE"):
        body["voice"] = os.environ["BLAND_VOICE"]

    start = request("POST", API, body)
    call_id = start.get("call_id")
    if not call_id:
        sys.exit(f"Kein call_id erhalten: {json.dumps(start, ensure_ascii=False)}")
    print(f"Anruf gestartet (call_id {call_id}), warte auf Ergebnis ...", flush=True)

    deadline = time.time() + int(os.environ.get("BLAND_MAX_WAIT", "600"))
    info = {}
    while time.time() < deadline:
        time.sleep(10)
        info = request("GET", f"{API}/{call_id}")
        if info.get("completed") or info.get("status") in (
            "completed", "failed", "busy", "no-answer", "canceled"
        ):
            # Zusammenfassung wird kurz nach Gesprächsende erzeugt
            for _ in range(6):
                if info.get("summary"):
                    break
                time.sleep(5)
                info = request("GET", f"{API}/{call_id}")
            break
    else:
        print("Zeitlimit erreicht, Anruf noch nicht abgeschlossen.")
        sys.exit(2)

    status = info.get("status")
    answered_by = info.get("answered_by")
    print(f"Status: {status} | angenommen von: {answered_by} | Dauer: {info.get('call_length')} min")
    print(f"Zusammenfassung: {info.get('summary') or '-'}")
    print("Transkript:")
    print(info.get("concatenated_transcript") or "-")
    if status != "completed" or answered_by in ("voicemail", "no-answer"):
        sys.exit(2)


if __name__ == "__main__":
    main()
