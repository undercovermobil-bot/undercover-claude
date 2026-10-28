'use strict';
// Uji Kode.gs dengan data asli. Pakai:  node uji/uji.js Kode.gs   (fixture: uji/fixture.json dari ekstrak.py)
const fs = require('fs');
const path = require('path');
const { Spreadsheet, buatKonteks, bekukanJamHost } = require('./mock');
bekukanJamHost();   // jam uji = tengah hari WIB (lihat mock.js)

const KODE = process.argv[2];
const DATA = JSON.parse(fs.readFileSync(path.join(__dirname, 'fixture.json'), 'utf8'));
let gagal = 0, lulus = 0;
let DAFTAR_UJI = null;
try { DAFTAR_UJI = require('./daftar-urutan'); } catch (e) { /* uji daftar sungguhan dilewati */ }
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
  if (!opsi.tanpaUrutan) {
    buatUrutanCermin(ss, 'UC', 'Stok Cover UC', 196);
    buatUrutanCermin(ss, 'STP', 'Stok Cover STP', 107);
  }
  const ctx = buatKonteks(ss, Object.assign({ kode: KODE }, opsi));
  return { ss, ctx };
}
// Daftar urutan "cermin": urutan dan isi sama persis dengan sheet lama (baris 4..akhir). Dasar semua uji lama.
const HEADER_URUTAN = ['No', 'Nama Produk', 'Kode SKU', 'Baris lama', 'Nama di sheet lama', 'Harga dari baris', 'Catatan'];
function tulisUrutan(ss, nama, baris) {
  const sh = ss.insertSheet(nama);
  sh.maxCols = 12; sh.maxRows = Math.max(400, baris.length + 20);
  sh.getRange(1, 1, 1, HEADER_URUTAN.length).setValues([HEADER_URUTAN]);
  if (baris.length) sh.getRange(2, 1, baris.length, HEADER_URUTAN.length).setValues(baris.map((b, i) => [i + 1, b.nama, b.sku || '', b.baris, b.namaLama === undefined ? b.nama : b.namaLama, b.harga === undefined ? '' : b.harga, '']));
  return sh;
}
function buatUrutanCermin(ss, kode, namaLama, akhir) {
  const lama = ss.getSheetByName(namaLama), baris = [];
  for (let r = 4; r <= akhir; r++) {
    const nm = lama.peek(r, 2) ? lama.peek(r, 2).v : '', sk = lama.peek(r, 3) ? lama.peek(r, 3).v : '';
    baris.push({ nama: nm, sku: sk, baris: r });
  }
  return tulisUrutan(ss, 'Urutan ' + kode, baris);
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
cek(ctx.__triggers.length === 3 && ctx.__triggers.filter(t => t.getHandlerFunction() === 'prosesInputStok').length === 1 && ctx.__triggers.filter(t => t.getHandlerFunction() === 'sapuInputStok' && t.menit === ctx.__KONFIG.SAPU_MENIT).length === 1, 'trigger tidak dobel: 1 edit + 1 penyapu tiap SAPU_MENIT menit + 1 rekap harian');
cek(ctx.__triggers.filter(t => t.getHandlerFunction() === 'rekapHarianOtomatis' && t.hari === 1 && t.jam === ctx.__KONFIG.REKAP_JAM && t.nearMenit === ctx.__KONFIG.REKAP_MENIT && t.zona === 'Asia/Jakarta').length === 1, 'trigger rekap harian: tiap hari, jam/menit KONFIG, zona WIB');
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
cek(b0.ss.sheets.map(s => s.name).join('|') === 'Stok Cover UC|Stok Cover STP|Resi Keluar Stok|Urutan UC|Urutan STP', 'batal: tidak ada perubahan');

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
cek(b1.ss.sheets.map(s => s.name).join('|') === 'Stok Cover UC|Stok Cover STP|Resi Keluar Stok|Urutan UC|Urutan STP' && /Migrasi GAGAL.*tidak diubah/.test(b1.ctx.__alerts.join(' ')) &&
  snap(b1.ss.getSheetByName('Stok Cover UC')) === snapUC, 'rollback saat gagal: ' + b1.ss.sheets.map(s => s.name).join('|'));

// ---------- migrasi UC & STP
ctx.__alerts.length = 0;
ctx.migrasiStokUC();

console.log('ALERT UC:\n  ' + ctx.__alerts.join('\n  ').replace(/\n/g, '\n    '));
ctx.__alerts.length = 0;
ctx.migrasiStokSTP();
const alertSTP = ctx.__alerts.join('\n');
console.log('ALERT STP:\n  ' + ctx.__alerts.join('\n  ').replace(/\n/g, '\n    '));
cek(ss.sheets.map(s => s.name).join('|') === 'Stok Cover UC|Stok Cover UC (lama)|Stok Cover STP|Stok Cover STP (lama)|Resi Keluar Stok|Urutan UC|Urutan STP|Log Stok UC|Rekap Harian UC|Log Stok STP|Rekap Harian STP',
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
    if (v(r, 1) !== r - 3) selisih++;   // kolom No = nomor urut baru
    for (let c = 2; c <= 3; c++) if (String(lama.peek(r, c) ? lama.peek(r, c).v : '').trim() !== v(r, c)) selisih++;   // nama & SKU di-trim
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
cek(logUC().getRange(2, 7, 3, 1).getValues().map(r => r[0]).join() === 'IN,OUT,KOREKSI', 'satu batch: yang diproses terakhir paling atas (per warna: STOK, OUT, IN)');
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
// jam baris lama tidak berubah saat bergeser (disalin apa adanya, tanpa konversi), dan tidak ada baris kosong di antara data
{
  const t2 = logUC().peek(2, 1).v;
  edit(U, 22, E, 1);
  cek(logUC().peek(3, 1).v === t2, 'jam baris yang bergeser identik: ' + t2 + ' vs ' + logUC().peek(3, 1).v);
  const kolA = logUC().getRange(2, 3, nLog(), 1).getValues().map(r => r[0]);
  cek(kolA.every(x => x !== ''), 'tidak ada baris kosong di antara data log');
  edit(U, 22, F, 1);
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
const FORMULA_IN_KOMA = '=IF(ISNUMBER(E4),AND(E4>0,E4<=9999,E4=INT(E4)),IF(ISTEXT(E4),REGEXMATCH(E4,"^\\s*[Bb]\\s*[0-9]+\\s*$"),FALSE))';
cek(FORMULA_IN_KOMA.indexOf('OR(') < 0 && FORMULA_IN_KOMA.indexOf('INT(') < FORMULA_IN_KOMA.indexOf('ISTEXT('), 'rumus validasi IN/OUT: INT() hanya di cabang angka, tanpa OR/AND yang merambatkan #VALUE! untuk "B1"');
cek(dvAkhir && dvAkhir.f === FORMULA_IN_KOMA || U.peek(4, E).dv.f === FORMULA_IN_KOMA, 'validasi IN memuat batas atas + pola B1: ' + U.peek(4, E).dv.f);

// ---------- hasil review: ketikan susulan di sel yang sama tidak terhapus
{
  const Rg = Object.getPrototypeOf(U.getRange(1, 1));
  const asli = Rg.getValues;
  let sudah = false;
  Rg.getValues = function () {
    const out = asli.call(this);
    if (!sudah && this.sh === U && this.r === 4 && this.c === 1 && this.nc >= 40) {
      sudah = true;                                   // pembacaan blok awal oleh trigger
      U.getRange(4, E).setValue(5);                   // staf mengetik ulang 5 sebelum trigger selesai
    }
    return out;
  };
  const stokAwal = uv(4, D);
  U.getRange(4, E).setValue(50);
  ctx.prosesInputStok({ range: U.getRange(4, E), source: ss });
  Rg.getValues = asli;
  // ketikan susulan tidak terhapus begitu saja: putaran penyapuan berikutnya (masih dalam eksekusi yang sama) memprosesnya
  cek(uv(4, D) === stokAwal + 55 && uv(4, E) === '', 'ketikan susulan diproses putaran berikutnya, tidak hilang: stok ' + uv(4, D) + ', sel IN ' + uv(4, E));
  ctx.prosesInputStok({ range: U.getRange(4, E), source: ss });   // eksekusi susulan: tidak ada yang tersisa, tidak dobel
  cek(uv(4, D) === stokAwal + 55 && uv(4, E) === '', 'eksekusi susulan tidak menghitung dobel: ' + uv(4, D));
  edit(U, 4, F, 55);
}

// ---------- input cepat: kejadian edit terlewat / pembacaan ketinggalan tidak meninggalkan angka
{
  const b = siapkan(); b.ctx.migrasiStokUC(); b.ctx.migrasiStokSTP(); b.ctx.aktifkanInputOtomatis();
  const BU = b.ss.getSheetByName('Stok Cover UC'), BS = b.ss.getSheetByName('Stok Cover STP');
  const LU = b.ss.getSheetByName('Log Stok UC'), LS = b.ss.getSheetByName('Log Stok STP');
  const picu = (sh, r, c, extra = {}) => b.ctx.prosesInputStok(Object.assign({ range: sh.getRange(r, c), source: b.ss }, extra));
  const v = (sh, r, c) => (sh.peek(r, c) || { v: '' }).v;
  const nLogU = () => LU.getLastRow() - 1;
  const keterangan = () => LU.getRange(2, 12, nLogU(), 1).getValues().map(x => x[0]);

  // 1. lima sel diketik cepat, trigger hanya sampai untuk sel pertama dan ketiga (kejadian lain terlewat)
  const awal = [5, 6, 7, 8, 9].map(r => v(BU, r, 4));
  [5, 6, 7, 8, 9].forEach(r => BU.getRange(r, 5).setValue(2));
  picu(BU, 5, 5); picu(BU, 7, 5);
  cek([5, 6, 7, 8, 9].every((r, i) => v(BU, r, 4) === awal[i] + 2 && v(BU, r, 5) === ''), 'kejadian terlewat: semua sel IN diproses oleh trigger berikutnya: ' + [5, 6, 7, 8, 9].map(r => v(BU, r, 4) + '/' + v(BU, r, 5)).join(' '));
  cek(nLogU() === 5 && keterangan().filter(k => /Diproses penyapuan otomatis/.test(k)).length === 4, 'kejadian terlewat: 5 baris log, 4 ditandai penyapuan (' + nLogU() + ')');
  picu(BU, 5, 5);
  cek(nLogU() === 5 && [5, 6, 7, 8, 9].every((r, i) => v(BU, r, 4) === awal[i] + 2), 'trigger berikutnya tidak menghitung dobel');

  // 2. sel yang ditolak (catatan merah) tidak disentuh penyapuan, meski stok sudah cukup; diketik ulang → diproses
  const s4 = v(BU, 4, 4);
  BU.getRange(4, 6).setValue(s4 + 50); picu(BU, 4, 6);
  cek(v(BU, 4, 4) === s4 && /DITOLAK/.test(BU.peek(4, 6).note), 'OUT berlebih ditolak (catatan merah)');
  BU.getRange(4, 5).setValue(100); picu(BU, 4, 5);   // stok naik 100 → OUT tadi sekarang muat
  cek(v(BU, 4, 4) === s4 + 100 && v(BU, 4, 6) === s4 + 50 && /DITOLAK/.test(BU.peek(4, 6).note), 'sapuan melewati sel bercatatan: OUT yang pernah ditolak tidak dieksekusi sendiri');
  BU.getRange(4, 6).setValue(s4 + 50); picu(BU, 4, 6);
  cek(v(BU, 4, 4) === 50 && v(BU, 4, 6) === '' && BU.peek(4, 6).note === '', 'sel bercatatan diketik ulang oleh staf: diproses');

  // 3. galat sementara di tengah proses: sel yang STOK-nya sudah naik dikosongkan + dilog (tidak dobel saat disapu lagi)
  {
    const r3 = [40, 41, 42], awal3 = r3.map(r => v(BU, r, 4));
    r3.forEach(r => BU.getRange(r, 5).setValue(1));
    const Rg = Object.getPrototypeOf(BU.getRange(1, 1)), asliSet = Rg.setValue; let n = 0;
    const logSebelum = nLogU();
    Rg.setValue = function (x) { if (this.sh === BU && this.c === 4 && ++n === 3) throw new Error('Service error: Spreadsheets'); return asliSet.call(this, x); };
    let galat = null;
    try { picu(BU, 40, 5); } catch (err) { galat = err; }
    Rg.setValue = asliSet;
    cek(galat && /Service error/.test(galat.message), 'galat layanan dilempar ulang (terlihat di Executions)');
    cek(v(BU, 40, 4) === (awal3[0] || 0) + 1 && v(BU, 41, 4) === (awal3[1] || 0) + 1 && v(BU, 42, 4) === awal3[2] && v(BU, 40, 5) === '' && v(BU, 41, 5) === '' && v(BU, 42, 5) === 1, 'galat tengah proses: sel yang sudah masuk STOK dikosongkan, sisanya tetap menunggu');
    cek(nLogU() === logSebelum + 2, 'galat tengah proses: baris yang sudah masuk tetap dicatat di Log');
    b.ctx.sapuInputStok();
    cek(r3.every((r, i) => v(BU, r, 4) === (awal3[i] || 0) + 1 && v(BU, r, 5) === '') && nLogU() === logSebelum + 3, 'penyapu berikutnya: tiap sel dihitung tepat sekali');
  }
  // 3b. OUT diperiksa sebelum IN pada warna yang sama (OUT yang tak muat ditolak, tidak lolos karena IN yang baru diketik)
  {
    const s16 = v(BU, 16, 4); BU.getRange(16, 5).setValue(10); BU.getRange(16, 6).setValue(s16 + 5);
    b.ctx.sapuInputStok();
    cek(v(BU, 16, 4) === s16 + 10 && v(BU, 16, 5) === '' && v(BU, 16, 6) === s16 + 5 && /DITOLAK/.test(BU.peek(16, 6).note), 'IN dan OUT bersamaan: OUT dicek lebih dulu terhadap stok (ditolak), IN diproses');
    BU.getRange(16, 6).setValue(''); b.ctx.prosesInputStok({ range: BU.getRange(16, 6), source: b.ss });
  }
  // 3c. atribusi Log: sel yang disapu tidak diberi nama staf yang kebetulan menjalankan eksekusi
  {
    BU.getRange(17, 5).setValue(1); BU.getRange(18, 5).setValue(1);
    picu(BU, 17, 5, { user: { getEmail: () => 'stafB@x' } });
    const baris = LU.getRange(2, 1, 2, 12).getValues();   // terbaru di atas: 2 baris terakhir ditulis
    const edit17 = baris.find(x => x[2] === 17), sapu18 = baris.find(x => x[2] === 18);
    cek(edit17 && edit17[10] === 'stafB@x' && edit17[11] === '' && sapu18 && sapu18[10] === '' && /Diproses penyapuan otomatis/.test(sapu18[11]), 'Log: sel yang diedit atas nama editor, sel yang disapu tanpa nama + keterangan penyapuan');
  }
  // 3d. rentang edit banyak sel yang terpotong ke satu sel tetap dicatat "banyak sel"
  {
    const sebelum = nLogU();
    const rg = { getSheet: () => BU, getRow: () => 197, getColumn: () => 4, getNumRows: () => 3, getNumColumns: () => 1 };   // baris 197 (kosong) .. 199 (rekap): terpotong ke 1 sel
    b.ctx.prosesInputStok({ range: rg, source: b.ss });
    cek(nLogU() === sebelum + 1 && /Edit banyak sel sekaligus/.test(LU.getRange(2, 12).getValue()), 'rentang banyak sel yang terpotong ke satu sel: tetap dicatat "banyak sel", bukan "edit langsung"');
  }
  // 3d2. staf menghapus angka yang akan ditolak selagi diproses: sel kosong tidak boleh tertinggal merah, tidak ada log DITOLAK palsu
  {
    const Rg = Object.getPrototypeOf(BU.getRange(1, 1)), asli = Rg.getValues; let sekali = false;
    BU.getRange(26, 6).setValue(5000);   // OUT jauh melebihi stok → akan ditolak
    const logSebelum = nLogU();
    Rg.getValues = function () { const o = asli.call(this); if (!sekali && this.sh === BU && this.r === 4 && this.c === 1 && this.nc >= 40) { sekali = true; BU.getRange(26, 6).setValue(''); } return o; };
    picu(BU, 26, 5);
    Rg.getValues = asli;
    cek((BU.peek(26, 6) || { note: '' }).note === '' && (BU.peek(26, 6) || { bg: null }).bg === null && nLogU() === logSebelum, 'angka dihapus staf selagi diproses: tidak ada tanda merah / log DITOLAK palsu');
  }
  // 3e. semua catatan buatan script dikenali pembersih (tidak ada tanda yang tertinggal selamanya / catatan staf yang ikut terhapus)
  {
    const catatan = [];
    BU.getRange(20, 5).setValue('abc'); picu(BU, 20, 5); catatan.push(BU.peek(20, 5).note);                   // teks
    BU.getRange(197, 5).setValue(1); picu(BU, 197, 5); catatan.push(BU.peek(197, 5).note);                    // tanpa nama produk
    BU.getRange(21, 4).setValue('x'); BU.getRange(21, 5).setValue(1); picu(BU, 21, 5); catatan.push(BU.peek(21, 5).note);   // STOK bukan angka
    BU.getRange(22, 4).setValue('x'); picu(BU, 22, 4); catatan.push(BU.peek(22, 4).note);                    // STOK diedit jadi teks
    BU.getRange(23, 6).setValue(99999); picu(BU, 23, 6); catatan.push(BU.peek(23, 6).note);                   // OUT melebihi stok / di atas batas
    BU.cell(24, 5).note = 'Sistem sibuk: koreksi'; catatan.push('Sistem sibuk, belum diproses');
    cek(catatan.length === 6 && catatan.every(n => n && b.ctx.catatanSistem_(n)) && !b.ctx.catatanSistem_('catatan buatan staf'), 'semua jenis catatan script dikenali catatanSistem_: ' + JSON.stringify(catatan.map(n => String(n).slice(0, 18))));
    [[20, 5], [197, 5], [21, 5], [23, 6]].forEach(([r, c]) => { BU.getRange(r, c).setValue(''); picu(BU, r, c); });
    BU.getRange(21, 4).setValue(3); picu(BU, 21, 4); BU.getRange(22, 4).setValue(3); picu(BU, 22, 4);
  }

  // 4. penyapu waktu: angka tertinggal di kedua sheet tanpa kejadian edit sama sekali
  {
    const u13 = v(BU, 13, 4), s6 = v(BS, 6, 4);
    BU.getRange(13, 5).setValue(1); BS.getRange(6, 5).setValue(4); BS.getRange(6, 6).setValue(1);
    const n0 = nLogU(), m0 = LS.getLastRow() - 1;
    b.ctx.sapuInputStok();
    cek(v(BU, 13, 4) === u13 + 1 && v(BU, 13, 5) === '' && v(BS, 6, 5) === '' && v(BS, 6, 6) === '', 'penyapu: angka tertinggal di UC dan STP diproses');
    cek(nLogU() === n0 + 1 && LS.getLastRow() - 1 === m0 + 2 && /Diproses penyapuan otomatis/.test(LS.getRange(2, 12).getValue()), 'penyapu: tercatat di log masing-masing, ditandai diproses ulang');
    b.ctx.sapuInputStok();
    cek(nLogU() === n0 + 1 && LS.getLastRow() - 1 === m0 + 2, 'penyapu kedua kali: tidak ada yang berubah');
  }

  // 5. sel tertunda karena sistem sibuk dicoba lagi otomatis
  {
    const u14 = v(BU, 14, 4); BU.getRange(14, 5).setValue(2); BU.getRange(14, 5).setNote('Sistem sibuk, belum diproses. Akan dicoba lagi otomatis');
    b.ctx.sapuInputStok();
    cek(v(BU, 14, 4) === u14 + 2 && v(BU, 14, 5) === '' && BU.peek(14, 5).note === '', 'catatan "sistem sibuk": dicoba lagi dan berhasil');
  }

  // 6. edit di luar area IN/OUT/STOK (kolom Value) tidak memicu penyapuan
  {
    const u15 = v(BU, 15, 4); BU.getRange(15, 5).setValue(1);
    b.ctx.prosesInputStok({ range: BU.getRange(15, 52), source: b.ss, value: '1' });
    cek(v(BU, 15, 4) === u15 && v(BU, 15, 5) === 1, 'edit kolom Value: tidak ada penyapuan (hanya penyapu waktu / edit IN/OUT berikutnya)');
    b.ctx.sapuInputStok(); cek(v(BU, 15, 4) === u15 + 1, 'penyapu waktu memprosesnya');
  }

  // 7. pasang / matikan trigger: edit + penyapu; instalasi lama (hanya edit) ditambahi penyapu
  {
    const c = siapkan(); c.ctx.migrasiStokUC();
    c.ctx.aktifkanInputOtomatis(); const dua = c.ctx.__triggers.map(t => t.getHandlerFunction()).sort().join();
    c.ctx.aktifkanInputOtomatis();
    cek(dua === 'prosesInputStok,rekapHarianOtomatis,sapuInputStok' && c.ctx.__triggers.length === 3 && /sudah aktif/.test(c.ctx.__alerts.slice(-1)[0]), 'aktifkan: edit + penyapu + rekap harian, tidak dobel');
    c.ctx.matikanInputOtomatis();
    cek(c.ctx.__triggers.length === 0 && /3 trigger dihapus/.test(c.ctx.__alerts.slice(-1)[0]), 'matikan: ketiga trigger dihapus');
    c.ctx.__triggers.push({ getHandlerFunction: () => 'prosesInputStok' });   // pemasangan versi lama: hanya trigger edit
    c.ctx.cekStatus();
    cek(new RegExp('Penyapu angka tertinggal \\(tiap ' + c.ctx.__KONFIG.SAPU_MENIT + ' menit\\): 0\\s+← belum ada').test(c.ctx.__alerts.slice(-1)[0]), 'cekStatus: peringatan penyapu belum ada');
    c.ctx.aktifkanInputOtomatis();
    cek(c.ctx.__triggers.length === 3 && /Ditambahkan sekarang: penyapu, rekap harian/.test(c.ctx.__alerts.slice(-1)[0]), 'aktifkan ulang melengkapi penyapu + rekap harian pada instalasi lama, tanpa menggandakan edit');
  }
}

// ---------- tanda merah basi pada sel kosong dibersihkan penyapuan
{
  const b = siapkan(); b.ctx.migrasiStokUC(); b.ctx.aktifkanInputOtomatis();
  const BU = b.ss.getSheetByName('Stok Cover UC');
  const merah = (r, c, cat) => { const x = BU.cell(r, c); x.bg = '#e06666'; x.note = cat; };
  merah(9, 5, 'Sistem sibuk, belum diproses. Akan dicoba lagi otomatis');   // sel kosong + tanda sistem (sisa balapan)
  merah(10, 6, 'DITOLAK: OUT 9 melebihi stok 2. Stok tidak berubah.');      // staf menghapus angkanya, kejadian hapus terlewat
  merah(11, 5, 'catatan buatan staf: jangan hapus');                         // catatan staf di sel kosong: dibiarkan
  BU.getRange(12, 5).setValue(1);
  b.ctx.prosesInputStok({ range: BU.getRange(12, 5), source: b.ss, value: '1' });
  cek(BU.peek(9, 5).bg === null && BU.peek(9, 5).note === '' && BU.peek(10, 6).bg === null && BU.peek(10, 6).note === '', 'tanda sistem basi di sel kosong dibersihkan oleh penyapuan');
  cek(BU.peek(11, 5).note === 'catatan buatan staf: jangan hapus' && BU.peek(11, 5).bg === '#e06666', 'catatan buatan staf di sel kosong tidak disentuh');
  // sel berisi angka dengan tanda DITOLAK tetap dibiarkan
  const s20 = (BU.peek(20, 4) || { v: '' }).v;
  BU.getRange(20, 6).setValue(9999); b.ctx.prosesInputStok({ range: BU.getRange(20, 6), source: b.ss });
  b.ctx.sapuInputStok();
  cek(BU.peek(20, 6).v === 9999 && /DITOLAK/.test(BU.peek(20, 6).note) && (BU.peek(20, 4) || { v: '' }).v === s20, 'sel berisi angka & ditolak tetap merah setelah penyapuan');
}

// ---------- lokal file menolak rumus validasi berkoma (id_ID: "Argumen aturan validasi data ... tidak valid"): migrasi tidak boleh gagal
{
  const koma = f => f.indexOf(',') >= 0;
  const stokKoma = '=AND(ISNUMBER(D4),D4>=0,D4<=9999,D4=INT(D4))', stokTitik = '=AND(ISNUMBER(D4);D4>=0;D4<=9999;D4=INT(D4))';
  const inTitik = '=IF(ISNUMBER(E4);AND(E4>0;E4<=9999;E4=INT(E4));IF(ISTEXT(E4);REGEXMATCH(E4;"^\\s*[Bb]\\s*[0-9]+\\s*$");FALSE))';   // satu aturan untuk IN dan OUT (rumus relatif; mock tidak menggeser E4 ke F4)
  const jalan = opsi => {
    const b = siapkan(opsi); b.ctx.migrasiStokUC();
    const BU = b.ss.getSheetByName('Stok Cover UC');
    return { b, BU, akhir: b.ctx.__alerts.slice(-1)[0], semua: b.ctx.__alerts.join('\n'), dv: (r, c) => (BU.peek(r, c) || {}).dv };
  };
  // normal (lokal en_US): rumus berkoma dipakai, tanpa catatan validasi
  { const r = jalan({}); cek(!!r.dv(4, 4) && r.dv(4, 4).f === stokKoma && /Migrasi selesai|siap/.test(r.akhir) && !/Validasi angka/.test(r.akhir), 'lokal en_US: rumus berkoma, tanpa catatan validasi'); }
  // lokal titik koma: rumus berkoma ditolak di tiap titik (require / build / apply) → pakai titik koma, migrasi selesai
  for (const di of ['require', 'build', 'apply']) {
    const r = jalan({ tolakValidasi: { di, formula: koma } });
    cek(!/GAGAL/.test(r.semua) && /siap/.test(r.akhir) && r.b.ss.getSheetByName('Stok Cover UC (lama)') && !r.b.ss.getSheetByName('Stok Cover UC (baru)'), 'lokal titik koma (' + di + '): migrasi selesai');
    cek(!!r.dv(4, 4) && !!r.dv(4, 5) && !!r.dv(4, 6) && r.dv(4, 4).f === stokTitik && r.dv(4, 5).f === inTitik && r.dv(4, 6).f === inTitik && r.dv(4, 5).invalid === false, 'lokal titik koma (' + di + '): validasi memakai rumus bertitik koma, tolak isian salah');
    cek(!/Validasi angka/.test(r.akhir), 'lokal titik koma (' + di + '): tanpa catatan (perilaku sama)');
    cek(!!r.dv(184, 5) && !!r.dv(184, 4), 'lokal titik koma (' + di + '): validasi sampai baris produk terakhir (184)');
  }
  // semua rumus ditolak: aturan "angka antara"
  { const r = jalan({ tolakValidasi: { di: 'apply', formula: () => true } });
    cek(/siap/.test(r.akhir) && !/GAGAL/.test(r.semua) && !!r.dv(4, 4) && String((r.dv(4, 4) || {}).angka) === '0,9999' && !r.dv(4, 5) && !r.dv(4, 6), 'rumus ditolak semua: STOK aturan angka antara 0-9999; IN/OUT tanpa validasi (aturan angka antara akan memblokir B1)');
    cek(/aturan sederhana/.test(r.akhir) && /desimal lolos/.test(r.akhir) && /TIDAK terpasang/.test(r.akhir), 'rumus ditolak semua: catatan menjelaskan STOK sederhana dan IN/OUT tanpa validasi'); }
  // semua ditolak: validasi dilewati, migrasi tetap selesai, script tetap menolak isian salah
  { const r = jalan({ tolakValidasi: { di: 'apply', formula: () => true, rentang: true } });
    cek(/siap/.test(r.akhir) && !/GAGAL/.test(r.semua) && !r.dv(4, 5) && !r.dv(4, 4), 'semua aturan ditolak: migrasi selesai tanpa validasi');
    cek(/TIDAK terpasang/.test(r.akhir) && /tanda merah/.test(r.akhir), 'semua aturan ditolak: catatan jelas');
    r.b.ctx.aktifkanInputOtomatis();
    const sebelum = Number(r.BU.getRange(4, 4).getValue()) || 0;
    r.BU.getRange(4, 5).setValue('abc'); r.b.ctx.prosesInputStok({ range: r.BU.getRange(4, 5), source: r.b.ss, value: 'abc' });
    cek(r.BU.peek(4, 5).bg === '#e06666' && /angka bulat/.test(r.BU.peek(4, 5).note) && (Number(r.BU.getRange(4, 4).getValue()) || 0) === sebelum, 'tanpa validasi sel: huruf tetap ditolak script (merah + catatan)');
    r.BU.getRange(4, 5).setValue(3); r.b.ctx.prosesInputStok({ range: r.BU.getRange(4, 5), source: r.b.ss, value: '3' });
    cek((Number(r.BU.getRange(4, 4).getValue()) || 0) === sebelum + 3 && r.BU.peek(4, 5).v === '', 'tanpa validasi sel: angka valid tetap diproses'); }
}

// =====================================================================================================
// Pembatalan salah ketik ("B" + jumlah), total harian, rekap harian, menu 4, pengaman label (hasil kritik desain 2026-10-21)
// =====================================================================================================
const SEDIA_UC = opsi => {
  const b = siapkan(opsi); b.ctx.migrasiStokUC(); b.ctx.aktifkanInputOtomatis();
  const BU = b.ss.getSheetByName('Stok Cover UC');
  const o = {
    b, BU, ctx: b.ctx, ss: b.ss,
    LG: () => b.ss.getSheetByName('Log Stok UC'),
    st: (r, c) => Number((BU.peek(r, c) || { v: 0 }).v) || 0,
    sel: (r, c) => BU.peek(r, c) || { v: '', note: '', bg: null },
    kirim: (r, c, v) => { BU.getRange(r, c).setValue(v); b.ctx.prosesInputStok({ range: BU.getRange(r, c), source: b.ss, value: String(v) }); },
    log1: () => o.LG().getRange(2, 1, 1, 12).getValues()[0],
    nLog: () => o.LG().getLastRow() - 1,
    kons: () => b.ctx.__KONFIG,
  };
  return o;
};
const A_STOK = 4, A_IN = 5, A_OUT = 6, H_STOK = 7, H_IN = 8, H_OUT = 9;   // warna 1 (Abu-abu) dan 2 (Hitam), baris 4 = Honda Brio

// ---------- pembatalan B: alur dasar OUT, batas = net hari ini, tercatat Qty negatif
{
  const u = SEDIA_UC();
  const s0 = u.st(4, A_STOK);
  u.kirim(4, A_OUT, 3);
  cek(u.st(4, A_STOK) === s0 - 3 && u.sel(4, A_OUT).v === '', 'B: OUT 3 biasa');
  u.kirim(4, A_OUT, 'B1');
  const l = u.log1();
  cek(u.st(4, A_STOK) === s0 - 2 && u.sel(4, A_OUT).v === '' && l[6] === 'OUT' && l[7] === -1 && l[8] === s0 - 3 && l[9] === s0 - 2 && /BATAL OUT/.test(l[11]) && u.nLog() === 2,
    'B1 membatalkan 1 OUT: STOK naik 1, Log OUT Qty -1 "BATAL OUT" (' + JSON.stringify(l) + ')');
  cek(u.ss.toasts.slice(-1)[0].indexOf('BATAL OUT 1') >= 0, 'B: toast menyebut BATAL OUT 1');
  u.kirim(4, A_OUT, ' b 2 ');   // sisa net = 2: pas
  cek(u.st(4, A_STOK) === s0 && u.nLog() === 3, 'b 2 (huruf kecil + spasi) membatalkan sisa OUT hari ini');
  u.kirim(4, A_OUT, 'B1');       // net 0 -> ditolak
  const n = { bg: u.sel(4, A_OUT).bg, note: u.sel(4, A_OUT).note };
  cek(u.st(4, A_STOK) === s0 && n.bg === '#e06666' && /^DITOLAK: batal OUT 1 melebihi OUT HARI INI .*tercatat 0/.test(n.note) && u.log1()[6] === 'DITOLAK' && u.log1()[7] === 1,
    'B melebihi net hari ini ditolak (merah + catatan + Log DITOLAK): ' + n.note);
  u.kirim(4, A_OUT, '');
  cek(u.sel(4, A_OUT).bg === null && u.sel(4, A_OUT).note === '', 'sel B ditolak bisa dihapus (tampilan kembali normal)');
  // catatan penolakan dikenali sebagai catatan sistem: pembersih tanda basi
  const peta = u.ctx.bacaPeta_(u.BU);
  cek(u.ctx.catatanSistem_(n.note) && peta.labelAda === true, 'catatan DITOLAK B dikenali catatanSistem_; peta.labelAda true');
}

// ---------- pembatalan B: IN (butuh STOK cukup), produk/warna/jenis harus sama, minus tetap ditolak, flag mati
{
  const u = SEDIA_UC();
  u.BU.getRange(4, A_STOK).setValue(2);                // setup: STOK kecil
  u.kirim(4, A_IN, 10);                                // STOK 12
  u.kirim(4, A_OUT, 11);                               // STOK 1
  u.kirim(4, A_IN, 'B9');                              // net IN hari ini 10 >= 9, tapi STOK 1 < 9
  cek(u.st(4, A_STOK) === 1 && /DITOLAK: batal IN 9 melebihi stok 1/.test(u.sel(4, A_IN).note), 'B IN melebihi STOK ditolak: ' + u.sel(4, A_IN).note);
  u.kirim(4, A_IN, 'B1');
  const l = u.log1();
  cek(u.st(4, A_STOK) === 0 && l[6] === 'IN' && l[7] === -1 && /BATAL IN/.test(l[11]), 'B1 pada IN: STOK turun 1, Log IN Qty -1');
  u.kirim(4, A_IN, 'B20');
  cek(/melebihi IN HARI INI .*tercatat 9/.test(u.sel(4, A_IN).note), 'B melebihi net IN hari ini ditolak (net setelah B sebelumnya = 9)');
  u.kirim(4, A_IN, '');
  // warna lain / jenis lain tidak bisa dipakai
  u.kirim(4, H_OUT, 3);                                // OUT Hitam
  u.kirim(4, A_OUT, 'B1');                             // Abu-abu OUT: net sudah dikoreksi ke 0 oleh uji di atas? (OUT 11) -> pakai kombinasi jelas berbeda
  const stokAbu = u.st(4, A_STOK);
  u.kirim(4, A_OUT, '');
  u.kirim(4, H_IN, 'B1');                              // Hitam IN: tidak ada IN hari ini untuk Hitam
  cek(/DITOLAK: batal IN 1 melebihi IN HARI INI .*tercatat 0/.test(u.sel(4, H_IN).note), 'B pada jenis lain (IN) untuk warna yang hanya punya OUT ditolak');
  u.kirim(4, H_IN, '');
  // produk lain
  u.kirim(5, A_OUT, 'B1');
  cek(/tercatat 0/.test(u.sel(5, A_OUT).note), 'B pada produk lain yang tidak punya OUT hari ini ditolak');
  u.kirim(5, A_OUT, '');
  // minus tetap ditolak dan petunjuknya menyebut B
  const s = u.st(4, H_STOK);
  u.kirim(4, H_OUT, -1);
  cek(u.st(4, H_STOK) === s && u.sel(4, H_OUT).bg === '#e06666' && /B1/.test(u.sel(4, H_OUT).note) && /minus tidak dipakai/.test(u.sel(4, H_OUT).note), 'minus ditolak dengan petunjuk B1: ' + u.sel(4, H_OUT).note);
  u.kirim(4, H_OUT, '');
  // varian B yang tidak valid
  for (const v of ['B0', 'B99999', 'B1.5', 'B', 'BB1', 'B-1']) {
    u.kirim(4, H_OUT, v);
    cek(u.sel(4, H_OUT).bg === '#e06666' && /^Isi angka bulat/.test(u.sel(4, H_OUT).note) && u.st(4, H_STOK) === s, 'B tidak valid ditolak: "' + v + '"');
    u.kirim(4, H_OUT, '');
  }
  // flag mati: B diperlakukan seperti teks biasa
  u.kons().IZINKAN_PEMBATALAN = false;
  u.kirim(4, H_OUT, 'B1');
  cek(u.sel(4, H_OUT).bg === '#e06666' && /^Isi angka bulat 1–9999\.$/.test(u.sel(4, H_OUT).note), 'IZINKAN_PEMBATALAN=false: B1 ditolak seperti teks (tanpa petunjuk B): ' + u.sel(4, H_OUT).note);
}

// ---------- pembatalan B: lintas hari ditolak; B tertinggal diproses penyapu; Log dibaca hanya bila ada B
{
  const u = SEDIA_UC();
  const cfg = u.kons().SISTEM[0];
  const kemarin = Math.floor(u.ctx.waktuSerial_(new Date())) - 1 + 0.5;
  u.ctx.tulisLog_(u.ss, cfg, [[kemarin, 'Stok Cover UC', 4, 'Honda Brio', 'HND-BRI-UA-R-G1', 'Abu-abu', 'OUT', 5, 40, 35, '', '']]);
  const s0 = u.st(4, A_STOK);
  u.kirim(4, A_OUT, 'B2');
  cek(u.st(4, A_STOK) === s0 && /DITOLAK: batal OUT 2 melebihi OUT HARI INI .*tercatat 0.*hari lain/.test(u.sel(4, A_OUT).note), 'B untuk entri kemarin ditolak (lintas hari ke admin): ' + u.sel(4, A_OUT).note);
  u.kirim(4, A_OUT, '');
  // penyapu memproses B yang tertinggal di sel (tanpa event edit)
  u.kirim(4, A_OUT, 4);                                 // OUT 4 hari ini
  u.BU.getRange(4, A_OUT).setValue('B3');               // tertinggal, tanpa event
  u.kons().SAPU_JAM = { awal: 0, akhir: 24 };
  u.ctx.sapuInputStok();
  const l = u.log1();
  cek(u.st(4, A_STOK) === s0 - 1 && u.sel(4, A_OUT).v === '' && l[7] === -3 && /BATAL OUT; Diproses penyapuan/.test(l[11]), 'penyapu memproses B tertinggal: ' + JSON.stringify(l));
  // anggaran pembacaan: entri biasa tidak membaca Log; entri B membaca Log
  let bacaLog = 0;
  const RgProto = Object.getPrototypeOf(u.BU.getRange(1, 1));
  const asliGV = RgProto.getValues;
  RgProto.getValues = function () { if (this.sh.name === 'Log Stok UC') bacaLog++; return asliGV.apply(this, arguments); };
  u.kirim(4, A_IN, 2);
  const biasa = bacaLog;
  u.kirim(4, A_OUT, 'B1');
  const denganB = bacaLog;
  RgProto.getValues = asliGV;
  cek(biasa === 0 && denganB === 1, 'Log dibaca hanya saat ada entri B (entri biasa 0 pembacaan, entri B 1): ' + biasa + '/' + denganB);
}

// ---------- jalur penyelamatan prosesPutaran_ tidak menggandakan baris Log
{
  for (const sesudahTulis of [true, false]) {
    const u = SEDIA_UC();
    const asli = u.ctx.tulisLog_;
    let sekali = true;
    u.ctx.tulisLog_ = function (...a) {
      if (!sesudahTulis && sekali) { sekali = false; throw new Error('Service Spreadsheets timed out'); }
      asli.apply(this, a);
      if (sekali) { sekali = false; throw new Error('Service Spreadsheets timed out'); }
    };
    const s0 = u.st(4, A_STOK);
    let galat = null;
    try { u.kirim(4, A_OUT, 2); } catch (e) { galat = e; }
    cek(galat && /timed out/.test(galat.message) && u.st(4, A_STOK) === s0 - 2 && u.sel(4, A_OUT).v === '', 'penyelamatan (' + (sesudahTulis ? 'galat sesudah log tertulis' : 'galat sebelum log tertulis') + '): STOK benar, sel kosong, galat dilempar ulang');
    cek(u.nLog() === 1 && u.log1()[6] === 'OUT' && u.log1()[7] === 2, 'penyelamatan (' + (sesudahTulis ? 'sesudah' : 'sebelum') + '): tepat SATU baris Log (' + u.nLog() + ')');
  }
}

// ---------- galat DI TENGAH tulisLog_ (sesudah sisip, sebelum isi): jalur penyelamatan tidak menggandakan entri lama
{
  for (const tahap of ['copyTo', 'setValues']) {
    for (const nEntri of [1, 2]) {
      const u = SEDIA_UC();
      u.kirim(4, A_OUT, 3);   // entri lama di puncak Log
      if (nEntri === 2) { u.kons().SAPU_JAM = { awal: 0, akhir: 24 }; }
      const nLama = u.nLog();
      const RgProto = Object.getPrototypeOf(u.BU.getRange(1, 1));
      const asli = RgProto[tahap];
      let sekali = true;
      RgProto[tahap] = function () {
        const isiLog = this.sh.name === 'Log Stok UC' && (tahap === 'copyTo' || arguments[0].length === nEntri);
        if (sekali && isiLog) { sekali = false; throw new Error('Service Spreadsheets timed out'); }
        return asli.apply(this, arguments);
      };
      let galat = null;
      try {
        if (nEntri === 1) u.kirim(6, A_OUT, 2);
        else { u.BU.getRange(6, A_OUT).setValue(2); u.BU.getRange(7, A_OUT).setValue(1); u.ctx.prosesInputStok({ range: u.BU.getRange(6, A_OUT, 2, 1), source: u.ss }); }
      } catch (e) { galat = e; }
      RgProto[tahap] = asli;
      const ket = 'galat di ' + tahap + ' (' + nEntri + ' entri)';
      const baris = u.LG().getRange(2, 1, u.nLog(), 12).getValues();
      cek(galat && /timed out/.test(galat.message), ket + ': galat dilempar ulang');
      cek(baris.length === nLama + nEntri && baris.every(r => r[0] !== ''), ket + ': Log bertambah tepat ' + nEntri + ' baris, tanpa baris kosong (' + nLama + ' → ' + baris.length + ')');
      cek(baris.filter(r => r[7] === 3).length === 1, ket + ': entri lama (OUT 3) tetap SATU');
      cek(baris.slice(0, nEntri).every(r => r[6] === 'OUT' && (r[7] === 2 || r[7] === 1)), ket + ': entri baru di puncak');
    }
  }
}

// ---------- label TOTAL STOK hilang: tidak ada yang diproses (baris rekap/total tidak terbaca sebagai produk)
{
  const u = SEDIA_UC();
  const peta = u.ctx.bacaPeta_(u.BU);
  cek(peta.labelAda === true && u.BU.peek(peta.barisTotal, 2).v === 'TOTAL STOK', 'label TOTAL STOK terdeteksi');
  const lbl = u.BU.peek(peta.barisTotal, 2).v;
  u.BU.getRange(peta.barisTotal, 2).setValue('');
  const s0 = u.st(4, A_STOK), n0 = u.nLog();
  u.kirim(4, A_IN, 2);
  cek(u.st(4, A_STOK) === s0 && u.sel(4, A_IN).v === 2 && u.nLog() === n0, 'label hilang: edit IN tidak diproses (stok/Log tetap)');
  u.kons().SAPU_JAM = { awal: 0, akhir: 24 };
  u.ctx.sapuInputStok();
  cek(u.st(4, A_STOK) === s0 && u.sel(4, A_IN).v === 2 && u.nLog() === n0, 'label hilang: penyapu tidak memproses');
  u.ctx.cekStatus();
  cek(/label "TOTAL STOK" di kolom B HILANG/.test(u.ctx.__alerts.slice(-1)[0]), 'label hilang: cekStatus memperingatkan');
  u.ctx.kunciKolomStok();
  cek(/Stok Cover UC: label "TOTAL STOK" di kolom B hilang.*DILEWATI/.test(u.ctx.__alerts.slice(-1)[0]), 'label hilang: kunciKolomStok melewati sheet itu (tidak membuka sel rekap)');
  u.BU.getRange(peta.barisTotal, 2).setValue(lbl);
  u.ctx.sapuInputStok();
  cek(u.st(4, A_STOK) === s0 + 2 && u.sel(4, A_IN).v === '', 'label dikembalikan: sel yang tertinggal diproses penyapu');
}

// ---------- total harian di bawah TOTAL STOK (rumus langsung ke Log) + validasi IN/OUT memuat pola B
{
  const u = SEDIA_UC();
  const peta = u.ctx.bacaPeta_(u.BU);
  const rm = peta.barisTotal + 1;
  cek(u.BU.peek(rm, 2).v === 'MASUK / KELUAR HARI INI', 'baris rekap harian tepat di bawah TOTAL STOK');
  cek(u.BU.peek(rm, 3).f === u.ctx.rumusTotalHarian_('Log Stok UC', 'OUT') && u.BU.peek(rm + 1, 3).f === u.ctx.rumusTotalHarian_('Log Stok UC', 'IN'), 'C(rekap) = total KELUAR, C(rekap+1) = total MASUK, langsung dari Log');
  cek(u.ctx.rumusTotalHarian_('Log Stok UC', 'OUT') === "=SUMIFS('Log Stok UC'!$H:$H,'Log Stok UC'!$G:$G,\"OUT\",'Log Stok UC'!$D:$D,\"<>Motor\",'Log Stok UC'!$A:$A,\">=\"&TODAY(),'Log Stok UC'!$A:$A,\"<\"&(TODAY()+1))", 'rumus total harian: SUMIFS atas Qty (bersih) tanpa kriteria warna, tanpa produk terpisah (Motor)');
  cek(u.BU.peek(rm, 3).nf === '"Keluar "#,##0" unit";"Keluar -"#,##0" unit"' && u.BU.peek(rm + 1, 3).nf === '"Masuk "#,##0" unit";"Masuk -"#,##0" unit"', 'format total harian dua seksi (negatif tidak tampil "-Keluar")');
  cek(u.BU.peek(1, 4).v === u.ctx.__K.TEKS_BANNER_BARU && /B1/.test(u.BU.peek(1, 4).v), 'banner memuat petunjuk pembatalan');
  cek(u.BU.peek(4, A_IN).dv && /REGEXMATCH/.test(u.BU.peek(4, A_IN).dv.f) && /ketik B/.test(u.BU.peek(4, A_IN).dv.help) && !/REGEXMATCH/.test(u.BU.peek(4, A_STOK).dv.f), 'validasi IN/OUT memuat pola B + teks bantuan; STOK tanpa pola B');
  const sel1 = u.ctx.rumusTotalHarian_('Log Stok UC', 'IN');
  cek(sel1.indexOf('"IN"') > 0 && sel1.indexOf('$F:$F') < 0, 'total masuk: tanpa kriteria warna');
}

// ---------- fungsi agregasi rekap: bersih, pembatalan, opname, ditolak, waktu tak terbaca, masa depan
{
  const u = SEDIA_UC();
  const t = h => h + 0.5;
  const baris = [
    [t(100), 'S', 4, 'P', 'K', 'W', 'IN', 5, 10, 15, '', ''], [t(100), 'S', 4, 'P', 'K', 'W', 'OUT', 3, 15, 12, '', ''],
    [t(100), 'S', 4, 'P', 'K', 'W', 'OUT', -1, 12, 13, '', 'BATAL OUT'], [t(100), 'S', 4, 'P', 'K', 'W', 'IN', -2, 13, 11, '', 'BATAL IN'],
    [t(100), 'S', 4, 'P', 'K', 'W', 'KOREKSI', '', 11, 20, '', ''], [t(100), 'S', 4, 'P', 'K', 'W', 'KOREKSI', '', '', 7, '', ''],
    [t(100), 'S', 4, 'P', 'K', 'W', 'DITOLAK', 9, 11, 11, '', ''],
    [t(101), 'S', 4, 'P', 'K', 'W', 'OUT', 2, 11, 9, '', ''],
    [null, 'S', 4, 'P', 'K', 'W', 'OUT', 2, 11, 9, '', ''],              // waktu tak terbaca
    [t(100), 'S', 4, 'P', 'K', 'W', 'OUT', 'x', 11, 9, '', ''],          // Qty rusak
    [t(500), 'S', 4, 'P', 'K', 'W', 'OUT', 2, 11, 9, '', ''],            // masa depan (> sampai)
    [t(50), 'S', 4, 'P', 'K', 'W', 'OUT', 7, 11, 4, '', ''],             // lebih tua dari "dari"
  ];
  const a = u.ctx.agregasiBaris_(baris, 90, 200);
  const h = a.hari[100], h2 = a.hari[101];
  cek(h.masuk === 3 && h.keluar === 2 && h.entri === 2 && h.batalIN === 2 && h.batalOUT === 1 && h.opnameEntri === 2 && h.opnameSelisih === 9 && h.ditolak === 1, 'agregasi hari 100: ' + JSON.stringify(h));
  cek(h2.keluar === 2 && h2.entri === 1 && !a.hari[50] && !a.hari[500], 'agregasi: hari 101 benar; hari lebih tua dari "dari" dan masa depan tidak ikut');
  cek(a.info.tidakTerbaca === 1 && a.info.qtyRusak === 1 && a.info.masaDepan === 1 && a.info.dibaca === baris.length, 'agregasi: info tidak terbaca/qty rusak/masa depan: ' + JSON.stringify(a.info));
}

// ---------- rekap harian: alur nyata, idempoten, tidak pernah menurun otomatis, hari tanpa sumber dipertahankan, bangun ulang
{
  const u = SEDIA_UC();
  const cfg = u.kons().SISTEM[0];
  const rk = () => u.ss.getSheetByName('Rekap Harian UC');
  const hari0 = Math.floor(u.ctx.waktuSerial_(new Date()));
  const tabel = () => { const n = rk().getLastRow() - 1; return n > 0 ? rk().getRange(2, 1, n, 13).getValues().map(r => r.map((x, i) => (i === 0 || i === 10) && x instanceof Date ? (i === 0 ? Math.floor(u.ctx.waktuSerial_(x)) : 'W') : x)) : []; };
  cek(!!rk() && rk().getRange(1, 1, 1, 13).getValues()[0].join('|') === u.ctx.__K.HEADER_REKAP.join('|') && rk().frozenRows === 1, 'migrasi membuat sheet Rekap Harian UC dengan judul kolom');
  u.kirim(4, A_OUT, 3); u.kirim(4, A_OUT, 'B1'); u.kirim(4, A_IN, 4); u.kirim(5, A_OUT, 2);
  u.ctx.rekapHarianOtomatis();
  const t1 = tabel();
  cek(t1.length === 1, 'rekap: satu baris (hari ini)');
  const r = t1[0];
  cek(r[1] === 4 && r[2] === 4 && r[3] === 0 && r[4] === 3 && r[5] === 0 && r[6] === 1 && r[9] === 0 && r[11] === 'OK', 'rekap hari ini: Masuk 4, Keluar 3+2-1=4, Entri 3, Dibatalkan OUT 1: ' + JSON.stringify(r));
  cek(rk().peek(1, 1).bg === '#cfe2f3' && Number(rk().peek(2, 15).v) > hari0, 'rekap: header berwarna + O2 = waktu hitung terakhir');
  u.ctx.rekapHarianOtomatis();
  cek(JSON.stringify(tabel().map(x => x.slice(0, 10))) === JSON.stringify(t1.map(x => x.slice(0, 10))), 'rekap: jalan dua kali, hasil sama (idempoten)');
  // hari lama yang sumbernya tidak ada dipertahankan; baris manual (catatan) terbawa
  rk().insertRowsBefore(3, 1);
  rk().getRange(3, 1, 1, 13).setValues([[hari0 - 40, 9, 8, 1, 7, 0, 0, 0, 0, 0, hari0 - 40, 'OK', 'catatan saya']]);
  rk().getRange(2, 13).setValue('cek stok');
  u.ctx.rekapHarianOtomatis();
  const t2 = tabel();
  cek(t2.length === 2 && t2[1][1] === 9 && t2[1][12] === 'catatan saya' && t2[0][12] === 'cek stok', 'rekap: hari lama tanpa sumber dipertahankan; kolom Catatan terbawa per tanggal');
  cek(t2[0][0] === hari0 && t2[1][0] === hari0 - 40, 'rekap: kolom Tanggal = nomor hari WIB, terbaru di atas');
  // tidak pernah menurun otomatis (mis. Log sudah diarsipkan): Entri tersimpan lebih besar dari sumber
  rk().getRange(2, 5).setValue(99);
  u.ctx.rekapHarianOtomatis();
  const t3 = tabel();
  cek(t3[0][4] === 99 && /^SUMBER BERKURANG/.test(t3[0][11]), 'rekap otomatis tidak menurunkan angka tersimpan: Status SUMBER BERKURANG');
  // menu "Bangun ulang": boleh menurunkan
  u.ctx.__opsi.jawab = 'YES';
  u.ctx.bangunUlangRekap();
  const t4 = tabel();
  cek(t4[0][4] === 3 && t4[0][11] === 'OK' && /Rekap harian dibangun ulang|dibangun ulang/.test(u.ctx.__alerts.slice(-2).join('|')), 'Bangun ulang (paksa) menurunkan ke angka sumber, Status OK');
  // menu "Perbarui sekarang"
  u.ctx.perbaruiRekapSekarang();
  cek(/Rekap Harian UC: 1 hari ditulis/.test(u.ctx.__alerts.slice(-1)[0]) && /Rekap Harian STP: belum ada|Rekap Harian STP: 0 hari/.test(u.ctx.__alerts.slice(-1)[0]) === true, 'Perbarui sekarang: laporan per sheet (STP belum dimigrasi -> belum ada)');
  // tryLock skrip gagal -> galat (Executions berstatus Failed), tidak diam-diam
  u.ctx.__opsi.lockSkripGagal = true;
  let g = null; try { u.ctx.rekapHarianOtomatis(); } catch (e) { g = e; }
  u.ctx.__opsi.lockSkripGagal = false;
  cek(g && /Rekap lain sedang berjalan/.test(g.message), 'rekap harian: lock gagal dilempar sebagai galat');
  // Log terlalu besar -> berhenti dengan petunjuk, tanpa menulis
  const sebelum = JSON.stringify(tabel());
  u.kons().REKAP_BATAS_BARIS = 1;
  g = null; try { u.ctx.rekapHarianOtomatis(); } catch (e) { g = e; }
  u.kons().REKAP_BATAS_BARIS = 60000;
  cek(g && /terlalu besar/.test(g.message) && /TIDAK mengurangi/.test(g.message) && /REKAP_BATAS_BARIS/.test(g.message) && JSON.stringify(tabel()) === sebelum, 'rekap: Log terlalu besar -> galat jelas, tabel tidak berubah');
  // trigger tanpa sheet rekap (STP belum dimigrasi / rekap dihapus): lewati, tidak membuat sheet, tidak galat
  u.ss.deleteSheet(rk());
  u.ctx.rekapHarianOtomatis();
  cek(!u.ss.getSheetByName('Rekap Harian UC'), 'trigger rekap tidak membuat sheet yang hilang');
}

// ---------- rekap harian: tabel yang ada dirapikan tanpa sisa (tanggal ganda digabung, baris kosong dirapatkan)
{
  const u = SEDIA_UC();
  const rk = () => u.ss.getSheetByName('Rekap Harian UC');
  const hari0 = Math.floor(u.ctx.waktuSerial_(new Date()));
  u.kirim(4, A_OUT, 2);
  u.ctx.rekapHarianOtomatis();
  // tanggal ganda (salin-tempel staf): dua baris untuk hari yang sama, satu baris kosong di tengah, satu hari lama
  rk().insertRowsBefore(3, 3);
  rk().getRange(3, 1, 3, 13).setValues([[hari0, 0, 99, -99, 1, 0, 0, 0, 0, 0, hari0, 'OK', 'catatan ganda'], ['', '', '', '', '', '', '', '', '', '', '', '', ''], [hari0 - 9, 5, 4, 1, 3, 0, 0, 0, 0, 0, hari0 - 9, 'OK', '']]);
  u.ctx.rekapHarianOtomatis();
  const n = rk().getLastRow() - 1;
  const isi = rk().getRange(2, 1, n, 13).getValues();
  const nilaiA = isi.map(r => r[0] instanceof Date ? Math.floor(u.ctx.waktuSerial_(r[0])) : r[0]);
  cek(n === 2 && nilaiA[0] === hari0 && nilaiA[1] === hari0 - 9 && isi[0][2] === 2 && isi[1][1] === 5, 'rekap: tanggal ganda digabung (angka dari Log menang), baris kosong dirapatkan, tidak ada sisa di bawah: ' + JSON.stringify(nilaiA));
  cek(/catatan ganda/.test(isi[0][12]), 'rekap: catatan dari baris ganda digabung');
}

// ---------- aktifkan melengkapi instalasi 2 trigger (edit + penyapu) dengan rekap harian saja
{
  const c = siapkan(); c.ctx.migrasiStokUC();
  c.ctx.__triggers.push({ getHandlerFunction: () => 'prosesInputStok' }, { getHandlerFunction: () => 'sapuInputStok' });
  c.ctx.aktifkanInputOtomatis();
  const f = c.ctx.__triggers.map(t => t.getHandlerFunction()).sort().join();
  cek(f === 'prosesInputStok,rekapHarianOtomatis,sapuInputStok' && /Ditambahkan sekarang: rekap harian\./.test(c.ctx.__alerts.slice(-1)[0]), 'aktifkan: instalasi edit+penyapu hanya ditambah rekap harian, tanpa menggandakan: ' + f);
}

// ---------- rekap harian: sumber campuran (urutan acak, Date vs angka, arsip, duplikat, batas hari WIB, zona file lain, catch-up)
{
  const u = SEDIA_UC();
  const cfg = u.kons().SISTEM[0];
  const rk = () => u.ss.getSheetByName('Rekap Harian UC');
  const hari0 = Math.floor(u.ctx.waktuSerial_(new Date()));
  const baris = (w, jenis, q, k) => [w, 'Stok Cover UC', 4, 'Honda Brio', 'HND-BRI-UA-R-G1', 'Abu-abu', jenis, q, 10, 10, '', k || ''];
  const sebelumTengah = hari0 - 3 + 0.9999, sesudahTengah = hari0 - 2 + 1e-4;   // 23:59:50 hari D dan 00:00:08 hari D+1 (WIB)
  const rows = [baris(sesudahTengah, 'OUT', 4), baris(sebelumTengah, 'OUT', 5), baris(hari0 - 3 + 0.5, 'IN', 9), baris(hari0 - 2 + 0.2, 'OUT', 1), baris(hari0 - 3 + 0.3, 'OUT', -1, 'BATAL OUT')];
  const tulis = rs => { rs.forEach(x => u.ctx.tulisLog_(u.ss, cfg, [x])); };
  tulis(rows);
  // Log DIACAK manual (tidak terurut) + baris teks: hasil harus sama
  u.ctx.rekapHarianOtomatis();
  const tabelNilai = () => { const n = rk().getLastRow() - 1; return n > 0 ? rk().getRange(2, 1, n, 13).getValues().map(r => r.slice(1, 7)) : []; };
  const acuan = JSON.stringify(tabelNilai());
  // hari D+1 (hari0-2): OUT 4 (00:00:08) + OUT 1; hari D (hari0-3): OUT 5 (23:59:50) - 1 (batal) = 4, IN 9
  cek(acuan === JSON.stringify([[0, 5, -5, 2, 0, 0], [9, 4, 5, 2, 0, 1]]), 'rekap campuran: dua hari, batas tengah malam WIB benar, pembatalan bersih: ' + acuan);
  const LG = u.LG();
  const n = LG.getLastRow() - 1;
  const isi = LG.getRange(2, 1, n, 12).getValues(); // Date di kolom A
  const ac = isi.slice().reverse();
  LG.getRange(2, 1, n, 12).setValues(ac.map(r => { const c = r.slice(); if (c[0] instanceof Date) c[0] = u.ctx.waktuSerial_(c[0]); return c; }));
  rk().getRange(2, 1, rk().getLastRow() - 1, 13).clearContent();
  u.ctx.rekapHarianOtomatis();
  cek(JSON.stringify(tabelNilai()) === acuan, 'rekap: Log diurutkan terbalik -> hasil sama dengan Log terurut');
  // zona file lain (jalur lambat)
  rk().getRange(2, 1, rk().getLastRow() - 1, 13).clearContent();
  u.ss.tz = 'America/Los_Angeles';
  u.ctx.perbaruiRekapSatu_(u.ss, cfg, { semua: true, paksa: false });
  u.ss.tz = 'Asia/Jakarta';
  cek(JSON.stringify(tabelNilai()) === acuan, 'rekap: zona file bukan WIB (jalur lambat) -> hasil sama');
  // arsip: pindahkan baris bulan lalu; rekap bangun ulang dari Log + arsip, dan duplikat (arsip terhenti sebelum hapus) dihitung sekali
  rk().getRange(2, 1, rk().getLastRow() - 1, 13).clearContent();
  const arsip = u.ss.insertSheet('Arsip Log Stok UC 2026-01');
  arsip.getRange(1, 1, 1, 12).setValues([u.ctx.__K.HEADER_LOG]);
  const lamaHari = hari0 - 200;
  arsip.getRange(2, 1, 2, 12).setValues([baris(lamaHari + 0.4, 'OUT', 6), baris(lamaHari + 0.1, 'IN', 2)]);
  arsip.getRange(2, 1, 2, 1).setNumberFormat('dd/MM/yyyy HH:mm:ss');
  // duplikat: salin salah satu baris arsip ke Log juga
  u.ctx.tulisLog_(u.ss, cfg, [baris(lamaHari + 0.4, 'OUT', 6)]);
  u.ctx.perbaruiRekapSatu_(u.ss, cfg, { semua: true, paksa: false });
  const tb = rk().getRange(2, 1, rk().getLastRow() - 1, 13).getValues();
  const hariLama = tb.find(r => r[2] === 6 && r[1] === 2);
  cek(!!hariLama && tb.length === 3 && hariLama[4] === 2, 'rekap penuh: arsip ikut dibaca; baris duplikat Log+arsip dihitung sekali (Keluar 6 bukan 12, Entri 2)');
  // nama arsip yang menyerupai tidak ikut
  const mirip = u.ss.insertSheet('Arsip Log Stok UC 2026-01 salinan');
  mirip.getRange(1, 1, 1, 12).setValues([u.ctx.__K.HEADER_LOG]);
  mirip.getRange(2, 1, 1, 12).setValues([baris(lamaHari - 5 + 0.4, 'OUT', 77)]);
  u.ctx.perbaruiRekapSatu_(u.ss, cfg, { semua: true, paksa: false });
  cek(!rk().getRange(2, 1, rk().getLastRow() - 1, 13).getValues().some(r => r[2] === 77), 'rekap: sheet yang namanya hanya mirip arsip diabaikan');
  // catch-up: tabel berhenti jauh di belakang -> jendela melebar sampai hari tersimpan terakhir - 1
  rk().getRange(2, 1, rk().getLastRow() - 1, 13).clearContent();
  rk().getRange(2, 1, 1, 13).setValues([[hari0 - 6, 1, 1, 0, 1, 0, 0, 0, 0, 0, hari0 - 6, 'OK', '']]);
  rk().getRange(2, 1, 1, 1).setNumberFormat('dd/MM/yyyy');
  u.ctx.tulisLog_(u.ss, cfg, [baris(hari0 - 5 + 0.5, 'OUT', 8)]);
  u.ctx.rekapHarianOtomatis();
  cek(rk().getRange(2, 1, rk().getLastRow() - 1, 13).getValues().some(r => r[2] === 8), 'rekap otomatis: hari terlewat (trigger bolong) ikut dihitung (catch-up)');
}

// ---------- rekap: hari yang sudah pindah ke arsip sebelum dihitung final tetap benar; peringatan baris rusak; kolom status terhapus
{
  const u = SEDIA_UC();
  const cfg = u.kons().SISTEM[0];
  const rk = () => u.ss.getSheetByName('Rekap Harian UC');
  const hari0 = Math.floor(u.ctx.waktuSerial_(new Date()));
  const baris = (w, jenis, q) => [w, 'Stok Cover UC', 4, 'Honda Brio', 'HND-BRI-UA-R-G1', 'Abu-abu', jenis, q, 10, 10, '', ''];
  const tabel = () => rk().getRange(2, 1, Math.max(1, rk().getLastRow() - 1), 13).getValues().filter(r => r[0] !== '');
  // tabel menyimpan hari-1 baru sebagian (Keluar 1, Entri 1); sisa harinya (OUT 40, 8 entri) hanya ada di arsip bulan yang sama
  const bulan = u.ctx.bulanDariNomor_(hari0 - 1);
  const arsip = u.ss.insertSheet('Arsip Log Stok UC ' + bulan);
  arsip.getRange(1, 1, 1, 12).setValues([u.ctx.__K.HEADER_LOG]);
  const isiArsip = []; for (let i = 0; i < 8; i++) isiArsip.push(baris(hari0 - 1 + 0.1 + i * 0.05, 'OUT', 5));
  arsip.getRange(2, 1, 8, 12).setValues(isiArsip);
  rk().getRange(2, 1, 1, 13).setValues([[hari0 - 1, 0, 1, -1, 1, 0, 0, 0, 0, 0, hari0 - 1, 'OK', '']]);
  rk().getRange(2, 1, 1, 1).setNumberFormat('dd/MM/yyyy');
  u.ctx.tulisLog_(u.ss, cfg, [baris(hari0 + 0.01, 'OUT', 2)]);
  u.ctx.rekapHarianOtomatis();
  const t = tabel();
  const kemarin = t.find(r => Math.floor(u.ctx.waktuSerial_(r[0])) === hari0 - 1 || r[0] === hari0 - 1);
  cek(!!kemarin && kemarin[2] === 40 && kemarin[4] === 8, 'rekap malam: hari yang sudah pindah ke arsip tetap dihitung penuh (Keluar 40, Entri 8): ' + JSON.stringify(kemarin));
  // baris rusak: Waktu teks + Qty kosong -> peringatan di O3 (jalur malam), tidak ada hari nol palsu
  u.ctx.tulisLog_(u.ss, cfg, [baris(hari0 - 3 + 0.5, 'OUT', ''), baris('21/10/2026 14:03:11', 'OUT', 100)]);
  u.ctx.rekapHarianOtomatis();
  const o3 = String(rk().getRange(2, 15, 2, 1).getValues()[1][0]);
  cek(/^PERIKSA/.test(o3) && /Waktu tak terbaca/.test(o3) && /Qty bukan angka/.test(o3), 'rekap malam: peringatan baris rusak tersimpan di O3: ' + o3);
  cek(!tabel().some(r => (r[0] === hari0 - 3 || Math.floor(u.ctx.waktuSerial_(r[0])) === hari0 - 3) && r[4] === 0 && r[1] === 0 && r[2] === 0), 'rekap: hari yang hanya berisi Qty rusak tidak tampil sebagai baris nol "OK"');
  u.ctx.cekStatus();
  cek(/PERIKSA: .*Waktu tak terbaca/.test(u.ctx.__alerts.slice(-1)[0]), 'cekStatus menampilkan peringatan rekap');
  // bersih lagi -> O3 kosong
  const LG = u.LG(); const nLog = LG.getLastRow() - 1;
  const semua = LG.getRange(2, 1, nLog, 12).getValues().filter(r => !(r[7] === '' || r[3] === 'Honda Brio' && r[7] === 100));
  LG.getRange(2, 1, nLog, 12).clearContent();
  LG.getRange(2, 1, semua.length, 12).setValues(semua);
  u.ctx.rekapHarianOtomatis();
  cek(String(rk().getRange(3, 15).getValue()) === '' || /^PERIKSA/.test(String(rk().getRange(3, 15).getValue())), 'O3 diperbarui tiap hitung');
  // kolom status terhapus: cekStatus tetap tampil, malam tetap jalan
  rk().getRange(1, 14, 3, 2).clearContent(); rk().maxCols = 13;   // staf menghapus kolom N dst.
  let galat = null; try { u.ctx.cekStatus(); } catch (e) { galat = e; }
  cek(!galat && /Rekap Harian UC/.test(u.ctx.__alerts.slice(-1)[0]), 'cekStatus tidak galat bila kolom status rekap terhapus: ' + (galat && galat.message));
  galat = null; try { u.ctx.rekapHarianOtomatis(); } catch (e) { galat = e; }
  cek(!galat, 'rekap malam tetap jalan bila kolom status terhapus: ' + (galat && galat.message));
}

// ---------- rekap: tabel kosong + sheet tanpa kolom status → malam tetap bisa menulis; batas baris jalur malam 3x lebih longgar
{
  const u = SEDIA_UC();
  const rk = u.ss.getSheetByName('Rekap Harian UC');
  rk.maxCols = 13;
  let galat = null; try { u.ctx.rekapHarianOtomatis(); } catch (e) { galat = e; }
  cek(!galat && rk.maxCols >= 15, 'rekap malam pada tabel kosong dan sheet tanpa kolom status: kolom ditambah, tidak galat: ' + (galat && galat.message));
  const hari0 = Math.floor(u.ctx.waktuSerial_(new Date()));
  const cfg = u.kons().SISTEM[0];
  for (let i = 0; i < 6; i++) u.ctx.tulisLog_(u.ss, cfg, [[hari0 + 0.01 * (i + 1), 'Stok Cover UC', 4, 'Honda Brio', 'X', 'Abu-abu', 'OUT', 1, 10, 9, '', '']]);
  rk.getRange(2, 1, 1, 13).setValues([[hari0 - 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, hari0 - 1, 'OK', '']]);   // tabel berisi → jalur malam (jendela)
  u.kons().REKAP_BATAS_BARIS = 2;   // 6 baris: lewat batas penuh (2) tetapi di bawah batas jalur malam (6)
  galat = null; try { u.ctx.rekapHarianOtomatis(); } catch (e) { galat = e; }
  let galatPenuh = null; try { u.ctx.perbaruiRekapSatu_(u.ss, cfg, { semua: true, paksa: false }); } catch (e) { galatPenuh = e; }
  u.kons().REKAP_BATAS_BARIS = 60000;
  cek(!galat && !!galatPenuh && /terlalu besar/.test(galatPenuh.message), 'batas baris: jalur malam longgar (3x), jalur penuh tetap ketat');
}

// ---------- total di kolom C: Keluar/Masuk hari ini + kemarin (tanpa Motor) + 4 baris Motor sendiri; menu 4 melengkapi dan membersihkan rumus lama
{
  const u = SEDIA_UC();
  const peta = u.ctx.bacaPeta_(u.BU), rm = peta.barisTotal + 1;
  const f = i => u.BU.getRange(rm + i, 3).getFormula();
  const log = "'Log Stok UC'!";
  cek(/^=SUMIFS\('Log Stok UC'!\$H:\$H,.*"OUT".*"<>Motor".*">="&TODAY\(\),.*"<"&\(TODAY\(\)\+1\)\)$/.test(f(0)), 'C(mutasi): Keluar hari ini (tanpa Motor)');
  cek(/"IN".*"<>Motor".*">="&TODAY\(\)/.test(f(1)), 'C(mutasi+1): Masuk hari ini (tanpa Motor)');
  cek(/"OUT".*"<>Motor".*">="&\(TODAY\(\)-1\),.*"<"&TODAY\(\)\)$/.test(f(2)), 'C(mutasi+2): Keluar kemarin [TODAY()-1, TODAY())');
  cek(/"IN".*"<>Motor".*">="&\(TODAY\(\)-1\),.*"<"&TODAY\(\)\)$/.test(f(3)), 'C(mutasi+3): Masuk kemarin [TODAY()-1, TODAY())');
  cek(/"OUT".*\$D:\$D,"Motor".*">="&TODAY\(\),.*"<"&\(TODAY\(\)\+1\)\)$/.test(f(4)) && f(4).indexOf('<>') < 0, 'C(mutasi+4): Motor keluar hari ini (hanya Motor)');
  cek(/"IN".*\$D:\$D,"Motor".*">="&TODAY\(\)/.test(f(5)) && /"OUT".*"Motor".*TODAY\(\)-1/.test(f(6)) && /"IN".*"Motor".*TODAY\(\)-1/.test(f(7)), 'C(mutasi+5..7): Motor masuk hari ini, keluar kemarin, masuk kemarin');
  cek(f(8) === '', 'tidak ada baris lagi di bawah Motor masuk kemarin');
  cek([0, 1, 2, 3, 4, 5, 6, 7].every(i => f(i).indexOf(log) > 0) && /Keluar kemarin/.test(u.BU.peek(rm + 2, 3).nf) && /Masuk kemarin/.test(u.BU.peek(rm + 3, 3).nf) && /Motor keluar /.test(u.BU.peek(rm + 4, 3).nf) && /Motor masuk kemarin/.test(u.BU.peek(rm + 7, 3).nf), 'semua rumus merujuk Log sheet ini; format menyebut periode dan Motor');
  cek(u.BU.getColumnWidth(3) >= 170, 'kolom C cukup lebar untuk teks periode');
  // sheet versi sebelumnya: rumus lama di bawah rencana (mis. 7 hari / bulan ini) dihapus; rumus/isian staf tidak disentuh
  const q = "'Log Stok UC'!";
  u.BU.getRange(rm + 8, 3).setFormulas([['=SUMIFS(' + q + '$H:$H,' + q + '$G:$G,"OUT",' + q + '$A:$A,">="&(TODAY()-6),' + q + '$A:$A,"<"&(TODAY()+1))']]);
  u.BU.getRange(rm + 9, 3).setFormulas([['=TODAY()-6']]);
  u.BU.setColumnWidth(3, 130);
  u.ctx.perbaruiSheetLama();
  const lap = u.ctx.__alerts.slice(-1)[0];
  cek(/C\d+ \(rumus lama dihapus\)/.test(lap) && f(8) === '' && u.BU.getRange(rm + 9, 3).getFormula() === '=TODAY()-6', 'menu 4: rumus lama milik script dihapus, rumus staf utuh');
  u.BU.getRange(rm + 9, 3).clearContent();
  u.BU.getRange(rm + 2, 3).clearContent(); u.BU.getRange(rm + 2, 3).setValue('catatan staf 2');
  u.ctx.perbaruiSheetLama();
  cek(u.BU.getRange(rm + 2, 3).getValue() === 'catatan staf 2' && /sel C\d+ berisi sesuatu yang bukan rumus total harian; TIDAK ditimpa/.test(u.ctx.__alerts.slice(-1)[0]) && u.BU.getColumnWidth(3) >= 170, 'menu 4: sel asing TIDAK ditimpa; kolom C dilebarkan');
  // produk terpisah dimatikan: tidak ada pengecualian di total utama; baris Motor milik script dibersihkan oleh menu 4
  u.kons().PRODUK_TERPISAH = { label: 'Motor', nama: [] };
  cek(u.ctx.rumusTotalHarian_('Log Stok UC', 'OUT') === "=SUMIFS('Log Stok UC'!$H:$H,'Log Stok UC'!$G:$G,\"OUT\",'Log Stok UC'!$A:$A,\">=\"&TODAY(),'Log Stok UC'!$A:$A,\"<\"&(TODAY()+1))" && u.ctx.totalHarian_().length === 4, 'PRODUK_TERPISAH.nama = []: total utama memuat semua produk, 4 baris');
  u.BU.getRange(rm + 2, 3).clearContent();
  u.ctx.perbaruiSheetLama();
  cek(f(4) === '' && f(7) === '' && /rumus lama dihapus/.test(u.ctx.__alerts.slice(-1)[0]), 'menu 4 saat dimatikan: baris Motor milik script dibersihkan');
  u.kons().PRODUK_TERPISAH = { label: 'Motor', nama: ['Mo~to*r?"x'] };
  cek(u.ctx.rumusTotalHarian_('Log Stok UC', 'OUT').indexOf('"<>Mo~~to~*r~?""x"') > 0, 'karakter khusus kriteria SUMIFS (~ * ? ") di-escape');
}

