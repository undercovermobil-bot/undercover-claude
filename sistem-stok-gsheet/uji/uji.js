'use strict';
// Uji Kode.gs dengan data asli. Pakai:  node uji/uji.js Kode.gs   (fixture: uji/fixture.json dari ekstrak.py)
const fs = require('fs');
const path = require('path');
const { Spreadsheet, buatKonteks } = require('./mock');

const KODE = process.argv[2];
const DATA = JSON.parse(fs.readFileSync(path.join(__dirname, 'fixture.json'), 'utf8'));
let gagal = 0, lulus = 0;
function cek(kond, pesan) { if (kond) lulus++; else { gagal++; console.log('GAGAL:', pesan); } }

function siapkan(opsi = {}) {
  const ss = new Spreadsheet();
  for (const nama of ['Stok Cover UC', 'Stok Cover STP', 'Resi Keluar Stok']) {
    const sh = ss.insertSheet(nama);
    sh.maxCols = 40; sh.maxRows = 1121;
    for (const [k, v] of Object.entries(DATA[nama] || {})) {
      const [r, c] = k.split(',').map(Number);
      if (typeof v === 'string' && v.startsWith('=')) sh.cell(r, c).f = v; else sh.cell(r, c).v = v;
    }
  }
  const ctx = buatKonteks(ss, Object.assign({ kode: KODE }, opsi));
  return { ss, ctx };
}
function siapkanSalinan(dari, jawab) {
  const b = siapkan();
  b.ctx.migrasiStokUC(); b.ctx.migrasiStokSTP();
  b.ctx.__opsi.jawab = jawab;   // jawaban dialog berikutnya
  for (const nama of ['Log Stok UC', 'Log Stok STP']) {
    const asal = dari.ss.getSheetByName(nama), tujuan = b.ss.getSheetByName(nama);
    const n = asal.getLastRow();
    if (n > 1) { pastikanTujuan(tujuan, n); tujuan.getRange(2, 1, n - 1, 12).setValues(asal.getRange(2, 1, n - 1, 12).getValues()); }
    tujuan.getRange(2, 1, Math.max(n - 1, 1), 1).setNumberFormat('dd/MM/yyyy HH:mm:ss');
  }
  return b;
}
function pastikanTujuan(sh, baris) { if (sh.getMaxRows() < baris) sh.insertRowsAfter(sh.getMaxRows(), baris - sh.getMaxRows() + 5); }
// nilai sel Waktu: Date (jam dinding WIB, zona file WIB) -> nomor seri
const keSerial = v => v instanceof Date ? (v.getTime() + 7 * 3600e3 - Date.UTC(1899, 11, 30)) / 86400000 : v;
const snap = sh => JSON.stringify([...sh.cells.entries()].map(([k, x]) => [k, x.v, x.f]));
const W = 16;

const { ss, ctx } = siapkan();
const lamaUC = ss.getSheetByName('Stok Cover UC');
const lamaSTP = ss.getSheetByName('Stok Cover STP');
const snapUC = snap(lamaUC), snapSTP = snap(lamaSTP);

// ---------- sebelum migrasi: trigger aktif, edit sheet format lama tidak diproses
ctx.aktifkanInputOtomatis(); ctx.aktifkanInputOtomatis();
cek(ctx.__triggers.length === 1, 'trigger tidak dobel');
lamaUC.getRange(4, 5).setValue(9);
ctx.prosesInputStok({ range: lamaUC.getRange(4, 5), source: ss });
cek(lamaUC.peek(4, 4).v === 39 && lamaUC.peek(4, 5).v === 9 && !ss.getSheetByName('Log Stok UC'), 'sheet format lama tidak disentuh trigger');
lamaUC.getRange(4, 5).setValue(3);
ctx.__alerts.length = 0; ctx.kunciKolomStok();
cek(/belum dimigrasi/.test(ctx.__alerts[0]) && lamaUC.protections.length === 0, 'kunci sebelum migrasi dilewati');

// ---------- dialog migrasi menyebut perubahan zona waktu (file belum WIB)
const bz = siapkan();
bz.ctx.migrasiStokUC();
cek(/Zona waktu file diubah dari America\/Los_Angeles ke Asia\/Jakarta/.test(bz.ctx.__alerts[0]) && bz.ss.getSpreadsheetTimeZone() === 'Asia/Jakarta', 'dialog menyebut perubahan zona');

// ---------- migrasi dibatalkan user
const b0 = siapkan({ jawab: 'NO' });
b0.ctx.migrasiStokUC();
cek(b0.ss.sheets.map(s => s.name).join('|') === 'Stok Cover UC|Stok Cover STP|Resi Keluar Stok', 'batal: tidak ada perubahan');

