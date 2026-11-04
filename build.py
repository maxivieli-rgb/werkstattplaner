#!/usr/bin/env python3
"""Baut aus der claude.ai-Version (app.html) die eigenständige App www/index.html."""
import re, sys, pathlib

WEB = "--web" in sys.argv  # Version für den Link (läuft in claude.ai-Ansicht): Leiste oben lassen
args = [a for a in sys.argv[1:] if not a.startswith("--")]
SRC = pathlib.Path(args[0] if args else "/home/claude/app/app.html")
OUT = pathlib.Path(__file__).parent / ("web" if WEB else "www") / "index.html"
s = SRC.read_text(encoding="utf-8")


def rep(a, b, count=1):
    global s
    n = s.count(a)
    assert n == count, f"{n}x statt {count}x: {a[:80]!r}"
    s = s.replace(a, b)


def rx(pattern, repl, count=1, flags=re.S):
    global s
    s, n = re.subn(pattern, repl, s, flags=flags)
    assert n == count, f"{n}x statt {count}x: {pattern[:80]!r}"


# --- Kopf: Titel, eigenes viewport, keine Online-Schriften (App muss offline gehen) ---
rep("<title>App-Zentrale</title>", "<title>Werkstattplaner</title>")
rep('<meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover">',
    '<meta name=viewport content="width=device-width,initial-scale=1,maximum-scale=1,viewport-fit=cover">'
    '<meta name="format-detection" content="telephone=no"><meta name="theme-color" content="#141518">')