// ---------- produk terpisah (Motor): total utama dan Rekap utama TANPA Motor; Motor punya kolom Q:R sendiri di Rekap
{
  const u = SEDIA_UC();
  const cfg = u.kons().SISTEM[0];
  const hari0 = Math.floor(u.ctx.waktuSerial_(new Date()));
  const baris = (w, produk, jenis, q) => [w, 'Stok Cover UC', 4, produk, 'X', 'Abu-abu', jenis, q, 10, 10, '', ''];
  const a = u.ctx.agregasiBaris_([baris(hari0 + 0.1, 'Honda Brio', 'OUT', 5), baris(hari0 + 0.2, 'Motor', 'OUT', 3), baris(hari0 + 0.3, 'motor', 'IN', 4),
    baris(hari0 + 0.4, 'Motor', 'OUT', -1), baris(hari0 + 0.5, 'Honda Brio', 'IN', 2), baris(hari0 + 0.6, 'Motor Matic', 'OUT', 7)], null, hari0).hari[hari0];
  cek(a.keluar === 12 && a.masuk === 2 && a.terpisahKeluar === 2 && a.terpisahMasuk === 4, 'agregasi: Motor (huruf besar/kecil diabaikan, pembatalan bersih) terpisah; "Motor Matic" tetap produk biasa: ' + JSON.stringify(a));
  cek(a.entri === 5 && a.batalOUT === 0, 'agregasi: Entri menghitung semua produk; pembatalan Motor tidak masuk Dibatalkan (unit) utama: ' + a.entri + '/' + a.batalOUT);
  // rekap tertulis: Q1:R1 berjudul Motor (sheet baru), nilai di Q:R, utama tanpa Motor
  const rk = u.ss.getSheetByName('Rekap Harian UC');
  cek(rk.getRange(1, 17, 1, 2).getValues()[0].join('|') === 'Masuk motor (unit)|Keluar motor (unit)', 'sheet Rekap baru: judul kolom Q:R untuk Motor');
  u.ctx.tulisLog_(u.ss, cfg, [baris(hari0 + 0.1, 'Honda Brio', 'OUT', 5), baris(hari0 + 0.2, 'Motor', 'OUT', 3), baris(hari0 + 0.3, 'Motor', 'IN', 4)]);
  u.ctx.perbaruiRekapSatu_(u.ss, cfg, { semua: true, paksa: false });
  const r2 = rk.getRange(2, 1, 1, 18).getValues()[0];
  cek(r2[1] === 0 && r2[2] === 5 && r2[16] === 4 && r2[17] === 3, 'rekap: Masuk/Keluar utama tanpa Motor (0/5); Q:R = Motor masuk/keluar (4/3): ' + JSON.stringify([r2[1], r2[2], r2[16], r2[17]]));
  // sumber berkurang: baris lama dipertahankan UTUH termasuk kolom Motor
  rk.getRange(2, 5).setValue(99);
  u.ctx.perbaruiRekapSatu_(u.ss, cfg, { semua: true, paksa: false });
  const r3 = rk.getRange(2, 1, 1, 18).getValues()[0];
  cek(/SUMBER BERKURANG/.test(r3[11]) && r3[16] === 4 && r3[17] === 3, 'rekap: hari "sumber berkurang" dipertahankan, kolom Motor ikut utuh');
  // sheet rekap lama tanpa kolom Q:R (sebelum fitur ini): menu nightly TIDAK menulis Q:R; menu 4 memasang judul lalu mengisi
  rk.getRange(2, 5).setValue(1);   // kembali ke jumlah entri yang wajar (bukan sumber berkurang)
  rk.getRange(1, 17, 1, 2).clearContent(); rk.getRange(2, 17, 1, 2).clearContent(); rk.maxCols = 15;
  u.ctx.rekapHarianOtomatis();
  cek(rk.maxCols === 15 && rk.getRange(2, 1, 1, 13).getValues()[0][0] !== '', 'rekap lama tanpa kolom Q:R: trigger malam tetap jalan, tidak menambah/menulis kolom Motor');
  u.ctx.perbaruiSheetLama();
  const r4 = rk.getRange(2, 1, 1, 18).getValues()[0];
  cek(rk.getRange(1, 17, 1, 2).getValues()[0].join('|') === 'Masuk motor (unit)|Keluar motor (unit)' && r4[16] === 4 && r4[17] === 3, 'menu 4: judul Q:R dipasang dan Motor terisi dari riwayat Log');
  // isian lain di Q1:R1: tidak ditimpa
  rk.getRange(1, 17, 1, 2).setValues([['punya staf', 'x']]);
  rk.getRange(2, 17, 1, 2).setValues([['a', 'b']]);
  u.ctx.rekapHarianOtomatis();
  u.ctx.perbaruiSheetLama();
  cek(rk.getRange(1, 17).getValue() === 'punya staf' && rk.getRange(2, 17).getValue() === 'a' && /kolom Q:R .* berisi hal lain/.test(u.ctx.__alerts.slice(-1)[0]), 'isian staf di Q:R tidak ditimpa; dilaporkan');
  // tabel menyusut (tanggal ganda digabung): sisa di Q:R ikut dibersihkan
  const u2 = SEDIA_UC();
  const rk2 = u2.ss.getSheetByName('Rekap Harian UC');
  const cfg2 = u2.kons().SISTEM[0];
  u2.ctx.tulisLog_(u2.ss, cfg2, [baris(hari0 + 0.1, 'Honda Brio', 'OUT', 5)]);
  u2.ctx.perbaruiRekapSatu_(u2.ss, cfg2, { semua: true, paksa: false });
  rk2.getRange(3, 1, 1, 13).setValues([[hari0, 0, 1, -1, 0, 0, 0, 0, 0, 0, hari0, 'OK', '']]); rk2.getRange(3, 1).setNumberFormat('dd/MM/yyyy');
  rk2.getRange(3, 17, 1, 2).setValues([[77, 88]]);
  u2.ctx.perbaruiRekapSatu_(u2.ss, cfg2, { semua: true, paksa: false });
  cek(rk2.getRange(3, 1).getValue() === '' && rk2.getRange(3, 17, 1, 2).getValues()[0].join('') === '', 'tabel menyusut: sisa kolom Motor (Q:R) dibersihkan');
  // dimatikan: Rekap tanpa kolom Motor, Masuk/Keluar utama memuat semua
  u.kons().PRODUK_TERPISAH = { label: 'Motor', nama: [] };
  const b = u.ctx.agregasiBaris_([baris(hari0 + 0.2, 'Motor', 'OUT', 3)], null, hari0).hari[hari0];
  cek(b.keluar === 3 && b.terpisahKeluar === 0, 'nama [] : Motor dihitung seperti produk lain');
}