// ---------- warnaTambahan: 'setelah' tidak ada -> dibatalkan tanpa perubahan; sudah ada -> tidak dobel
const b3 = siapkan();
b3.ctx.__KONFIG.SISTEM[1].warnaTambahan = [{ nama: 'Orange', setelah: 'Hijau' }];
b3.ctx.migrasiStokSTP();
cek(/tidak ada di header/.test(b3.ctx.__alerts[0] || '') && !b3.ss.getSheetByName('Stok Cover STP (lama)'), 'setelah salah: batal');
const b4 = siapkan();
b4.ctx.__KONFIG.SISTEM[1].warnaTambahan = [{ nama: 'Hitam', setelah: 'Abu-abu' }];
b4.ctx.migrasiStokSTP();
const s4 = b4.ss.getSheetByName('Stok Cover STP');
cek(s4.getRange(3, 1, 1, s4.getMaxColumns()).getValues()[0].filter(x => x === 'STOK').length === 16 && s4.peek(3, 52).v === 'Reguler', 'warna yang sudah ada tidak ditambah dobel');

// ---------- migrasi gagal di tengah -> rollback
const b1 = siapkan();
const asli = Object.getPrototypeOf(b1.ss.sheets[0]).setFrozenColumns;
Object.getPrototypeOf(b1.ss.sheets[0]).setFrozenColumns = function () { throw new Error('simulasi error'); };
b1.ctx.migrasiStokUC();
Object.getPrototypeOf(b1.ss.sheets[0]).setFrozenColumns = asli;
cek(b1.ss.sheets.map(s => s.name).join('|') === 'Stok Cover UC|Stok Cover STP|Resi Keluar Stok|Log Stok UC' &&
  snap(b1.ss.getSheetByName('Stok Cover UC')) === snapUC, 'rollback saat gagal: ' + b1.ss.sheets.map(s => s.name).join('|'));

// ---------- migrasi UC & STP
ctx.__alerts.length = 0;
ctx.migrasiStokUC();

console.log('ALERT UC:\n  ' + ctx.__alerts.join('\n  ').replace(/\n/g, '\n    '));
ctx.__alerts.length = 0;
ctx.migrasiStokSTP();
const alertSTP = ctx.__alerts.join('\n');
console.log('ALERT STP:\n  ' + ctx.__alerts.join('\n  ').replace(/\n/g, '\n    '));
cek(ss.sheets.map(s => s.name).join('|') === 'Stok Cover UC|Stok Cover UC (lama)|Stok Cover STP|Stok Cover STP (lama)|Resi Keluar Stok|Log Stok UC|Log Stok STP',
  'urutan tab: ' + ss.sheets.map(s => s.name).join('|'));
cek(snap(lamaUC) === snapUC && lamaUC.name === 'Stok Cover UC (lama)', 'isi sheet lama UC utuh (termasuk reseller baris 201+)');
cek(snap(lamaSTP) === snapSTP && lamaSTP.name === 'Stok Cover STP (lama)', 'isi sheet lama STP utuh');
ctx.__alerts.length = 0; ctx.migrasiStokUC();
cek(/sudah pernah dimigrasi/.test(ctx.__alerts[0] || ''), 'migrasi ulang ditolak');

// peta: indeks warna sheet baru -> indeks warna sheet lama (null = warna baru)
function cekStruktur(nama, lama, akhir, labelPrem, peta) {
  const sh = ss.getSheetByName(nama);
  const v = (r, c) => { const x = sh.peek(r, c); return x ? (x.f || x.v) : ''; };
  const Wb = peta.length, kolValue = 4 + 3 * Wb;
  peta.forEach((k, i) => {
    if (k !== null) cek(v(2, 4 + 3 * i) === String(lama.peek(2, 4 + 2 * k).v).trim(), nama + ' nama warna i=' + i);
    cek(v(3, 4 + 3 * i) === 'STOK' && v(3, 5 + 3 * i) === 'IN' && v(3, 6 + 3 * i) === 'OUT', nama + ' label i=' + i);
  });
  cek(v(3, kolValue) === 'Reguler' && v(3, kolValue + 2) === labelPrem && v(3, kolValue + 4) === 'Total Value', nama + ' label value: ' + v(3, kolValue + 2));
  let selisih = 0, unitLama = 0, unitBaru = 0;
  for (let r = 4; r <= akhir; r++) {
    for (let c = 1; c <= 3; c++) if ((lama.peek(r, c) ? lama.peek(r, c).v : '') !== v(r, c)) selisih++;
    peta.forEach((k, i) => {
      const x = k === null ? null : lama.peek(r, 4 + 2 * k); const lv = x && typeof x.v === 'number' ? x.v : '';
      if (lv !== v(r, 4 + 3 * i)) selisih++;
      if (v(r, 5 + 3 * i) !== '' || v(r, 6 + 3 * i) !== '') selisih++;
      unitLama += lv || 0; unitBaru += v(r, 4 + 3 * i) || 0;
    });
  }
  cek(selisih === 0 && unitLama === unitBaru, `${nama} data tersalin persis (selisih ${selisih}, unit ${unitLama}/${unitBaru})`);
  cek(v(akhir + 1, 2) === '' && v(akhir + 2, 2) === 'TOTAL STOK' && v(akhir + 3, 2) === 'MASUK / KELUAR HARI INI', nama + ' posisi total');
  cek(v(akhir + 2, 4) === `=SUM(D4:D${akhir + 1})`, nama + ' total STOK: ' + v(akhir + 2, 4));
  cek(v(akhir + 3, 5).includes(`'Log Stok ${nama.slice(-2) === 'UC' ? 'UC' : 'STP'}'!`), nama + ' mutasi merujuk log sendiri');
  console.log(`${nama}: produk baris 4-${akhir}, ${Wb} warna, total unit ${unitBaru}`);
  return { sh, v, kolValue };
}
const uc = cekStruktur('Stok Cover UC', lamaUC, 196, 'Premium', [...Array(16).keys()]);
const PETA_STP = [0, 1, 2, 3, 4, null, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15];   // Orange disisip setelah Hijau Army
const stp = cekStruktur('Stok Cover STP', lamaSTP, 107, 'Transparan', PETA_STP);
cek(stp.v(2, 19) === 'Orange' && stp.v(2, 16) === 'Hijau Army' && stp.v(2, 22) === 'Elite Abu', 'STP Orange setelah Hijau Army');
cek(stp.kolValue === 55 && uc.kolValue === 52, 'kolom value: UC AZ, STP BC');
cek(stp.v(110, 20).includes('S$2'), 'STP mutasi Orange merujuk header Orange');
cek(/Warna baru: Orange \(setelah Hijau Army, stok awal kosong, value ikut harga Reguler\)/.test(alertSTP), 'konfirmasi menyebut Orange');

