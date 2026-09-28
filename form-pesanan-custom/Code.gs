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
 *  - Ukuran cover (Subcompact/Compact/Midsize/Large/Jumbo) terisi otomatis dari sheet
 *    "Ukuran Mobil"; harga per tipe dari sheet "Matriks Harga" (keduanya bisa diedit).
 *
 * Setup sekali: jalankan fungsi `siapkan` dari editor Apps Script, lalu Deploy sebagai Web app.
 * Panduan lengkap: PANDUAN-SETUP.md
 */

const SHEET_DAFTAR = 'Daftar Mobil';
const SHEET_REKAP = 'Rekap Pesanan';
const SHEET_RINGKASAN = 'Ringkasan';
const HEADER_DAFTAR = ['Merek', 'Model', 'Generasi / Tahun', 'Sumber', 'Ditambahkan'];
const HEADER_REKAP = ['Waktu', 'Merek', 'Model', 'Generasi / Tahun', 'Model Baru?', 'Ukuran'];
const SHEET_UKURAN = 'Ukuran Mobil';
const SHEET_MATRIKS = 'Matriks Harga';
const HEADER_UKURAN = ['Merek', 'Model', 'Ukuran', 'Sumber'];
const HEADER_MATRIKS = ['Ukuran', 'Pcs/Roll', 'Reguler', 'Strip', 'Premium', 'Exclusive', 'Contoh Mobil'];
// Harga link custom UA per ukuran (file "Judul Deskripsi Harga Custom UA.txt", 2026-09-25).
// Reguler = lantai tier Pcs/Roll + Rp5.000; Strip = Reguler + 43rb; Premium = Reguler + 414rb;
// Exclusive = Premium + 400rb. Hanya dipakai saat sheet "Matriks Harga" belum ada — setelah itu
// harga diubah langsung di sheet.
const MATRIKS_AWAL = [
  ['Subcompact', 7, 301000, 344000, 715000, 1115000, 'Wuling Air EV, Wuling Mini EV'],
  ['Compact', 6, 337000, 380000, 751000, 1151000, 'Honda Brio, Honda Jazz, Suzuki Karimun, Suzuki Ignis, Toyota Yaris, Toyota Raize'],
  ['Midsize', 5, 387000, 430000, 801000, 1201000, 'Toyota Avanza, Daihatsu Xenia, Toyota Rush, Toyota Innova, Toyota Vios, Honda HR-V'],
  ['Large', 4, 462000, 505000, 876000, 1276000, 'Toyota Fortuner, Mitsubishi Pajero Sport, Toyota Alphard, Toyota Vellfire, Toyota Hilux'],
  ['Jumbo', 3, 583000, 626000, 997000, 1397000, 'Toyota HiAce']
];
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
  rekap.getRange('B:F').setNumberFormat('@');
  if (!rekap.getRange('F1').getDisplayValue()) rekap.getRange('F1').setValue('Ukuran');
  rekap.setFrozenRows(1);

  let matriks = ss.getSheetByName(SHEET_MATRIKS);
  if (!matriks) {
    matriks = ss.insertSheet(SHEET_MATRIKS);
    matriks.getRange(1, 1, 1, HEADER_MATRIKS.length).setValues([HEADER_MATRIKS]).setFontWeight('bold');
    matriks.getRange(2, 1, MATRIKS_AWAL.length, HEADER_MATRIKS.length).setValues(MATRIKS_AWAL);
    matriks.getRange('C:F').setNumberFormat('#,##0');
    matriks.setFrozenRows(1);
  }
  let ukuran = ss.getSheetByName(SHEET_UKURAN);
  if (!ukuran) {
    ukuran = ss.insertSheet(SHEET_UKURAN);
    ukuran.getRange('A:D').setNumberFormat('@');
    ukuran.getRange(1, 1, 1, HEADER_UKURAN.length).setValues([HEADER_UKURAN]).setFontWeight('bold');
    ukuran.getRange(2, 1, UKURAN_AWAL.length, 4).setValues(UKURAN_AWAL.map(function (r) {
      return [r[0], r[1], r[2], 'Pcs/Roll HPP'];
    }));
    ukuran.setFrozenRows(1);
  }

  const ringkas = ss.getSheetByName(SHEET_RINGKASAN) || ss.insertSheet(SHEET_RINGKASAN);
  ringkas.clear();
  ringkas.getRange('A1').setFormula(
    "=QUERY('" + SHEET_REKAP + "'!B:D,\"select B, C, count(D) where B is not null " +
    "group by B, C order by count(D) desc label count(D) 'Jumlah Pesanan'\",1)");
  ringkas.getRange('E1').setFormula(
    "=QUERY('" + SHEET_REKAP + "'!B:D,\"select B, C, D, count(B) where B is not null " +
    "group by B, C, D order by count(B) desc label count(B) 'Jumlah Pesanan'\",1)");
  ringkas.getRange('J1').setFormula(
    "=QUERY('" + SHEET_REKAP + "'!B:F,\"select F, count(B) where B is not null " +
    "group by F order by count(B) desc label F 'Ukuran', count(B) 'Jumlah Pesanan'\",1)");
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

