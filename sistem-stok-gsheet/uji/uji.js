'use strict';
const fs = require('fs');
const path = require('path');
const { Spreadsheet, buatKonteks } = require('./mock');

const KODE = process.argv[2];
const DATA = JSON.parse(fs.readFileSync(path.join(__dirname, 'uc.json'), 'utf8'));
let gagal = 0, lulus = 0;
function cek(kond, pesan) { if (kond) lulus++; else { gagal++; console.log('GAGAL:', pesan); } }

function siapkan(opsi = {}) {
  const ss = new Spreadsheet();
  const src = ss.insertSheet('Stok Cover UC');
  src.maxCols = 40; src.maxRows = 1121;
  for (const [k, v] of Object.entries(DATA)) {
    const [r, c] = k.split(',').map(Number);
    if (typeof v === 'string' && v.startsWith('=')) src.cell(r, c).f = v; else src.cell(r, c).v = v;
  }
  const ctx = buatKonteks(ss, Object.assign({ kode: KODE }, opsi));
  return { ss, src, ctx };
}

// ---------- migrasi
const { ss, src, ctx } = siapkan();
const snapshotSrc = JSON.stringify([...src.cells.entries()].map(([k, x]) => [k, x.v, x.f]));
ctx.migrasiStokUC();
const sh = ss.getSheetByName('Stok UC Sistem');
cek(sh, 'sheet sistem dibuat');
cek(ss.getSheetByName('Log Stok'), 'sheet log dibuat');
cek(JSON.stringify([...src.cells.entries()].map(([k, x]) => [k, x.v, x.f])) === snapshotSrc, 'sheet sumber tidak berubah');
cek(ss.sheets.map(s => s.name).join('|') === 'Stok Cover UC|Stok UC Sistem|Log Stok', 'urutan sheet: ' + ss.sheets.map(s => s.name).join('|'));
console.log('ALERT migrasi:\n  ' + ctx.__alerts.join('\n  ').replace(/\n/g, '\n    '));

const v = (r, c) => { const x = sh.peek(r, c); return x ? (x.f || x.v) : ''; };
// header
const W = 16;
for (let k = 0; k < W; k++) {
  cek(v(2, 4 + 3 * k) === String(src.peek(2, 4 + 2 * k).v).trim(), 'nama warna k=' + k);
  cek(v(3, 4 + 3 * k) === 'STOK' && v(3, 5 + 3 * k) === 'IN' && v(3, 6 + 3 * k) === 'OUT', 'label STOK/IN/OUT k=' + k);
}
cek(v(3, 52) === 'Reguler' && v(3, 55) === 'Exclusive' && v(3, 56) === 'Total Value', 'label value');
// data: STOK = IN lama, IN/OUT baru kosong
let selisih = 0, totalUnitLama = 0, totalUnitBaru = 0;
for (let r = 4; r <= 196; r++) {
  for (let c = 1; c <= 3; c++) if ((src.peek(r, c) ? src.peek(r, c).v : '') !== v(r, c)) selisih++;
  for (let k = 0; k < W; k++) {
    const lama = src.peek(r, 4 + 2 * k); const lv = lama && typeof lama.v === 'number' ? lama.v : '';
    if (lv !== v(r, 4 + 3 * k)) selisih++;
    if (v(r, 5 + 3 * k) !== '' || v(r, 6 + 3 * k) !== '') selisih++;
    totalUnitLama += lv || 0; totalUnitBaru += v(r, 4 + 3 * k) || 0;
  }
}
cek(selisih === 0, 'data tersalin persis (selisih ' + selisih + ')');
cek(totalUnitLama === totalUnitBaru, `total unit ${totalUnitLama} vs ${totalUnitBaru}`);
console.log('Total unit:', totalUnitBaru);
cek(v(4, 52) === '=(D4+G4+J4+M4+P4)*281000', 'formula Reguler baris 4: ' + v(4, 52));
cek(v(4, 53) === '=(S4+V4+Y4+AB4+AE4+AH4+AK4+AN4+AQ4)*341000', 'formula Strip baris 4: ' + v(4, 53));
cek(v(4, 54) === '=(AT4)*680000' && v(4, 55) === '=(AW4)*1180000' && v(4, 56) === '=SUM(AZ4:BC4)', 'formula premium/excl/total baris 4');
cek(v(40, 54) === '' && v(40, 53) !== '', 'baris 40 premium rusak dikosongkan, strip tetap');
cek(v(50, 52) === '' && v(50, 56) === '', 'baris tanpa formula lama tetap kosong');
cek(v(198, 2) === 'TOTAL STOK' && v(199, 2) === 'MASUK / KELUAR HARI INI', 'label total & mutasi');
cek(v(198, 4) === '=SUM(D4:D196)', 'total STOK Abu: ' + v(198, 4));
cek(v(198, 3) === '=SUMIF($D$3:$AY$3,"STOK",D198:AY198)', 'total unit: ' + v(198, 3));
cek(v(199, 5).startsWith("=SUMIFS('Log Stok'!$H:$H,'Log Stok'!$B:$B,\"Stok UC Sistem\",'Log Stok'!$F:$F,D$2,'Log Stok'!$G:$G,\"IN\""), 'mutasi IN: ' + v(199, 5));
cek(v(199, 6).includes('"OUT"') && v(199, 4) === '', 'mutasi OUT & STOK kosong');
cek(v(198, 52) === '=SUM(AZ4:AZ196)' && v(198, 56) === '=SUM(BD4:BD196)', 'total value');
cek(sh.frozenRows === 3 && sh.frozenCols === 2, 'freeze');
const dvIn = sh.peek(4, 5).dv, dvStok = sh.peek(4, 4).dv, dvOut = sh.peek(4, 6).dv;
cek(dvIn && dvIn.f === '=AND(ISNUMBER(E4),E4>0,E4=INT(E4))' && dvOut === dvIn && !dvIn.invalid, 'validasi IN/OUT: ' + (dvIn && dvIn.f));
cek(dvStok && dvStok.f === '=AND(ISNUMBER(D4),D4>=0,D4=INT(D4))', 'validasi STOK');
// migrasi ulang ditolak
ctx.__alerts.length = 0; ctx.migrasiStokUC();
cek(/sudah ada/.test(ctx.__alerts[0] || ''), 'migrasi ulang ditolak');