cek(uc.v(4, 52) === '=(D4+G4+J4+M4+P4)*281000' && uc.v(4, 53) === '=(S4+V4+Y4+AB4+AE4+AH4+AK4+AN4+AQ4)*341000', 'UC formula baris 4');
cek(uc.v(4, 54) === '=(AT4)*680000' && uc.v(4, 55) === '=(AW4)*1180000' && uc.v(4, 56) === '=SUM(AZ4:BC4)', 'UC premium/excl/total');
cek(uc.v(40, 54) === '' && uc.v(50, 52) === '', 'UC baris 40 premium & baris 50 kosong');
cek(stp.v(10, 55) === '=(D10+G10+J10+M10+P10+S10)*257000', 'STP baris 10 L9 dibetulkan + Orange: ' + stp.v(10, 55));
cek(stp.v(5, 56) === '=(V5+Y5+AB5+AE5+AH5+AK5+AN5+AQ5+AT5)*257000', 'STP baris 5 strip lengkap: ' + stp.v(5, 56));
cek(stp.v(5, 57) === '=(AW5)*110000' && stp.v(5, 59) === '=SUM(BC5:BF5)', 'STP transparan/total baris 5: ' + stp.v(5, 57));
cek(stp.v(4, 56) === '' && stp.v(4, 58) === '' && stp.v(102, 55) === '', 'STP tanpa harga tetap kosong');
cek(/DIPERBAIKI baris 10 Toyota Innova/.test(alertSTP) && (alertSTP.match(/DIPERBAIKI baris (5|6|7|8|11) /g) || []).length === 5, 'STP catatan diperbaiki 5-8,10,11');
cek(!/Exclusive: \d+ baris/.test(alertSTP), 'STP Exclusive tidak dilaporkan');

// ---------- edit
const logUC = () => ss.getSheetByName('Log Stok UC');
const logSTP = () => ss.getSheetByName('Log Stok STP');
const nLog = () => logUC().getLastRow() - 1;      // log Stok Cover UC
const nLogS = () => logSTP().getLastRow() - 1;    // log Stok Cover STP
function edit(sh, r, c, nilai, extra = {}) {
  sh.getRange(r, c).setValue(nilai);
  ctx.prosesInputStok(Object.assign({ range: sh.getRange(r, c), source: ss, value: nilai }, extra));
}
function paste(sh, r, c, arr) {
  sh.getRange(r, c, arr.length, arr[0].length).setValues(arr);
  ctx.prosesInputStok({ range: sh.getRange(r, c, arr.length, arr[0].length), source: ss });
}
const U = uc.sh, S = stp.sh, uv = uc.v, sv = stp.v;
const D = 4, E = 5, F = 6, G = 7, I = 9;

edit(U, 4, E, 5);
cek(uv(4, D) === 44 && uv(4, E) === '' && nLog() === 1, 'IN 5: ' + uv(4, D));
const l1 = logUC().getRange(2, 1, 1, 12).getValues()[0];
cek(l1[1] === 'Stok Cover UC' && l1[2] === 4 && l1[3] === 'Honda Brio' && l1[4] === 'HND-BRI-UA-R-G1' && l1[5] === 'Abu-abu' &&
  l1[6] === 'IN' && l1[7] === 5 && l1[8] === 39 && l1[9] === 44 && (typeof l1[0] === 'number' || l1[0] instanceof Date), 'isi log: ' + JSON.stringify(l1));