/** Matriks harga dari sheet: [[ukuran, pcs, reguler, strip, premium, exclusive, contoh], ...] */
function matriks_(ss) {
  const sh = ss.getSheetByName(SHEET_MATRIKS);
  if (!sh || sh.getLastRow() < 2) return MATRIKS_AWAL;
  return sh.getRange(2, 1, sh.getLastRow() - 1, 7).getValues()
    .filter(function (r) { return rapikan_(r[0]); })
    .map(function (r) {
      return [rapikan_(r[0]), r[1], Number(r[2]) || 0, Number(r[3]) || 0, Number(r[4]) || 0,
        Number(r[5]) || 0, String(r[6] || '')];
    });
}

function daftarUkuran_(ss) {
  return matriks_(ss).map(function (r) { return r[0]; });
}

/** Ejaan resmi ukuran ("midsize" -> "Midsize"); '' kalau tidak dikenal. */
function ukuranResmi_(ss, u) {
  const k = kunci_(u);
  return daftarUkuran_(ss).find(function (x) { return kunci_(x) === k; }) || '';
}

/** Map "merek|model" (kunci) -> ukuran, dari sheet "Ukuran Mobil". */
function petaUkuran_(ss) {
  const sh = ss.getSheetByName(SHEET_UKURAN);
  const peta = new Map();
  if (!sh || sh.getLastRow() < 2) return peta;
  sh.getRange(2, 1, sh.getLastRow() - 1, 3).getDisplayValues().forEach(function (r) {
    if (r[0] && r[1] && r[2]) peta.set(kunci_(r[0]) + '|' + kunci_(r[1]), rapikan_(r[2]));
  });
  return peta;
}