// ---------- petunjuk B hanya pada isian yang mirip usaha membatalkan; validasi: galat layanan tidak menghapus validasi lama
{
  const u = SEDIA_UC();
  const tolak = v => { u.kirim(4, A_OUT, v); return u.sel(4, A_OUT).note; };
  cek(/Ketik B \+ jumlah/.test(tolak(-1)) || /ketik B \+ jumlah/i.test(u.sel(4, A_OUT).note), 'isian minus: petunjuk B ditampilkan');
  u.kirim(4, A_OUT, ''); 
  cek(!/B \+ jumlah/.test(tolak('2pcs')) && /belum tercatat/.test(u.sel(4, A_OUT).note), 'isian teks biasa: tanpa petunjuk B, "belum tercatat"');
  u.kirim(4, A_OUT, '');
  cek(!/B \+ jumlah/.test(tolak('1,5')) && /belum tercatat/.test(u.sel(4, A_OUT).note), 'isian desimal: tanpa petunjuk B');
  u.kirim(4, A_OUT, '');
  cek(/B \+ jumlah/.test(tolak('B0')), 'B0: petunjuk B ditampilkan');
  u.kirim(4, A_OUT, '');
  // flag mati: pesan lama persis
  u.kons().IZINKAN_PEMBATALAN = false;
  cek(tolak('2pcs') === 'Isi angka bulat 1–9999.', 'flag mati: pesan lama tidak berubah: ' + u.sel(4, A_OUT).note);
  u.kons().IZINKAN_PEMBATALAN = true;
  // pasangValidasi_: galat layanan -> 'sementara', validasi lama dibiarkan
  const rg = u.BU.getRange(4, A_IN, 5, 2);
  rg.setDataValidation(u.ctx.SpreadsheetApp.newDataValidation().requireNumberBetween(1, 9999).build());
  const RgProto = Object.getPrototypeOf(rg);
  const asli = RgProto.setDataValidation;
  RgProto.setDataValidation = function () { throw new Error('Service Spreadsheets timed out'); };
  const hasil = u.ctx.pasangValidasi_(rg, 'E4', 'inout');
  RgProto.setDataValidation = asli;
  cek(hasil === 'sementara' && !!u.BU.peek(4, A_IN).dv, 'galat layanan: dilaporkan sementara, validasi lama TIDAK dihapus (' + hasil + ')');
}