// jam Log = jam WIB (UTC+7) sekarang, apa pun zona waktu file (mock: Los_Angeles)
const wibSekarang = (Date.now() + 7 * 3600e3 - Date.UTC(1899, 11, 30)) / 86400000;
// sel Waktu berformat tanggal: Sheets mengembalikan Date (jam dinding WIB karena zona file WIB)
const l1Nomor = l1[0] instanceof Date ? (l1[0].getTime() + 7 * 3600e3 - Date.UTC(1899, 11, 30)) / 86400000 : l1[0];
cek(Math.abs(l1Nomor - wibSekarang) < 2 / 1440, 'jam log WIB: ' + l1Nomor + ' vs ' + wibSekarang);
cek(ss.getSpreadsheetTimeZone() === 'Asia/Jakarta', 'zona waktu file diset WIB: ' + ss.getSpreadsheetTimeZone());
edit(U, 4, I, 3); cek(uv(4, G) === 27 && uv(4, I) === '', 'OUT 3');
ctx.prosesInputStok({ range: U.getRange(4, I), source: ss }); cek(uv(4, G) === 27 && nLog() === 2, 'trigger ganda tidak dobel');
edit(U, 4, I, 100);
cek(uv(4, G) === 27 && uv(4, I) === 100 && U.peek(4, I).bg === '#e06666' && /DITOLAK/.test(U.peek(4, I).note) && nLog() === 3, 'OUT berlebih ditolak');
ctx.prosesInputStok({ range: U.getRange(4, I), source: ss }); cek(nLog() === 3, 'penolakan tidak dicatat dobel');
edit(U, 4, I, ''); cek(U.peek(4, I).bg === null && U.peek(4, I).note === '', 'hapus sel ditolak -> reset ke tanpa warna');
edit(U, 4, E, 'abc'); cek(uv(4, D) === 44 && /angka bulat/.test(U.peek(4, E).note), 'teks ditolak');
edit(U, 4, E, 1.5); cek(uv(4, D) === 44 && U.peek(4, E).bg === '#e06666', 'desimal ditolak');
edit(U, 4, E, -2); cek(uv(4, D) === 44, 'negatif ditolak');
edit(U, 4, E, ' 7 '); cek(uv(4, D) === 51 && uv(4, E) === '', 'string angka diterima');
paste(U, 5, E, [[2], [3]]); cek(uv(5, D) === 26 && uv(6, D) === 10, 'paste multi-baris');
paste(U, 7, D, [[10, 2, 1]]); cek(uv(7, D) === 11, 'paste STOK+IN+OUT');
edit(U, 8, D, 20, { oldValue: '16' });
const lk = logUC().getRange(2, 7, 1, 4).getValues()[0];   // terbaru = baris 2
cek(lk[0] === 'KOREKSI' && lk[2] === 16 && lk[3] === 20, 'koreksi manual: ' + JSON.stringify(lk));
// warna: header & STOK = warna cover, IN/OUT tanpa warna
const bg = (sh, r, c) => { const x = sh.peek(r, c); return x ? x.bg : null; };
const fc = (sh, r, c) => { const x = sh.peek(r, c); return x ? x.fc : null; };
const WARNA = { 'Abu-abu': '#999999', 'Hitam': '#000000', 'Biru Benhur': '#0000ff', 'Merah': '#ff0000', 'Hijau Army': '#38761d',
  'Orange': '#ff9900', 'Elite Abu': '#999999', 'Elite Biru': '#0000ff', 'Elite Merah': '#ff0000', 'Epic Abu': '#999999',
  'Epic Biru': '#0000ff', 'Epic Merah': '#ff0000', 'Warior Abu': '#999999', 'Warior Biru': '#0000ff', 'Warior Merah': '#ff0000',
  'Premium': '#efefef', 'Transparan': '#efefef', 'Exclusive': '#d9d9d9' };