/** Dipanggil form: matriks harga + ukuran per model. */
function ambilUkuran() {
  const ss = ss_();
  return {
    matriks: matriks_(ss),
    peta: Array.from(petaUkuran_(ss), function (e) { return [e[0], e[1]]; })
  };
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

function tambahUkuran_(ss, merek, model, ukuran, sumber) {
  const sh = ss.getSheetByName(SHEET_UKURAN);
  if (!sh) return;
  const r = sh.getLastRow() + 1;
  sh.getRange(r, 1, 1, 4).setNumberFormat('@')
    .setValues([[teks_(merek), teks_(model), ukuran, sumber]]);
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
  if (!rapikan_(input.ukuran)) throw new Error('Ukuran wajib dipilih.');
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
    const ukuran = ukuranResmi_(ss, input.ukuran);
    if (!ukuran) throw new Error('Ukuran "' + rapikan_(input.ukuran) + '" tidak ada di Matriks Harga.');
    const waktu = new Date();

    if (baru) tambahKeDaftar_(daftar, merek, model, gen, 'Manual');
    if (!petaUkuran_(ss).has(kunci_(merek) + '|' + kunci_(model))) {
      tambahUkuran_(ss, merek, model, ukuran, 'Manual');
    }
    const rr = rekap.getLastRow() + 1;
    rekap.getRange(rr, 2, 1, 5).setNumberFormat('@');
    rekap.getRange(rr, 1, 1, 6).setValues([[waktu, teks_(merek), teks_(model), teks_(gen), baru ? 'Ya' : '', ukuran]]);
    pasangDropdown_(rekap, rr, 1, baru ? katalog_(daftar) : k);
    SpreadsheetApp.flush();
    return { merek: merek, model: model, gen: gen, baru: baru, ukuran: ukuran };
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
  const aturUkuran = aturan_(daftarUkuran_(rekap.getParent()));
  rekap.getRange(mulai, 6, jumlah, 1).setDataValidations(nilai.map(function () { return [aturUkuran]; }));
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
  if (r1 < r0 || c1 < 2 || c0 > 6) return;
  const diedit = function (kol) { return kol >= c0 && kol <= c1; };

  const ss = rekap.getParent();
  const daftar = ss.getSheetByName(SHEET_DAFTAR);
  let k = katalog_(daftar);
  const peta = petaUkuran_(ss);
  const n = r1 - r0 + 1;
  const lama = rekap.getRange(r0, 2, n, 5).getDisplayValues();
  const hasil = lama.map(function (v) {
    let me = rapikan_(v[0]), mo = rapikan_(v[1]), ge = rapikan_(v[2]), tanda = v[3];
    let uk = v[4] ? (ukuranResmi_(ss, v[4]) || rapikan_(v[4])) : '';
    if (!me && !mo && !ge) return ['', '', '', tanda, uk];
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
    // Ukuran ikut model: diisi/diganti otomatis saat Merek/Model diedit (kecuali Ukuran ikut diedit)
    const ukPeta = peta.get(kunci_(me) + '|' + kunci_(mo));
    // Merek/Model diganti (Ukuran tidak ikut diedit) -> Ukuran ikut data model baru, atau
    // dikosongkan kalau model itu belum punya data (jangan warisi ukuran model sebelumnya).
    if ((diedit(2) || diedit(3)) && !diedit(6)) uk = ukPeta || '';
    else if (!uk && ukPeta) uk = ukPeta;
    if (me && mo && uk && !ukPeta && ukuranResmi_(ss, uk)) {
      tambahUkuran_(ss, me, mo, ukuranResmi_(ss, uk), 'Manual (edit sheet)');
      peta.set(kunci_(me) + '|' + kunci_(mo), uk);
    }
    return [teks_(me), teks_(mo), teks_(ge), tanda, uk];
  });
  const berubah = hasil.some(function (v, i) {
    return v.some(function (x, j) { return String(x).replace(/^'/, '') !== lama[i][j]; });
  });
  if (berubah) {
    rekap.getRange(r0, 2, n, 5).setNumberFormat('@');
    rekap.getRange(r0, 2, n, 5).setValues(hasil);
  }
  pasangDropdown_(rekap, r0, n, k);
}

/* ===================== Data awal ukuran (dipakai siapkan() sekali) =====================
 * Ukuran = tier Pcs/Roll di "DATA UC HPP Top 100 Terlaris.xlsx" (291 model, 29-08-2026):
 * 7 = Subcompact, 6 = Compact, 5 = Midsize, 4 = Large, 3 = Jumbo.
 * Dikonfirmasi user 2026-09-28: Honda Jazz = Compact, Suzuki Ignis = Compact, Daihatsu Sigra = Midsize.
 * Model lain belum punya ukuran -> admin pilih saat mencatat, lalu tersimpan otomatis.
 */
const UKURAN_AWAL = [
  ["Audi", "A3", "Midsize"],
  ["Audi", "A4", "Midsize"],
  ["Audi", "A6", "Midsize"],
  ["Audi", "A8", "Midsize"],
  ["Audi", "Q3", "Midsize"],
  ["Audi", "Q8", "Midsize"],
  ["BMW", "i4", "Midsize"],
  ["BMW", "i8", "Midsize"],
  ["BMW", "iX", "Midsize"],
  ["BMW", "M2", "Midsize"],
  ["BMW", "M3", "Midsize"],
  ["BMW", "Seri 2", "Midsize"],
  ["BMW", "Seri 3", "Midsize"],
  ["BMW", "Seri 4", "Midsize"],
  ["BMW", "Seri 5", "Midsize"],
  ["BMW", "Seri 7", "Midsize"],
  ["BMW", "Seri 8", "Midsize"],
  ["BMW", "X1", "Midsize"],
  ["BMW", "X3", "Midsize"],
  ["BMW", "X5", "Midsize"],
  ["BMW", "Z4", "Compact"],
  ["BYD", "Atto 1", "Compact"],
  ["BYD", "Atto 3", "Midsize"],
  ["BYD", "SEAL", "Midsize"],
  ["Chery", "Omoda 5", "Midsize"],
  ["Chery", "Tiggo 7 Pro", "Midsize"],
  ["Chery", "Tiggo 8", "Compact"],
  ["Chery", "Tiggo 8 Pro", "Midsize"],
  ["Chery", "Tiggo Cross", "Midsize"],
  ["Chevrolet", "Aveo", "Compact"],
  ["Chevrolet", "Captiva", "Midsize"],
  ["Chevrolet", "Cruze", "Midsize"],
  ["Chevrolet", "Optra Magnum", "Midsize"],
  ["Chevrolet", "Orlando", "Large"],
  ["Chevrolet", "Spark", "Compact"],
  ["Chevrolet", "Spin", "Midsize"],
  ["Chevrolet", "Trailblazer", "Large"],
  ["Chevrolet", "Trax", "Compact"],
  ["Chevrolet", "Trooper", "Midsize"],
  ["Citroen", "C3", "Midsize"],
  ["Daihatsu", "Ayla", "Compact"],
  ["Daihatsu", "Ceria", "Compact"],
  ["Daihatsu", "Espass", "Midsize"],
  ["Daihatsu", "Feroza", "Midsize"],
  ["Daihatsu", "Feroza Long", "Midsize"],
  ["Daihatsu", "Gran Max Minibus / Blind Van", "Large"],
  ["Daihatsu", "Gran Max Pick Up", "Midsize"],
  ["Daihatsu", "Hi Max", "Midsize"],
  ["Daihatsu", "Luxio", "Midsize"],
  ["Daihatsu", "Rocky", "Compact"],
  ["Daihatsu", "Sigra", "Midsize"],
  ["Daihatsu", "Sirion", "Compact"],
  ["Daihatsu", "Taft GT", "Midsize"],
  ["Daihatsu", "Taruna", "Compact"],
  ["Daihatsu", "Terios", "Midsize"],
  ["Daihatsu", "Xenia", "Midsize"],
  ["Datsun", "Cross", "Compact"],
  ["Datsun", "Go", "Compact"],
  ["Datsun", "Go Plus", "Compact"],
  ["DFSK", "Glory 560", "Midsize"],
  ["DFSK", "Glory 580", "Midsize"],
  ["DFSK", "Glory i-Auto", "Midsize"],
  ["DFSK", "Seres E1", "Compact"],
  ["Dodge", "Journey", "Midsize"],
  ["Ferrari", "812 Superfast", "Midsize"],
  ["Ferrari", "GTC4Lusso", "Midsize"],
  ["Ferrari", "SF90 Stradale", "Midsize"],
  ["Fiat", "500", "Compact"],
  ["Ford", "Ecosport", "Midsize"],
  ["Ford", "Escape", "Midsize"],
  ["Ford", "Everest", "Midsize"],
  ["Ford", "Fiesta", "Compact"],
  ["Ford", "Focus", "Midsize"],
  ["Ford", "Laser", "Midsize"],
  ["Ford", "Ranger", "Large"],
  ["GAC Aion", "Hyptec HT", "Midsize"],
  ["Geely", "EX2", "Compact"],
  ["Holden", "Holden", "Midsize"],
  ["Honda", "Accord", "Midsize"],
  ["Honda", "BR-V", "Midsize"],
  ["Honda", "Brio Satya / RS", "Compact"],
  ["Honda", "City Hatchback RS", "Compact"],
  ["Honda", "City Sedan", "Compact"],
  ["Honda", "Civic", "Midsize"],
  ["Honda", "Civic Hatchback", "Midsize"],
  ["Honda", "Civic Type R", "Midsize"],
  ["Honda", "CR-V", "Midsize"],
  ["Honda", "Freed", "Midsize"],
  ["Honda", "HR-V / e:N1", "Midsize"],
  ["Honda", "Jazz", "Compact"],
  ["Honda", "Mobilio", "Midsize"],
  ["Honda", "Odyssey", "Midsize"],
  ["Honda", "Stream", "Midsize"],
  ["Honda", "WR-V", "Compact"],
  ["Hummer", "H1", "Midsize"],
  ["Hyundai", "Accent", "Midsize"],
  ["Hyundai", "Atoz", "Compact"],
  ["Hyundai", "Avega", "Midsize"],
  ["Hyundai", "Avega Hatchback", "Compact"],
  ["Hyundai", "Creta", "Midsize"],
  ["Hyundai", "Elantra", "Midsize"],
  ["Hyundai", "Excel", "Midsize"],
  ["Hyundai", "Getz", "Compact"],
  ["Hyundai", "Grand i10", "Compact"],
  ["Hyundai", "Ioniq 5", "Midsize"],
  ["Hyundai", "Kona", "Compact"],
  ["Hyundai", "Palisade", "Large"],
  ["Hyundai", "Santa Fe", "Midsize"],
  ["Hyundai", "Sonata", "Midsize"],
  ["Hyundai", "Stargazer", "Midsize"],
  ["Hyundai", "Staria", "Large"],
  ["Hyundai", "Tucson", "Midsize"],
  ["Isuzu", "Mux", "Midsize"],
  ["Isuzu", "Panther", "Midsize"],
  ["Jeep", "Cherokee", "Midsize"],
  ["Jeep", "Compass", "Midsize"],
  ["Jeep", "Wrangler", "Large"],
  ["Jeep", "Wrangler Rubicon", "Large"],
  ["Kia", "Carens", "Midsize"],
  ["Kia", "Grand Carnival", "Midsize"],
  ["Kia", "Picanto", "Compact"],
  ["Kia", "Rio Hatchback", "Compact"],
  ["Kia", "Rio Sedan", "Midsize"],
  ["Kia", "Sedona", "Large"],
  ["Kia", "Seltos", "Midsize"],
  ["Kia", "Sonet", "Midsize"],
  ["Kia", "Sportage", "Midsize"],
  ["Lamborghini", "Aventador", "Midsize"],
  ["Lamborghini", "Huracan", "Midsize"],
  ["Land Rover", "Range Rover", "Large"],
  ["Lexus", "ES", "Midsize"],
  ["Lexus", "GS", "Midsize"],
  ["Lexus", "LM", "Large"],
  ["Lexus", "LS", "Midsize"],
  ["Lexus", "LX", "Midsize"],
  ["Lexus", "NX", "Midsize"],
  ["Lexus", "RX", "Midsize"],
  ["Maserati", "Quattroporte", "Midsize"],
  ["Mazda", "2 Hatchback", "Compact"],
  ["Mazda", "2 Sedan", "Midsize"],
  ["Mazda", "3", "Midsize"],
  ["Mazda", "6", "Midsize"],
  ["Mazda", "Biante", "Large"],
  ["Mazda", "BT-50", "Large"],
  ["Mazda", "CX-3", "Midsize"],
  ["Mazda", "CX-30", "Midsize"],
  ["Mazda", "CX-60", "Midsize"],
  ["Mazda", "CX-7", "Midsize"],
  ["Mazda", "CX-8", "Midsize"],
  ["Mazda", "CX-9", "Midsize"],
  ["Mazda", "CX5", "Midsize"],
  ["Mazda", "MX 5 RF", "Compact"],
  ["McLaren", "570S", "Midsize"],
  ["Mercedes-Benz", "A Class", "Midsize"],
  ["Mercedes-Benz", "B Class", "Midsize"],
  ["Mercedes-Benz", "C Class", "Midsize"],
  ["Mercedes-Benz", "CLA Class", "Midsize"],
  ["Mercedes-Benz", "CLS Class", "Midsize"],
  ["Mercedes-Benz", "E Class", "Midsize"],
  ["Mercedes-Benz", "G Class", "Large"],
  ["Mercedes-Benz", "GLA Class", "Midsize"],
  ["Mercedes-Benz", "GLC Class", "Midsize"],
  ["Mercedes-Benz", "GLE Class", "Midsize"],
  ["Mercedes-Benz", "GLS Class", "Large"],
  ["Mercedes-Benz", "S Class", "Midsize"],
  ["Mercedes-Benz", "SLK Class", "Compact"],
  ["MG (Morris Garages)", "4 EV", "Midsize"],
  ["MG (Morris Garages)", "HS", "Midsize"],
  ["MG (Morris Garages)", "S5 EV", "Midsize"],
  ["MG (Morris Garages)", "ZS", "Midsize"],
  ["MG (Morris Garages)", "ZS Crossover", "Midsize"],
  ["MG (Morris Garages)", "ZS EV", "Midsize"],
  ["MINI", "Clubman", "Midsize"],
  ["MINI", "Convertible", "Midsize"],
  ["MINI", "Cooper", "Compact"],
  ["MINI", "Countryman", "Compact"],
  ["Mitsubishi Motors", "Delica", "Large"],
  ["Mitsubishi Motors", "Destinator", "Midsize"],
  ["Mitsubishi Motors", "Galant", "Midsize"],
  ["Mitsubishi Motors", "Grandis", "Midsize"],
  ["Mitsubishi Motors", "Kuda", "Midsize"],
  ["Mitsubishi Motors", "L300 Pickup", "Midsize"],
  ["Mitsubishi Motors", "Lancer", "Compact"],
  ["Mitsubishi Motors", "Mirage", "Compact"],
  ["Mitsubishi Motors", "Outlander", "Midsize"],
  ["Mitsubishi Motors", "Pajero Sport", "Large"],
  ["Mitsubishi Motors", "Triton", "Midsize"],
  ["Mitsubishi Motors", "Xforce", "Midsize"],
  ["Mitsubishi Motors", "Xpander", "Midsize"],
  ["Mitsubishi Motors", "Xpander Cross", "Midsize"],
  ["Nissan", "Elgrand", "Large"],
  ["Nissan", "Evalia", "Midsize"],
  ["Nissan", "Juke", "Compact"],
  ["Nissan", "Kicks e-POWER", "Midsize"],
  ["Nissan", "Livina / Grand Livina", "Midsize"],
  ["Nissan", "Livina X-Gear", "Midsize"],
  ["Nissan", "Magnite", "Midsize"],
  ["Nissan", "March", "Compact"],
  ["Nissan", "Navara", "Midsize"],
  ["Nissan", "Note", "Compact"],
  ["Nissan", "Serena", "Large"],
  ["Nissan", "Teana", "Midsize"],
  ["Nissan", "Terra", "Midsize"],
  ["Nissan", "Terrano", "Midsize"],
  ["Nissan", "X-Trail", "Midsize"],
  ["Opel", "Blazer", "Midsize"],
  ["Peugeot", "206", "Compact"],
  ["Peugeot", "405", "Midsize"],
  ["Peugeot", "406", "Midsize"],
  ["Peugeot", "5008", "Midsize"],
  ["Porsche", "718 Cayman", "Compact"],
  ["Porsche", "911", "Midsize"],
  ["Porsche", "Cayenne", "Midsize"],
  ["Porsche", "Panamera", "Midsize"],
  ["Porsche", "Taycan", "Midsize"],
  ["Renault", "Koleos", "Midsize"],
  ["Rolls-Royce", "Rolls-Royce Ghost", "Midsize"],
  ["Subaru", "Forester", "Midsize"],
  ["Subaru", "WRX", "Midsize"],
  ["Subaru", "XV", "Midsize"],
  ["Suzuki", "Aerio Hatchback", "Compact"],
  ["Suzuki", "APV Arena / Blind Van", "Midsize"],
  ["Suzuki", "APV Luxury", "Midsize"],
  ["Suzuki", "Baleno", "Midsize"],
  ["Suzuki", "Carry", "Midsize"],
  ["Suzuki", "Ciaz", "Midsize"],
  ["Suzuki", "Ertiga", "Midsize"],
  ["Suzuki", "Forsa", "Midsize"],
  ["Suzuki", "Fronx", "Compact"],
  ["Suzuki", "Grand Vitara", "Midsize"],
  ["Suzuki", "Ignis", "Compact"],
  ["Suzuki", "Jimny", "Compact"],
  ["Suzuki", "Karimun", "Compact"],
  ["Suzuki", "S-Presso", "Compact"],
  ["Suzuki", "Splash", "Compact"],
  ["Suzuki", "Swift", "Compact"],
  ["Suzuki", "SX4", "Compact"],
  ["Suzuki", "XL7", "Midsize"],
  ["Timor", "Timor", "Compact"],
  ["Toyota", "Agya", "Compact"],
  ["Toyota", "Alphard", "Large"],
  ["Toyota", "Avanza", "Midsize"],
  ["Toyota", "Calya", "Midsize"],
  ["Toyota", "Camry", "Midsize"],
  ["Toyota", "CHR", "Midsize"],
  ["Toyota", "Corolla", "Midsize"],
  ["Toyota", "Corolla Altis", "Midsize"],
  ["Toyota", "Corona", "Midsize"],
  ["Toyota", "Crown", "Midsize"],
  ["Toyota", "Etios Valco", "Compact"],
  ["Toyota", "Fortuner", "Large"],
  ["Toyota", "GR 86", "Midsize"],
  ["Toyota", "GR Corolla", "Compact"],
  ["Toyota", "GR Yaris", "Midsize"],
  ["Toyota", "Hardtop", "Midsize"],
  ["Toyota", "Harrier", "Midsize"],
  ["Toyota", "HiAce", "Jumbo"],
  ["Toyota", "Hilux", "Large"],
  ["Toyota", "Innova", "Midsize"],
  ["Toyota", "Kijang", "Midsize"],
  ["Toyota", "Land Cruiser", "Large"],
  ["Toyota", "Nav1", "Midsize"],
  ["Toyota", "Previa", "Midsize"],
  ["Toyota", "Raize", "Compact"],
  ["Toyota", "Rush", "Midsize"],
  ["Toyota", "Sienta", "Compact"],
  ["Toyota", "Soluna", "Compact"],
  ["Toyota", "Starlet", "Compact"],
  ["Toyota", "Vellfire", "Large"],
  ["Toyota", "Veloz", "Midsize"],
  ["Toyota", "Vios", "Midsize"],
  ["Toyota", "Voxy", "Large"],
  ["Toyota", "Wish", "Midsize"],
  ["Toyota", "Yaris", "Compact"],
  ["Toyota", "Yaris Cross", "Midsize"],
  ["Volkswagen", "Beetle", "Compact"],
  ["Volkswagen", "Golf", "Compact"],
  ["Volkswagen", "Polo", "Compact"],
  ["Volkswagen", "Scirocco", "Compact"],
  ["Volkswagen", "Tiguan", "Midsize"],
  ["Volvo", "850 Sedan", "Midsize"],
  ["Volvo", "960", "Midsize"],
  ["Volvo", "XC40", "Midsize"],
  ["Wuling", "Air EV", "Subcompact"],
  ["Wuling", "Almaz", "Midsize"],
  ["Wuling", "Alvez", "Midsize"],
  ["Wuling", "BinguoEV", "Compact"],
  ["Wuling", "Confero", "Midsize"],
  ["Wuling", "Cortez", "Midsize"],
  ["Wuling", "Mini EV", "Subcompact"]
];
