/**
 * Form Pesanan Custom — Undercover (Google Apps Script, terikat ke Google Sheet).
 *
 * Admin membuka link web app -> isi Merek, Model, Generasi/Tahun -> Simpan.
 *  - Setiap simpan = 1 baris baru di sheet "Rekap Pesanan" (waktu dicatat otomatis).
 *  - Kalau kombinasi Merek/Model/Generasi belum ada di "Daftar Mobil" (diketik manual),
 *    kombinasi itu otomatis ditambahkan ke "Daftar Mobil" (Sumber = Manual),
 *    jadi pesanan berikutnya sudah muncul di dropdown.
 *  - Sheet "Ringkasan" = jumlah pesanan per model & per generasi (rumus QUERY).
 *  - Di sheet "Rekap Pesanan", kolom Merek/Model/Generasi punya dropdown bertingkat
 *    (dipasang oleh simpan() & onEdit) untuk revisi langsung di sheet.
 *
 * Setup sekali: jalankan fungsi `siapkan` dari editor Apps Script, lalu Deploy sebagai Web app.
 * Panduan lengkap: PANDUAN-SETUP.md
 */

const SHEET_DAFTAR = 'Daftar Mobil';
const SHEET_REKAP = 'Rekap Pesanan';
const SHEET_RINGKASAN = 'Ringkasan';
const HEADER_DAFTAR = ['Merek', 'Model', 'Generasi / Tahun', 'Sumber', 'Ditambahkan'];
const HEADER_REKAP = ['Waktu', 'Merek', 'Model', 'Generasi / Tahun', 'Model Baru?'];
const MAKS_PANJANG = 80;

function doGet() {
  return HtmlService.createHtmlOutputFromFile('Index')
    .setTitle('Catat Pesanan Custom — Undercover')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

/** Jalankan SEKALI dari editor Apps Script (pilih fungsi "siapkan" -> Run). */
function siapkan() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  PropertiesService.getScriptProperties().setProperty('SPREADSHEET_ID', ss.getId());

  const daftar = ss.getSheetByName(SHEET_DAFTAR) || ss.insertSheet(SHEET_DAFTAR);
  if (daftar.getLastRow() === 0) daftar.appendRow(HEADER_DAFTAR);
  daftar.getRange('A:D').setNumberFormat('@');

  const rekap = ss.getSheetByName(SHEET_REKAP) || ss.insertSheet(SHEET_REKAP);
  if (rekap.getLastRow() === 0) rekap.appendRow(HEADER_REKAP);
  rekap.getRange('A:A').setNumberFormat('dd/mm/yyyy hh:mm');
  rekap.getRange('B:E').setNumberFormat('@');
  rekap.setFrozenRows(1);

  const ringkas = ss.getSheetByName(SHEET_RINGKASAN) || ss.insertSheet(SHEET_RINGKASAN);
  ringkas.clear();
  ringkas.getRange('A1').setFormula(
    "=QUERY('" + SHEET_REKAP + "'!B:D,\"select B, C, count(D) where B is not null " +
    "group by B, C order by count(D) desc label count(D) 'Jumlah Pesanan'\",1)");
  ringkas.getRange('E1').setFormula(
    "=QUERY('" + SHEET_REKAP + "'!B:D,\"select B, C, D, count(B) where B is not null " +
    "group by B, C, D order by count(B) desc label count(B) 'Jumlah Pesanan'\",1)");
  ringkas.setFrozenRows(1);
  pasangDropdownSemua();
  return 'Siap. Daftar Mobil: ' + (daftar.getLastRow() - 1) + ' baris.';
}

function ss_() {
  const id = PropertiesService.getScriptProperties().getProperty('SPREADSHEET_ID');
  return id ? SpreadsheetApp.openById(id) : SpreadsheetApp.getActiveSpreadsheet();
}

function rapikan_(s) {
  return String(s == null ? '' : s).replace(/\s+/g, ' ').trim().slice(0, MAKS_PANJANG);
}

function kunci_(s) {
  return rapikan_(s).toLowerCase();
}

/** Teks yg diawali = + - @ bisa dibaca Sheets sbg rumus -> paksa jadi teks biasa. */
function teks_(s) {
  return /^[=+\-@]/.test(s) ? "'" + s : s;
}

function barisDaftar_(sheet) {
  const n = sheet.getLastRow() - 1;
  return n > 0 ? sheet.getRange(2, 1, n, 3).getDisplayValues() : [];
}

/**
 * Dipanggil halaman form saat dibuka.
 * Return array (bukan object) supaya model bernama angka ("5", "206") tidak berubah urutan:
 *   [[merek, [[model, [generasi, ...]], ...]], ...]
 */