for (const [sh, akhir, Wb] of [[U, 196, 16], [S, 107, 17]]) {
  let salah = 0, dicek = 0;
  for (let i = 0; i < Wb; i++) {
    const c = 4 + 3 * i, nama = sh.peek(2, c).v, exp = WARNA[nama];
    if (!exp) { salah++; continue; }
    for (const [r, k] of [[2, 0], [2, 1], [2, 2], [3, 0], [4, 0], [akhir, 0]]) { dicek++; if (bg(sh, r, c + k) !== exp) salah++; }
    for (const r of [3, 4, 50, akhir]) for (const k of [1, 2]) { dicek++; if (bg(sh, r, c + k) !== null) salah++; }
  }
  cek(salah === 0, sh.name + ' warna cover header/STOK, IN/OUT tanpa warna (' + salah + ' salah dari ' + dicek + ')');
}
cek(fc(U, 4, 4 + 3) === '#ffffff' && bg(U, 4, 4 + 3) === '#000000' && fc(U, 4, 4) === '#000000', 'font putih di hitam, hitam di abu');
cek(bg(U, 1, 4) === '#00ffff' && fc(U, 1, 4) === '#ff0000', 'banner D1 cyan teks merah');
cek(bg(S, 4, 19) === '#ff9900' && S.peek(2, 19).v === 'Orange', 'STP Orange berwarna oranye');
cek(bg(U, 4, 2) === null && bg(U, 4, 3) === null, 'nama produk & SKU tanpa warna');
// STOK Hitam diketik huruf -> merah error, lalu angka valid -> kembali hitam
U.getRange(4, 7).setValue('x'); ctx.prosesInputStok({ range: U.getRange(4, 7), source: ss });
cek(bg(U, 4, 7) === '#e06666', 'STOK huruf -> error merah');
U.getRange(4, 7).setValue(27); ctx.prosesInputStok({ range: U.getRange(4, 7), source: ss });
cek(bg(U, 4, 7) === '#000000' && fc(U, 4, 7) === '#ffffff' && uv(4, 7) === 27, 'STOK valid -> warna cover kembali');
const n0 = nLog();
edit(U, 4, 52, 123); cek(nLog() === n0, 'kolom value diabaikan');
edit(U, 198, E, 5); cek(nLog() === n0, 'baris total diabaikan'); U.getRange(198, E).setValue('');
edit(U, 197, E, 5); cek(nLog() === n0 && /tanpa nama/.test(U.peek(197, E).note), 'baris kosong ditolak');
edit(U, 4, 6, 51); cek(uv(4, D) === 0, 'OUT habis -> 0');

// STP
const stpAwal = sv(4, G);
edit(S, 4, 8, 2); cek(sv(4, G) === stpAwal + 2, 'STP IN Hitam: ' + stpAwal + '->' + sv(4, G));
edit(S, 107, 4 + 3 * 15 + 2, 1); cek(sv(107, 4 + 3 * 15) === 0, 'STP C Class OUT Transparan 1 -> 0');
const lt = logSTP().getRange(2, 2, 1, 6).getValues()[0];
cek(lt[0] === 'Stok Cover STP' && lt[1] === 107 && lt[2] === 'C Class' && lt[4] === 'Transparan' && lt[5] === 'OUT', 'log STP: ' + JSON.stringify(lt));
edit(S, 4, 20, 3); cek(sv(4, 19) === 3 && sv(4, 20) === '', 'STP IN Orange 3');
const lo = logSTP().getRange(2, 6, 1, 5).getValues()[0];
cek(lo[0] === 'Orange' && lo[1] === 'IN' && lo[2] === 3 && lo[3] === 0 && lo[4] === 3, 'log Orange: ' + JSON.stringify(lo));
edit(S, 4, 21, 5); cek(sv(4, 19) === 3 && /DITOLAK/.test(S.peek(4, 21).note), 'OUT Orange melebihi stok ditolak');
edit(S, 4, 21, '');

// ---------- log per sheet, terbaru di atas
cek(nLogS() === 4 && nLog() > 3, 'log terpisah: UC ' + nLog() + ' baris, STP ' + nLogS() + ' baris');
{
  const semua = logUC().getRange(2, 1, nLog(), 12).getValues();
  let urut = true; for (let i = 1; i < semua.length; i++) if (semua[i - 1][0] < semua[i][0] - 1e-9) urut = false;
  cek(urut, 'log UC terurut terbaru di atas (waktu menurun)');
  cek(semua.every(r => r[1] === 'Stok Cover UC') && logSTP().getRange(2, 2, 3, 1).getValues().every(r => r[0] === 'Stok Cover STP'), 'tiap log hanya memuat sheet-nya');
  const h = logUC().peek(1, 1);
  cek(logUC().getRange(1, 1).getValue() === 'Waktu' && logUC().frozenRows === 1 && logUC().peek(2, 1).bg === null, 'header tetap di baris 1, baris data tanpa warna header');
  cek(logUC().peek(2, 1).nf === 'dd/MM/yyyy HH:mm:ss', 'kolom Waktu berformat tanggal-jam');
  const q = ss.getSheetByName('Stok Cover UC').peek(199, 5).f, qs = ss.getSheetByName('Stok Cover STP').peek(110, 5).f;
  cek(q.includes("'Log Stok UC'!") && !q.includes('Log Stok STP') && !q.includes('$B:$B'), 'rekap UC merujuk log UC: ' + q.slice(0, 60));
  cek(qs.includes("'Log Stok STP'!") && !qs.includes('Log Stok UC'), 'rekap STP merujuk log STP');
}
// dua edit berturut-turut: yang kedua di baris 2, yang pertama bergeser ke baris 3
edit(U, 20, E, 1); edit(U, 21, E, 1);
{
  const [a, b] = [logUC().getRange(2, 3, 1, 1).getValue(), logUC().getRange(3, 3, 1, 1).getValue()];
  cek(a === 21 && b === 20, 'terbaru paling atas: baris 2 = sheet baris 21, baris 3 = baris 20 (' + a + ',' + b + ')');
}
edit(U, 20, F, 1); edit(U, 21, F, 1);