// ---------- trigger
ctx.aktifkanInputOtomatis(); ctx.aktifkanInputOtomatis();
cek(ctx.__triggers.length === 1, 'trigger tidak dobel');

// ---------- edit
const log = ss.getSheetByName('Log Stok');
const nLog = () => log.getLastRow() - 1;
function edit(r, c, nilai, extra = {}) {
  sh.getRange(r, c).setValue(nilai);
  ctx.prosesInputStok(Object.assign({ range: sh.getRange(r, c), source: ss, value: nilai }, extra));
}
function paste(r, c, arr) {
  sh.getRange(r, c, arr.length, arr[0].length).setValues(arr);
  ctx.prosesInputStok({ range: sh.getRange(r, c, arr.length, arr[0].length), source: ss });
}
const D = 4, E = 5, F = 6, G = 7, H = 8, I = 9;

edit(4, E, 5);                                        // IN 5 Brio Abu: 39 -> 44
cek(v(4, D) === 44 && v(4, E) === '' && nLog() === 1, 'IN 5: stok ' + v(4, D));
const l1 = log.getRange(2, 1, 1, 12).getValues()[0];
cek(l1[1] === 'Stok UC Sistem' && l1[2] === 4 && l1[3] === 'Honda Brio' && l1[4] === 'HND-BRI-UA-R-G1' && l1[5] === 'Abu-abu' &&
  l1[6] === 'IN' && l1[7] === 5 && l1[8] === 39 && l1[9] === 44 && Object.prototype.toString.call(l1[0]) === '[object Date]', 'isi log IN: ' + JSON.stringify(l1));

edit(4, I, 3);                                        // OUT 3 Brio Hitam: 30 -> 27
cek(v(4, G) === 27 && v(4, I) === '', 'OUT 3: stok ' + v(4, G));

ctx.prosesInputStok({ range: sh.getRange(4, I), source: ss });   // trigger ganda: sel sudah kosong
cek(v(4, G) === 27 && nLog() === 2, 'trigger ganda tidak menghitung dobel');

edit(4, I, 100);                                      // OUT > stok: ditolak
cek(v(4, G) === 27 && v(4, I) === 100 && sh.peek(4, I).bg === '#e06666' && /DITOLAK/.test(sh.peek(4, I).note) && nLog() === 3,
  'OUT berlebih ditolak');
ctx.prosesInputStok({ range: sh.getRange(4, I), source: ss });   // trigger ganda pada sel ditolak
cek(nLog() === 3, 'penolakan tidak dicatat dobel');
edit(4, I, '');                                       // hapus -> reset warna
cek(sh.peek(4, I).bg === '#f4cccc' && sh.peek(4, I).note === '' && v(4, G) === 27, 'hapus sel ditolak -> reset');

edit(4, E, 'abc');  cek(v(4, D) === 44 && /angka bulat/.test(sh.peek(4, E).note), 'teks ditolak');
edit(4, E, 1.5);    cek(v(4, D) === 44 && sh.peek(4, E).bg === '#e06666', 'desimal ditolak');
edit(4, E, -2);     cek(v(4, D) === 44 && sh.peek(4, E).bg === '#e06666', 'negatif ditolak');
edit(4, E, ' 7 ');  cek(v(4, D) === 51 && v(4, E) === '' && sh.peek(4, E).bg === '#d9ead3', 'string angka diterima: ' + v(4, D));

