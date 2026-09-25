/**
 * Form Pesanan Custom — Undercover (Google Apps Script, terikat ke Google Sheet).
 *
 * Admin membuka link web app -> isi Merek, Model, Generasi/Tahun -> Simpan.
 *  - Setiap simpan = 1 baris baru di sheet "Rekap Pesanan" (waktu dicatat otomatis).
 *  - Kalau kombinasi Merek/Model/Generasi belum ada di "Daftar Mobil" (diketik manual),
 *    kombinasi itu otomatis ditambahkan ke "Daftar Mobil" (Sumber = Manual),
 *    jadi pesanan berikutnya sudah muncul di dropdown.
 *  - Sheet "Ringkasan" = jumlah pesanan per model & per generasi (rumus QUERY).
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
 * Simpan 1 pesanan. input = {merek, model, gen}.
 * Ejaan disamakan ke yg sudah ada di Daftar Mobil (tidak peka huruf besar/kecil & spasi),
 * supaya "toyota avanza" tidak jadi model baru dobel.
 */
function simpan(input) {
  let merek = rapikan_(input && input.merek);
  let model = rapikan_(input && input.model);
  let gen = rapikan_(input && input.gen);
  if (!merek || !model || !gen) throw new Error('Merek, Model, dan Generasi / Tahun wajib diisi.');

  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    const ss = ss_();
    const daftar = ss.getSheetByName(SHEET_DAFTAR);
    const rekap = ss.getSheetByName(SHEET_REKAP);
    const rows = barisDaftar_(daftar);

    const rMerek = rows.find(function (r) { return kunci_(r[0]) === kunci_(merek); });
    if (rMerek) merek = rapikan_(rMerek[0]);
    const rModel = rows.find(function (r) {
      return kunci_(r[0]) === kunci_(merek) && kunci_(r[1]) === kunci_(model);
    });
    if (rModel) model = rapikan_(rModel[1]);
    const rGen = rows.find(function (r) {
      return kunci_(r[0]) === kunci_(merek) && kunci_(r[1]) === kunci_(model) &&
        kunci_(r[2]) === kunci_(gen);
    });
    if (rGen) gen = rapikan_(rGen[2]);
    const baru = !rGen;
    const waktu = new Date();

    if (baru) {
      const rd = daftar.getLastRow() + 1;
      daftar.getRange(rd, 1, 1, 4).setNumberFormat('@');
      daftar.getRange(rd, 1, 1, 5).setValues([[teks_(merek), teks_(model), teks_(gen), 'Manual', waktu]]);
    }
    const rr = rekap.getLastRow() + 1;
    rekap.getRange(rr, 2, 1, 4).setNumberFormat('@');
    rekap.getRange(rr, 1, 1, 5).setValues([[waktu, teks_(merek), teks_(model), teks_(gen), baru ? 'Ya' : '']]);
    SpreadsheetApp.flush();
    return { merek: merek, model: model, gen: gen, baru: baru };
  } finally {
    lock.releaseLock();
  }
}