// ---------- STOK 0 tampil kosong (format), IN/OUT format angka
cek([4, 50, 196].every(r => [4, 7, 10, 16 + 3 * 4].every(c => U.peek(r, c) && U.peek(r, c).nf === '0;-0;;@')), 'STOK UC berformat nol-kosong');
cek([4, 50, 196].every(r => [5, 6, 8, 9].every(c => U.peek(r, c) && U.peek(r, c).nf === '0')), 'IN/OUT UC berformat angka');
cek(S.peek(4, 19).nf === '0;-0;;@' && S.peek(107, 4 + 3 * 15).nf === '0;-0;;@' && S.peek(4, 20).nf === '0', 'STP (termasuk Orange) sama');
edit(U, 4, E, 1); edit(U, 4, F, 1);
cek(U.peek(4, E).nf === '0' && U.peek(4, D).nf === '0;-0;;@', 'format tetap setelah sel diproses');
U.getRange(4, 4).setValue(33); ctx.prosesInputStok({ range: U.getRange(4, 4), source: ss });
cek(U.peek(4, 4).nf === '0;-0;;@', 'format STOK tetap setelah koreksi manual');

// sheet lain diedit -> diabaikan
const resi = ss.getSheetByName('Resi Keluar Stok');
const n1 = nLog(); resi.getRange(2, 5).setValue(5);
ctx.prosesInputStok({ range: resi.getRange(2, 5), source: ss }); cek(nLog() === n1, 'sheet lain diabaikan');
const arsip = ss.getSheetByName('Stok Cover UC (lama)');
arsip.getRange(4, 5).setValue(1); ctx.prosesInputStok({ range: arsip.getRange(4, 5), source: ss });
cek(nLog() === n1 && arsip.peek(4, 4).v === 39, 'sheet arsip diabaikan');

// ---------- hasil review: zona waktu dipaksa saat input diproses
ss.tz = 'America/Los_Angeles';
const stokZona = uv(4, D);
edit(U, 4, E, 1);
cek(ss.getSpreadsheetTimeZone() === 'Asia/Jakarta' && uv(4, D) === stokZona + 1, 'zona file dikembalikan ke WIB saat input diproses');
edit(U, 4, F, 1);

// ---------- hasil review: tanggal/angka di luar batas ditolak
edit(U, 5, E, 46024);   // "1/2" yang terbaca sebagai tanggal
cek(uv(5, D) === 26 && /1–9999/.test(U.peek(5, E).note) && U.peek(5, E).bg === '#e06666', 'serial tanggal ditolak (> MAKS_QTY)');
edit(U, 5, E, '');
cek(U.peek(5, E).bg === null, 'reset sel setelah angka ditolak');
const dvAkhir = U.peek(5, E).dv;
cek(dvAkhir && dvAkhir.f === '=AND(ISNUMBER(E4),E4>0,E4<=9999,E4=INT(E4))' || U.peek(4, E).dv.f === '=AND(ISNUMBER(E4),E4>0,E4<=9999,E4=INT(E4))', 'validasi IN memuat batas atas: ' + U.peek(4, E).dv.f);

// ---------- hasil review: ketikan susulan di sel yang sama tidak terhapus
{
  const Rg = Object.getPrototypeOf(U.getRange(1, 1));
  const asli = Rg.getValues;
  let sudah = false;
  Rg.getValues = function () {
    const out = asli.call(this);
    if (!sudah && this.sh === U && this.r === 4 && this.c === 1 && this.nr === 1 && this.nc >= 40) {
      sudah = true;                                   // pembacaan blok awal oleh trigger
      U.getRange(4, E).setValue(5);                   // staf mengetik ulang 5 sebelum trigger selesai
    }
    return out;
  };
  const stokAwal = uv(4, D);
  U.getRange(4, E).setValue(50);
  ctx.prosesInputStok({ range: U.getRange(4, E), source: ss });
  Rg.getValues = asli;
  cek(uv(4, D) === stokAwal + 50 && uv(4, E) === 5, 'ketikan susulan tidak terhapus: stok ' + uv(4, D) + ', sel IN ' + uv(4, E));
  ctx.prosesInputStok({ range: U.getRange(4, E), source: ss });   // eksekusi berikutnya memproses ketikan baru
  cek(uv(4, D) === stokAwal + 55 && uv(4, E) === '', 'ketikan susulan diproses eksekusi berikutnya: ' + uv(4, D));
  edit(U, 4, F, 55);
}