// ---------- menu 4: naikkan versi sheet yang sudah dimigrasi (tanpa migrasi ulang)
{
  const keKeadaLama = u => {
    const peta = u.ctx.bacaPeta_(u.BU);
    const rm = peta.barisTotal + 1;
    u.BU.getRange(rm, 3, 2, 1).clearContent(); u.BU.getRange(rm, 3, 2, 1).setNumberFormat(null);
    u.BU.getRange(1, 4).setValue(u.ctx.__K.TEKS_BANNER_LAMA);
    Object.keys(peta.kolom).forEach(c => {
      if (peta.kolom[c].jenis === 'STOK') return;
      for (let r = 4; r < peta.barisTotal - 1; r++) { const x = u.BU.cell(r, Number(c)); x.dv = { f: '=AND(ISNUMBER(' + 'X' + '),X>0)', invalid: false, help: 'lama' }; }
    });
    u.ss.deleteSheet(u.ss.getSheetByName('Rekap Harian UC'));
    return rm;
  };
  const cuplik = u => {
    const peta = u.ctx.bacaPeta_(u.BU), rm = peta.barisTotal + 1;
    const rk = u.ss.getSheetByName('Rekap Harian UC');
    return JSON.stringify([u.BU.peek(rm, 3).f, u.BU.peek(rm + 1, 3).f, u.BU.peek(rm, 3).nf, u.BU.peek(1, 4).v, u.BU.peek(4, A_IN).dv && u.BU.peek(4, A_IN).dv.f, u.BU.peek(4, A_OUT).dv && u.BU.peek(4, A_OUT).dv.f,
      u.BU.peek(peta.barisTotal - 2, A_IN).dv && u.BU.peek(peta.barisTotal - 2, A_IN).dv.f, !!rk, rk && rk.getLastRow()]);
  };
  const u = SEDIA_UC();
  const baru = cuplik(u);
  u.kirim(4, A_OUT, 3);                                  // ada log sebelum menu 4: riwayat ikut terbangun
  const rm = keKeadaLama(u);
  cek(cuplik(u) !== baru && !u.BU.peek(rm, 3).f && u.BU.peek(1, 4).v === u.ctx.__K.TEKS_BANNER_LAMA && !u.ss.getSheetByName('Rekap Harian UC'), 'menu 4 (setup): keadaan lama dibuat ulang (tanpa total harian, banner lama, tanpa rekap)');
  const stokSebelum = [u.st(4, A_STOK), u.st(4, H_STOK)];
  u.ctx.__opsi.jawab = 'YES';
  u.ctx.perbaruiSheetLama();
  const lapor = u.ctx.__alerts.slice(-1)[0];
  const sesudah = cuplik(u);
  cek(u.BU.peek(rm, 3).f === u.ctx.rumusTotalHarian_('Log Stok UC', 'OUT') && u.BU.peek(rm + 1, 3).f === u.ctx.rumusTotalHarian_('Log Stok UC', 'IN'), 'menu 4: total harian ditulis di baris yang ditemukan lewat label');
  cek(u.BU.peek(1, 4).v === u.ctx.__K.TEKS_BANNER_BARU && /REGEXMATCH/.test(u.BU.peek(4, A_IN).dv.f) && /REGEXMATCH/.test(u.BU.peek(4, A_OUT).dv.f), 'menu 4: banner dan validasi IN/OUT diperbarui');
  cek(!!u.ss.getSheetByName('Rekap Harian UC') && u.ss.getSheetByName('Rekap Harian UC').getLastRow() === 2, 'menu 4: sheet Rekap Harian dibuat dan riwayat dari Log terisi (1 hari)');
  cek(/validasi IN\/OUT diperbarui di 16 dari 16 warna/.test(lapor) && new RegExp('total harian C' + rm + ' \\(Keluar\\), C' + (rm + 1) + ' \\(Masuk\\)').test(lapor) && /banner diperbarui/.test(lapor) && /Rekap Harian UC: 1 hari ditulis/.test(lapor) && !/GAGAL/.test(lapor), 'menu 4: laporan per langkah: ' + lapor.replace(/\n/g, ' / ').slice(0, 500));
  cek(/"Stok Cover STP": belum berformat STOK\/IN\/OUT/.test(lapor), 'menu 4: STP yang belum dimigrasi dilewati tanpa galat');
  cek(u.st(4, A_STOK) === stokSebelum[0] && u.st(4, H_STOK) === stokSebelum[1] && u.nLog() === 1, 'menu 4: STOK dan Log tidak berubah');
  // hasil sama dengan migrasi baru (cuplikan sel) dan idempoten
  const ringkas = x => JSON.stringify(JSON.parse(x).slice(0, 8));
  cek(ringkas(sesudah) === ringkas(baru), 'menu 4: hasil sama dengan migrasi baru (rumus total harian, format, banner, validasi IN/OUT, sheet rekap ada)');
  const sebelumUlang = cuplik(u);
  u.ctx.perbaruiSheetLama();
  cek(cuplik(u) === sebelumUlang && !/GAGAL/.test(u.ctx.__alerts.slice(-1)[0]), 'menu 4: dijalankan dua kali -> hasil sama (idempoten)');
  // trigger rekap belum terpasang -> diingatkan
  u.ctx.matikanInputOtomatis();
  u.ctx.perbaruiSheetLama();
  cek(/Trigger rekap harian BELUM terpasang/.test(u.ctx.__alerts.slice(-1)[0]), 'menu 4: mengingatkan trigger rekap harian bila belum ada');
}