function ambilDaftar() {
  const rows = barisDaftar_(ss_().getSheetByName(SHEET_DAFTAR));
  const peta = new Map();
  rows.forEach(function (r) {
    const merek = rapikan_(r[0]), model = rapikan_(r[1]), gen = rapikan_(r[2]);
    if (!merek || !model) return;
    if (!peta.has(merek)) peta.set(merek, new Map());
    const mm = peta.get(merek);
    if (!mm.has(model)) mm.set(model, []);
    if (gen && mm.get(model).indexOf(gen) === -1) mm.get(model).push(gen);
  });
  return Array.from(peta, function (e) { return [e[0], Array.from(e[1])]; });
}

/**
 * Katalog dari "Daftar Mobil": ejaan resmi + daftar pilihan dropdown.
 * Semua pencocokan tidak peka huruf besar/kecil & spasi ganda.
 */
function katalog_(daftar) {
  const rows = barisDaftar_(daftar);
  const merekResmi = new Map(), modelResmi = new Map(), genResmi = new Map();
  const models = new Map(), gens = new Map();
  rows.forEach(function (r) {
    const me = rapikan_(r[0]), mo = rapikan_(r[1]), ge = rapikan_(r[2]);
    if (!me) return;
    const km = kunci_(me);
    if (!merekResmi.has(km)) { merekResmi.set(km, me); models.set(km, []); }
    if (!mo) return;
    const kmo = km + '|' + kunci_(mo);
    if (!modelResmi.has(kmo)) { modelResmi.set(kmo, mo); models.get(km).push(mo); gens.set(kmo, []); }
    if (!ge) return;
    const kg = kmo + '|' + kunci_(ge);
    if (!genResmi.has(kg)) { genResmi.set(kg, ge); gens.get(kmo).push(ge); }
  });
  const urut = function (a, b) { return a.localeCompare(b, 'id', { numeric: true, sensitivity: 'base' }); };
  return {
    merek: function (me) { return merekResmi.get(kunci_(me)) || rapikan_(me); },
    model: function (me, mo) { return modelResmi.get(kunci_(me) + '|' + kunci_(mo)) || rapikan_(mo); },
    gen: function (me, mo, ge) {
      return genResmi.get(kunci_(me) + '|' + kunci_(mo) + '|' + kunci_(ge)) || rapikan_(ge);
    },
    adaModel: function (me, mo) { return modelResmi.has(kunci_(me) + '|' + kunci_(mo)); },
    adaGen: function (me, mo, ge) { return genResmi.has(kunci_(me) + '|' + kunci_(mo) + '|' + kunci_(ge)); },
    daftarMerek: function () { return Array.from(merekResmi.values()).sort(urut); },
    daftarModel: function (me) { return (models.get(kunci_(me)) || []).slice().sort(urut); },
    daftarGen: function (me, mo) { return (gens.get(kunci_(me) + '|' + kunci_(mo)) || []).slice(); }
  };
}

function tambahKeDaftar_(daftar, merek, model, gen, sumber) {
  const rd = daftar.getLastRow() + 1;
  daftar.getRange(rd, 1, 1, 4).setNumberFormat('@');
  daftar.getRange(rd, 1, 1, 5).setValues([[teks_(merek), teks_(model), teks_(gen), sumber, new Date()]]);
}

/**
 * Simpan 1 pesanan. input = {merek, model, gen}.
 * Ejaan disamakan ke yg sudah ada di Daftar Mobil (tidak peka huruf besar/kecil & spasi),
 * supaya "toyota avanza" tidak jadi model baru dobel.
 */
function simpan(input) {
  if (!rapikan_(input && input.merek) || !rapikan_(input && input.model) || !rapikan_(input && input.gen)) {
    throw new Error('Merek, Model, dan Generasi / Tahun wajib diisi.');
  }
  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    const ss = ss_();
    const daftar = ss.getSheetByName(SHEET_DAFTAR);
    const rekap = ss.getSheetByName(SHEET_REKAP);
    const k = katalog_(daftar);
    const merek = k.merek(input.merek);
    const model = k.model(merek, input.model);
    const gen = k.gen(merek, model, input.gen);
    const baru = !k.adaGen(merek, model, gen);
    const waktu = new Date();

    if (baru) tambahKeDaftar_(daftar, merek, model, gen, 'Manual');
    const rr = rekap.getLastRow() + 1;
    rekap.getRange(rr, 2, 1, 4).setNumberFormat('@');
    rekap.getRange(rr, 1, 1, 5).setValues([[waktu, teks_(merek), teks_(model), teks_(gen), baru ? 'Ya' : '']]);
    pasangDropdown_(rekap, rr, 1, baru ? katalog_(daftar) : k);
    SpreadsheetApp.flush();
    return { merek: merek, model: model, gen: gen, baru: baru };
  } finally {
    lock.releaseLock();
  }
}