// lock gagal
const b2 = siapkan({ lockGagal: true });
b2.ctx.migrasiStokUC();
const sh2 = b2.ss.getSheetByName('Stok Cover UC');
sh2.getRange(4, E).setValue(5);
b2.ctx.prosesInputStok({ range: sh2.getRange(4, E, 1, 2), source: b2.ss });
cek(sh2.peek(4, D).v === 39 && /sibuk/.test(sh2.peek(4, E).note) && !sh2.peek(4, F).note, 'lock gagal: input tetap, ditandai');
sh2.getRange(4, D).setValue(77);
b2.ctx.prosesInputStok({ range: sh2.getRange(4, D), source: b2.ss });
cek(sh2.peek(4, D).v === 77 && /belum tercatat di Log/.test(sh2.peek(4, D).note), 'lock gagal: koreksi STOK ditandai');

// ---------- hasil review: warnaTambahan berantai + data terbaru setelah dialog
const b5 = siapkan();
b5.ctx.__KONFIG.SISTEM[1].warnaTambahan = [{ nama: 'Orange', setelah: 'Hijau Army' }, { nama: 'Silver', setelah: 'Orange' }, { nama: 'Pink', setelah: 'Hijau Army' }];
b5.ctx.migrasiStokSTP();
const s5 = b5.ss.getSheetByName('Stok Cover STP');
const namaB5 = []; for (let c = 4; c <= 4 + 3 * 19; c += 3) namaB5.push(s5.peek(2, c) ? s5.peek(2, c).v : '');
cek(namaB5.slice(4, 10).join('|') === 'Hijau Army|Orange|Silver|Pink|Elite Abu|Elite Biru', 'warna berantai & urutan config: ' + namaB5.slice(0, 12).join('|'));
const b6 = siapkan({ saatAlert: a => { if (/Migrasi Stok Cover UC/.test(String(a[0])) ) b6.ss.getSheetByName('Stok Cover UC').getRange(10, 4).setValue(17); } });
b6.ctx.migrasiStokUC();
cek(b6.ss.getSheetByName('Stok Cover UC').peek(10, 4).v === 17, 'data diambil ulang setelah dialog: ' + b6.ss.getSheetByName('Stok Cover UC').peek(10, 4).v);