// ---------- menu 4: pengaman (akun non-pemilik, sel terisi, produk bertambah, label hilang, validasi ditolak Google)
{
  const SIAP = () => { const u = SEDIA_UC(); u.ctx.__opsi.jawab = 'YES'; return u; };
  const peta0 = u => u.ctx.bacaPeta_(u.BU);
  // akun tanpa hak edit: tidak ada yang berubah
  { const u = SIAP(); const rm = peta0(u).barisTotal + 1;
    u.BU.getRange(rm, 3, 2, 1).clearContent();
    u.BU.protections.push(Object.assign(new (Object.getPrototypeOf(u.BU.protect()).constructor)(), { bolehEdit: false }));
    u.ctx.perbaruiSheetLama();
    cek(!u.BU.peek(rm, 3).f && /DILEWATI. Sheet dikunci/.test(u.ctx.__alerts.slice(-1)[0]), 'menu 4: sheet dikunci + bukan pemilik -> dilewati, tidak ada perubahan'); }
  // sel target berisi sesuatu: tidak ditimpa, sel lain tetap diproses
  { const u = SIAP(); const rm = peta0(u).barisTotal + 1;
    u.BU.getRange(rm, 3).clearContent(); u.BU.getRange(rm, 3).setValue('catatan staf'); u.BU.getRange(rm + 1, 3).clearContent();
    u.ctx.perbaruiSheetLama();
    cek(u.BU.peek(rm, 3).v === 'catatan staf' && !u.BU.peek(rm, 3).f && u.BU.peek(rm + 1, 3).f === u.ctx.rumusTotalHarian_('Log Stok UC', 'IN') && new RegExp('sel C' + rm + ' berisi sesuatu').test(u.ctx.__alerts.slice(-1)[0]),
      'menu 4: sel C berisi teks tidak ditimpa dan dilaporkan; sel di bawahnya tetap diisi'); }
  // produk bertambah (baris disisip di atas TOTAL): total harian di baris label, kolom SKU produk tidak tertimpa
  { const u = SIAP(); const p = peta0(u);
    const kosong = p.barisTotal - 1;
    u.BU.insertRowsBefore(kosong, 3);
    for (let i = 0; i < 3; i++) { u.BU.cell(kosong + i, 2).v = 'Produk Baru ' + i; u.BU.cell(kosong + i, 3).v = 'SKU-BARU-' + i; }
    const p2 = peta0(u);
    cek(p2.barisTotal === p.barisTotal + 3 && p2.labelAda, 'setup: 3 produk disisip, TOTAL STOK bergeser 3 baris');
    u.ctx.perbaruiSheetLama();
    const rm2 = p2.barisTotal + 1;
    cek(u.BU.peek(rm2, 3).f === u.ctx.rumusTotalHarian_('Log Stok UC', 'OUT') && u.BU.peek(kosong, 3).v === 'SKU-BARU-0' && !u.BU.peek(kosong, 3).f && u.BU.peek(p2.barisTotal, 3).f !== u.ctx.rumusTotalHarian_('Log Stok UC', 'OUT'),
      'menu 4: total harian di baris berlabel (bukan alamat tetap); kolom SKU produk baru tidak tertimpa'); }
  // label hilang
  { const u = SIAP(); const p = peta0(u); u.BU.getRange(p.barisTotal, 2).setValue('');
    u.ctx.perbaruiSheetLama();
    cek(/label "TOTAL STOK" di kolom B tidak ditemukan, dilewati/.test(u.ctx.__alerts.slice(-1)[0]), 'menu 4: label TOTAL STOK hilang -> dilewati'); }
  // semua rumus validasi ditolak Google: validasi IN/OUT dikosongkan (B1 harus bisa diketik), STOK tidak disentuh, dilaporkan
  { const u = SIAP(); u.ctx.__opsi.tolakValidasi = { di: 'apply', formula: () => true, rentang: true };
    u.ctx.perbaruiSheetLama();
    cek(!u.BU.peek(4, A_IN).dv && !u.BU.peek(4, A_OUT).dv && u.BU.peek(4, A_STOK).dv && /validasi IN\/OUT diperbarui di 0 dari 16 warna/.test(u.ctx.__alerts.slice(-1)[0]) && /DITOLAK Google/.test(u.ctx.__alerts.slice(-1)[0]),
      'menu 4: Google menolak semua aturan -> validasi IN/OUT lama dikosongkan dan dilaporkan'); }
  // banner D1 yang sudah diubah manual tidak ditimpa
  { const u = SIAP(); u.BU.getRange(1, 4).setValue('Banner buatan sendiri');
    u.ctx.perbaruiSheetLama();
    cek(u.BU.peek(1, 4).v === 'Banner buatan sendiri' && /banner D1 sudah diubah manual; tidak diganti/.test(u.ctx.__alerts.slice(-1)[0]), 'menu 4: banner yang diubah manual tidak ditimpa dan dilaporkan'); }
  // lokal titik koma: menu 4 memakai varian titik koma (diingat untuk area berikutnya)
  { const u = SIAP(); u.ctx.__opsi.tolakValidasi = { di: 'apply', formula: f => f.indexOf(',') >= 0 };
    u.ctx.perbaruiSheetLama();
    cek(/REGEXMATCH\(E4;"/.test(u.BU.peek(4, A_IN).dv.f) && /rumus titik koma/.test(u.ctx.__alerts.slice(-1)[0]), 'menu 4: lokal titik koma -> rumus bertitik koma terpasang'); }
}

// ---------- cekStatus, kunci, migrasi: rekap ikut dilaporkan/dikunci/dibuat
{
  const u = SEDIA_UC();
  u.ctx.cekStatus();
  const st = u.ctx.__alerts.slice(-1)[0];
  cek(/Rekap harian \(tiap malam ±00\.30 WIB\): 1/.test(st) && /"Rekap Harian UC": 0 hari tersimpan; belum pernah dihitung/.test(st) && /interval trigger sebenarnya dilihat di Apps Script/.test(st), 'cekStatus: trigger rekap + status sheet rekap + catatan interval: ' + st.replace(/\n/g, ' / ').slice(0, 300));
  u.kirim(4, A_OUT, 1); u.ctx.rekapHarianOtomatis(); u.ctx.cekStatus();
  cek(/"Rekap Harian UC": 1 hari tersimpan; terakhir dihitung \d\d\/\d\d\/\d{4} \d\d:\d\d WIB/.test(u.ctx.__alerts.slice(-1)[0]) && !/lebih dari 26 jam/.test(u.ctx.__alerts.slice(-1)[0]), 'cekStatus: rekap terakhir dihitung ditampilkan');
  u.ss.getSheetByName('Rekap Harian UC').getRange(2, 15).setValue(u.ctx.waktuSerial_(new Date()) - 2);
  u.ctx.cekStatus();
  cek(/lebih dari 26 jam lalu/.test(u.ctx.__alerts.slice(-1)[0]), 'cekStatus: rekap basi (>26 jam) diperingatkan');
  u.ctx.kunciKolomStok();
  cek(u.ss.getSheetByName('Rekap Harian UC').protections.length === 1 && u.ss.getSheetByName('Log Stok UC').protections.length === 1, 'kunci kolom STOK: sheet Rekap Harian ikut dikunci');
}

// ---------- hemat kuota: reset tampilan sel hanya bila sel punya catatan (tanda merah selalu disertai catatan)
{
  const b = siapkan(); b.ctx.migrasiStokUC(); b.ctx.aktifkanInputOtomatis();
  const BU = b.ss.getSheetByName('Stok Cover UC');
  const Rg = Object.getPrototypeOf(BU.getRange(1, 1));
  const hit = {};
  ['setBackground', 'setFontColor', 'setNumberFormat', 'setNote'].forEach(n => { const asli = Rg[n]; Rg[n] = function (...a) { hit[n] = (hit[n] || 0) + 1; return asli.apply(this, a); }; });
  const reset = () => { for (const k of Object.keys(hit)) delete hit[k]; };
  const jml = () => Object.values(hit).reduce((a, x) => a + x, 0);
  const stok = (r, c) => Number((BU.peek(r, c) || { v: 0 }).v) || 0;
  // 1. entri IN biasa: STOK naik, sel kosong lagi, TIDAK ada panggilan reset format/catatan pada sel (hanya Log yang mengatur format)
  const sebelum = stok(9, 4);
  BU.getRange(9, 5).setValue(3); reset();
  b.ctx.prosesInputStok({ range: BU.getRange(9, 5), source: b.ss, value: '3' });
  cek(stok(9, 4) === sebelum + 3 && BU.peek(9, 5).v === '' && !hit.setBackground && !hit.setFontColor && !hit.setNote && hit.setNumberFormat === 1, 'entri IN biasa: tanpa reset warna/catatan sel (' + JSON.stringify(hit) + ')');
  // 2. sel menolak (merah + catatan) lalu diketik ulang valid: tanda merah dibersihkan
  BU.getRange(9, 6).setValue(9999); b.ctx.prosesInputStok({ range: BU.getRange(9, 6), source: b.ss, value: '9999' });
  cek(BU.peek(9, 6).bg === '#e06666' && /DITOLAK/.test(BU.peek(9, 6).note), 'OUT berlebih: merah + catatan');
  BU.getRange(9, 6).setValue(1); reset();
  b.ctx.prosesInputStok({ range: BU.getRange(9, 6), source: b.ss, value: '1' });
  cek(BU.peek(9, 6).v === '' && BU.peek(9, 6).bg === null && BU.peek(9, 6).note === '' && hit.setNote === 1 && hit.setBackground === 1, 'sel bercatatan diketik ulang valid: tanda merah dibersihkan (' + JSON.stringify(hit) + ')');
  // 3. menghapus angka di sel biasa (tanpa catatan): tidak ada panggilan reset; sel bercatatan: reset
  BU.getRange(10, 5).setValue(''); reset();
  b.ctx.prosesInputStok({ range: BU.getRange(10, 5), source: b.ss, value: '' });
  cek(jml() === 0, 'hapus sel biasa: tanpa panggilan reset (' + JSON.stringify(hit) + ')');
  const x = BU.cell(10, 6); x.bg = '#e06666'; x.note = 'DITOLAK: contoh';
  BU.getRange(10, 6).setValue(''); reset();
  b.ctx.prosesInputStok({ range: BU.getRange(10, 6), source: b.ss, value: '' });
  cek(BU.peek(10, 6).bg === null && BU.peek(10, 6).note === '' && hit.setNote === 1, 'hapus sel bercatatan: tampilan dikembalikan');
  // catatan buatan staf (bukan tanda sistem) pada sel kosong di area edit: perilaku lama, tampilan dikembalikan
  const y = BU.cell(11, 5); y.bg = '#e06666'; y.note = 'catatan staf';
  BU.getRange(11, 5).setValue(''); reset();
  b.ctx.prosesInputStok({ range: BU.getRange(11, 5), source: b.ss, value: '' });
  cek(BU.peek(11, 5).bg === null && BU.peek(11, 5).note === '', 'sel kosong di area edit bercatatan staf: tampilan dikembalikan (perilaku lama)');
}

// ---------- hemat kuota: lock singkat, putaran verifikasi, penyapu hanya jam kerja
{
  const b = siapkan(); b.ctx.migrasiStokUC(); b.ctx.aktifkanInputOtomatis();
  const BU = b.ss.getSheetByName('Stok Cover UC');
  const v = (r, c) => (BU.peek(r, c) || { v: '' }).v;
  // a. waktu tunggu lock: IN/OUT singkat, koreksi STOK lama
  const dicatat = []; const asliLock = b.ctx.LockService.getDocumentLock;
  b.ctx.LockService.getDocumentLock = () => ({ tryLock: ms => { dicatat.push(ms); return true; }, releaseLock() {} });
  BU.getRange(30, 5).setValue(1); b.ctx.prosesInputStok({ range: BU.getRange(30, 5), source: b.ss });
  BU.getRange(30, 4).setValue(40); b.ctx.prosesInputStok({ range: BU.getRange(30, 4), source: b.ss });
  b.ctx.LockService.getDocumentLock = asliLock;
  cek(dicatat[0] === 3000 && dicatat[1] === 25000, 'lock: IN/OUT menunggu ' + dicatat[0] + ' ms, koreksi STOK ' + dicatat[1] + ' ms');
  // b. sel yang diketik selagi putaran pertama berjalan diproses putaran kedua; tidak ada putaran sia-sia
  const Rg = Object.getPrototypeOf(BU.getRange(1, 1)), asli = Rg.getValues; let sekali = false, bacaan = 0;
  const s31 = v(31, 4), s32 = v(32, 4);
  BU.getRange(31, 5).setValue(2);
  Rg.getValues = function () { const o = asli.call(this); if (this.sh === BU && this.r === 4 && this.c === 1 && this.nc >= 40) { bacaan++; if (!sekali) { sekali = true; BU.getRange(32, 5).setValue(3); } } return o; };
  b.ctx.prosesInputStok({ range: BU.getRange(31, 5), source: b.ss, value: '2' });
  Rg.getValues = asli;
  cek(v(31, 4) === s31 + 2 && v(32, 4) === s32 + 3 && v(32, 5) === '', 'sel yang diketik selagi diproses ikut terbawa putaran berikutnya');
  cek(bacaan >= 3 && bacaan <= 6, 'jumlah putaran wajar (' + bacaan + ' pembacaan blok)');
  // c. putaran maksimum membatasi (tidak berputar tanpa akhir)
  const n0 = b.ss.getSheetByName('Log Stok UC').getLastRow();
  // d. penyapu di luar jam kerja langsung berhenti; di dalam jam kerja bekerja
  const jamWib = Number(new Intl.DateTimeFormat('en-GB', { timeZone: 'Asia/Jakarta', hour: '2-digit', hourCycle: 'h23' }).format(new Date()));
  BU.getRange(33, 5).setValue(1); const s33 = v(33, 4);
  b.ctx.__KONFIG.SAPU_JAM = { awal: (jamWib + 1) % 24, akhir: (jamWib + 2) % 24 || 24 };
  if (b.ctx.__KONFIG.SAPU_JAM.awal < b.ctx.__KONFIG.SAPU_JAM.akhir) { b.ctx.sapuInputStok(); cek(v(33, 4) === s33 && v(33, 5) === 1, 'penyapu di luar jam kerja: tidak memproses'); }
  b.ctx.__KONFIG.SAPU_JAM = { awal: 0, akhir: 24 }; b.ctx.sapuInputStok();
  cek(v(33, 4) === s33 + 1 && v(33, 5) === '', 'penyapu di dalam jam kerja: memproses');
  // e. penyapu tanpa apa pun tertinggal tidak membaca catatan (hemat) dan tidak mengubah apa pun
  let catatanDibaca = 0; const asliCat = Rg.getNotes; Rg.getNotes = function () { catatanDibaca++; return asliCat.call(this); };
  const logSebelum = b.ss.getSheetByName('Log Stok UC').getLastRow();
  b.ctx.sapuInputStok();
  Rg.getNotes = asliCat;
  cek(catatanDibaca === 0 && b.ss.getSheetByName('Log Stok UC').getLastRow() === logSebelum, 'penyapu kosong: tanpa baca catatan, log tetap');
}

// ---------- penyapu: galat satu sheet tidak menghentikan sheet lain
{
  const b = siapkan(); b.ctx.migrasiStokUC(); b.ctx.migrasiStokSTP(); b.ctx.aktifkanInputOtomatis();
  const BU = b.ss.getSheetByName('Stok Cover UC'), BS = b.ss.getSheetByName('Stok Cover STP');
  BU.getRange(5, 5).setValue(1); BS.getRange(5, 5).setValue(1);
  const s5 = (BS.peek(5, 4) || { v: '' }).v;
  const Rg = Object.getPrototypeOf(BU.getRange(1, 1)), asli = Rg.getValues;
  Rg.getValues = function () { if (this.sh === BU && this.nc >= 40) throw new Error('Service error: Spreadsheets'); return asli.call(this); };
  b.ctx.__KONFIG.SAPU_JAM = { awal: 0, akhir: 24 };
  let galat = null; try { b.ctx.sapuInputStok(); } catch (err) { galat = err; }
  Rg.getValues = asli;
  cek(galat && /Penyapu gagal: Stok Cover UC/.test(galat.message) && (BS.peek(5, 4) || { v: '' }).v === s5 + 1 && (BS.peek(5, 5) || { v: '' }).v === '', 'penyapu: galat di UC dilaporkan, STP tetap disapu');
}

// lock gagal
const b2 = siapkan({ lockGagal: true });
b2.ctx.migrasiStokUC();
const sh2 = b2.ss.getSheetByName('Stok Cover UC');
sh2.getRange(4, E).setValue(5);
b2.ctx.prosesInputStok({ range: sh2.getRange(4, E, 1, 2), source: b2.ss });
cek(sh2.peek(4, D).v === 39 && sh2.peek(4, E).v === 5 && !sh2.peek(4, E).note && sh2.peek(4, E).bg === null && !b2.ss.toasts.some(t => /Sistem sibuk/.test(t)), 'lock gagal: angka IN tetap, TIDAK ditandai merah dan tanpa toast (diproses pemegang lock / penyapu)');
{ b2.ctx.__opsi.lockGagal = false; b2.ctx.sapuInputStok(); cek(sh2.peek(4, D).v === 44 && sh2.peek(4, E).v === '', 'lock gagal: angka yang tertunda diproses penyapu setelah lock bebas'); b2.ctx.__opsi.lockGagal = true; }
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

// ---------- cekStatus menyebut ada / belum adanya sheet daftar urutan
{
  const c1 = siapkan({ tanpaUrutan: true }); c1.ctx.cekStatus();
  cek(/daftar urutan "Urutan UC" BELUM ada/.test(c1.ctx.__alerts[0]), 'cekStatus: daftar urutan belum ada');
  const c2 = siapkan(); c2.ctx.cekStatus();
  cek(/daftar urutan "Urutan UC" sudah ada/.test(c2.ctx.__alerts[0]), 'cekStatus: daftar urutan sudah ada');
}

// ---------- hasil review ke-2: status rekap lama, arsip aman diulang
{
  const bs = siapkan();
  bs.ctx.migrasiStokUC();
  const sU = bs.ss.getSheetByName('Stok Cover UC');
  bs.ctx.__alerts.length = 0; bs.ctx.cekStatus();
  cek(!/versi lama/.test(bs.ctx.__alerts[0]), 'cekStatus: rekap baru tidak diperingatkan');
  sU.getRange(199, 5).setValue("=SUMIFS('Log Stok'!$H:$H,'Log Stok'!$B:$B,\"Stok Cover UC\")");
  bs.ctx.__alerts.length = 0; bs.ctx.cekStatus();
  cek(/rekap per warna masih merujuk log versi lama/.test(bs.ctx.__alerts[0]), 'cekStatus: rekap merujuk log lama diperingatkan');
}
{
  const nowS = (Date.now() + 7 * 3600e3 - Date.UTC(1899, 11, 30)) / 86400000;
  const L1 = Math.floor(nowS) - 40, L2 = Math.floor(nowS) - 75;
  const isi = (w, n) => [w, 'Stok Cover UC', 4, 'Produk ' + n, 'SKU', 'Abu-abu', 'IN', n, 0, n, 'u@x', ''];
  const baru = () => {
    const bb = siapkan();
    bb.ctx.migrasiStokUC(); bb.ctx.aktifkanInputOtomatis();
    const LB = bb.ss.getSheetByName('Log Stok UC');
    // urutan seperti log yang pernah diurutkan manual: lama, baru, lama, aneh, baru (bukan terurut waktu)
    const baris = [isi(L1 + 0.2, 1), isi(nowS, 2), isi(L2 + 0.4, 3), isi('teks-aneh', 4), isi(nowS - 0.001, 5), isi(L1 + 0.8, 6)];
    baris.forEach((r, i) => LB.getRange(2 + i, 1, 1, 12).setValues([r]));
    LB.getRange(2, 1, baris.length, 1).setNumberFormat('dd/MM/yyyy HH:mm:ss');
    return { bb, LB };
  };
  const bln = nomor => { const d = new Date(Math.floor(nomor * 86400000) + Date.UTC(1899, 11, 30)); return d.getUTCFullYear() + '-' + ('0' + (d.getUTCMonth() + 1)).slice(-2); };
  const arsipNama = n => 'Arsip Log Stok UC ' + bln(n);

  // (a) baris tersebar: yang bulan ini & tak terbaca tetap di tempat relatifnya
  {
    const { bb, LB } = baru();
    bb.ctx.arsipkanLogBulanLalu();
    const sisa = LB.getRange(2, 4, LB.getLastRow() - 1, 1).getValues().map(r => r[0]);
    cek(sisa.join() === 'Produk 2,Produk 4,Produk 5', 'baris tersebar: sisa Log urutan semula: ' + sisa.join());
    const a1 = bb.ss.getSheetByName(arsipNama(L1)), a2 = bb.ss.getSheetByName(arsipNama(L2));
    cek(a1 && a2 && a1.getLastRow() === 3 && a2.getLastRow() === 2, 'baris tersebar: arsip per bulan terisi');
    cek(a1.getRange(2, 4, 2, 1).getValues().map(r => r[0]).join() === 'Produk 6,Produk 1', 'arsip terurut terbaru di atas');
  }
  // (b) gagal di tengah (deleteRows error) lalu diulang: arsip tidak ganda
  {
    const { bb, LB } = baru();
    const asli = Object.getPrototypeOf(LB).deleteRows;
    Object.getPrototypeOf(LB).deleteRows = function () { throw new Error('You are trying to edit a protected cell or object'); };
    bb.ctx.__alerts.length = 0;
    bb.ctx.arsipkanLogBulanLalu();
    Object.getPrototypeOf(LB).deleteRows = asli;
    cek(/GAGAL.*Aman diulang/.test(bb.ctx.__alerts.join(' ')), 'kegagalan dilaporkan, bukan exception mentah');
    const a1 = bb.ss.getSheetByName(arsipNama(L1));
    cek(a1.getLastRow() === 3 && LB.getLastRow() === 7, 'gagal di tengah: arsip sudah terisi, Log masih utuh');
    bb.ctx.arsipkanLogBulanLalu();
    cek(a1.getLastRow() === 3 && bb.ss.getSheetByName(arsipNama(L2)).getLastRow() === 2, 'diulang: arsip tidak ganda');
    cek(LB.getLastRow() === 4 && LB.getRange(2, 4, 3, 1).getValues().map(r => r[0]).join() === 'Produk 2,Produk 4,Produk 5', 'diulang: Log bersih, sisa utuh');
    bb.ctx.arsipkanLogBulanLalu();
    cek(a1.getLastRow() === 3, 'dijalankan ketiga kali: tetap tidak ganda');
  }
  // (c) Log dikunci & akun ini bukan editor proteksi: tidak menulis apa pun
  {
    const { bb, LB } = baru();
    const p = LB.protect(); p.bolehEdit = false;
    bb.ctx.__alerts.length = 0;
    bb.ctx.arsipkanLogBulanLalu();
    cek(/DILEWATI.*dikunci/.test(bb.ctx.__alerts.join(' ')) && !bb.ss.sheets.some(x => /^Arsip /.test(x.name)) && LB.getLastRow() === 7, 'log terkunci: dilewati sebelum menulis apa pun');
  }
  // (d) arsip yang sudah ada berisi waktu teks: tidak hilang saat digabung
  {
    const { bb, LB } = baru();
    bb.ctx.arsipkanLogBulanLalu();
    const a1 = bb.ss.getSheetByName(arsipNama(L1));
    a1.getRange(3, 1).setValue('catatan manual');          // waktu tak terbaca di arsip
    const sebelum = a1.getLastRow();
    LB.getRange(LB.getLastRow() + 1, 1, 1, 12).setValues([isi(L1 + 0.5, 7)]);
    LB.getRange(LB.getLastRow(), 1).setNumberFormat('dd/MM/yyyy HH:mm:ss');
    bb.ctx.arsipkanLogBulanLalu();
    const col = a1.getRange(2, 1, a1.getLastRow() - 1, 1).getValues().map(r => r[0]);
    cek(a1.getLastRow() === sebelum + 1 && col.includes('catatan manual'), 'waktu teks di arsip tidak hilang saat digabung');
  }
}

// ---------- daftar urutan: susun ulang, gabung, produk baru, pengaman
{
  const nm = r => String(lamaUC.peek(r, 2).v).trim();
  const sk = r => String((lamaUC.peek(r, 3) || { v: '' }).v);
  const cermin = () => { const a = []; for (let r = 4; r <= 196; r++) a.push({ nama: nm(r), sku: sk(r), baris: r, namaLama: nm(r), harga: '' }); return a; };
  const siapkanUC = (daftar, opsi = {}) => { const b = siapkan(Object.assign({ tanpaUrutan: true }, opsi)); if (daftar) tulisUrutan(b.ss, 'Urutan UC', daftar); return b; };
  const namaTab = b => b.ss.sheets.map(x => x.name).join('|');
  const TAB_AWAL = 'Stok Cover UC|Stok Cover STP|Resi Keluar Stok|Urutan UC';
  const semuaAlert = b => b.ctx.__alerts.join(' || ');
  const barisUC = b => b.ss.getSheetByName('Stok Cover UC');
  const stokWarna = (sh, r) => { const o = []; for (let k = 0; k < 16; k++) o.push((sh.peek(r, 4 + 3 * k) || { v: '' }).v); return o; };
  const lamaWarna = r => { const o = []; for (let k = 0; k < 16; k++) { const x = lamaUC.peek(r, 4 + 2 * k); o.push(x && typeof x.v === 'number' ? x.v : ''); } return o; };

  // (d) sheet Urutan tidak ada
  { const b = siapkanUC(null); b.ctx.migrasiStokUC();
    cek(/"Urutan UC" tidak ditemukan/.test(semuaAlert(b)) && namaTab(b) === 'Stok Cover UC|Stok Cover STP|Resi Keluar Stok', 'tanpa sheet Urutan: ditolak, tidak ada perubahan'); }
  // (e) judul kolom hilang
  { const d = cermin(); const b = siapkanUC(d); b.ss.getSheetByName('Urutan UC').getRange(1, 4).setValue('Lain'); b.ctx.migrasiStokUC();
    cek(/harus berisi judul kolom "baris lama"/.test(semuaAlert(b)) && namaTab(b) === TAB_AWAL, 'judul kolom hilang: ditolak'); }
  // (h) nama berawalan "="
  { const d = cermin(); const b = siapkanUC(d); const c = b.ss.getSheetByName('Urutan UC').cell(5, 2); c.v = '=SUM(A1)'; c.f = ''; b.ctx.migrasiStokUC();
    cek(/tidak boleh diawali tanda "="/.test(semuaAlert(b)) && namaTab(b) === TAB_AWAL, 'nama berawalan "=": ditolak'); }
  // (c) satu baris lama dipakai dua kali
  { const d = cermin(); d[5].baris = 4; d[5].namaLama = nm(4); const b = siapkanUC(d); b.ctx.migrasiStokUC();
    cek(/sudah dipakai oleh baris daftar/.test(semuaAlert(b)) && namaTab(b) === TAB_AWAL, 'baris lama ganda: ditolak'); }
  // (l) baris di luar rentang, tanpa nama lama
  { const d = cermin(); d[0].baris = 300; d[0].namaLama = 'Tidak Ada Produk Ini'; const b = siapkanUC(d); b.ctx.migrasiStokUC();
    cek(/di luar daftar produk sheet lama/.test(semuaAlert(b)) && /tidak ditemukan/.test(semuaAlert(b)) && namaTab(b) === TAB_AWAL, 'baris di luar rentang & nama tak ditemukan: ditolak'); }
  // (b) nama tidak cocok & tidak unik → ditolak
  { const d = cermin(); d[0].baris = 99; d[0].namaLama = nm(10); d[1].baris = 98; d[1].namaLama = nm(10);
    const b = siapkanUC(d); b.ss.getSheetByName('Stok Cover UC').getRange(12, 2).setValue(nm(10)); b.ctx.migrasiStokUC();
    cek(/ada di 2 baris/.test(semuaAlert(b)) && namaTab(b) === TAB_AWAL, 'nama ganda di sheet lama: ditolak, tidak menebak'); }
  // jumlah nama ≠ jumlah baris
  { const d = cermin(); d[2].baris = '6, 7'; d[2].namaLama = nm(6); const b = siapkanUC(d); b.ctx.migrasiStokUC();
    cek(/"Nama di sheet lama" harus berisi nama untuk tiap nomor/.test(semuaAlert(b)) && namaTab(b) === TAB_AWAL, 'jumlah nama ≠ jumlah baris: ditolak'); }
  // (a) sheet lama bergeser: nomor baris salah tapi nama unik → ditemukan lewat nama, ada catatan
  { const d = cermin(); d[6].baris = 11;   // produk baris 10 ditulis "baris 11"; produk baris 11 tetap baris 11
    const b = siapkanUC(d); b.ctx.migrasiStokUC();
    const sh = barisUC(b);
    cek(namaTab(b).includes('Stok Cover UC (lama)') && /1 nomor "Baris lama" di daftar sudah tidak cocok/.test(b.ctx.__alerts[0]) && /sudah bergeser; stok diambil lewat nama baris/.test(semuaAlert(b)), 'nomor baris geser: dicari lewat nama, disebut di dialog & catatan');
    cek(JSON.stringify(stokWarna(sh, 10)) === JSON.stringify(lamaWarna(10)) && JSON.stringify(stokWarna(sh, 11)) === JSON.stringify(lamaWarna(11)), 'nomor baris geser: stok tetap milik produk yang benar'); }
  // kolom "Nama di sheet lama" wajib: hilang / kosong → ditolak (pengaman tidak boleh mati diam-diam)
  { const d = cermin(); const b = siapkanUC(d); b.ss.getSheetByName('Urutan UC').getRange(1, 5).setValue('Catatan lain'); b.ctx.migrasiStokUC();
    cek(/harus berisi judul kolom "nama di sheet lama"/.test(semuaAlert(b)) && namaTab(b) === TAB_AWAL, 'kolom nama lama hilang: ditolak'); }
  { const d = cermin().map(x => Object.assign({}, x, { namaLama: x.baris === 10 ? '' : x.namaLama })); const b = siapkanUC(d); b.ctx.migrasiStokUC();
    cek(/Nama di sheet lama" harus berisi nama untuk tiap nomor/.test(semuaAlert(b)) && namaTab(b) === TAB_AWAL, 'sel nama lama kosong: ditolak'); }
  // (f) baris berstok tak disebut daftar → ditambahkan di bawah; baris stok 0 tak disebut → tidak ikut
  { const d = cermin().filter(x => x.baris !== 4 && x.baris !== 195);
    const b = siapkanUC(d); b.ctx.migrasiStokUC();
    const sh = barisUC(b), a0 = b.ctx.__alerts[0];
    cek(/PERHATIAN: 1 baris sheet lama BERSTOK/.test(a0) && /1 baris sheet lama tidak ikut/.test(a0) && /Honda Brio/.test(a0), 'baris berstok tak ada di daftar: peringatan di dialog');
    cek(sh.peek(4 + 191, 2).v === 'Honda Brio' && JSON.stringify(stokWarna(sh, 4 + 191)) === JSON.stringify(lamaWarna(4)) && !sh.peek(4 + 192, 2) && sh.peek(4 + 193, 2).v === 'TOTAL STOK', 'baris berstok ditaruh di bawah, 192 produk'); }
  // (g) produk BARU: harga dari baris lama / tanpa harga
  { const d = cermin(); d.splice(3, 0, { nama: 'Mobil Baru A', sku: 'XXX-AAA-UA-R-G1', baris: '', namaLama: '', harga: 4 }, { nama: 'Mobil Baru B', sku: 'XXX-BBB-UA-R-G1', baris: '', namaLama: '', harga: '' });
    const b = siapkanUC(d); b.ctx.migrasiStokUC();
    const sh = barisUC(b), f = (r, c) => (sh.peek(r, c) || { f: '' }).f;
    cek(sh.peek(7, 2).v === 'Mobil Baru A' && stokWarna(sh, 7).every(v => v === '') && stokWarna(sh, 8).every(v => v === ''), 'produk baru: stok kosong');
    cek(f(7, 52) === '=(D7+G7+J7+M7+P7)*281000' && f(7, 56) === '=SUM(AZ7:BC7)', 'produk baru: harga mengikuti baris 4 yang ditunjuk: ' + f(7, 52));
    cek(f(8, 52) === '' && f(8, 56) === '' && /baris sheet baru [0-9, ]*\b8\b/.test(semuaAlert(b)), 'produk baru tanpa harga: value kosong & dilaporkan');
    cek(/2 produk BARU/.test(semuaAlert(b)), 'catatan produk baru');
    cek(sh.peek(9, 2).v === nm(7) && JSON.stringify(stokWarna(sh, 9)) === JSON.stringify(lamaWarna(7)) && sh.peek(4, 2).v === 'Honda Brio', 'produk lama sesudah produk baru bergeser benar'); }
  // (i) gabung dua baris: stok dijumlah, harga baris pertama, catatan kalau beda
  { const d = cermin().filter(x => x.baris !== 5); d[0] = { nama: 'Honda Brio / Agya Gabungan', sku: 'GAB-UA-R-G1', baris: '4, 5', namaLama: nm(4) + ' | ' + nm(5), harga: '' };
    const b = siapkanUC(d); b.ctx.migrasiStokUC();
    const sh = barisUC(b), esp = lamaWarna(4).map((v, k) => (v === '' && lamaWarna(5)[k] === '') ? '' : (v || 0) + (lamaWarna(5)[k] || 0));
    cek(JSON.stringify(stokWarna(sh, 4)) === JSON.stringify(esp) && sh.peek(4, 2).v === 'Honda Brio / Agya Gabungan', 'gabung: stok dijumlah per warna');
    cek(sh.peek(4, 52).f === '=(D4+G4+J4+M4+P4)*281000' && /harga Reguler beda antar baris yang digabung \(281000 \/ 277000\)/.test(semuaAlert(b)), 'gabung: harga baris pertama + catatan harga beda');
    cek(/gabungan beberapa baris lama/.test(b.ctx.__alerts[0]) && /sama dengan sheet lama/.test(b.ctx.__alerts[0]), 'gabung: dialog menyebut gabungan & total sama'); }

  // nama baris lama dibetulkan user setelah daftar dibuat ("Toyota Swift" → "Suzuki Swift"): diterima, nama ikut, disebut
  { const b = siapkanUC(cermin()); b.ss.getSheetByName('Stok Cover UC').getRange(19, 2).setValue('Suzuki Swift'); b.ctx.migrasiStokUC();
    const sh = barisUC(b);
    cek(namaTab(b).includes('(lama)') && sh.peek(19, 2).v === 'Suzuki Swift' && JSON.stringify(stokWarna(sh, 19)) === JSON.stringify(lamaWarna(19)) &&
      /1 nama baris lama sudah diganti.*"Toyota Swift" → "Suzuki Swift" \(baris 19\)/.test(b.ctx.__alerts[0]), 'nama baris lama dibetulkan: dipakai, nama ikut, disebut di dialog'); }
  // diganti total (tak ada kata sama): ditolak, dengan petunjuk cara memperbaiki daftar
  { const b = siapkanUC(cermin()); b.ss.getSheetByName('Stok Cover UC').getRange(19, 2).setValue('Mobil Lain Sekali'); b.ctx.migrasiStokUC();
    cek(namaTab(b) === TAB_AWAL && /tidak ditemukan di sheet lama\. Kalau nama baris itu memang sudah diganti, ubah kolom "Nama di sheet lama"/.test(semuaAlert(b)), 'nama baris lama diganti total: ditolak + petunjuk'); }
  // nama di baris itu adalah produk lain di daftar (baris bertukar nama): bukan "diganti", ditangani lewat nama
  { const b = siapkanUC(cermin()); const lm = b.ss.getSheetByName('Stok Cover UC'); lm.getRange(19, 2).setValue(nm(20)); lm.getRange(20, 2).setValue(nm(19)); b.ctx.migrasiStokUC();
    const sh = barisUC(b);
    cek(namaTab(b).includes('(lama)') && /2 nomor "Baris lama" di daftar sudah tidak cocok/.test(b.ctx.__alerts[0]) && !/sudah diganti sejak daftar dibuat/.test(b.ctx.__alerts[0]) && JSON.stringify(stokWarna(sh, 19)) === JSON.stringify(lamaWarna(20)) && sh.peek(19, 2).v === 'Toyota Swift', 'nama bertukar antar baris: dipetakan lewat nama, bukan dianggap diganti'); }
  // sel IN berupa teks: angka murni dibaca sebagai angka (dengan catatan); bukan angka → dikosongkan + dilaporkan
  { const b = siapkanUC(cermin()); const lm = b.ss.getSheetByName('Stok Cover UC');
    lm.getRange(4, 4).setValue('39');      // Honda Brio Abu-abu, aslinya 39 → teks
    lm.getRange(5, 4).setValue('abc');     // Agya Abu-abu: bukan angka
    b.ctx.migrasiStokUC();
    const sh = barisUC(b);
    cek(sh.peek(4, 4).v === 39 && sh.peek(5, 4).v === '' && /1 sel IN berisi angka berformat teks/.test(b.ctx.__alerts[0]) && /1 sel IN bukan angka/.test(b.ctx.__alerts[0]),
      'IN teks: angka murni dibaca, bukan angka dikosongkan, disebut di dialog'); }
  // baris tak ada di daftar dengan IN teks / bukan angka: tidak hilang diam-diam
  { const d = cermin().filter(x => x.baris !== 42 && x.baris !== 49);
    const b = siapkanUC(d); const lm = b.ss.getSheetByName('Stok Cover UC');
    lm.getRange(42, 4).setValue('6'); lm.getRange(49, 6).setValue('banyak');   // 42: teks angka (stok 6), 49: isi aneh (stok 0)
    b.ctx.migrasiStokUC();
    const sh = barisUC(b), a0 = b.ctx.__alerts[0];
    cek(/PERHATIAN: 2 baris sheet lama BERSTOK/.test(a0) && sh.peek(4 + 191, 2).v === nm(42) && sh.peek(4 + 191, 4).v === 6 && sh.peek(4 + 192, 2).v === nm(49), 'baris tak terdaftar dengan IN teks / aneh: ditaruh di bawah, tidak hilang'); }
  // staf menambah sendiri produk yang di daftar berstatus BARU: stok tidak hilang, ada petunjuk
  { const d = cermin().filter(x => x.baris !== 109); d.push({ nama: 'Mini Cooper 5 Pintu', sku: 'MNI-COO-UA-R-5P', baris: '', namaLama: '', harga: 109 });
    const b = siapkanUC(d); const lm = b.ss.getSheetByName('Stok Cover UC'); lm.getRange(109, 2).setValue('Mini Cooper 5 Pintu'); lm.getRange(109, 4).setValue(3);
    b.ctx.migrasiStokUC();
    cek(/Namanya sama dengan produk BARU "Mini Cooper 5 Pintu"/.test(semuaAlert(b)) && barisUC(b).peek(4 + 193, 4).v === 3, 'produk BARU sudah ditambah staf: stok tidak hilang, ada petunjuk'); }
  // sheet daftar ganda hasil impor ("Urutan UC 1")
  { const b = siapkanUC(cermin()); tulisUrutan(b.ss, 'Urutan UC 1', cermin()); b.ctx.migrasiStokUC();
    cek(/namanya mirip "Urutan UC".*"Urutan UC 1"/.test(semuaAlert(b)) && namaTab(b).indexOf('(lama)') < 0, 'sheet daftar ganda: ditolak'); }
  { const b = siapkanUC(null); tulisUrutan(b.ss, 'Urutan UC 1', cermin()); b.ctx.migrasiStokUC();
    cek(/Yang ada: "Urutan UC 1"/.test(semuaAlert(b)), 'nama daftar tidak persis: petunjuk nama yang ada'); }
  // Sort sebagian kolom: Nama Produk terlepas dari Baris lama → ditolak
  { const d = cermin(); const nama = d.map(x => x.nama); nama.push(nama.shift());   // geser satu: kolom B terlepas dari C..E
    d.forEach((x, i) => { x.nama = nama[i]; });
    const b = siapkanUC(d); b.ctx.migrasiStokUC();
    cek(/sama sekali beda dari nama baris lama/.test(semuaAlert(b)) && namaTab(b) === TAB_AWAL, 'nama produk terlepas dari baris lama: ditolak'); }
  // baris tanpa Baris lama dan tanpa Kode SKU (mis. baris TOTAL): ditolak
  { const d = cermin(); d.push({ nama: 'TOTAL', sku: '', baris: '', namaLama: '', harga: '' });
    const b = siapkanUC(d); b.ctx.migrasiStokUC();
    cek(/tidak punya "Baris lama" maupun Kode SKU/.test(semuaAlert(b)) && namaTab(b) === TAB_AWAL, 'baris TOTAL / catatan: ditolak'); }
  // sheet sisa migrasi terhenti
  { const b = siapkanUC(cermin()); b.ss.insertSheet('Stok Cover UC (baru)'); b.ctx.migrasiStokUC();
    cek(/sisa migrasi yang terhenti/.test(semuaAlert(b)) && namaTab(b).indexOf('(lama)') < 0, 'sheet sementara sisa: ditolak dengan petunjuk'); }
  // sheet lama bergeser (dua baris bertukar): stok & harga donor ikut produk yang benar
  if (typeof DAFTAR_UJI !== 'undefined' && DAFTAR_UJI) {
    const bs = siapkan({ tanpaUrutan: true });
    const lm = bs.ss.getSheetByName('Stok Cover UC');
    const tukar = (a, c) => {
      for (let col = 1; col <= 40; col++) {
        const x = lm.cell(a, col), y = lm.cell(c, col);
        const ganti = (f, dari, ke) => String(f).replace(/([A-Z]+)(\d+)/g, (m, h, n) => (Number(n) === dari ? h + ke : m));
        const xv = { v: x.v, f: x.f }, yv = { v: y.v, f: y.f };
        x.v = yv.v; x.f = yv.f ? ganti(yv.f, c, a) : ''; y.v = xv.v; y.f = xv.f ? ganti(xv.f, a, c) : '';
      }
    };
    const harga0 = (r, gi) => { const f = lamaUC.peek(r, 36 + gi); const m = f && String(f.f).match(/\*\s*\(?\s*(\d+)\s*\)?\s*$/); return m ? m[1] : null; };
    tukar(18, 43);   // Toyota Yaris ↔ Mercedes E Class
    tulisUrutan(bs.ss, 'Urutan UC', DAFTAR_UJI.UC.map(e => ({ nama: e.nama, sku: e.sku, baris: e.baris.join(', '), namaLama: e.namaLama.join(' | '), harga: e.harga })));
    bs.ctx.migrasiStokUC();
    const sh = bs.ss.getSheetByName('Stok Cover UC'), idx = DAFTAR_UJI.UC.findIndex(e => e.nama === 'Toyota Yaris Gen 1 (2006-2013)'), idx2 = DAFTAR_UJI.UC.findIndex(e => e.nama === 'Suzuki APV Arena');
    const yaris = DAFTAR_UJI.UC.findIndex(e => e.nama === 'Toyota Yaris'), eclass = DAFTAR_UJI.UC.findIndex(e => e.nama === 'Mercedes Benz E Class');
    const tail = (r, gi) => { const f = (sh.peek(r, 52 + gi) || { f: '' }).f; const m = f.match(/\*(\d+)$/); return m ? m[1] : null; };
    cek(/2 nomor "Baris lama" di daftar sudah tidak cocok/.test(bs.ctx.__alerts[0]), 'baris bertukar: disebut di dialog');
    cek(JSON.stringify(stokWarna(sh, 4 + yaris)) === JSON.stringify(lamaWarna(18)) && JSON.stringify(stokWarna(sh, 4 + eclass)) === JSON.stringify(lamaWarna(43)), 'baris bertukar: stok mengikuti produk');
    cek(tail(4 + yaris, 0) === harga0(18, 0) && tail(4 + eclass, 0) === harga0(43, 0), 'baris bertukar: harga mengikuti produk');
    cek(tail(4 + idx, 0) === harga0(18, 0) && tail(4 + idx, 2) === harga0(18, 2) && tail(4 + idx2, 2) === harga0(43, 2), 'baris bertukar: harga donor produk BARU ikut dipetakan');
  }
  // sheet lama berubah selama sheet baru dibangun → dibatalkan bersih
  { const b = siapkanUC(cermin()); const asli = b.ctx.bangunSheet_; const lm = b.ss.getSheetByName('Stok Cover UC');
    b.ctx.bangunSheet_ = function (...a) { asli.apply(this, a); lm.getRange(10, 4).setValue(99); };
    b.ctx.migrasiStokUC();
    cek(/berubah selama migrasi/.test(semuaAlert(b)) && namaTab(b) === TAB_AWAL && lm.getName() === 'Stok Cover UC', 'perubahan selama membangun: dibatalkan, sheet lama utuh'); }
  // baris produk ditambah staf selama dialog terbuka → ikut (di bawah) dan tidak hilang
  { const b = siapkanUC(cermin(), { saatAlert: a => { if (/Migrasi Stok Cover UC/.test(String(a[0]))) { const lm = b.ss.getSheetByName('Stok Cover UC'); lm.getRange(197, 2).setValue('Produk Susulan'); lm.getRange(197, 4).setValue(7); } } });
    b.ctx.migrasiStokUC();
    const sh = barisUC(b);
    cek(sh && sh.peek(4 + 193, 2) && sh.peek(4 + 193, 2).v === 'Produk Susulan' && sh.peek(4 + 193, 4).v === 7, 'produk ditambah selama dialog: ikut di bawah'); }

}

// daftar urutan sungguhan (100 SKU terlaris) terhadap data asli
const DAFTAR = DAFTAR_UJI;
if (!DAFTAR) console.log('LEWATI uji daftar sungguhan (uji/daftar-urutan.js tidak ada)');
if (DAFTAR) {
  const bd = siapkan({ tanpaUrutan: true });
  const kePeta = e => ({ nama: e.nama, sku: e.sku, baris: e.baris.join(', '), namaLama: e.namaLama.join(' | '), harga: e.harga });
  tulisUrutan(bd.ss, 'Urutan UC', DAFTAR.UC.map(kePeta)); tulisUrutan(bd.ss, 'Urutan STP', DAFTAR.STP.map(kePeta));
  bd.ctx.migrasiStokUC(); const alertUCd = bd.ctx.__alerts.join('\n'); bd.ctx.__alerts.length = 0; bd.ctx.migrasiStokSTP();
  for (const [kode, nama, daftar, peta, akhir] of [['UC', 'Stok Cover UC', DAFTAR.UC, [...Array(16).keys()], 196], ['STP', 'Stok Cover STP', DAFTAR.STP, PETA_STP, 107]]) {
    const sh = bd.ss.getSheetByName(nama), lama = bd.ss.getSheetByName(nama + ' (lama)');
    let salah = 0, unitBaru = 0, unitLama = 0;
    daftar.forEach((e, i) => {
      const r = 4 + i;
      if (sh.peek(r, 2).v !== e.nama.trim() || String((sh.peek(r, 3) || { v: '' }).v) !== e.sku || sh.peek(r, 1).v !== i + 1) salah++;
      peta.forEach((k, w) => {
        let exp = '';
        if (k !== null) e.baris.forEach(rl => { const x = lama.peek(rl, 4 + 2 * k); if (x && typeof x.v === 'number') exp = (exp === '' ? 0 : exp) + x.v; });
        const got = (sh.peek(r, 4 + 3 * w) || { v: '' }).v;
        if (got !== exp) salah++;
        unitBaru += got || 0;
      });
    });
    for (let r = 4; r <= akhir; r++) for (let k = 0; k < 16; k++) { const x = lama.peek(r, 4 + 2 * k); if (x && typeof x.v === 'number') unitLama += x.v; }
    cek(salah === 0 && unitBaru === unitLama, `${kode} daftar sungguhan: ${daftar.length} baris sesuai, stok per warna & total ${unitBaru}/${unitLama} (salah ${salah})`);
    const nBaru = daftar.length;
    cek(!sh.peek(4 + nBaru, 2) && sh.peek(5 + nBaru, 2).v === 'TOTAL STOK' && sh.peek(5 + nBaru, 4).f === `=SUM(D4:D${4 + nBaru})`, `${kode} daftar sungguhan: baris TOTAL STOK di bawah produk terakhir`);
    // Value produk baru: harga mengikuti baris yang ditunjuk
    let sf = 0;
    const kolV = 4 + 3 * peta.length;
    daftar.filter(e => !e.baris.length && e.harga !== '').forEach(e => {
      const r = 4 + daftar.indexOf(e);
      for (let gi = 0; gi < 4; gi++) {
        const fl = lama.peek(e.harga, 36 + gi) ? lama.peek(e.harga, 36 + gi).f : '';
        const m = String(fl).match(/\*\s*\(?\s*(\d+)\s*\)?\s*$/);
        const got = (sh.peek(r, kolV + gi) || { f: '' }).f;
        if (m ? !got.endsWith('*' + m[1]) : got !== '') sf++;
      }
    });
    cek(sf === 0, `${kode} daftar sungguhan: harga Value produk baru mengikuti baris donor (salah ${sf})`);
    // harga Value produk yang dipindah: harus dari baris asalnya sendiri, bukan baris pada urutan yang sama
    let sp = 0, nCek = 0;
    daftar.forEach((e, i) => {
      if (!e.baris.length) return;
      for (let gi = 0; gi < 4; gi++) {
        const harga = e.baris.map(rl => { const fl = lama.peek(rl, 36 + gi) ? lama.peek(rl, 36 + gi).f : ''; const m = String(fl).match(/\*\s*\(?\s*(\d+)\s*\)?\s*$/); return m ? m[1] : null; }).find(x => x !== null);
        const got = (sh.peek(4 + i, kolV + gi) || { f: '' }).f; nCek++;
        if (harga ? !got.endsWith('*' + harga) : got !== '') sp++;
      }
    });
    cek(sp === 0 && nCek > 200, `${kode} daftar sungguhan: harga Value tiap produk dari baris asalnya (salah ${sp} dari ${nCek})`);
  }
  cek(/46 sel OUT masih terisi/.test(alertUCd), 'dialog UC daftar sungguhan: peringatan OUT terisi');
  cek(/181 produk/.test(alertUCd) && /BARU/.test(alertUCd) && /sama dengan sheet lama/.test(alertUCd) && /29 baris sheet lama tidak ikut/.test(alertUCd), 'dialog UC daftar sungguhan: ' + alertUCd.split('\n')[0]);
  cek(bd.ss.getSheetByName('Stok Cover UC').peek(4, 2).v === 'Honda Brio' && bd.ss.getSheetByName('Stok Cover UC').peek(4 + 180, 2).v === 'Motor', 'UC: hijau di atas, sisa stok (Motor) di bawah');
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

// =====================================================================================================
// LAYOUT BARU (2026-10-24): STOK | OUT | OUT HARI INI. Stok masuk diketik di STOK (KOREKSI), kolom IN dihapus.
// =====================================================================================================
// Jam palsu: geser "sekarang" di konteks kode (Log dan reset memakai detik sebagai resolusi).
const geserJam = (u, ms) => { u.ctx.__geser = (u.ctx.__geser || 0) + ms; const g = u.ctx.__geser; require('vm').runInContext('Date = (function (Asli) { return class extends Asli { constructor(...a) { if (a.length) super(...a); else super(Asli.now() + ' + g + '); } static now() { return Asli.now() + ' + g + '; } }; })(Object.getPrototypeOf(Date) === Function.prototype ? Date : Date);', u.ctx); };
const B_STOK = 4, B_OUT = 5, B_HARI = 6, H2_STOK = 7, H2_OUT = 8, H2_HARI = 9;
const SEDIA_BARU = () => SEDIA_UC({ layout: 'baru' });
const hariSel = (u, r, c) => { const x = u.BU.peek(r, c); return x ? x.v : ''; };
const statusHari = u => JSON.parse(u.ctx.__propDok['HARI|Stok Cover UC'] || 'null');

// ---------- struktur sheet baru
{
  const u = SEDIA_BARU();
  const peta = u.ctx.bacaPeta_(u.BU);
  cek(peta.layoutBaru === true && peta.kolom[B_STOK].jenis === 'STOK' && peta.kolom[B_OUT].jenis === 'OUT' && peta.kolom[B_HARI].jenis === 'HARI' && peta.kolom[B_OUT].kolomHari === B_HARI, 'peta layout baru: STOK/OUT/HARI, OUT tahu kolom HARI-nya');
  cek([4, 5, 6, 7, 8, 9].map(c => u.BU.peek(3, c).v).join('|') === 'STOK|OUT|OUT HARI INI|STOK|OUT|OUT HARI INI', 'judul baris 3 per warna');
  cek(!!u.BU.peek(4, B_OUT).dv && /REGEXMATCH/.test(u.BU.peek(4, B_OUT).dv.f) && !u.BU.peek(4, B_HARI).dv && !!u.BU.peek(4, B_STOK).dv, 'validasi: OUT menerima B+angka, OUT HARI INI TANPA validasi (cegah segitiga merah "Invalid"), STOK tetap');
  cek(u.BU.peek(4, B_HARI).bg === '#efefef' && u.BU.peek(4, B_HARI).nf === u.kons().FORMAT_STOK && u.BU.getColumnWidth(B_HARI) === u.ctx.__K.LEBAR_KOLOM_HARI, 'kolom OUT HARI INI: latar abu muda, nol tidak tampil, lebar sendiri');
  cek(u.BU.getRange(1, 4).getValue() === u.ctx.__K.TEKS_BANNER_HARI, 'banner menjelaskan: stok masuk diketik di STOK');
  const rm = peta.barisTotal + 1;
  const f = i => u.BU.getRange(rm + i, 3).getFormula();
  const eb = peta.barisTotal - 1;
  cek(f(0) === '=SUMIF($D$3:$AY$3,"OUT HARI INI",$D$' + rm + ':$AY$' + rm + ')-SUMPRODUCT((TRIM($B$4:$B$' + eb + ')="Motor")*($D$3:$AY$3="OUT HARI INI"),$D$4:$AY$' + eb + ')', 'C(mutasi): Keluar hari ini = jumlah kolom OUT HARI INI dikurangi Motor: ' + f(0));
  cek(/"OUT".*"<>Motor".*TODAY\(\)-1/.test(f(1)) && /SUMPRODUCT/.test(f(2)) && f(2).indexOf('-SUMPRODUCT') < 0 && /"OUT".*"Motor".*TODAY\(\)-1/.test(f(3)) && f(4) === '', 'baris lain: Keluar kemarin (Log), Motor keluar hari ini (kolom), Motor keluar kemarin (Log); tanpa baris Masuk');
  cek(u.BU.getRange(rm, B_HARI).getFormula() === '=SUM(F4:F' + eb + ')' && u.BU.getRange(rm, B_OUT).getFormula() === '' && u.BU.getRange(rm, H2_HARI).getFormula() === '=SUM(I4:I' + eb + ')', 'total per warna di kolom OUT HARI INI; kolom OUT kosong');
  cek(statusHari(u) && statusHari(u).hari === Math.floor(u.ctx.waktuSerial_(new Date())), 'migrasi menyimpan status hari ini');
}

// ---------- OUT mengisi OUT HARI INI; B mengurangi; ditolak tidak mengubah
{
  const u = SEDIA_BARU();
  geserJam(u, 3000);   // sesudah detik migrasi (status "sejak")
  const s0 = u.st(4, B_STOK);
  u.kirim(4, B_OUT, 3);
  cek(u.st(4, B_STOK) === s0 - 3 && u.sel(4, B_OUT).v === '' && hariSel(u, 4, B_HARI) === 3 && u.log1()[6] === 'OUT' && u.log1()[7] === 3, 'OUT 3: STOK turun 3, sel OUT kosong, OUT HARI INI = 3, Log OUT 3');
  u.kirim(4, B_OUT, 2);
  cek(hariSel(u, 4, B_HARI) === 5, 'OUT 2 lagi: OUT HARI INI = 5 (kumulatif)');
  u.kirim(4, B_OUT, 'B1');
  cek(hariSel(u, 4, B_HARI) === 4 && u.st(4, B_STOK) === s0 - 4 && u.log1()[7] === -1 && /BATAL OUT/.test(u.log1()[11]), 'B1: OUT HARI INI turun jadi 4, STOK naik 1, Log Qty -1');
  u.kirim(4, B_OUT, 'B9');
  cek(hariSel(u, 4, B_HARI) === 4 && u.st(4, B_STOK) === s0 - 4 && u.sel(4, B_OUT).bg === '#e06666' && /DITOLAK/.test(u.sel(4, B_OUT).note), 'B melebihi net hari ini: ditolak, OUT HARI INI dan STOK tidak berubah');
  u.kirim(4, B_OUT, '');
  u.kirim(4, B_OUT, s0 + 50);
  cek(hariSel(u, 4, B_HARI) === 4 && u.sel(4, B_OUT).bg === '#e06666', 'OUT melebihi stok: ditolak, OUT HARI INI tidak berubah');
  u.kirim(4, B_OUT, '');
  u.kirim(4, H2_OUT, 1); u.kirim(5, B_OUT, 2);
  cek(hariSel(u, 4, H2_HARI) === 1 && hariSel(u, 5, B_HARI) === 2 && hariSel(u, 4, B_HARI) === 4, 'warna dan produk lain punya catatan sendiri-sendiri');
  // edit manual di OUT HARI INI diabaikan (tanpa Log, tanpa tanda merah)
  const n = u.nLog();
  u.BU.getRange(4, B_HARI).setValue(77);
  u.ctx.prosesInputStok({ range: u.BU.getRange(4, B_HARI), source: u.ss, value: '77' });
  cek(u.nLog() === n && u.sel(4, B_HARI).bg === '#efefef' && hariSel(u, 4, B_HARI) === 4, 'edit manual di OUT HARI INI tidak dicatat dan angkanya dikembalikan dari Log (4, bukan 77)');
  // angka tertinggal di OUT (trigger terlewat) diproses penyapu dan ikut mengisi OUT HARI INI
  u.BU.getRange(6, B_OUT).setValue(2);
  const sb = u.st(6, B_STOK);
  u.ctx.sapuInputStok();
  cek(u.st(6, B_STOK) === sb - 2 && hariSel(u, 6, B_HARI) === 2 && u.sel(6, B_OUT).v === '', 'penyapu: angka tertinggal di OUT diproses dan masuk OUT HARI INI');
}

// ---------- ganti hari, reset, hitung ulang
{
  const u = SEDIA_BARU();
  const hari = Math.floor(u.ctx.waktuSerial_(new Date()));
  u.kirim(4, B_OUT, 2);
  // hari berganti (status kemarin, sel masih berisi angka kemarin): entri pertama hari ini mengosongkan dulu
  u.ctx.__propDok['HARI|Stok Cover UC'] = JSON.stringify({ hari: hari - 1, sejak: hari - 1 });
  u.BU.getRange(4, B_HARI).setValue(9); u.BU.getRange(5, B_HARI).setValue(4);
  u.kirim(6, B_OUT, 1);
  cek(hariSel(u, 4, B_HARI) === '' && hariSel(u, 5, B_HARI) === '' && hariSel(u, 6, B_HARI) === 1 && statusHari(u).hari === hari, 'hari berganti: OUT HARI INI kemarin dikosongkan sebelum entri pertama hari ini');
  // trigger malam melakukannya walau tidak ada entri
  u.ctx.__propDok['HARI|Stok Cover UC'] = JSON.stringify({ hari: hari - 1, sejak: hari - 1 });
  u.BU.getRange(4, B_HARI).setValue(9);
  u.ctx.rekapHarianOtomatis();
  cek(hariSel(u, 4, B_HARI) === '' && statusHari(u).hari === hari, 'trigger malam: hari berganti, OUT HARI INI kosong tanpa menunggu entri');
  // tanpa status (mis. properti hilang): dibangun dari Log hari ini
  delete u.ctx.__propDok['HARI|Stok Cover UC'];
  u.BU.getRange(4, B_HARI).setValue(55); u.BU.getRange(7, B_HARI).setValue(5);
  u.kirim(5, B_OUT, 1);
  cek(hariSel(u, 4, B_HARI) === 2 && hariSel(u, 6, B_HARI) === 1 && hariSel(u, 5, B_HARI) === 1 && hariSel(u, 7, B_HARI) === '', 'status hilang: dibangun dari Log (OUT 2 baris 4, OUT 1 baris 6, OUT 1 baris 5), angka liar dibuang');
}
{
  const u = SEDIA_BARU();
  u.kirim(4, B_OUT, 3); u.kirim(5, B_OUT, 2);
  const nLog = u.nLog();
  const LGbaris = () => u.LG().getRange(2, 1, u.nLog(), 12).getValues().map(r => r.slice(6, 8).join(':')).join(',');
  const logSebelum = LGbaris();
  // jawab TIDAK: tidak ada yang berubah
  u.ctx.__opsi.jawab = 'NO';
  u.ctx.rekapDanResetHariIni();
  u.ctx.__opsi.jawab = 'YES';
  cek(hariSel(u, 4, B_HARI) === 3 && hariSel(u, 5, B_HARI) === 2, 'rekap + reset: jawab Tidak -> tidak ada yang berubah');
  geserJam(u, 3000);
  u.ctx.rekapDanResetHariIni();
  geserJam(u, 3000);
  const rk = u.ss.getSheetByName('Rekap Harian UC');
  const r2 = rk.getRange(2, 1, 1, 18).getValues()[0];
  cek(r2[2] === 5 && r2[4] === 2, 'rekap + reset: rekap menyimpan SEMUA entri sebelum reset (Keluar 5, Entri 2): ' + JSON.stringify(r2.slice(0, 5)));
  cek(hariSel(u, 4, B_HARI) === '' && hariSel(u, 5, B_HARI) === '' && u.nLog() === nLog && LGbaris() === logSebelum, 'rekap + reset: OUT HARI INI kosong; Log tidak berubah');
  cek(statusHari(u).sejak > Math.floor(u.ctx.waktuSerial_(new Date())) && /direset ke 0/.test(u.ctx.__alerts.slice(-1)[0]), 'rekap + reset: status "sejak" = saat reset; dialog melapor');
  // entri sesudah reset mulai dari 0; rekap hari ini ikut bertambah
  u.kirim(4, B_OUT, 1);
  cek(hariSel(u, 4, B_HARI) === 1, 'sesudah reset: OUT HARI INI mulai dari 0 (1, bukan 4)');
  // B atas entri SEBELUM reset: boleh (net dari Log), OUT HARI INI tidak jadi minus
  u.kirim(4, B_OUT, 'B2');
  cek(hariSel(u, 4, B_HARI) === 0 && u.sel(4, B_OUT).note === '', 'B atas entri sebelum reset: diterima, OUT HARI INI tidak minus (0)');
  // hitung ulang dari Log sejak reset: hanya entri sesudah reset (OUT 1, B2 -> bersih -1 -> 0)
  u.BU.getRange(4, B_HARI).setValue(99); u.BU.getRange(9, H2_HARI).setValue(7);
  u.ctx.hitungUlangOutHariIni();
  cek(hariSel(u, 4, B_HARI) === '' && hariSel(u, 9, H2_HARI) === '' && /dihitung ulang dari Log/.test(u.ctx.__alerts.slice(-1)[0]), 'hitung ulang: angka liar dibuang, hanya entri sejak reset yang dihitung');
  // tanpa reset: hitung ulang sejak tengah malam memuat semua entri hari ini
  delete u.ctx.__propDok['HARI|Stok Cover UC'];
  u.ctx.hitungUlangOutHariIni();
  cek(hariSel(u, 5, B_HARI) === 2 && hariSel(u, 4, B_HARI) === 2, 'hitung ulang sejak tengah malam: net per produk (baris 4: 3+1-2 = 2, baris 5 = 2)');
  // rekap tidak ada -> reset dibatalkan
  u.ss.deleteSheet(u.ss.getSheetByName('Rekap Harian UC'));
  u.kirim(6, B_OUT, 1);
  u.ctx.rekapDanResetHariIni();
  cek(hariSel(u, 6, B_HARI) === 1 && /reset Stok Cover UC DIBATALKAN/.test(u.ctx.__alerts.slice(-1)[0]), 'rekap + reset: sheet rekap tidak ada -> reset dibatalkan');
}
{
  // sheet masih susunan lama: tombol reset/hitung ulang menolak dengan petunjuk
  const u = SEDIA_UC();
  u.ctx.rekapDanResetHariIni();
  cek(/menu 5/.test(u.ctx.__alerts.slice(-1)[0]), 'rekap + reset pada susunan lama: diarahkan ke menu 5');
  u.ctx.hitungUlangOutHariIni();
  cek(/menu 5/.test(u.ctx.__alerts.slice(-1)[0]), 'hitung ulang pada susunan lama: diarahkan ke menu 5');
}

// ---------- reset: entri di detik yang sama dengan reset dianggap sebelum reset; baris ganda; rekap gagal -> tidak reset
{
  const u = SEDIA_BARU();
  u.kirim(4, B_OUT, 3);
  u.ctx.rekapDanResetHariIni();
  u.ctx.hitungUlangOutHariIni();
  cek(hariSel(u, 4, B_HARI) === '', 'hitung ulang: entri yang terjadi sebelum/di detik reset tidak ikut dihitung lagi');
  // dua baris dengan nama + SKU sama: hanya baris pertama yang menerima angkanya
  const v = SEDIA_BARU();
  v.BU.getRange(6, 2, 1, 2).setValues([[v.BU.peek(5, 2).v, v.BU.peek(5, 3).v]]);
  geserJam(v, 3000);   // entri sesudah migrasi (status "sejak" = saat migrasi, resolusi detik)
  v.kirim(5, B_OUT, 2);
  v.ctx.hitungUlangOutHariIni();
  cek(hariSel(v, 5, B_HARI) === 2 && hariSel(v, 6, B_HARI) === '', 'hitung ulang: baris ganda (nama + SKU sama) -> hanya baris pertama berisi');
  // rekap gagal -> reset dibatalkan
  const w = SEDIA_BARU();
  w.kirim(4, B_OUT, 2);
  w.kons().REKAP_BATAS_BARIS = 0;
  w.ctx.rekapDanResetHariIni();
  w.kons().REKAP_BATAS_BARIS = 60000;
  cek(hariSel(w, 4, B_HARI) === 2 && /reset Stok Cover UC DIBATALKAN/.test(w.ctx.__alerts.slice(-1)[0]), 'rekap gagal: reset dibatalkan, OUT HARI INI utuh');
  // rekap + reset hanya untuk sheet berformat baru; yang lama tidak disentuh
}

// ---------- ketahanan (hasil tinjauan independen): gagal menulis OUT HARI INI / membaca Log / ganti hari tidak boleh merusak STOK dan Log
{
  const RgP = u => Object.getPrototypeOf(u.BU.getRange(1, 1));
  // (1) penulisan OUT HARI INI selalu gagal: entri diproses SEKALI, tidak terpotong berulang oleh penyapu
  const u = SEDIA_BARU();
  geserJam(u, 3000);   // sesudah detik migrasi (status "sejak")
  const asli = RgP(u).setValue;
  RgP(u).setValue = function (v) { if (this.sh.name === 'Stok Cover UC' && this.c === B_HARI) throw new Error('Service Spreadsheets timed out'); return asli.call(this, v); };
  const s0 = u.st(4, B_STOK);
  u.kirim(4, B_OUT, 3);
  u.ctx.sapuInputStok(); u.ctx.sapuInputStok(); u.ctx.sapuInputStok();
  RgP(u).setValue = asli;
  cek(u.st(4, B_STOK) === s0 - 3 && u.sel(4, B_OUT).v === '' && u.nLog() === 1 && u.log1()[7] === 3, 'OUT HARI INI gagal ditulis: STOK terpotong SEKALI (bukan berulang), sel OUT kosong, Log 1 baris');
  u.ctx.hitungUlangOutHariIni();
  cek(hariSel(u, 4, B_HARI) === 3, 'dan "Hitung ulang" memulihkan OUT HARI INI dari Log');
  // (2) membaca Log untuk "stok sebelum" gagal: koreksi tetap tercatat
  const v = SEDIA_BARU();
  const asliGV = RgP(v).getValues;
  v.kirim(4, B_OUT, 1);
  RgP(v).getValues = function () { if (this.sh.name === 'Log Stok UC') throw new Error('Service Spreadsheets timed out'); return asliGV.apply(this, arguments); };
  const n0 = v.nLog();
  v.BU.getRange(4, B_STOK).setValue(44);
  v.ctx.prosesInputStok({ range: v.BU.getRange(4, B_STOK), source: v.ss, value: '44' });
  RgP(v).getValues = asliGV;
  cek(v.nLog() === n0 + 1 && v.log1()[6] === 'KOREKSI' && v.log1()[9] === 44 && v.log1()[8] === '' && /tidak diketahui/.test(v.log1()[11]), 'baca Log gagal: KOREKSI tetap tercatat, stok sebelum "tidak diketahui"');
  // (3) e.oldValue "0" tanpa catatan Log: dianggap tidak diketahui (bukan 0 palsu)
  const w = SEDIA_BARU();
  w.BU.getRange(30, B_STOK).setValue(40);
  w.ctx.prosesInputStok({ range: w.BU.getRange(30, B_STOK), source: w.ss, value: '40', oldValue: '0' });
  cek(w.log1()[8] === '' && /tidak diketahui/.test(w.log1()[11]), 'e.oldValue "0" dan Log kosong: stok sebelum dianggap tidak diketahui');
  // (4) ganti hari gagal (izin): STOK dan Log tetap diproses, OUT HARI INI dilewati dengan peringatan
  const x = SEDIA_BARU();
  const hari = Math.floor(x.ctx.waktuSerial_(new Date()));
  x.ctx.__propDok['HARI|Stok Cover UC'] = JSON.stringify({ hari: hari - 1, sejak: hari - 1 });
  x.BU.getRange(5, B_HARI).setValue(8);
  const sheetP = Object.getPrototypeOf(x.BU);
  const asliRL = sheetP.getRangeList;
  sheetP.getRangeList = function () { throw new Error('Anda tidak punya izin'); };
  const sx = x.st(4, B_STOK);
  x.kirim(4, B_OUT, 2);
  sheetP.getRangeList = asliRL;
  cek(x.st(4, B_STOK) === sx - 2 && x.nLog() === 1 && x.sel(4, B_OUT).v === '' && hariSel(x, 4, B_HARI) === '' && /OUT HARI INI belum diperbarui/.test(x.ss.toasts.slice(-1)[0] + x.ss.toasts.join('|')), 'ganti hari gagal: STOK dan Log tetap diproses, OUT HARI INI dilewati + toast peringatan');
  // (5) hari yang dipakai untuk rollover = hari stempel Log (satu instan): hari depan menghapus angka hari ini
  const y = SEDIA_BARU();
  y.kirim(4, B_OUT, 2);
  const peta = y.ctx.bacaPeta_(y.BU);
  y.ctx.pastikanHariBerjalan_(y.ss, y.BU, y.kons().SISTEM[0], peta, Math.floor(y.ctx.waktuSerial_(new Date())) + 1);
  cek(hariSel(y, 4, B_HARI) === '' && JSON.parse(y.ctx.__propDok['HARI|Stok Cover UC']).hari === Math.floor(y.ctx.waktuSerial_(new Date())) + 1, 'pastikanHariBerjalan_ memakai hari yang diberikan pemanggil (hari berikutnya mengosongkan)');
}

// ---------- STOK diketik langsung: Stok Sebelum dari Log (e.oldValue tidak diandalkan)
{
  const u = SEDIA_BARU();
  const s0 = u.st(4, B_STOK);
  u.kirim(4, B_OUT, 3);   // Log: sesudah = s0-3
  u.BU.getRange(4, B_STOK).setValue(s0 + 5);
  u.ctx.prosesInputStok({ range: u.BU.getRange(4, B_STOK), source: u.ss, value: String(s0 + 5), oldValue: undefined });
  let l = u.log1();
  cek(l[6] === 'KOREKSI' && l[8] === s0 - 3 && l[9] === s0 + 5 && l[11] === 'Edit langsung kolom STOK' && hariSel(u, 4, B_HARI) === 3, 'ketik STOK: KOREKSI dengan stok sebelum dari Log (e.oldValue kosong); OUT HARI INI tidak berubah');
  u.BU.getRange(4, B_STOK).setValue(s0 + 9);
  u.ctx.prosesInputStok({ range: u.BU.getRange(4, B_STOK), source: u.ss, value: String(s0 + 9), oldValue: '0' });   // Google kadang memberi 0 padahal sel berisi
  l = u.log1();
  cek(l[8] === s0 + 5 && l[9] === s0 + 9, 'ketik STOK lagi: stok sebelum = hasil KOREKSI sebelumnya (bukan "0" dari e.oldValue)');
  // produk belum pernah tercatat di Log: pakai e.oldValue bila ada, kalau tidak "tidak diketahui"
  const sa = u.st(20, B_STOK);
  u.BU.getRange(20, B_STOK).setValue(sa + 1);
  u.ctx.prosesInputStok({ range: u.BU.getRange(20, B_STOK), source: u.ss, value: String(sa + 1), oldValue: String(sa) });
  cek(u.log1()[8] === sa, 'produk belum ada di Log: memakai e.oldValue');
  u.BU.getRange(21, B_STOK).setValue(7);
  u.ctx.prosesInputStok({ range: u.BU.getRange(21, B_STOK), source: u.ss, value: '7' });
  cek(u.log1()[8] === '' && /stok sebelum tidak diketahui/.test(u.log1()[11]), 'tanpa Log dan tanpa e.oldValue: kosong + keterangan "tidak diketahui" (bukan 0 palsu)');
  // tempel beberapa sel sekaligus: tiap sel memakai Log
  u.kirim(5, B_OUT, 1); u.kirim(5, H2_OUT, 1);
  const sb = u.st(5, B_STOK), sc = u.st(5, H2_STOK);
  u.BU.getRange(5, B_STOK).setValue(sb + 4); u.BU.getRange(5, H2_STOK).setValue(sc + 2);
  u.ctx.prosesInputStok({ range: u.BU.getRange(5, B_STOK, 1, 4), source: u.ss });
  const dua = u.LG().getRange(2, 1, 2, 12).getValues();
  cek(dua.every(x => x[6] === 'KOREKSI') && dua.some(x => x[8] === sb && x[9] === sb + 4) && dua.some(x => x[8] === sc && x[9] === sc + 2) && /Edit banyak sel sekaligus$/.test(dua[0][11]), 'tempel banyak sel STOK: stok sebelum tiap sel dari Log');
}

// ---------- menu 5: ubah susunan sheet yang sudah dimigrasi
{
  const u = SEDIA_UC();   // susunan lama
  const hari = Math.floor(u.ctx.waktuSerial_(new Date()));
  u.kirim(4, 6, 3);       // OUT warna 1 baris 4 (kolom lama OUT = 6)
  u.kirim(4, 5, 5);       // IN warna 1 baris 4
  u.kirim(5, 9, 2);       // OUT warna 2 baris 5
  const stokSebelum = u.BU.getRange(4, 4, 30, 6).getValues();
  const logSebelum = u.nLog();
  const peta0 = u.ctx.bacaPeta_(u.BU), rm = peta0.barisTotal + 1;
  cek(peta0.layoutBaru === false, 'sheet awal: susunan lama');
  u.ctx.ubahSusunanKolom();
  const lap = u.ctx.__alerts.slice(-1)[0];
  const peta = u.ctx.bacaPeta_(u.BU);
  cek(peta.layoutBaru === true && peta.kolom[5].jenis === 'OUT' && peta.kolom[6].jenis === 'HARI', 'menu 5: label baris 3 diubah (kolom ke-2 = OUT, ke-3 = OUT HARI INI)');
  cek(hariSel(u, 4, 6) === 3 && hariSel(u, 5, 9) === 2 && hariSel(u, 4, 5) === '', 'menu 5: OUT HARI INI diisi dari OUT hari ini di Log (IN diabaikan)');
  cek(u.nLog() === logSebelum && JSON.stringify(u.BU.getRange(4, 4, 30, 6).getValues().map((r, i) => [r[0], r[3]])) === JSON.stringify(stokSebelum.map(r => [r[0], r[3]])), 'menu 5: STOK dan Log tidak berubah');
  cek(u.BU.getRange(rm, 6).getFormula() === '=SUM(F4:F' + (peta.barisTotal - 1) + ')' && u.BU.getRange(rm, 5).getFormula() === '' && u.BU.getRange(rm + 1, 3).getFormula().indexOf('"IN"') < 0, 'menu 5: total per warna diganti; baris Masuk dihapus dari kolom C');
  cek(/SUMIF\(\$D\$3/.test(u.BU.getRange(rm, 3).getFormula()) && u.BU.getRange(rm + 4, 3).getFormula() === '' && u.BU.getRange(rm + 7, 3).getFormula() === '', 'menu 5: rencana total baru (4 baris), sisa rumus lama dihapus');
  cek(!u.BU.peek(4, 6).dv && !!u.BU.peek(4, 5).dv && /REGEXMATCH/.test(u.BU.peek(4, 5).dv.f) && u.BU.peek(4, 6).bg === '#efefef', 'menu 5: validasi OUT, OUT HARI INI tanpa validasi, tampilan abu muda');
  cek(u.BU.getRange(1, 4).getValue() === u.ctx.__K.TEKS_BANNER_HARI && /susunan kolom diubah/.test(lap) && statusHari(u).hari === hari, 'menu 5: banner baru, status hari tersimpan, laporan');
  u.kirim(4, 5, 1);
  cek(hariSel(u, 4, 6) === 4 && u.sel(4, 5).v === '', 'sesudah menu 5: OUT di kolom ke-2 berjalan dan menambah OUT HARI INI');
  // diulang: dilewati
  u.ctx.ubahSusunanKolom();
  cek(/sudah berformat STOK\/OUT\/OUT HARI INI; susunan tidak diubah/.test(u.ctx.__alerts.slice(-1)[0]) && /total harian|banner sudah sesuai|validasi IN\/OUT diperbarui/.test(u.ctx.__alerts.slice(-1)[0]), 'menu 5 diulang pada sheet yang sudah baru: susunan tidak diubah, tapi tampilan/validasi/total dilengkapi (menu 4)');
  // menu 4 pada susunan baru: aman diulang
  u.ctx.perbaruiSheetLama();
  u.ctx.perbaruiSheetLama();
  cek(!/GAGAL/.test(u.ctx.__alerts.slice(-1)[0]) && hariSel(u, 4, 6) === 4, 'menu 4 pada susunan baru: aman diulang, tidak merusak OUT HARI INI');
}
{
  // angka tertinggal di IN/OUT: sheet dilewati, tidak ada yang diubah
  const u = SEDIA_UC();
  u.BU.getRange(7, 8).setValue(3);   // IN warna 2 baris 7, belum diproses
  u.ctx.ubahSusunanKolom();
  cek(/DILEWATI\. Masih ada isi di kolom IN\/OUT: baris 7 H/.test(u.ctx.__alerts.slice(-1)[0]) && u.ctx.bacaPeta_(u.BU).layoutBaru === false && u.BU.peek(3, 5).v === 'IN', 'menu 5: angka tertinggal -> sheet dilewati, susunan lama utuh');
  u.BU.getRange(7, 8).clearContent();
  u.BU.protections = u.BU.protections || [];
  const p = u.BU.protect(); p.bolehEdit = false;
  u.ctx.ubahSusunanKolom();
  cek(/Sheet dikunci/.test(u.ctx.__alerts.slice(-1)[0]) && u.ctx.bacaPeta_(u.BU).layoutBaru === false, 'menu 5: sheet terkunci untuk akun ini -> dilewati');
}
{
  // sel asing di kolom C tidak ditimpa; label TOTAL STOK hilang -> dilewati
  const u = SEDIA_UC();
  const peta = u.ctx.bacaPeta_(u.BU), rm = peta.barisTotal + 1;
  u.BU.getRange(rm + 1, 3).clearContent(); u.BU.getRange(rm + 1, 3).setValue('catatan staf');
  u.ctx.ubahSusunanKolom();
  cek(u.BU.getRange(rm + 1, 3).getValue() === 'catatan staf' && /TIDAK ditimpa/.test(u.ctx.__alerts.slice(-1)[0]) && u.ctx.bacaPeta_(u.BU).layoutBaru === true, 'menu 5: sel asing di kolom C tidak ditimpa, susunan tetap berubah');
  const w = SEDIA_UC();
  const pw = w.ctx.bacaPeta_(w.BU);
  w.BU.getRange(pw.barisTotal, 2).setValue('');
  w.ctx.ubahSusunanKolom();
  cek(/label "TOTAL STOK".*dilewati/.test(w.ctx.__alerts.slice(-1)[0]) && w.ctx.bacaPeta_(w.BU).layoutBaru === false, 'menu 5: label TOTAL STOK hilang -> dilewati');
}

// ---------- menu 5: ketahanan (hasil tinjauan independen)
{
  // sheet campuran (konversi sebelumnya terhenti): dilanjutkan, bukan "sudah berformat"
  const u = SEDIA_UC();
  [4, 7, 10, 13, 16].forEach(c => u.BU.getRange(3, c + 1, 1, 2).setValues([['OUT', 'OUT HARI INI']]));
  cek(u.ctx.bacaPeta_(u.BU).layoutBaru === true, 'sheet campuran: terbaca layout baru (sebagian)');
  u.ctx.ubahSusunanKolom();
  const p = u.ctx.bacaPeta_(u.BU);
  const stok = Object.keys(p.kolom).map(Number).filter(c => p.kolom[c].jenis === 'STOK');
  cek(stok.every(c => p.kolom[c + 1].jenis === 'OUT' && p.kolom[c + 2].jenis === 'HARI') && /susunan kolom diubah \(11 warna\)/.test(u.ctx.__alerts.slice(-1)[0]), 'sheet campuran: sisa blok lama diubah, laporan menyebut 11 warna: ' + u.ctx.__alerts.slice(-1)[0].slice(0, 120));
}
{
  // angka masuk di antara pemeriksaan pertama dan penulisan label: DIBATALKAN, tidak ada yang berubah
  const u = SEDIA_UC();
  const RgP = Object.getPrototypeOf(u.BU.getRange(1, 1));
  const asli = RgP.getValues;
  let blok = 0;
  RgP.getValues = function () {
    if (this.sh.name === 'Stok Cover UC' && this.r === 4 && this.c === 1 && this.nr > 50) { blok++; if (blok === 2) u.BU.getRange(7, 8).setValue(3); }
    return asli.apply(this, arguments);
  };
  u.ctx.ubahSusunanKolom();
  RgP.getValues = asli;
  cek(/DIBATALKAN \(belum ada yang diubah\)/.test(u.ctx.__alerts.slice(-1)[0]) && u.ctx.bacaPeta_(u.BU).layoutBaru === false && u.BU.peek(3, 5).v === 'IN', 'angka masuk sesudah pemeriksaan pertama: DIBATALKAN, label tetap lama');
}
{
  // angka diketik sesudah label ditulis: dilaporkan; sisa tanda merah di kolom IN lama dibersihkan; catatan menu 3
  const u = SEDIA_UC();
  u.ctx.kunciKolomStok();
  u.BU.getRange(6, 5).setNote('DITOLAK: sisa').setBackground('#e06666');
  const asliPS = u.ctx.perbaruiSatu_;
  u.ctx.perbaruiSatu_ = function (...a) { const r = asliPS.apply(this, a); u.BU.getRange(7, 5).setValue(3); u.BU.getRange(7, 6).setValue(4); return r; };
  u.ctx.ubahSusunanKolom();
  const lap = u.ctx.__alerts.slice(-1)[0];
  cek(/PERIKSA, angka diketik selagi proses: .*baris 7 OUT Abu-abu = 3.*baris 7 OUT HARI INI Abu-abu = 4/.test(lap), 'angka yang diketik selagi proses dilaporkan (OUT dari IN lama, OUT HARI INI ditimpa)');
  cek(u.BU.peek(6, 5).note === '' && u.BU.peek(6, 5).bg === null, 'sisa tanda merah dan catatan dari kolom IN lama dibersihkan');
  cek(/PROTEKSI menu 3 masih memakai susunan lama/.test(lap), 'laporan: proteksi menu 3 lama -> jalankan ulang menu 3');
}
{
  // penulisan OUT HARI INI gagal sekali: status ditandai "perlu", entri berikutnya membangun ulang dari Log (sejak reset)
  const u = SEDIA_BARU();
  geserJam(u, 3000);
  const RgP = Object.getPrototypeOf(u.BU.getRange(1, 1));
  const asli = RgP.setValue;
  let gagalSekali = true;
  RgP.setValue = function (v) { if (gagalSekali && this.sh.name === 'Stok Cover UC' && this.c === B_HARI) { gagalSekali = false; throw new Error('Service Spreadsheets timed out'); } return asli.call(this, v); };
  u.kirim(4, B_OUT, 3);
  RgP.setValue = asli;
  cek(u.ctx.__propDok['PERLU|Stok Cover UC'] === '1' && u.ss.toasts.some(t => /OUT HARI INI gagal ditulis/.test(t)) && hariSel(u, 4, B_HARI) === '', 'tulis OUT HARI INI gagal: status "perlu" + toast, STOK/Log sudah benar');
  u.kirim(5, B_OUT, 2);
  cek(hariSel(u, 4, B_HARI) === 3 && hariSel(u, 5, B_HARI) === 2 && !u.ctx.__propDok['PERLU|Stok Cover UC'], 'entri berikutnya: OUT HARI INI dibangun ulang dari Log (3 dan 2), status pulih');
}
{
  // nama "Motor " (spasi ekor) di sheet tetap dikenali (TRIM) seperti di Log
  const u = SEDIA_BARU();
  cek(/TRIM\(\$B\$4:/.test(u.BU.getRange(u.ctx.bacaPeta_(u.BU).barisTotal + 1, 3).getFormula()), 'rumus total memakai TRIM pada nama produk (samakan dengan Log yang sudah di-trim)');
}

// ---------- tinjauan 3: stok masuk bersamaan dengan OUT, penanda tangan total, Log panjang, rangkaian reset, lock sibuk
{
  // (B) STOK diketik (antre lock) sementara OUT sel yang sama sudah diproses dari angka baru: rantai Log putus -> KOREKSI terlambat
  const u = SEDIA_BARU();
  geserJam(u, 3000);
  const s0 = u.st(4, B_STOK);
  u.kirim(4, B_OUT, 1);                            // Log: s0 -> s0-1
  u.BU.getRange(4, B_STOK).setValue(s0 + 10);      // staf mengetik STOK; kejadian editnya belum diproses (antre)
  u.kirim(4, B_OUT, 2);                            // OUT diproses dari sel yang sudah berisi s0+10 -> s0+8
  const nSebelum = u.nLog();
  u.ctx.prosesInputStok({ range: u.BU.getRange(4, B_STOK), source: u.ss, value: String(s0 + 8) });   // kejadian edit STOK akhirnya tiba
  const l = u.log1();
  cek(u.nLog() === nSebelum + 1 && l[6] === 'KOREKSI' && l[8] === s0 - 1 && l[9] === s0 + 10 && /Dicatat terlambat/.test(l[11]), 'STOK + OUT bersamaan: perubahan yang hilang dicatat sebagai KOREKSI terlambat (' + JSON.stringify(l.slice(6, 12)) + ')');
  // tanpa rantai putus: edit STOK yang sama dengan Log tetap dicatat biasa (bukan terlambat)
  const v = SEDIA_BARU();
  v.kirim(4, B_OUT, 1);
  const sv = v.st(4, B_STOK);
  v.ctx.prosesInputStok({ range: v.BU.getRange(4, B_STOK), source: v.ss, value: String(sv) });
  cek(v.log1()[6] === 'KOREKSI' && !/terlambat/.test(v.log1()[11]) && v.log1()[8] === sv && v.log1()[9] === sv, 'tanpa rantai putus: KOREKSI biasa (sebelum = sesudah), bukan "terlambat"');
}
{
  // menu 4 diulang pada susunan baru: tanpa pesan "TIDAK ditimpa" (rumus Motor ber-TRIM dikenali milik script); rumus SUMIF buatan staf tidak ditimpa/dihapus
  const u = SEDIA_BARU();
  u.ctx.perbaruiSheetLama();
  const lap1 = u.ctx.__alerts.slice(-1)[0];
  u.ctx.perbaruiSheetLama();
  cek(!/TIDAK ditimpa/.test(lap1) && !/TIDAK ditimpa/.test(u.ctx.__alerts.slice(-1)[0]), 'menu 4 pada susunan baru (diulang): tidak ada "TIDAK ditimpa" palsu');
  const rm = u.ctx.bacaPeta_(u.BU).barisTotal + 1;
  u.BU.getRange(rm + 6, 3).setFormulas([['=SUMIF($D$3:$AY$3,"STOK",$D$186:$AY$186)']]);   // rumus staf, bukan milik script
  u.ctx.perbaruiSheetLama();
  cek(u.BU.getRange(rm + 6, 3).getFormula() === '=SUMIF($D$3:$AY$3,"STOK",$D$186:$AY$186)', 'rumus SUMIF buatan staf di bawah rencana: tidak dihapus');
}
{
  // Log panjang: OUT hari ini tertimbun >3000 baris KOREKSI: bangun ulang tetap benar; melewati batas -> galat, kolom TIDAK dinolkan
  const u = SEDIA_BARU();
  geserJam(u, 3000);
  u.kirim(4, B_OUT, 3); u.kirim(5, B_OUT, 2);
  const cfg = u.kons().SISTEM[0];
  const t = u.ctx.waktuSerial_(new Date());
  const banyak = [];
  for (let i = 0; i < 3100; i++) banyak.push([t + 1e-6 * (i + 1), 'Stok Cover UC', 30, 'Honda City', 'X', 'Abu-abu', 'KOREKSI', '', 1, 2, '', '']);
  u.ctx.tulisLog_(u.ss, cfg, banyak);
  u.BU.getRange(4, B_HARI).setValue(99);
  u.ctx.hitungUlangOutHariIni();
  cek(hariSel(u, 4, B_HARI) === 3 && hariSel(u, 5, B_HARI) === 2, 'Log > 3000 baris sejak waktu mulai: bangun ulang dibaca bertahap dan tetap benar (3 dan 2)');
  u.kons().BATAS_BACA_HARI = 3000;
  u.BU.getRange(4, B_HARI).setValue(7);
  u.ctx.hitungUlangOutHariIni();
  u.kons().BATAS_BACA_HARI = 30000;
  cek(hariSel(u, 5, B_HARI) === 2 && /terlalu panjang/.test(u.ctx.__alerts.slice(-1)[0]), 'Log melewati batas baca: galat jelas, kolom tidak dinolkan');
}
{
  // rangkaian reset: B atas entri sebelum reset lalu OUT: angka bangun ulang = angka langsung (klem 0 tiap langkah); entri kemarin tidak ikut
  const u = SEDIA_BARU();
  geserJam(u, 3000);
  u.kirim(4, B_OUT, 3);
  const cfg = u.kons().SISTEM[0];
  const hari = Math.floor(u.ctx.waktuSerial_(new Date()));
  u.ctx.tulisLog_(u.ss, cfg, [[hari - 1 + 0.5, 'Stok Cover UC', 4, u.BU.peek(4, 2).v, u.BU.peek(4, 3).v, 'Abu-abu', 'OUT', 40, 1, 1, '', '']]);   // kemarin
  geserJam(u, 3000);
  u.ctx.rekapDanResetHariIni();
  geserJam(u, 3000);
  u.kirim(4, B_OUT, 'B1');
  u.kirim(4, B_OUT, 2);
  const langsung = hariSel(u, 4, B_HARI);
  u.ctx.hitungUlangOutHariIni();
  cek(langsung === 2 && hariSel(u, 4, B_HARI) === 2, 'rangkaian reset: angka langsung = angka bangun ulang (2), entri kemarin (40) tidak ikut');
  // dua kali pulih (tempel di OUT HARI INI) sesudah reset tetap memakai "sejak" reset
  u.BU.getRange(4, B_HARI).setValue(88);
  u.ctx.prosesInputStok({ range: u.BU.getRange(4, B_HARI), source: u.ss, value: '88' });
  u.BU.getRange(4, B_HARI).setValue(99);
  u.ctx.prosesInputStok({ range: u.BU.getRange(4, B_HARI), source: u.ss, value: '99' });
  cek(hariSel(u, 4, B_HARI) === 2, 'pemulihan berulang sesudah reset: tetap sejak reset (2), bukan sejak tengah malam');
  // rentang yang menjangkau OUT dan OUT HARI INI sekaligus: OUT diproses, lalu OUT HARI INI dikembalikan dari Log
  u.BU.getRange(6, B_OUT).setValue(2); u.BU.getRange(6, B_HARI).setValue(99);
  u.ctx.prosesInputStok({ range: u.BU.getRange(6, B_OUT, 1, 2), source: u.ss });
  cek(hariSel(u, 6, B_HARI) === 2 && u.sel(6, B_OUT).v === '', 'edit menjangkau OUT dan OUT HARI INI: OUT diproses, OUT HARI INI = 2 (bukan 99/101)');
}
{
  // lock sibuk saat pemulihan: ditandai, dipulihkan pada eksekusi berikutnya (penyapu)
  const u = SEDIA_BARU();
  geserJam(u, 3000);
  u.kirim(4, B_OUT, 3);
  u.BU.getRange(4, B_HARI).setValue(99);
  u.ctx.__opsi.lockGagal = true;
  u.ctx.prosesInputStok({ range: u.BU.getRange(4, B_HARI), source: u.ss, value: '99' });
  u.ctx.__opsi.lockGagal = false;
  cek(hariSel(u, 4, B_HARI) === 99 && u.ctx.__propDok['PERLU|Stok Cover UC'] === '1', 'lock sibuk saat pemulihan: ditandai "perlu"');
  u.ctx.sapuInputStok();
  cek(hariSel(u, 4, B_HARI) === 3 && !u.ctx.__propDok['PERLU|Stok Cover UC'], 'penyapu berikutnya memulihkan dari Log dan menghapus tanda');
}
{
  // menu 5: penjaga yang belum teruji
  const u = SEDIA_UC();
  u.BU.getRange(8, 6).setValue(2);   // angka di kolom OUT lama (STOK=D, IN=E, OUT=F)
  u.ctx.ubahSusunanKolom();
  cek(/DILEWATI\. Masih ada isi di kolom IN\/OUT: baris 8 F/.test(u.ctx.__alerts.slice(-1)[0]) && u.ctx.bacaPeta_(u.BU).layoutBaru === false, 'menu 5: angka di kolom OUT lama juga menghalangi');
  const w = SEDIA_UC();
  w.BU.getRange(3, 6).setValue('IN');   // blok pertama jadi STOK | IN | IN (tidak lazim)
  w.ctx.ubahSusunanKolom();
  cek(/susunan kolom tidak lazim/.test(w.ctx.__alerts.slice(-1)[0]) && w.ctx.bacaPeta_(w.BU).layoutBaru === false, 'menu 5: susunan tidak lazim -> dilewati');
  const x = SEDIA_UC();
  const rm = x.ctx.bacaPeta_(x.BU).barisTotal + 1;
  x.BU.getRange(rm, 2).setValue('');
  x.ctx.ubahSusunanKolom();
  cek(/baris "MASUK \/ KELUAR HARI INI" tidak ditemukan/.test(x.ctx.__alerts.slice(-1)[0]) && x.ctx.bacaPeta_(x.BU).layoutBaru === false, 'menu 5: baris MASUK/KELUAR HARI INI hilang -> dilewati');
}
{
  // beberapa produk terpisah: utama mengurangi semuanya, terpisah menjumlahkan semuanya
  const u = SEDIA_UC({ layout: 'baru' });
  u.kons().PRODUK_TERPISAH = { label: 'Khusus', nama: ['Motor', 'Sepeda'] };
  const f = u.ctx.rumusPlan_(u.ctx.totalHarian_(true)[0], { log: 'Log Stok UC', akhirKol: 'AY', barisMutasi: 187, barisAkhirData: 185 });
  const g = u.ctx.rumusPlan_(u.ctx.totalHarian_(true)[2], { log: 'Log Stok UC', akhirKol: 'AY', barisMutasi: 187, barisAkhirData: 185 });
  cek((f.match(/-SUMPRODUCT/g) || []).length === 2 && /"Motor"/.test(f) && /"Sepeda"/.test(f) && (g.match(/SUMPRODUCT/g) || []).length === 2 && /\)\+SUMPRODUCT/.test(g) && g.indexOf('=SUMIF') < 0, 'dua produk terpisah: total utama mengurangi dua kali, total terpisah menjumlah dua');
}
{
  // UC susunan baru + STP susunan lama (kondisi nyata saat hanya satu sheet dikonversi): semua jalur tetap jalan
  const u = SEDIA_UC();
  u.ctx.migrasiStokSTP();
  const stp = u.ss.getSheetByName('Stok Cover STP');
  const cfgUC = u.kons().SISTEM[0];
  u.ctx.ubahSusunanSatu_(u.ss, cfgUC);
  cek(u.ctx.bacaPeta_(u.BU).layoutBaru === true && u.ctx.bacaPeta_(stp).layoutBaru === false, 'campuran: UC susunan baru, STP susunan lama');
  geserJam(u, 3000);
  const sU = u.st(4, 4);
  u.kirim(4, 5, 2);   // UC: kolom OUT baru
  const stpS = (r, c) => Number((stp.peek(r, c) || { v: 0 }).v) || 0;
  const sS = stpS(4, 4);
  stp.getRange(4, 5).setValue(3);   // STP: kolom IN lama
  u.ctx.prosesInputStok({ range: stp.getRange(4, 5), source: u.ss, value: '3' });
  cek(u.st(4, 4) === sU - 2 && hariSel(u, 4, 6) === 2 && stpS(4, 4) === sS + 3 && (stp.peek(4, 5) || { v: '' }).v === '', 'campuran: edit UC (OUT) dan STP (IN) masing-masing benar');
  stp.getRange(4, 6).setValue(1);   // STP OUT lama tertinggal, diproses penyapu
  u.ctx.sapuInputStok();
  cek(stpS(4, 4) === sS + 2 && u.st(4, 4) === sU - 2, 'campuran: penyapu memproses STP lama tanpa mengganggu UC baru');
  u.ctx.rekapHarianOtomatis();
  u.ctx.cekStatus();
  const st = u.ctx.__alerts.slice(-1)[0];
  cek(/"Stok Cover UC": format STOK\/OUT\/OUT HARI INI \(aktif\)/.test(st) && /"Stok Cover STP": format STOK\/IN\/OUT \(aktif; susunan lama/.test(st), 'campuran: cek status menyebut dua susunan berbeda');
  u.ctx.rekapDanResetHariIni();
  cek(/Stok Cover UC: OUT HARI INI direset/.test(u.ctx.__alerts.slice(-1)[0]) && !/Stok Cover STP: OUT HARI INI direset/.test(u.ctx.__alerts.slice(-1)[0]), 'campuran: tombol reset hanya untuk sheet susunan baru');
}

{
  // bangun ulang tanpa status ("sejak" tidak diberikan): mulai TENGAH MALAM hari ini; entri kemarin tidak ikut
  const u = SEDIA_BARU();
  geserJam(u, 3000);
  const cfg = u.kons().SISTEM[0];
  const hari = Math.floor(u.ctx.waktuSerial_(new Date()));
  u.ctx.tulisLog_(u.ss, cfg, [[hari - 1 + 0.9, 'Stok Cover UC', 4, u.BU.peek(4, 2).v, u.BU.peek(4, 3).v, 'Abu-abu', 'OUT', 40, 1, 1, '', '']]);   // 23:36 kemarin
  u.kirim(4, B_OUT, 3);
  delete u.ctx.__propDok['HARI|Stok Cover UC'];
  u.kirim(5, B_OUT, 1);   // status hilang -> dibangun dari Log sejak tengah malam
  cek(hariSel(u, 4, B_HARI) === 3 && hariSel(u, 5, B_HARI) === 1, 'bangun ulang tanpa status: sejak tengah malam hari ini; OUT kemarin (40) tidak ikut: ' + hariSel(u, 4, B_HARI));
}
{
  // menu 5: label baris 3 ditulis dengan SATU panggilan (atomik), bukan per warna
  const u = SEDIA_UC();
  const RgP = Object.getPrototypeOf(u.BU.getRange(1, 1));
  const asli = RgP.setValues;
  let panggilan = 0;
  RgP.setValues = function (v) { if (this.sh.name === 'Stok Cover UC' && this.r === 3 && this.nr === 1 && this.nc > 2 && v[0].some(x => x === 'OUT HARI INI')) panggilan++; return asli.apply(this, arguments); };
  u.ctx.ubahSusunanKolom();
  RgP.setValues = asli;
  cek(panggilan === 1 && u.ctx.bacaPeta_(u.BU).layoutBaru === true, 'menu 5: label baris 3 ditulis dalam satu panggilan (' + panggilan + ')');
}

{
  // sheet yang sudah dikonversi dengan kode lama (aturan "tolak semua" di OUT HARI INI): menu 4 menghapusnya (penyebab segitiga merah "Invalid")
  const u = SEDIA_BARU();
  const p = u.ctx.bacaPeta_(u.BU);
  u.BU.getRange(4, B_HARI, p.barisTotal - 4, 1).setDataValidation(u.ctx.SpreadsheetApp.newDataValidation().requireFormulaSatisfied('=FALSE').setAllowInvalid(false).build());
  cek(!!u.BU.peek(4, B_HARI).dv && /FALSE/.test(u.BU.peek(4, B_HARI).dv.f), 'prasyarat: aturan lama terpasang');
  u.ctx.perbaruiSheetLama();
  cek(!u.BU.peek(4, B_HARI).dv && !u.BU.peek(10, H2_HARI).dv && !!u.BU.peek(4, B_OUT).dv, 'menu 4: aturan "tolak semua" lama di OUT HARI INI dihapus; validasi OUT utuh');
}

{
  // sheet yang sudah dikonversi dengan kode lama (aturan "tolak semua" di OUT HARI INI) lalu kode diperbarui dan MENU 5 dijalankan (bukan menu 4)
  const u = SEDIA_BARU();
  const p = u.ctx.bacaPeta_(u.BU);
  u.BU.getRange(4, B_HARI, p.barisTotal - 4, 1).setDataValidation(u.ctx.SpreadsheetApp.newDataValidation().requireFormulaSatisfied('=FALSE').setAllowInvalid(false).build());
  u.ctx.ubahSusunanKolom();
  cek(!u.BU.peek(4, B_HARI).dv && !u.BU.peek(10, H2_HARI).dv, 'menu 5 pada sheet yang sudah baru: aturan "tolak semua" lama di OUT HARI INI ikut dihapus (segitiga merah hilang)');
}

{
  // toast pengingat tiap ada edit di kolom OUT HARI INI (tanpa kotak "jangan tampilkan lagi")
  const u = SEDIA_BARU();
  geserJam(u, 3000);
  u.kirim(4, B_OUT, 3);
  const n0 = u.ss.toasts.length;
  u.BU.getRange(4, B_HARI).setValue(77);
  u.ctx.prosesInputStok({ range: u.BU.getRange(4, B_HARI), source: u.ss, value: '77' });
  cek(u.ss.toasts.length === n0 + 1 && /terisi otomatis.*dikembalikan dari Log/.test(u.ss.toasts.slice(-1)[0]) && hariSel(u, 4, B_HARI) === 3, 'edit di OUT HARI INI: toast pengingat + angka dikembalikan dari Log');
  const n1 = u.ss.toasts.length;
  u.BU.getRange(5, B_OUT).setValue(1); u.BU.getRange(5, B_HARI).setValue(88);
  u.ctx.prosesInputStok({ range: u.BU.getRange(5, B_OUT, 1, 2), source: u.ss });
  cek(u.ss.toasts.slice(n1).some(t => /terisi otomatis/.test(t)), 'edit yang menjangkau OUT dan OUT HARI INI: toast pengingat juga muncul');
  const n2 = u.ss.toasts.length;
  u.kirim(6, B_OUT, 1);
  cek(!u.ss.toasts.slice(n2).some(t => /terisi otomatis/.test(t)), 'edit biasa di kolom OUT: tanpa toast pengingat');
}

// ---------- kunci, cek status, rekap pada susunan baru
{
  const u = SEDIA_BARU();
  u.ctx.kunciKolomStok();
  const p = u.BU.getProtections('SHEET').filter(x => x.desc === u.kons().DESKRIPSI_PROTEKSI).slice(-1)[0];
  const pr = u.BU.getProtections('RANGE').filter(x => x.desc === u.kons().DESKRIPSI_PROTEKSI_HARI);
  const adaDi = (kol) => p.unprot.some(r => r.c === kol);
  cek(adaDi(B_STOK) && adaDi(B_OUT) && !adaDi(B_HARI) && /STOK\/OUT tetap bisa diisi; popup peringatan di 16 kolom OUT HARI INI/.test(u.ctx.__alerts.slice(-1)[0]), 'kunci (susunan baru): STOK dan OUT bebas diisi staf, OUT HARI INI terkunci');
  cek(pr.length === 16 && pr.every(x => x.peringatan === true) && pr.map(x => x.rentang.c).join(',') === [6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51].join(','), 'kunci (susunan baru): 16 proteksi mode PERINGATAN, tepat di kolom OUT HARI INI');
  u.ctx.kunciKolomStok();
  cek(u.BU.getProtections('RANGE').filter(x => x.desc === u.kons().DESKRIPSI_PROTEKSI_HARI).length === 16 && u.BU.getProtections('SHEET').filter(x => x.desc === u.kons().DESKRIPSI_PROTEKSI).length === 1, 'kunci diulang: proteksi lama diganti, tidak menggandakan (16 peringatan + 1 sheet)');
  const lama = SEDIA_UC();
  lama.ctx.kunciKolomStok();
  cek(lama.BU.getProtections('RANGE').length === 0 && !/popup peringatan/.test(lama.ctx.__alerts.slice(-1)[0]), 'kunci (susunan lama): tidak ada proteksi peringatan');
  u.ctx.cekStatus();
  cek(/format STOK\/OUT\/OUT HARI INI \(aktif\); OUT HARI INI dihitung sejak/.test(u.ctx.__alerts.slice(-1)[0]) && !/merujuk log versi lama/.test(u.ctx.__alerts.slice(-1)[0]), 'cek status (susunan baru): menyebut susunan dan "dihitung sejak", tanpa peringatan palsu');
  // rekap: IN tidak ada lagi; Keluar dan Motor tetap benar
  u.ctx.tulisLog_(u.ss, u.kons().SISTEM[0], [[u.ctx.waktuSerial_(new Date()), 'Stok Cover UC', 184, 'Motor', '', 'Abu-abu', 'OUT', 3, 5, 2, '', '']]);
  u.kirim(4, B_OUT, 2);
  u.ctx.perbaruiRekapSekarang();
  const r = u.ss.getSheetByName('Rekap Harian UC').getRange(2, 1, 1, 18).getValues()[0];
  cek(r[1] === 0 && r[2] === 2 && r[17] === 3, 'rekap (susunan baru): Masuk 0, Keluar 2 (tanpa Motor), Keluar motor 3');
}

console.log(`\n${lulus} lulus, ${gagal} gagal`);
const dump = {};
for (const s of ss.sheets) { const o = {}; for (const [k, x] of s.cells) if (x.v !== '' || x.f) o[k] = x.f || (Object.prototype.toString.call(x.v) === '[object Date]' ? { date: x.v.toISOString() } : x.v); dump[s.name] = o; }
fs.writeFileSync(path.join(__dirname, 'hasil.json'), JSON.stringify(dump));
process.exit(gagal ? 1 : 0);