/* ===================== Dropdown di sheet "Rekap Pesanan" ===================== */

function aturan_(pilihan) {
  if (!pilihan.length) return null;
  // setAllowInvalid(true): nilai di luar daftar tetap boleh (tanda peringatan kecil),
  // supaya admin tetap bisa mengetik mobil baru langsung di sheet.
  return SpreadsheetApp.newDataValidation().requireValueInList(pilihan, true)
    .setAllowInvalid(true).build();
}

/** Pasang dropdown Merek/Model/Generasi untuk baris `mulai` s/d `mulai+jumlah-1`. */
function pasangDropdown_(rekap, mulai, jumlah, k) {
  if (jumlah < 1) return;
  const nilai = rekap.getRange(mulai, 2, jumlah, 3).getDisplayValues();
  const aturMerek = aturan_(k.daftarMerek());
  const dv = nilai.map(function (v) {
    return [aturMerek, v[0] ? aturan_(k.daftarModel(v[0])) : null,
      v[0] && v[1] ? aturan_(k.daftarGen(v[0], v[1])) : null];
  });
  rekap.getRange(mulai, 2, jumlah, 3).setDataValidations(dv);
}

/** Menu: pasang ulang dropdown di semua baris Rekap (mis. setelah Daftar Mobil diedit). */
function pasangDropdownSemua() {
  const ss = ss_();
  const rekap = ss.getSheetByName(SHEET_REKAP);
  const n = rekap.getLastRow() - 1;
  pasangDropdown_(rekap, 2, n, katalog_(ss.getSheetByName(SHEET_DAFTAR)));
  return n;
}

function onOpen() {
  SpreadsheetApp.getUi().createMenu('Form Pesanan')
    .addItem('Pasang ulang dropdown di Rekap Pesanan', 'pasangDropdownSemua')
    .addToUi();
}

/**
 * Edit langsung di sheet "Rekap Pesanan" (simple trigger, jalan otomatis):
 *  - ejaan Merek/Model/Generasi disamakan ke Daftar Mobil (rekap/Ringkasan tidak terpecah),
 *  - Merek diganti & Model lama bukan milik merek baru -> Model & Generasi dikosongkan,
 *    Model diganti & Generasi lama bukan milik model baru -> Generasi dikosongkan
 *    (kecuali kolom itu ikut diedit/di-paste bersamaan),
 *  - dropdown Model & Generasi baris itu disesuaikan,
 *  - kombinasi lengkap yg belum ada di Daftar Mobil -> ditambahkan (Sumber "Manual (edit sheet)").
 * Waktu pesanan TIDAK diubah.
 */
function onEdit(e) {
  if (!e || !e.range) return;
  const rekap = e.range.getSheet();
  if (rekap.getName() !== SHEET_REKAP) return;
  const r0 = Math.max(e.range.getRow(), 2), r1 = e.range.getLastRow();
  const c0 = e.range.getColumn(), c1 = e.range.getLastColumn();
  if (r1 < r0 || c1 < 2 || c0 > 4) return;
  const diedit = function (kol) { return kol >= c0 && kol <= c1; };

  const daftar = rekap.getParent().getSheetByName(SHEET_DAFTAR);
  let k = katalog_(daftar);
  const n = r1 - r0 + 1;
  const lama = rekap.getRange(r0, 2, n, 4).getDisplayValues();
  const hasil = lama.map(function (v) {
    let me = rapikan_(v[0]), mo = rapikan_(v[1]), ge = rapikan_(v[2]), tanda = v[3];
    if (!me && !mo && !ge) return ['', '', '', tanda];
    if (me) me = k.merek(me);
    if (diedit(2) && !diedit(3) && mo && !k.adaModel(me, mo) && k.daftarModel(me).length) { mo = ''; ge = ''; }
    if (mo) mo = k.model(me, mo);
    if ((diedit(2) || diedit(3)) && !diedit(4) && ge && !k.adaGen(me, mo, ge)) ge = '';
    if (ge) ge = k.gen(me, mo, ge);
    if (me && mo && ge && !k.adaGen(me, mo, ge)) {
      tambahKeDaftar_(daftar, me, mo, ge, 'Manual (edit sheet)');
      k = katalog_(daftar);
      tanda = 'Ya';
    }
    return [teks_(me), teks_(mo), teks_(ge), tanda];
  });
  const berubah = hasil.some(function (v, i) {
    return v.some(function (x, j) { return String(x).replace(/^'/, '') !== lama[i][j]; });
  });
  if (berubah) {
    rekap.getRange(r0, 2, n, 3).setNumberFormat('@');
    rekap.getRange(r0, 2, n, 4).setValues(hasil);
  }
  pasangDropdown_(rekap, r0, n, k);
}