// ---------- arsip log bulanan
{
  const ba = siapkan();
  ba.ctx.migrasiStokUC(); ba.ctx.migrasiStokSTP(); ba.ctx.aktifkanInputOtomatis();
  const BU = ba.ss.getSheetByName('Stok Cover UC'), LU = ba.ss.getSheetByName('Log Stok UC'), LS = ba.ss.getSheetByName('Log Stok STP');
  const e2 = (sh, r, c, n) => { sh.getRange(r, c).setValue(n); ba.ctx.prosesInputStok({ range: sh.getRange(r, c), source: ba.ss }); };
  e2(BU, 4, 5, 1); e2(BU, 5, 5, 1);                         // 2 mutasi bulan ini (UC)
  const nowS = (Date.now() + 7 * 3600e3 - Date.UTC(1899, 11, 30)) / 86400000;
  const bulanLalu = Math.floor(nowS) - 40, duaBulan = Math.floor(nowS) - 75;
  // baris lama disisipkan di bawah (urutan acak, satu bertipe Date lewat format tanggal, satu teks aneh)
  const tulisLama = (sh, baris0, rows) => rows.forEach((w, i) => sh.getRange(baris0 + i, 1, 1, 12).setValues([[w, 'x', 4 + i, 'Produk ' + i, 'SKU', 'Abu-abu', 'IN', 1, 0, 1, '', '']]));
  const lastU = LU.getLastRow();
  tulisLama(LU, lastU + 1, [bulanLalu + 0.5, duaBulan + 0.25, bulanLalu + 0.75]);
  LU.getRange(lastU + 4, 1, 1, 12).setValues([['bukan-waktu', 'x', 9, 'aneh', 'SKU', 'Abu-abu', 'IN', 1, 0, 1, '', '']]);
  LU.getRange(lastU + 1, 1, 3, 1).setNumberFormat('dd/MM/yyyy HH:mm:ss');   // sel Waktu berformat tanggal → getValues = Date
  const nLU = LU.getLastRow() - 1;
  const lastS = LS.getLastRow();
  e2(ba.ss.getSheetByName('Stok Cover STP'), 4, 5, 1);
  tulisLama(LS, LS.getLastRow() + 1, [bulanLalu + 0.1]);
  // dibatalkan
  const bn = siapkanSalinan(ba, 'NO');
  bn.ctx.arsipkanLogBulanLalu();
  cek(bn.ss.getSheetByName('Log Stok UC').getLastRow() - 1 === nLU && !bn.ss.sheets.some(x => /^Arsip /.test(x.name)), 'arsip dibatalkan: tidak ada perubahan');
  ba.ctx.__alerts.length = 0; ba.ctx.arsipkanLogBulanLalu();
  console.log('ALERT arsip:', ba.ctx.__alerts.join(' || ').replace(/\n/g, ' / '));
  const namaArsip = ba.ss.sheets.map(x => x.name).filter(x => /^Arsip /.test(x)).sort();
  const bln = nomor => { const d = new Date(Math.floor(nomor * 86400000) + Date.UTC(1899, 11, 30)); return d.getUTCFullYear() + '-' + ('0' + (d.getUTCMonth() + 1)).slice(-2); };
  const expU1 = 'Arsip Log Stok UC ' + bln(bulanLalu), expU2 = 'Arsip Log Stok UC ' + bln(duaBulan), expS = 'Arsip Log Stok STP ' + bln(bulanLalu);
  cek(JSON.stringify(namaArsip) === JSON.stringify([expU1, expU2, expS].sort()), 'sheet arsip per bulan & per log: ' + namaArsip.join(', '));
  const aU1 = ba.ss.getSheetByName(expU1);
  const isiU1 = aU1.getRange(2, 1, aU1.getLastRow() - 1, 1).getValues().map(r => keSerial(r[0]));
  cek(isiU1.length === 2 && isiU1[0] > isiU1[1] && Math.abs(isiU1[0] - (bulanLalu + 0.75)) < 1e-6, 'arsip bulan lalu terurut terbaru di atas: ' + isiU1.join(','));
  cek(typeof isiU1[0] === 'number' || Object.prototype.toString.call(isiU1[0]) === '[object Date]', 'waktu arsip tersimpan sebagai angka/tanggal');
  cek(aU1.getRange(1, 1).getValue() === 'Waktu' && aU1.frozenRows === 1, 'arsip punya header');
  const sisaU = LU.getRange(2, 1, LU.getLastRow() - 1, 1).getValues().map(r => keSerial(r[0]));
  cek(sisaU.length === 3 && sisaU.filter(v => typeof v === 'number' && v > nowS - 1).length === 2 && sisaU.includes('bukan-waktu'), 'Log UC tersisa: 2 bulan ini + 1 baris tak terbaca: ' + sisaU.length);
  cek(LS.getLastRow() - 1 === lastS - 1 + 1 && ba.ss.getSheetByName(expS).getLastRow() === 2, 'Log STP: 1 baris bulan ini tersisa, 1 diarsipkan');
  ba.ctx.__alerts.length = 0; ba.ctx.arsipkanLogBulanLalu();
  cek(/Tidak ada log bulan sebelum/.test(ba.ctx.__alerts[0]), 'arsip kedua kali: tidak ada yang dipindah');
  // arsip menambah baris ke sheet arsip bulan yang sama (susulan)
  tulisLama(LU, LU.getLastRow() + 1, [bulanLalu + 0.9]);
  LU.getRange(LU.getLastRow(), 1).setNumberFormat('dd/MM/yyyy HH:mm:ss');
  ba.ctx.arsipkanLogBulanLalu();
  const isiU1b = aU1.getRange(2, 1, aU1.getLastRow() - 1, 1).getValues().map(r => keSerial(r[0]));
  cek(isiU1b.length === 3 && isiU1b[0] > isiU1b[1] && isiU1b[1] > isiU1b[2], 'arsip susulan digabung & terurut: ' + isiU1b.length);
  e2(BU, 6, 5, 1);
  cek(LU.getRange(2, 3, 1, 1).getValue() === 6, 'input baru setelah arsip tetap masuk paling atas');
  // kunci mencakup arsip
  ba.ctx.kunciKolomStok();
  cek(ba.ss.getSheetByName(expU1).protections.filter(p => !p.removed).length === 1 && LU.protections.filter(p => !p.removed).length === 1 && LS.protections.filter(p => !p.removed).length === 1, 'kunci: log & arsip terkunci');
}

// kunci
ctx.__alerts.length = 0; ctx.kunciKolomStok(); ctx.kunciKolomStok();
for (const sh of [U, S]) {
  const prot = sh.protections.filter(p => !p.removed);
  cek(prot.length === 1 && prot[0].unprot.length === (sh === S ? 34 : 32) && prot[0].editors.join() === 'owner@x', sh.name + ' proteksi');
}
cek(lamaUC.protections.length === 0, 'arsip tidak dikunci');
console.log('ALERT kunci:', ctx.__alerts.slice(-1)[0].replace(/\n/g, ' / '));
ctx.__alerts.length = 0; ctx.cekStatus(); console.log('STATUS:', ctx.__alerts[0].replace(/\n/g, ' / '));

// log melewati batas baris
const penuh = logUC().getLastRow(); logUC().maxRows = penuh;
const stokPenuh = uv(4, D);
edit(U, 4, E, 1); cek(uv(4, D) === stokPenuh + 1 && logUC().getLastRow() === penuh + 1, 'log tumbuh melewati batas baris');

console.log(`\n${lulus} lulus, ${gagal} gagal`);
const dump = {};
for (const s of ss.sheets) { const o = {}; for (const [k, x] of s.cells) if (x.v !== '' || x.f) o[k] = x.f || (Object.prototype.toString.call(x.v) === '[object Date]' ? { date: x.v.toISOString() } : x.v); dump[s.name] = o; }
fs.writeFileSync(path.join(__dirname, 'hasil.json'), JSON.stringify(dump));
process.exit(gagal ? 1 : 0);