paste(5, E, [[2], [3]]);                              // paste 2 baris
cek(v(5, D) === 26 && v(6, D) === 10, 'paste multi-baris: ' + v(5, D) + ',' + v(6, D));

paste(7, D, [[10, 2, 1]]);                            // paste STOK+IN+OUT warna sama: 10 +2 -1
cek(v(7, D) === 11, 'paste STOK+IN+OUT: ' + v(7, D));
const lk = log.getRange(log.getLastRow() - 2, 7, 3, 4).getValues();
cek(lk[0][0] === 'KOREKSI' && lk[0][3] === 10 && lk[0][2] === '' && lk[1][0] === 'IN' && lk[2][0] === 'OUT', 'log koreksi multi: ' + JSON.stringify(lk));

edit(8, D, 20, { oldValue: '16' });                   // koreksi manual 1 sel
const lk2 = log.getRange(log.getLastRow(), 7, 1, 4).getValues()[0];
cek(v(8, D) === 20 && lk2[0] === 'KOREKSI' && lk2[2] === 16 && lk2[3] === 20, 'koreksi manual: ' + JSON.stringify(lk2));

const sebelum = nLog();
edit(4, 52, 123);  cek(nLog() === sebelum, 'edit kolom value diabaikan');
edit(2, E, 'x');   cek(nLog() === sebelum, 'edit header diabaikan'); sh.getRange(2, E).setValue('');
edit(198, E, 5);   cek(nLog() === sebelum && v(198, E) === 5, 'edit baris total diabaikan'); sh.getRange(198, E).setValue('');
edit(197, E, 5);   cek(nLog() === sebelum && /tanpa nama/.test(sh.peek(197, E).note), 'baris kosong ditolak');
edit(4, 2, 'Honda Brio X'); cek(nLog() === sebelum, 'edit nama diabaikan'); sh.getRange(4, 2).setValue('Honda Brio ');

edit(4, 6, 44);                                       // OUT persis = stok -> 0 boleh? stok Brio Abu 51
cek(v(4, D) === 7, 'OUT 44 dari 51: ' + v(4, D));
edit(4, 6, 7);  cek(v(4, D) === 0, 'OUT habis -> 0');

edit(30, 4 + 3 * 15 + 1, 2);                          // IN Exclusive baris kosong-stok
cek(v(30, 4 + 3 * 15) === 2, 'IN ke STOK kosong: ' + v(30, 4 + 3 * 15));

// lock gagal
const b = siapkan({ lockGagal: true });
b.ctx.migrasiStokUC();
const sh2 = b.ss.getSheetByName('Stok UC Sistem');
sh2.getRange(4, E).setValue(5);
b.ctx.prosesInputStok({ range: sh2.getRange(4, E, 1, 2), source: b.ss });
cek(sh2.peek(4, D).v === 39 && /sibuk/.test(sh2.peek(4, E).note) && !sh2.peek(4, F).note, 'lock gagal: input tetap, ditandai');

// kunci
ctx.__alerts.length = 0; ctx.kunciKolomStok(); ctx.kunciKolomStok();
const prot = sh.protections.filter(p => !p.removed);
cek(prot.length === 1 && prot[0].unprot.length === 32 && prot[0].editors.join() === 'owner@x', 'proteksi: ' + prot.length + ' ' + (prot[0] && prot[0].unprot.length));
cek(prot[0].unprot[0].r === 4 && prot[0].unprot[0].nr === 194 && prot[0].unprot[0].c === 5, 'area bebas E4:E197');
console.log('ALERT kunci:', ctx.__alerts.join(' / '));
ctx.__alerts.length = 0; ctx.cekStatus(); console.log('STATUS:', ctx.__alerts[0].replace(/\n/g, ' / '));

// log melebihi baris maksimum
const penuh = log.getLastRow(); log.maxRows = penuh;
edit(4, E, 1);
cek(v(4, D) === 1 && log.getLastRow() === penuh + 1 && log.maxRows > penuh, 'log tumbuh melewati batas baris');

console.log('Toast terakhir:', ss.toasts.slice(-1)[0]);
console.log(`\n${lulus} lulus, ${gagal} gagal`);

// ekspor untuk dihitung LibreOffice
const dump = {};
for (const s of ss.sheets) { const o = {}; for (const [k, x] of s.cells) if (x.v !== '' || x.f) o[k] = x.f || (Object.prototype.toString.call(x.v) === '[object Date]' ? { date: x.v.toISOString() } : x.v); dump[s.name] = o; }
fs.writeFileSync(path.join(__dirname, 'hasil.json'), JSON.stringify(dump));
process.exit(gagal ? 1 : 0);
