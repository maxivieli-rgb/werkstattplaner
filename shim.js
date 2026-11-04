/* Werkstattplaner – eigenständige App (ohne claude.ai).
   Ersetzt window.claude durch lokale Speicher auf dem Gerät:
   - db:        Dokumente in localStorage (pro Sammlung ein Eintrag)
   - assets:    Fotos in IndexedDB
   - downloads: PDF/Kalender über das Teilen-Menü des iPhones
   KI-Funktionen (sample, mcp) gibt es hier nicht. */
(function () {
  "use strict";
  window.__STANDALONE = true;
  const NS = "wp:";
  const clone = (x) => (x === undefined ? undefined : JSON.parse(JSON.stringify(x)));
  const load = (c) => { try { return JSON.parse(localStorage.getItem(NS + c) || "{}") || {}; } catch { return {}; } };
  const persist = (c, o) => {
    try { localStorage.setItem(NS + c, JSON.stringify(o)); }
    catch (e) { alert("Der Speicher ist voll. Bitte unter Mehr → Datensicherung eine Sicherung speichern und alte Aufträge löschen."); throw e; }
  };
  const subs = {};
  const rid = () => Date.now().toString(36) + Math.random().toString(36).slice(2, 10);
  const docSnap = (id, o) => ({ id, exists: id in o, data: () => (id in o ? clone(o[id]) : undefined) });
  function emit(c, s) {
    const o = load(c);
    if (s.id == null) {
      const docs = Object.keys(o).map((id) => docSnap(id, o));
      s.cb({ docs, size: docs.length, empty: !docs.length, forEach: (f) => docs.forEach(f) });
    } else s.cb(docSnap(s.id, o));
  }
  const notify = (c) => (subs[c] || []).forEach((s) => setTimeout(() => emit(c, s), 0));
  const listen = (c, id, cb) => {
    const s = { id, cb }; (subs[c] = subs[c] || []).push(s);
    setTimeout(() => emit(c, s), 0);
    return () => { subs[c] = (subs[c] || []).filter((x) => x !== s); };
  };
  const db = {
    collection(c) {
      return {
        id: c,
        doc(id) {
          id = id || rid();
          return {
            id,
            async set(d, opt) { const o = load(c); o[id] = opt && opt.merge ? { ...(o[id] || {}), ...clone(d) } : clone(d); persist(c, o); notify(c); },
            async update(d) { const o = load(c); o[id] = { ...(o[id] || {}), ...clone(d) }; persist(c, o); notify(c); },
            async delete() { const o = load(c); delete o[id]; persist(c, o); notify(c); },
            async get() { return docSnap(id, load(c)); },
            onSnapshot(cb) { return listen(c, id, cb); },
          };
        },
        async get() { const o = load(c); const docs = Object.keys(o).map((id) => docSnap(id, o)); return { docs, size: docs.length, empty: !docs.length, forEach: (f) => docs.forEach(f) }; },
        onSnapshot(cb) { return listen(c, null, cb); },
      };
    },
    doc(path) { const [c, id] = String(path).split("/"); return db.collection(c).doc(id); },
  };

  // ---- Fotos in IndexedDB ----
  const urls = {};
  let idb = null;
  const openIdb = () => new Promise((res) => {
    try {
      const r = indexedDB.open("wp-assets", 1);
      r.onupgradeneeded = () => r.result.createObjectStore("files");
      r.onsuccess = () => res(r.result);
      r.onerror = () => res(null);
    } catch { res(null); }
  });
  const tx = (mode, fn) => new Promise((res, rej) => {
    if (!idb) return rej(new Error("Fotospeicher nicht verfügbar"));
    const t = idb.transaction("files", mode), st = t.objectStore("files");
    const out = fn(st);
    t.oncomplete = () => res(out && out.result !== undefined ? out.result : out);
    t.onerror = () => rej(t.error);
  });
  const ready = (async () => {
    idb = await openIdb();
    if (!idb) return;
    await new Promise((res) => {
      const t = idb.transaction("files", "readonly"), st = t.objectStore("files");
      const cur = st.openCursor();
      cur.onsuccess = () => { const c = cur.result; if (!c) return; urls[c.key] = URL.createObjectURL(c.value); c.continue(); };
      t.oncomplete = res; t.onerror = res;
    });
  })();
  window.__blobUrl = (id) => urls[id] || "";
  const assets = {
    async upload(blob) {
      const id = rid() + rid();
      await tx("readwrite", (st) => st.put(blob, id));
      urls[id] = URL.createObjectURL(blob);
      return { id, url: urls[id], sizeBytes: blob.size, contentType: blob.type };
    },
    async delete(id) { await tx("readwrite", (st) => st.delete(id)); if (urls[id]) URL.revokeObjectURL(urls[id]); delete urls[id]; },
    async list() { return { assets: Object.keys(urls).map((id) => ({ id, url: urls[id] })), usage: {} }; },
  };

  // ---- Dateien weitergeben (PDF, Kalender, Sicherung) ----
  const toBase64 = (blob) => new Promise((res, rej) => { const r = new FileReader(); r.onload = () => res(String(r.result).split(",")[1]); r.onerror = rej; r.readAsDataURL(blob); });
  const native = () => !!(window.Capacitor && window.Capacitor.isNativePlatform && window.Capacitor.isNativePlatform());
  const plug = (n) => (window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins[n]) || null;
  async function saveFile({ filename, data }) {
    const type = /\.pdf$/i.test(filename) ? "application/pdf" : /\.ics$/i.test(filename) ? "text/calendar" : /\.json$/i.test(filename) ? "application/json" : "application/octet-stream";
    const blob = data instanceof Blob ? data : new Blob([data], { type });
    // in der claude.ai-Ansicht: über die Download-Funktion der Plattform
    try {
      const real = window.claude && typeof window.claude.use === "function" ? await window.claude.use("downloads") : null;
      if (real) { await real.save({ filename, data: blob }); return; }
    } catch (e) { if (e && e.code && e.code !== "not_granted") throw e; }
    const FS = plug("Filesystem"), SH = plug("Share");
    if (native() && FS && SH) {
      const w = await FS.writeFile({ path: filename, data: await toBase64(blob), directory: "CACHE" });
      await SH.share({ title: filename, files: [w.uri] });
      return;
    }
    const file = new File([blob], filename, { type });
    if (navigator.canShare && navigator.canShare({ files: [file] })) { await navigator.share({ files: [file], title: filename }); return; }
    const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = filename; document.body.append(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 60000);
  }
  const downloads = { save: saveFile };

  // ---- Datensicherung ----
  window.__backupExport = async () => {
    await ready;
    const data = {};
    for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i); if (k && (k.startsWith(NS) || k.startsWith("tb-") || k.startsWith("kk-") || k.startsWith("jv-"))) data[k] = localStorage.getItem(k); }
    const files = {};
    for (const id of Object.keys(urls)) { try { const b = await tx("readonly", (st) => st.get(id)); if (b) files[id] = { type: b.type, b64: await toBase64(b) }; } catch {} }
    const d = new Date(), p = (n) => String(n).padStart(2, "0");
    await saveFile({ filename: `Werkstattplaner-Sicherung-${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}.json`, data: JSON.stringify({ app: "werkstattplaner", v: 1, data, files }) });
  };
  window.__backupImport = async (file) => {
    const j = JSON.parse(await file.text());
    if (!j || j.app !== "werkstattplaner" || !j.data) throw new Error("Das ist keine Sicherung vom Werkstattplaner.");
    await ready;
    Object.keys(j.data).forEach((k) => localStorage.setItem(k, j.data[k]));
    for (const id of Object.keys(j.files || {})) {
      const f = j.files[id], bin = atob(f.b64), u = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
      await tx("readwrite", (st) => st.put(new Blob([u], { type: f.type }), id));
    }
    location.reload();
  };

  window.__wp = {
    async use(name) {
      if (name === "db") { await ready; return db; }
      if (name === "assets") { await ready; return idb ? assets : null; }
      if (name === "downloads") return downloads;
      return null;
    },
  };
})();