rx(r'<link rel="preconnect" href="https://fonts\.googleapis\.com">\s*', "")
rx(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2[^"]*">\s*', "")

# --- lokaler Speicher statt claude.ai ---
shim = (pathlib.Path(__file__).parent / "shim.js").read_text(encoding="utf-8")
s = s.replace("window.claude", "window.__wp")
rep("<script>\n", "<script>\n" + shim + "\n</script>\n<script>\n")
rep('const blobUrl = (id) => "/_blob/" + id;', 'const blobUrl = (id) => (window.__blobUrl ? window.__blobUrl(id) : "");')
rep('const BOT_TRIGGER = "trig_017CnZF6ZJ3L4ySxHKwk3csr"', 'const BOT_TRIGGER = ""')

# --- nur der Werkstattplaner: Startseite, Bot, Jarvis, Garantie raus ---
rep('<div class="app home" id="appRoot">', '<div class="app" id="appRoot">')
rep("  function showApp(name) {\n",
    '  function showApp(name) {\n    if (name !== "ws" && name !== "kk") name = "ws";\n')
rep('if (!sample) $("offline").hidden = false;', "")
for go in ("ideen", "ana", "ga"):
    rx(r'\s*<button class="mrow" data-go="%s">.*?</button>' % go, "")
# "Zur App-Zentrale" -> Kalkulator
rx(r'(<button class="mrow" data-go="home">.*?<b>)Zur App-Zentrale(</b><small>)Alle Apps(</small>)',
   r"\1Kalkulator\2Preis für eine Reparatur ausrechnen\3")
rep('else if (g === "home") showApp("home");', 'else if (g === "home") showApp("kk");')
# Zurück-Knöpfe
rep('<button class="backhome" id="toHome" aria-label="Zurück zur App-Auswahl">‹ Apps</button>', "")
rep('<button class="backhome" id="kHome" aria-label="Zurück zur App-Auswahl">‹ Apps</button>',
    '<button class="backhome" id="kHome" aria-label="Zurück zum Werkstattplaner">‹ Zurück</button>')
rep('$("toHome").onclick = () => showApp("home");', "")
rep('$("toHome").addEventListener("click", homeStat); ', "")
rep('$("kHome").onclick = () => showApp("home");', '$("kHome").onclick = () => showApp("ws");')

# --- KI-Funktionen ausblenden ---
rep('<details class="glass card sec" id="plAi">', '<details class="glass card sec" id="plAi" hidden>')
rep("    const SECS = [S2, ST, S9, S4, S3, S1, Sw, Sh, S5, SK, S8, S7];",
    "    const SECS = [S2, S4, S3, S1, Sw, Sh, S5, SK, S8, S7];")

# Kunden informieren: Vorlage statt KI
rep('''      if (!sample) { ms.className = "status err"; ms.textContent = "Das geht nur, wenn die App angemeldet in claude.ai offen ist."; return; }
      mb.disabled = true; mc.hidden = true; mo.textContent = ""; ms.className = "status"; ms.textContent = "Ich schreibe …";''',
    '''      if (!sample) { mo.textContent = msgTemplate(j, getAnlass().dataset.v, /Duze/.test(getAnrede().dataset.v)); ms.textContent = ""; mc.hidden = false; drawWa(); return; }
      mb.disabled = true; mc.hidden = true; mo.textContent = ""; ms.className = "status"; ms.textContent = "Ich schreibe …";''')
rep('const mb = el("button", "btn", "Nachricht an Kunden schreiben");', 'const mb = el("button", "btn", "Nachricht vorschlagen");')
TEMPLATE = r'''
  // Nachricht an den Kunden aus einer Vorlage (ohne KI)
  function msgTemplate(j, anlass, du) {
    const name = String(j.kunde || "").trim();
    const hallo = du ? `Hallo ${name.split(/\s+/)[0] || ""}`.trim() + "," : name ? `Guten Tag ${name},` : "Guten Tag,";
    const dein = du ? "dein" : "Ihr", deinem = du ? "deinem" : "Ihrem", dir = du ? "dir" : "Ihnen", du_ = du ? "du" : "Sie";
    const auto = j.auto ? `${dein} ${j.auto}` : `${dein} Auto`;
    const done = (j.arbeiten || []).filter((t) => t.done).map((t) => t.text);
    const offen = (j.arbeiten || []).filter((t) => !t.done).map((t) => t.text);
    const betrag = openSum(j);
    const gruss = "\n\nViele Grüße" + (firma && firma.name ? "\n" + firma.name : "");
    if (anlass === "fertig") {
      return `${hallo}\n\n${auto} ist fertig und kann abgeholt werden.` +
        (done.length ? ` Erledigt: ${done.join(", ")}.` : "") +
        (betrag > 0 ? ` Bei Abholung ${du ? "sind" : "sind"} noch ${eur(betrag)} zu zahlen.` : "") +
        `\n\nWann passt es ${dir}, vorbeizukommen?` + gruss;
    }
    if (anlass === "zahlung") {
      return `${hallo}\n\nkurze freundliche Erinnerung: Für die Reparatur an ${deinem} ${j.auto || "Auto"} ist noch ein Betrag von ${eur(betrag)} offen.` +
        ` ${du ? "Kannst du" : "Können Sie"} den Betrag in den nächsten Tagen überweisen oder ${du ? "dich" : "sich"} kurz bei mir melden?` +
        (firma && firma.iban ? `\n\nIBAN: ${firma.iban}` : "") + `\n\nDanke ${du ? "dir" : "Ihnen"}!` + gruss;
    }
    return `${hallo}\n\nkurzer Stand zu ${deinem} ${j.auto || "Auto"}:` +
      (done.length ? `\nErledigt: ${done.join(", ")}.` : "") +
      (offen.length ? `\nNoch offen: ${offen.join(", ")}.` : "") +
      (j.fertigBis ? `\nVoraussichtlich fertig am ${fmtDate(j.fertigBis)}.` : "") +
      `\n\nBei Fragen ${du ? "melde dich" : "melden Sie sich"} gern.` + gruss;
  }
'''
rep("  async function initWerkstatt() {", TEMPLATE + "  async function initWerkstatt() {")

# --- Tab-Leiste in der App wieder unten (dort gibt es keine Claude-Leiste) ---
if not WEB: rep('''.app > header { order: 0; } .app > .dock { order: 1; } .app > main { order: 2; }
.app > .dock, body.light .app > .dock { padding-bottom: 0; border-top: 0; border-bottom: 1px solid #2a2c31; }
.app > main > .wrap { padding-bottom: 120px; }''', '''.app > main > .wrap { padding-bottom: 24px; }''')
# Wischsperre gegen die Claude-Leiste wird hier nicht gebraucht
if not WEB: rep("    document.addEventListener(\"touchmove\", (e) => {", "    if (window.__STANDALONE) return;\n    document.addEventListener(\"touchmove\", (e) => {")

# --- Mehr: Datensicherung + Datenschutz ---
BACKUP = '''
        <div class="glass card" id="wpBackup">
          <h3>Datensicherung</h3>
          <p class="hint">Deine Daten liegen nur auf diesem iPhone. Speichere regelmäßig eine Sicherung (z. B. in iCloud Drive oder per Mail an dich). So kannst du alles auf ein neues Handy übertragen.</p>
          <div class="row"><button class="btn" id="wpExport">Sicherung speichern</button><label class="btn ghost" for="wpImport">Sicherung laden</label><input type="file" id="wpImport" accept=".json,application/json" hidden></div>
          <div class="status" id="wpBStat"></div>
        </div>
        <details class="glass card sec" id="wpPrivacy">
          <summary><span class="st">Datenschutz</span><span class="ss">Was mit deinen Daten passiert</span></summary>
          <div class="sb"><p class="hint">Alle Aufträge, Kunden, Fotos und Rechnungen werden ausschließlich auf diesem Gerät gespeichert. Die App sendet keine Daten an uns oder an Dritte, es gibt kein Konto, keine Werbung und keine Analyse-Tools. Nachrichten per WhatsApp oder Mail verschickst du selbst über die jeweilige App. Wenn du die App löschst, sind auch die Daten weg – denk an die Sicherung.</p></div>
        </details>
      </section>
      <!-- Ideen vom Bot -->'''
rep("""      </section>
      <!-- Ideen vom Bot -->""", BACKUP)
BACKUP_JS = '''
  // Datensicherung (eigenständige App)
  if ($("wpExport")) {
    const bs = $("wpBStat");
    $("wpExport").onclick = async () => { bs.className = "status"; bs.textContent = "Sicherung wird erstellt …"; try { await window.__backupExport(); bs.textContent = "Sicherung erstellt."; } catch (e) { bs.className = "status err"; bs.textContent = e && e.name === "AbortError" ? "" : "Das hat nicht geklappt: " + (e && e.message || e); } };
    $("wpImport").onchange = async (e) => { const f = e.target.files && e.target.files[0]; if (!f) return; if (!confirm("Sicherung laden? Gleichnamige Daten auf diesem iPhone werden ersetzt.")) return; try { await window.__backupImport(f); } catch (err) { bs.className = "status err"; bs.textContent = err.message || String(err); } };
  }
  showApp("ws");
'''
rep("  initWerkstatt();\n", "  initWerkstatt();\n" + BACKUP_JS)

# --- iPhone: Platz für Uhrzeit/Notch oben, "Bereit"-Anzeige weg ---
# (Hinweistext ist in der Quelle schon angepasst)
rep("</body></html>", """<style>
.app > header, #kApp > header { padding-top: env(safe-area-inset-top, 0px); }
#pulse { display: none !important; }
.app > .dock { padding-bottom: env(safe-area-inset-bottom, 0px); }
body { -webkit-user-select: none; user-select: none; -webkit-touch-callout: none; }
input, textarea, [contenteditable="true"], .rtxt, .jct, .hint { -webkit-user-select: text; user-select: text; }
</style>
</body></html>""")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(s, encoding="utf-8")
print("ok", OUT, len(s))
