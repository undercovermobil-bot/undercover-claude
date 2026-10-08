/**
 * SISTEM STOK OTOMATIS — Google Sheets + Apps Script
 *
 * Cara kerja:
 *   - Tiap warna punya 3 kolom: STOK | IN | OUT.
 *   - Staf ketik angka di IN atau OUT lalu Enter.
 *   - Script menambah/mengurangi STOK, mengosongkan sel IN/OUT,
 *     dan mencatat mutasi ke sheet "Log Stok".
 *   - OUT melebihi stok ditolak (sel merah + catatan), stok tidak berubah.
 *
 * Berlaku untuk sheet "Stok Cover UC" dan "Stok Cover STP" (KONFIG.SISTEM).
 * Pasang: lihat PANDUAN.md di folder yang sama.
 *
 * PENTING: jangan buat fungsi bernama onEdit di project ini.
 * Handler sengaja bernama prosesInputStok dan dipasang sebagai
 * trigger installable (menu "2. Aktifkan input otomatis").
 */

const KONFIG = {
  // nama  : sheet yang dipakai staf (setelah migrasi berformat STOK|IN|OUT)
  // arsip : nama baru untuk sheet lama saat migrasi (isinya tidak diubah)
  // log   : sheet riwayat mutasi khusus sheet ini (terbaru di baris 2, paling atas)
  // barisAkhir hanya cadangan; migrasi mencari sendiri baris produk terakhir
  //   (baris sebelum label "OUT"/"IN" di kolom B).
  // tanpaValue: grup yang memang tidak dijual di toko itu (tidak dilaporkan "tanpa harga").
  // warnaTambahan: warna baru yang belum ada di sheet lama. Dibuat kosong (stok 0) saat migrasi,
  //   diletakkan setelah warna `setelah`, ikut grup Value warna itu (harga per baris sama).
  SISTEM: [
    { nama: 'Stok Cover UC', arsip: 'Stok Cover UC (lama)', log: 'Log Stok UC', barisAwal: 4, barisAkhir: 196,
      tanpaValue: [], warnaTambahan: [] },
    { nama: 'Stok Cover STP', arsip: 'Stok Cover STP (lama)', log: 'Log Stok STP', barisAwal: 4, barisAkhir: 107,
      tanpaValue: ['Exclusive'], warnaTambahan: [{ nama: 'Orange', setelah: 'Hijau Army' }] },
  ],
  BARIS_DATA: 4,            // baris produk pertama di sheet sistem
  JUMLAH_WARNA: 16,         // jumlah warna di sheet LAMA (format IN/OUT)
  LABEL_TOTAL: 'TOTAL STOK',
  LABEL_MUTASI: 'MASUK / KELUAR HARI INI',
  ZONA_WAKTU: 'Asia/Jakarta',   // zona waktu file + jam di Log Stok (WIB)
  IZINKAN_STOK_MINUS: false,
  FORMAT_STOK: '0;-0;;@',       // angka 0 tidak ditampilkan (sel tampak kosong); nilainya tetap 0
  FORMAT_ANGKA: '0',            // IN / OUT
  FORMAT_WAKTU: 'dd/MM/yyyy HH:mm:ss',
  MAKS_QTY: 9999,               // batas IN/OUT/STOK per sel; sekaligus menolak tanggal yang terketik ("1/2" = 46024)
  WARNA_SEL: { ERROR: '#e06666', HEADER: '#cfe2f3', BANNER_BG: '#00ffff', BANNER_FG: '#ff0000' },
  // Warna header & kolom STOK per warna cover, dicocokkan dari nama warna (huruf kecil, mengandung `kunci`).
  // Yang cocok pertama dipakai. Kolom IN / OUT sengaja tanpa warna. Nilai bg = sama dengan sheet asli.
  PALET: [
    { kunci: 'hitam', bg: '#000000', fg: '#ffffff' },
    { kunci: 'biru', bg: '#0000ff', fg: '#ffffff' },
    { kunci: 'merah', bg: '#ff0000', fg: '#ffffff' },
    { kunci: 'hijau', bg: '#38761d', fg: '#ffffff' },
    { kunci: 'orange', bg: '#ff9900', fg: '#000000' },
    { kunci: 'abu', bg: '#999999', fg: '#000000' },
    { kunci: 'exclusive', bg: '#d9d9d9', fg: '#000000' },
    { kunci: 'premium', bg: '#efefef', fg: '#000000' },
    { kunci: 'transparan', bg: '#efefef', fg: '#000000' },
  ],
  DESKRIPSI_PROTEKSI: 'Sistem stok: hanya IN/OUT yang boleh diisi',
};

// Urutan warna di sheet: 0-4 Reguler, 5-13 Strip, 14 Premium (STP: Transparan), 15 Exclusive.
// Nama grup hanya cadangan; label diambil dari header baris 3 sheet lama.
const GRUP_VALUE = [
  { nama: 'Reguler', warna: [0, 1, 2, 3, 4] },
  { nama: 'Strip', warna: [5, 6, 7, 8, 9, 10, 11, 12, 13] },
  { nama: 'Premium', warna: [14] },
  { nama: 'Exclusive', warna: [15] },
];

const HEADER_LOG = ['Waktu', 'Sheet', 'Baris', 'Produk', 'Kode SKU', 'Warna', 'Jenis',
  'Qty', 'Stok Sebelum', 'Stok Sesudah', 'User', 'Keterangan'];

// ---------------------------------------------------------------- menu

function onOpen() {
  SpreadsheetApp.getUi().createMenu('📦 Sistem Stok')
    .addItem('1a. Ubah "' + KONFIG.SISTEM[0].nama + '" ke format STOK/IN/OUT', 'migrasiStokUC')
    .addItem('1b. Ubah "' + KONFIG.SISTEM[1].nama + '" ke format STOK/IN/OUT', 'migrasiStokSTP')
    .addItem('2. Aktifkan input otomatis', 'aktifkanInputOtomatis')
    .addItem('3. Kunci kolom STOK (opsional, pemilik file)', 'kunciKolomStok')
    .addSeparator()
    .addItem('Cek status', 'cekStatus')
    .addItem('Arsipkan log bulan lalu (opsional)', 'arsipkanLogBulanLalu')
    .addItem('Setel zona waktu file ke WIB', 'setelZonaWaktu')
    .addItem('Matikan input otomatis', 'matikanInputOtomatis')
    .addToUi();
}

// ---------------------------------------------------------------- handler edit

/**
 * Dipanggil trigger installable "On edit".
 * Nilai sel dibaca ulang SETELAH lock didapat, jadi trigger ganda
 * (mis. 2 orang sama-sama memasang trigger) tidak menghitung dobel:
 * eksekusi kedua menemukan sel IN/OUT sudah kosong.
 */
function prosesInputStok(e) {
  if (!e || !e.range) return;
  const sheet = e.range.getSheet();
  const namaSheet = sheet.getName();
  const cfg = KONFIG.SISTEM.find(s => s.nama === namaSheet);
  if (!cfg) return;

  const r0 = e.range.getRow();
  const c0 = e.range.getColumn();
  const r1 = r0 + e.range.getNumRows() - 1;
  const c1 = c0 + e.range.getNumColumns() - 1;
  if (r1 < KONFIG.BARIS_DATA) return;

  const peta = bacaPeta_(sheet);
  const barisAwal = Math.max(r0, KONFIG.BARIS_DATA);
  const barisAkhir = Math.min(r1, peta.barisTotal - 1);
  const kolomAkhir = Math.min(c1, peta.kolomTerakhir);
  if (barisAwal > barisAkhir || c0 > kolomAkhir) return;
  let relevan = false;
  for (let c = c0; c <= kolomAkhir; c++) if (peta.kolom[c]) relevan = true;
  if (!relevan) return;

  const lock = LockService.getDocumentLock();
  if (!lock.tryLock(25000)) {
    const isi = sheet.getRange(barisAwal, c0, barisAkhir - barisAwal + 1, kolomAkhir - c0 + 1).getValues();
    for (let r = barisAwal; r <= barisAkhir; r++) {
      for (let c = c0; c <= kolomAkhir; c++) {
        const info = peta.kolom[c];
        if (info && isi[r - barisAwal][c - c0] !== '') {
          tandaiError_(sheet.getRange(r, c), info.jenis === 'STOK'
            ? 'Sistem sibuk: koreksi STOK ini belum tercatat di Log. Ketik ulang angkanya.'
            : 'Sistem sibuk, belum diproses. Hapus lalu ketik ulang.');
        }
      }
    }
    return;
  }

  try {
    const ss = e.source || SpreadsheetApp.getActiveSpreadsheet();
    // Rekap "hari ini" memakai TODAY() menurut zona file, jam Log memakai WIB: samakan.
    if (ss.getSpreadsheetTimeZone() !== KONFIG.ZONA_WAKTU) ss.setSpreadsheetTimeZone(KONFIG.ZONA_WAKTU);
    const blok = sheet.getRange(barisAwal, 1, barisAkhir - barisAwal + 1, peta.kolomTerakhir).getValues();
    const satuSel = r0 === r1 && c0 === c1;
    const user = emailUser_(e);
    const waktu = waktuSerial_(new Date());   // jam WIB sebagai angka, tidak tergantung zona waktu file/script
    const log = [];
    const pesan = [];
    const selesai = [];   // sel IN/OUT yang sudah diproses, dikosongkan setelah dicek ulang

    for (let r = barisAwal; r <= barisAkhir; r++) {
      const baris = blok[r - barisAwal];
      const produk = String(baris[1]).trim();
      const sku = String(baris[2]).trim();

      for (let c = c0; c <= kolomAkhir; c++) {
        const info = peta.kolom[c];
        if (!info) continue;
        const sel = sheet.getRange(r, c);
        const nilai = baris[c - 1];

        // Admin mengetik langsung di kolom STOK (opname / koreksi).
        // Tulisan script sendiri tidak memicu onEdit, jadi ini pasti edit manusia.
        if (info.jenis === 'STOK') {
          const baru = angkaStok_(nilai);
          if (baru === null) {
            tandaiError_(sel, 'STOK harus angka bulat >= 0.');
            continue;
          }
          resetSel_(sel, 'STOK', info.warna);
          const lama = satuSel ? (angkaStok_(e.oldValue === undefined ? '' : e.oldValue)) : '';
          log.push([waktu, namaSheet, r, produk, sku, info.warna, 'KOREKSI', '', lama === null ? '' : lama, baru, user,
            satuSel ? 'Edit langsung kolom STOK' : 'Edit banyak sel sekaligus, stok sebelum tidak terbaca']);
          continue;
        }

        const qty = angkaInput_(nilai);
        if (qty === null) {               // sel dikosongkan
          resetSel_(sel, info.jenis, info.warna);
          continue;
        }
        if (!produk) {
          tandaiError_(sel, 'Baris ini tanpa nama produk, input tidak diproses.');
          continue;
        }
        if (isNaN(qty)) {
          tandaiError_(sel, 'Isi angka bulat 1–' + KONFIG.MAKS_QTY + '.');
          continue;
        }
        const sebelum = angkaStok_(baris[info.kolomStok - 1]);
        if (sebelum === null) {
          tandaiError_(sel, 'Kolom STOK warna ini berisi bukan angka. Perbaiki STOK dulu.');
          continue;
        }
        const sesudah = info.jenis === 'IN' ? sebelum + qty : sebelum - qty;
        if (sesudah < 0 && !KONFIG.IZINKAN_STOK_MINUS) {
          const catatan = 'DITOLAK: OUT ' + qty + ' melebihi stok ' + sebelum +
            '. Stok tidak berubah. Cek fisik barang, lalu hapus/ketik ulang.';
          if (tandaiError_(sel, catatan)) {
            log.push([waktu, namaSheet, r, produk, sku, info.warna, 'DITOLAK', qty, sebelum, sebelum, user,
              'OUT melebihi stok']);
          }
          continue;
        }

        sheet.getRange(r, info.kolomStok).setValue(sesudah);
        baris[info.kolomStok - 1] = sesudah;
        selesai.push({ r: r, c: c, nilai: nilai, sel: sel, jenis: info.jenis, warna: info.warna });
        baris[c - 1] = '';
        log.push([waktu, namaSheet, r, produk, sku, info.warna, info.jenis, qty, sebelum, sesudah, user, '']);
        pesan.push(produk + ' ' + info.warna + ': ' + sebelum + ' → ' + sesudah);
      }
    }

    if (selesai.length) {
      // Staf bisa mengetik ulang di sel yang sama selagi script berjalan: sel yang isinya sudah berubah
      // jangan dihapus; ketikan baru itu diproses eksekusi berikutnya.
      const terkini = sheet.getRange(barisAwal, c0, barisAkhir - barisAwal + 1, kolomAkhir - c0 + 1).getValues();
      selesai.forEach(x => {
        if (terkini[x.r - barisAwal][x.c - c0] === x.nilai) {
          x.sel.clearContent();
          resetSel_(x.sel, x.jenis, x.warna);
        }
      });
    }
    if (log.length) tulisLog_(ss, cfg, log);
    SpreadsheetApp.flush();   // wajib sebelum lock dilepas, supaya eksekusi berikutnya baca nilai terbaru
    if (pesan.length) {
      ss.toast(pesan.slice(0, 5).join('\n') + (pesan.length > 5 ? '\n+' + (pesan.length - 5) + ' lainnya' : ''),
        'Stok diperbarui', 5);
    }
  } finally {
    lock.releaseLock();
  }
}

// ---------------------------------------------------------------- migrasi

function migrasiStokUC() {
  migrasi_(KONFIG.SISTEM[0]);
}

function migrasiStokSTP() {
  migrasi_(KONFIG.SISTEM[1]);
}

/**
 * Sheet lama diganti nama jadi cfg.arsip (isinya tidak diubah),
 * sheet baru format STOK|IN|OUT dibuat dengan nama asli di posisi tab yang sama.
 */
function migrasi_(cfg) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const ui = SpreadsheetApp.getUi();
  if (ss.getSheetByName(cfg.arsip)) {
    ui.alert('"' + cfg.nama + '" sudah pernah dimigrasi (sheet "' + cfg.arsip + '" sudah ada).');
    return;
  }
  const src = ss.getSheetByName(cfg.nama);
  if (!src) {
    ui.alert('Sheet "' + cfg.nama + '" tidak ditemukan.');
    return;
  }
  if (Object.keys(bacaPeta_(src).kolom).length) {
    ui.alert('"' + cfg.nama + '" sudah berformat STOK / IN / OUT.');
    return;
  }

  const W = KONFIG.JUMLAH_WARNA;
  const barisAkhir = cariBarisAkhir_(src, cfg);
  const n = barisAkhir - cfg.barisAwal + 1;
  const namaWarna = src.getRange(2, 4, 1, 2 * W).getValues()[0]
    .filter((_, i) => i % 2 === 0).map(v => String(v).trim());
  const labelValue = src.getRange(3, 4 + 2 * W, 1, GRUP_VALUE.length + 1).getValues()[0]
    .map((v, i) => String(v).trim() || (i < GRUP_VALUE.length ? GRUP_VALUE[i].nama : 'Total Value'));
  let daftar;
  try {
    daftar = susunWarna_(namaWarna, cfg);
  } catch (err) {
    ui.alert(err.message);
    return;
  }
  let lama = src.getRange(cfg.barisAwal, 1, n, 3 + 2 * W).getValues();
  let fLama = src.getRange(cfg.barisAwal, 4 + 2 * W, n, GRUP_VALUE.length + 1).getFormulas();

  // OUT yang masih terisi: menurut alur lama, IN biasanya SUDAH dikurangi OUT.
  const outTerisi = [];
  lama.forEach((row, i) => {
    for (let k = 0; k < W; k++) {
      const o = row[4 + 2 * k];
      if (typeof o === 'number' && o !== 0) {
        outTerisi.push('baris ' + (cfg.barisAwal + i) + ' ' + String(row[1]).trim() + ' – ' + namaWarna[k] + ': OUT ' + o);
      }
    }
  });
  let tanya = 'Produk "' + cfg.nama + '" baris ' + cfg.barisAwal + '–' + barisAkhir + ' (' + n + ' produk) ' +
    'dipindah ke format STOK / IN / OUT.\n\n' +
    '• Sheet lama diganti nama jadi "' + cfg.arsip + '" (isinya tidak diubah, termasuk bagian di bawah baris ' +
    barisAkhir + ').\n• Sheet baru bernama "' + cfg.nama + '".\n• STOK awal = angka kolom IN sekarang.';
  daftar.forEach((w, i) => {
    if (w.kSumber === null) {
      tanya += '\n• Warna baru: ' + w.nama + ' (setelah ' + daftar[i - 1].nama + ', stok awal kosong, value ikut harga ' +
        labelValue[w.gi] + ').';
    }
  });
  if (outTerisi.length) {
    tanya += '\n\nPERHATIAN: ' + outTerisi.length + ' sel OUT masih terisi. Sistem menganggap IN sudah dikurangi OUT ' +
      '(sesuai alur lama). Kalau belum, batalkan dan rapikan dulu.\n' +
      outTerisi.slice(0, 8).join('\n') + (outTerisi.length > 8 ? '\n…' : '');
  }
  const zonaLama = ss.getSpreadsheetTimeZone();
  if (zonaLama !== KONFIG.ZONA_WAKTU) {
    tanya += '\n• Zona waktu file diubah dari ' + zonaLama + ' ke ' + KONFIG.ZONA_WAKTU +
      ' (supaya jam Log Stok dan rekap "hari ini" sesuai WIB). Isi sheet lain tidak berubah.';
  }
  tanya += '\n\nLanjutkan?';
  if (ui.alert('Migrasi ' + cfg.nama, tanya, ui.ButtonSet.YES_NO) !== ui.Button.YES) return;
  if (zonaLama !== KONFIG.ZONA_WAKTU) ss.setSpreadsheetTimeZone(KONFIG.ZONA_WAKTU);
  // Dialog bisa terbuka lama; staf lain mungkin mengubah sheet lama. Pakai data terbaru.
  lama = src.getRange(cfg.barisAwal, 1, n, 3 + 2 * W).getValues();
  fLama = src.getRange(cfg.barisAwal, 4 + 2 * W, n, GRUP_VALUE.length + 1).getFormulas();

  const peringatan = [];
  siapkanLog_(ss, cfg.log);
  src.setName(cfg.arsip);
  let sh = null;
  try {
    sh = ss.insertSheet(cfg.nama, src.getIndex() - 1);
    bangunSheet_(sh, cfg, { n, daftar, labelValue, lama, fLama, peringatan });
  } catch (err) {
    if (sh) ss.deleteSheet(sh);
    src.setName(cfg.nama);
    ui.alert('Migrasi GAGAL, sheet lama dikembalikan seperti semula.\n\n' + err.message);
    return;
  }

  let selesai = 'Sheet "' + cfg.nama + '" siap: ' + n + ' produk. Sheet lama: "' + cfg.arsip + '".' +
    '\n\nLangkah berikutnya: menu 📦 Sistem Stok → 2. Aktifkan input otomatis (cukup sekali untuk semua sheet).';
  if (peringatan.length) {
    selesai += '\n\nCatatan (' + peringatan.length + '):\n' + peringatan.slice(0, 20).join('\n') +
      (peringatan.length > 20 ? '\n…' : '');
  }
  console.log(selesai);
  ui.alert('Migrasi selesai', selesai, ui.ButtonSet.OK);
}

function bangunSheet_(sh, cfg, d) {
  const W = d.daftar.length;
  const n = d.n;
  const kolStok = k => 4 + 3 * k;
  const kolValue = 4 + 3 * W;
  const totalKolom = kolValue + GRUP_VALUE.length;   // 4 grup + Total Value
  const barisDataAkhir = KONFIG.BARIS_DATA + n - 1;
  const barisTotal = barisDataAkhir + 2;
  const barisMutasi = barisTotal + 1;
  pastikanUkuran_(sh, barisMutasi, totalKolom);

  // Header
  sh.getRange(1, 1).setValue('No');
  sh.getRange(1, 2).setValue('Nama Produk');
  sh.getRange(1, 3).setValue('Kode SKU');
  sh.getRange(1, 4).setValue('STOK dihitung otomatis. Isi angka di kolom IN / OUT lalu Enter. Jangan ketik di kolom STOK.');
  sh.getRange(1, kolValue).setValue('Value');
  sh.getRange(1, 1, 3, 1).merge();
  sh.getRange(1, 2, 3, 1).merge();
  sh.getRange(1, 3, 3, 1).merge();
  sh.getRange(1, 4, 1, 3 * W).merge();
  sh.getRange(1, kolValue, 2, totalKolom - kolValue + 1).merge();
  const label3 = [];
  for (let k = 0; k < W; k++) {
    sh.getRange(2, kolStok(k)).setValue(d.daftar[k].nama);
    sh.getRange(2, kolStok(k), 1, 3).merge();
    label3.push('STOK', 'IN', 'OUT');
  }
  sh.getRange(3, 4, 1, label3.length + d.labelValue.length).setValues([label3.concat(d.labelValue)]);

  // Data
  const data = d.lama.map((row, i) => {
    const out = [row[0], row[1], row[2]];
    for (let k = 0; k < W; k++) {
      const w = d.daftar[k];
      const v = w.kSumber === null ? '' : row[3 + 2 * w.kSumber];
      if (v !== '' && typeof v !== 'number') {
        d.peringatan.push('Baris ' + (cfg.barisAwal + i) + ' ' + w.nama + ': IN bukan angka ("' + v + '"), dikosongkan.');
      }
      out.push(typeof v === 'number' ? v : '', '', '');
    }
    return out;
  });
  sh.getRange(KONFIG.BARIS_DATA, 1, n, 3 + 3 * W).setValues(data);

  // Value: harga per baris diambil dari formula lama, referensi diganti ke kolom STOK.
  const tanpaHarga = GRUP_VALUE.map(() => []);
  const fBaru = d.fLama.map((f, i) => {
    const r = KONFIG.BARIS_DATA + i;
    const rLama = cfg.barisAwal + i;
    const produk = String(d.lama[i][1]).trim();
    const hasil = GRUP_VALUE.map((g, gi) => {
      if (!f[gi]) {
        tanpaHarga[gi].push(rLama);
        return '';
      }
      const harga = hargaDariFormula_(f[gi]);
      if (harga === null) {
        d.peringatan.push('Baris ' + rLama + ' ' + produk + ': formula ' + d.labelValue[gi] + ' lama rusak (' + f[gi] +
          '), dikosongkan. Isi harga manual.');
        return '';
      }
      if (!formulaLamaStandar_(f[gi], g.warna.map(k => 4 + 2 * k), rLama)) {
        d.peringatan.push('DIPERBAIKI baris ' + rLama + ' ' + produk + ': formula ' + d.labelValue[gi] + ' lama ' + f[gi] +
          ' → sekarang semua warna ' + d.labelValue[gi] + ' baris ini × ' + harga + ' (sama seperti baris lain).');
      }
      const refs = [];
      d.daftar.forEach((w, k) => { if (w.gi === gi) refs.push(huruf_(kolStok(k)) + r); });
      return '=(' + refs.join('+') + ')*' + harga;
    });
    hasil.push(f[GRUP_VALUE.length] ? '=SUM(' + huruf_(kolValue) + r + ':' + huruf_(kolValue + GRUP_VALUE.length - 1) + r + ')' : '');
    return hasil;
  });
  sh.getRange(KONFIG.BARIS_DATA, kolValue, n, GRUP_VALUE.length + 1).setFormulas(fBaru);
  tanpaHarga.forEach((rows, gi) => {
    if (rows.length && (cfg.tanpaValue || []).indexOf(d.labelValue[gi]) < 0) {
      d.peringatan.push(d.labelValue[gi] + ': ' + rows.length + ' baris tanpa formula harga, value kosong' +
        (rows.length <= 15 ? ' (baris ' + rows.join(', ') + ')' : '') + '.');
    }
  });

  // Total + mutasi hari ini. SUM sengaja sampai baris kosong di bawah produk: produk baru ditambah dengan
  // "Insert row above" pada baris kosong itu, sehingga rentang SUM ikut melebar.
  const akhirStok = huruf_(kolValue - 1);
  const q = "'" + cfg.log + "'!";
  const fTotal = ['=SUMIF($D$3:$' + akhirStok + '$3,"STOK",D' + barisTotal + ':' + akhirStok + barisTotal + ')'];
  const fMutasi = [''];
  for (let k = 0; k < W; k++) {
    const hs = huruf_(kolStok(k));
    fTotal.push('=SUM(' + hs + KONFIG.BARIS_DATA + ':' + hs + (barisDataAkhir + 1) + ')', '', '');
    fMutasi.push('');
    ['IN', 'OUT'].forEach(jenis => {
      fMutasi.push('=SUMIFS(' + q + '$H:$H,' + q + '$F:$F,' + hs + '$2,' +
        q + '$G:$G,"' + jenis + '",' + q + '$A:$A,">="&TODAY(),' + q + '$A:$A,"<"&(TODAY()+1))');
    });
  }
  for (let c = kolValue; c <= totalKolom; c++) {
    const h = huruf_(c);
    fTotal.push('=SUM(' + h + KONFIG.BARIS_DATA + ':' + h + (barisDataAkhir + 1) + ')');
    fMutasi.push('');
  }
  sh.getRange(barisTotal, 2).setValue(KONFIG.LABEL_TOTAL);
  sh.getRange(barisMutasi, 2).setValue(KONFIG.LABEL_MUTASI);
  sh.getRange(barisTotal, 3, 1, fTotal.length).setFormulas([fTotal]);
  sh.getRange(barisMutasi, 3, 1, fMutasi.length).setFormulas([fMutasi]);

  // Format
  sh.getRange(1, 1, 3, totalKolom).setFontWeight('bold').setHorizontalAlignment('center')
    .setVerticalAlignment('middle').setWrap(true);
  sh.getRange(1, 4, 1, 3 * W).setBackground(KONFIG.WARNA_SEL.BANNER_BG).setFontColor(KONFIG.WARNA_SEL.BANNER_FG);
  for (let k = 0; k < W; k++) {
    const c = kolStok(k);
    const w = warnaCover_(d.daftar[k].nama);   // IN / OUT sengaja tanpa warna
    if (w) {
      sh.getRange(2, c, 1, 3).setBackground(w.bg).setFontColor(w.fg);
      sh.getRange(3, c).setBackground(w.bg).setFontColor(w.fg);
      sh.getRange(KONFIG.BARIS_DATA, c, n, 1).setBackground(w.bg).setFontColor(w.fg);
    }
    sh.getRange(KONFIG.BARIS_DATA, c, n, 1).setFontWeight('bold');
    sh.getRange(2, c, barisMutasi - 1, 3).setBorder(null, true, null, true, null, null);
    sh.getRange(KONFIG.BARIS_DATA, c, n, 1).setDataValidation(aturanAngka_(huruf_(c) + KONFIG.BARIS_DATA, true));
    sh.getRange(KONFIG.BARIS_DATA, c + 1, n, 2).setDataValidation(aturanAngka_(huruf_(c + 1) + KONFIG.BARIS_DATA, false));
  }
  sh.getRange(KONFIG.BARIS_DATA, 4, barisMutasi - KONFIG.BARIS_DATA + 1, 3 * W).setHorizontalAlignment('center');
  sh.getRange(KONFIG.BARIS_DATA, 4, n, 3 * W).setNumberFormat(KONFIG.FORMAT_ANGKA);   // angka bulat; cegah format tanggal menempel
  for (let k = 0; k < W; k++) sh.getRange(KONFIG.BARIS_DATA, kolStok(k), n, 1).setNumberFormat(KONFIG.FORMAT_STOK);   // STOK 0 tampil kosong
  sh.getRange(KONFIG.BARIS_DATA, kolValue, barisMutasi - KONFIG.BARIS_DATA + 1, totalKolom - kolValue + 1)
    .setNumberFormat('#,##0');
  sh.getRange(barisTotal, 3).setNumberFormat('#,##0" unit"');
  sh.getRange(barisTotal, 1, 2, totalKolom).setFontWeight('bold');
  sh.setColumnWidth(1, 40);
  sh.setColumnWidth(2, 190);
  sh.setColumnWidth(3, 130);
  sh.setColumnWidths(4, 3 * W, 48);
  sh.setColumnWidths(kolValue, totalKolom - kolValue + 1, 110);
  sh.setFrozenRows(3);
  sh.setFrozenColumns(2);
}

// ---------------------------------------------------------------- trigger & proteksi

function aktifkanInputOtomatis() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const ui = SpreadsheetApp.getUi();
  const ada = ScriptApp.getProjectTriggers().filter(t => t.getHandlerFunction() === 'prosesInputStok');
  if (ada.length) {
    ui.alert('Input otomatis sudah aktif (' + ada.length + ' trigger milik akun ini).');
    return;
  }
  ScriptApp.newTrigger('prosesInputStok').forSpreadsheet(ss).onEdit().create();
  if (ss.getSpreadsheetTimeZone() !== KONFIG.ZONA_WAKTU) ss.setSpreadsheetTimeZone(KONFIG.ZONA_WAKTU);
  let pesan = 'Input otomatis AKTIF.\nTrigger berjalan atas nama akun: ' + Session.getEffectiveUser().getEmail() +
    '\n\nCoba: ketik 1 di kolom IN salah satu produk lalu Enter. STOK harus bertambah 1 dan sel IN kosong lagi.';
  const pemilik = ss.getOwner();
  if (pemilik && pemilik.getEmail() !== Session.getEffectiveUser().getEmail()) {
    pesan += '\n\nCATATAN: akun ini bukan pemilik file (' + pemilik.getEmail() + '). ' +
      'Kalau kolom STOK dikunci, pasang trigger dari akun pemilik.';
  }
  ui.alert(pesan);
}

function matikanInputOtomatis() {
  let n = 0;
  ScriptApp.getProjectTriggers().forEach(t => {
    if (t.getHandlerFunction() === 'prosesInputStok') {
      ScriptApp.deleteTrigger(t);
      n++;
    }
  });
  SpreadsheetApp.getUi().alert(n + ' trigger dihapus. Input IN/OUT tidak lagi diproses otomatis.');
}

/**
 * Kunci seluruh sheet sistem kecuali area IN/OUT, dan kunci sheet log.
 * Jalankan dari akun PEMILIK file. Editor lain tetap bisa isi IN/OUT;
 * hanya pemilik (dan editor yang ditambahkan manual di Data → Sheet & range dilindungi)
 * yang bisa ubah STOK langsung.
 */
function kunciKolomStok() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const ui = SpreadsheetApp.getUi();
  const me = Session.getEffectiveUser();
  const hasil = [];

  KONFIG.SISTEM.forEach(cfg => {
    const sh = ss.getSheetByName(cfg.nama);
    if (!sh) return;
    const peta = bacaPeta_(sh);
    if (!Object.keys(peta.kolom).length) {
      hasil.push(cfg.nama + ': belum dimigrasi, dilewati');
      return;
    }
    hapusProteksiLama_(sh);
    const bebas = [];
    Object.keys(peta.kolom).forEach(c => {
      if (peta.kolom[c].jenis !== 'STOK') {
        bebas.push(sh.getRange(KONFIG.BARIS_DATA, Number(c), peta.barisTotal - KONFIG.BARIS_DATA, 1));
      }
    });
    const p = sh.protect().setDescription(KONFIG.DESKRIPSI_PROTEKSI);
    p.setUnprotectedRanges(bebas);
    batasiKePemilik_(p, me);
    hasil.push(cfg.nama + ': dikunci, ' + bebas.length + ' kolom IN/OUT tetap bisa diisi');
  });

  KONFIG.SISTEM.forEach(cfg => {
    ss.getSheets().filter(x => x.getName() === cfg.log || x.getName().indexOf('Arsip ' + cfg.log + ' ') === 0).forEach(log => {
      hapusProteksiLama_(log);
      batasiKePemilik_(log.protect().setDescription(KONFIG.DESKRIPSI_PROTEKSI), me);
      hasil.push(log.getName() + ': dikunci penuh');
    });
  });
  ui.alert(hasil.length ? hasil.join('\n') : 'Sheet sistem belum ada. Jalankan langkah 1 dulu.');
}

/** Zona waktu file ke WIB. Baris Log yang sudah tercatat tidak berubah (jamnya tetap seperti yang tertulis). */
function setelZonaWaktu() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const lama = ss.getSpreadsheetTimeZone();
  ss.setSpreadsheetTimeZone(KONFIG.ZONA_WAKTU);
  SpreadsheetApp.getUi().alert('Zona waktu file: ' + lama + ' → ' + KONFIG.ZONA_WAKTU +
    '.\nBaris Log Stok yang sudah ada tidak berubah. Kalau itu hanya data uji, hapus saja barisnya.');
}

function cekStatus() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const t = ScriptApp.getProjectTriggers().filter(x => x.getHandlerFunction() === 'prosesInputStok').length;
  const baris = ['Trigger aktif (akun ini): ' + t + (t > 1 ? '  ← lebih dari 1, hapus lewat menu Matikan lalu aktifkan lagi' : '')];
  KONFIG.SISTEM.forEach(cfg => {
    const sh = ss.getSheetByName(cfg.nama);
    const status = !sh ? 'TIDAK ADA' : Object.keys(bacaPeta_(sh).kolom).length ? 'format STOK/IN/OUT (aktif)' : 'format lama (belum dimigrasi)';
    baris.push('"' + cfg.nama + '": ' + status);
  });
  KONFIG.SISTEM.forEach(cfg => {
    const log = ss.getSheetByName(cfg.log);
    baris.push('"' + cfg.log + '": ' + (log ? Math.max(log.getLastRow() - 1, 0) + ' baris mutasi' : 'BELUM ada'));
  });
  const zona = ss.getSpreadsheetTimeZone();
  baris.push('Zona waktu file: ' + zona + (zona === KONFIG.ZONA_WAKTU ? '' : '  ← bukan ' + KONFIG.ZONA_WAKTU + ', pilih menu "Setel zona waktu file ke WIB"'));
  SpreadsheetApp.getUi().alert(baris.join('\n'));
}

// ---------------------------------------------------------------- helper

/** Peta kolom dari header baris 2 (warna) dan 3 (STOK/IN/OUT). Tahan sisip kolom/baris. */
function bacaPeta_(sheet) {
  const lastCol = sheet.getLastColumn();
  const lastRow = sheet.getLastRow();
  const head = sheet.getRange(2, 1, 2, lastCol).getValues();
  const kolom = {};
  let stokCol = 0;
  let warna = '';
  let kolomTerakhir = 0;
  for (let c = 1; c <= lastCol; c++) {
    const label = String(head[1][c - 1]).trim().toUpperCase();
    if (label === 'STOK') {
      stokCol = c;
      warna = String(head[0][c - 1]).trim();
      kolom[c] = { jenis: 'STOK', warna: warna, kolomStok: c };
      kolomTerakhir = c;
    } else if ((label === 'IN' || label === 'OUT') && stokCol && c - stokCol <= 2) {
      kolom[c] = { jenis: label, warna: warna, kolomStok: stokCol };
      kolomTerakhir = c;
    }
  }
  let barisTotal = lastRow + 1;
  if (lastRow >= KONFIG.BARIS_DATA) {
    const b = sheet.getRange(KONFIG.BARIS_DATA, 2, lastRow - KONFIG.BARIS_DATA + 1, 1).getValues();
    for (let i = 0; i < b.length; i++) {
      if (String(b[i][0]).trim().toUpperCase() === KONFIG.LABEL_TOTAL) {
        barisTotal = KONFIG.BARIS_DATA + i;
        break;
      }
    }
  }
  return { kolom: kolom, barisTotal: barisTotal, kolomTerakhir: kolomTerakhir };
}

/** null = kosong, NaN = tidak valid, selain itu bilangan bulat > 0. */
function angkaInput_(v) {
  if (v === '' || v === null || v === undefined) return null;
  if (typeof v === 'string') {
    const s = v.trim();
    if (s === '') return null;
    if (!/^\d+$/.test(s)) return NaN;
    v = Number(s);
  }
  if (typeof v !== 'number' || !isFinite(v) || v <= 0 || Math.floor(v) !== v || v > KONFIG.MAKS_QTY) return NaN;
  return v;
}

/** Stok kosong = 0. null = tidak valid. */
function angkaStok_(v) {
  if (v === '' || v === null || v === undefined) return 0;
  if (typeof v === 'string') {
    const s = v.trim();
    if (s === '') return 0;
    if (!/^-?\d+$/.test(s)) return null;
    v = Number(s);
  }
  if (typeof v !== 'number' || !isFinite(v) || Math.floor(v) !== v) return null;
  if (v < 0 && !KONFIG.IZINKAN_STOK_MINUS) return null;
  return v;
}

/** Return true kalau catatan baru dipasang (bukan pengulangan catatan yang sama). */
function tandaiError_(sel, catatan) {
  if (sel.getNote() === catatan) return false;
  sel.setBackground(KONFIG.WARNA_SEL.ERROR).setNote(catatan);
  return true;
}

/**
 * Jam sekarang menurut KONFIG.ZONA_WAKTU sebagai nomor seri Sheets (hari sejak 30-12-1899, pecahan = jam).
 * Ditulis sebagai angka supaya tampilannya pasti WIB, berapa pun zona waktu file/script.
 */
function waktuSerial_(d, zona) {
  const p = Utilities.formatDate(d, zona || KONFIG.ZONA_WAKTU, 'yyyy-MM-dd-HH-mm-ss').split('-').map(Number);
  const ms = Date.UTC(p[0], p[1] - 1, p[2], p[3], p[4], p[5]) - Date.UTC(1899, 11, 30);
  return ms / 86400000 + 1e-8;   // +0,9 ms: cegah tampil mundur 1 detik karena pembulatan desimal
}

/** Kembalikan sel ke tampilan normal: STOK = warna cover, IN/OUT = tanpa warna. */
function resetSel_(sel, jenis, warna) {
  const w = jenis === 'STOK' ? warnaCover_(warna) : null;
  sel.setBackground(w ? w.bg : null).setFontColor(w ? w.fg : null).setNumberFormat(jenis === 'STOK' ? KONFIG.FORMAT_STOK : KONFIG.FORMAT_ANGKA).setNote('');
}

/** Warna cover dari nama warna ("Elite Biru" -> biru), atau null kalau tidak dikenal. */
function warnaCover_(nama) {
  const n = String(nama).toLowerCase();
  for (let i = 0; i < KONFIG.PALET.length; i++) {
    if (n.indexOf(KONFIG.PALET[i].kunci) >= 0) return KONFIG.PALET[i];
  }
  return null;
}

/** Mutasi terbaru ditaruh di baris 2 (paling atas), tepat di bawah header. */
function tulisLog_(ss, cfg, rows) {
  const sh = siapkanLog_(ss, cfg.log);
  const n = rows.length;
  if (sh.getMaxRows() < 2) sh.insertRowsAfter(1, 1);
  sh.insertRowsBefore(2, n);
  sh.getRange(2, 1, n, HEADER_LOG.length).clearFormat();   // baris baru bisa mewarisi format header
  sh.getRange(2, 1, n, 1).setNumberFormat(KONFIG.FORMAT_WAKTU);
  sh.getRange(2, 1, n, HEADER_LOG.length).setValues(rows);
}

function siapkanLog_(ss, nama) {
  let sh = ss.getSheetByName(nama);
  if (sh) return sh;
  sh = ss.insertSheet(nama);
  sh.getRange(1, 1, 1, HEADER_LOG.length).setValues([HEADER_LOG])
    .setFontWeight('bold').setBackground(KONFIG.WARNA_SEL.HEADER);
  sh.getRange('A:A').setNumberFormat(KONFIG.FORMAT_WAKTU);
  sh.setFrozenRows(1);
  [140, 100, 45, 190, 130, 90, 70, 50, 100, 100, 170, 200].forEach((w, i) => sh.setColumnWidth(i + 1, w));
  return sh;
}

// ---------------------------------------------------------------- arsip log bulanan

/** Nomor seri waktu dari nilai sel kolom Waktu (angka, atau Date kalau sel berformat tanggal). null = tidak terbaca. */
function waktuNomor_(v, zona) {
  if (typeof v === 'number' && isFinite(v)) return v;
  if (Object.prototype.toString.call(v) === '[object Date]' && !isNaN(v.getTime())) return waktuSerial_(v, zona);
  return null;
}

function bulanDariNomor_(w) {
  const d = new Date(Math.floor(w * 86400000) + Date.UTC(1899, 11, 30));
  return d.getUTCFullYear() + '-' + ('0' + (d.getUTCMonth() + 1)).slice(-2);
}

/**
 * Pindahkan baris Log sebelum bulan ini ke sheet "Arsip <nama log> <yyyy-MM>" (satu sheet per bulan,
 * terbaru di atas). Log hanya menyisakan bulan ini. Rekap "hari ini" tidak terpengaruh.
 */
function arsipkanLogBulanLalu() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const ui = SpreadsheetApp.getUi();
  const zona = ss.getSpreadsheetTimeZone();
  const bulanIni = bulanDariNomor_(waktuSerial_(new Date(), KONFIG.ZONA_WAKTU));

  const rencana = [];
  KONFIG.SISTEM.forEach(cfg => {
    const log = ss.getSheetByName(cfg.log);
    if (!log || log.getLastRow() < 2) return;
    const n = log.getLastRow() - 1;
    const simpan = [];
    const pindah = {};
    log.getRange(2, 1, n, HEADER_LOG.length).getValues().forEach(row => {
      const w = waktuNomor_(row[0], zona);
      if (w === null) { simpan.push(row); return; }   // baris yang jamnya tak terbaca dibiarkan di Log
      row[0] = w;
      const b = bulanDariNomor_(w);
      if (b < bulanIni) (pindah[b] = pindah[b] || []).push(row); else simpan.push(row);
    });
    if (Object.keys(pindah).length) rencana.push({ cfg: cfg, n: n, simpan: simpan, pindah: pindah });
  });
  if (!rencana.length) {
    ui.alert('Tidak ada log bulan sebelum ' + bulanIni + '.');
    return;
  }

  let tanya = 'Pindahkan log sebelum bulan ini (' + bulanIni + ') ke sheet arsip per bulan?\n';
  rencana.forEach(p => {
    tanya += '\n' + p.cfg.log + ':';
    Object.keys(p.pindah).sort().forEach(b => { tanya += '\n  • ' + b + ': ' + p.pindah[b].length + ' baris → "Arsip ' + p.cfg.log + ' ' + b + '"'; });
    tanya += '\n  Tersisa di Log: ' + p.simpan.length + ' baris.';
  });
  if (ui.alert('Arsipkan log', tanya, ui.ButtonSet.YES_NO) !== ui.Button.YES) return;

  const lock = LockService.getDocumentLock();
  if (!lock.tryLock(25000)) {
    ui.alert('Sistem sibuk, coba lagi sebentar lagi.');
    return;
  }
  try {
    const hasil = [];
    rencana.forEach(p => {
      const log = ss.getSheetByName(p.cfg.log);
      // Data di Log mungkin berubah selama dialog terbuka: kalau jumlah baris berbeda, batalkan bagian ini.
      if (log.getLastRow() - 1 !== p.n) {
        hasil.push(p.cfg.log + ': DILEWATI, Log berubah selama dialog. Jalankan lagi.');
        return;
      }
      Object.keys(p.pindah).sort().forEach(b => {
        const arsip = siapkanLog_(ss, 'Arsip ' + p.cfg.log + ' ' + b);
        const ada = arsip.getLastRow() > 1
          ? arsip.getRange(2, 1, arsip.getLastRow() - 1, HEADER_LOG.length).getValues().map(r => { r[0] = waktuNomor_(r[0], zona); return r; })
          : [];
        const gabung = ada.concat(p.pindah[b]).sort((x, y) => (y[0] || 0) - (x[0] || 0));
        pastikanUkuran_(arsip, gabung.length + 1, HEADER_LOG.length);
        arsip.getRange(2, 1, gabung.length, 1).setNumberFormat(KONFIG.FORMAT_WAKTU);
        arsip.getRange(2, 1, gabung.length, HEADER_LOG.length).setValues(gabung);
      });
      SpreadsheetApp.flush();
      log.getRange(2, 1, p.n, HEADER_LOG.length).clearContent();
      if (p.simpan.length) {
        const urut = p.simpan.sort((x, y) => (typeof y[0] === 'number' ? y[0] : 0) - (typeof x[0] === 'number' ? x[0] : 0));
        log.getRange(2, 1, urut.length, 1).setNumberFormat(KONFIG.FORMAT_WAKTU);
        log.getRange(2, 1, urut.length, HEADER_LOG.length).setValues(urut);
      }
      const lebih = p.n - p.simpan.length;
      if (lebih > 0 && log.getMaxRows() - lebih >= 2) log.deleteRows(p.simpan.length + 2, lebih);
      hasil.push(p.cfg.log + ': ' + lebih + ' baris diarsipkan, ' + p.simpan.length + ' baris tersisa.');
    });
    SpreadsheetApp.flush();
    ui.alert('Arsip selesai', hasil.join('\n') + '\n\nSheet arsip baru belum dikunci: jalankan menu 3 lagi bila log dikunci.', ui.ButtonSet.OK);
  } finally {
    lock.releaseLock();
  }
}

function pastikanUkuran_(sh, baris, kolom) {
  if (sh.getMaxRows() < baris) sh.insertRowsAfter(sh.getMaxRows(), baris - sh.getMaxRows() + 500);
  if (sh.getMaxColumns() < kolom) sh.insertColumnsAfter(sh.getMaxColumns(), kolom - sh.getMaxColumns());
}

/** Validasi data: STOK bulat >= 0, IN/OUT bulat > 0. sel = sel kiri-atas range. */
function aturanAngka_(sel, bolehNol) {
  const syarat = bolehNol ? sel + '>=0' : sel + '>0';
  return SpreadsheetApp.newDataValidation()
    .requireFormulaSatisfied('=AND(ISNUMBER(' + sel + '),' + syarat + ',' + sel + '<=' + KONFIG.MAKS_QTY + ',' + sel + '=INT(' + sel + '))')
    .setAllowInvalid(false)
    .setHelpText(bolehNol ? 'STOK: angka bulat 0–' + KONFIG.MAKS_QTY : 'Isi angka bulat 1–' + KONFIG.MAKS_QTY + ' lalu Enter')
    .build();
}

/**
 * Urutan warna sheet baru: warna sheet lama + warnaTambahan (disisip setelah warna `setelah`).
 * kSumber = indeks warna di sheet lama (null untuk warna baru), gi = indeks GRUP_VALUE.
 */
function susunWarna_(namaWarna, cfg) {
  const grupDari = k => GRUP_VALUE.findIndex(g => g.warna.indexOf(k) >= 0);
  const daftar = namaWarna.map((nama, k) => ({ nama: nama, kSumber: k, gi: grupDari(k), setelah: null }));
  const turunanDari = (x, induk) => {
    let p = x.setelah;
    for (let n = 0; p && n < 50; n++) {
      if (p === induk) return true;
      const y = daftar.find(z => z.nama === p);
      p = y ? y.setelah : null;
    }
    return false;
  };
  (cfg.warnaTambahan || []).forEach(t => {
    if (daftar.some(x => x.nama === t.nama)) return;   // sudah ada → lewati
    let i = daftar.findIndex(x => x.nama === t.setelah);   // boleh warna lama atau warna tambahan sebelumnya
    if (i < 0) {
      throw new Error('Warna tambahan "' + t.nama + '": warna "' + t.setelah + '" tidak ada di header "' + cfg.nama +
        '" dan bukan warna tambahan sebelumnya. Cek KONFIG.');
    }
    // lewati warna tambahan lain yang menempel pada induk yang sama (atau turunannya): urutan config terjaga
    while (i + 1 < daftar.length && daftar[i + 1].kSumber === null && turunanDari(daftar[i + 1], t.setelah)) i++;
    daftar.splice(i + 1, 0, { nama: t.nama, kSumber: null, gi: daftar[i].gi, setelah: t.setelah });
  });
  return daftar;
}

/** Baris produk terakhir = baris berisi terakhir sebelum label "OUT"/"IN" di kolom B. */
function cariBarisAkhir_(src, cfg) {
  const last = src.getLastRow();
  if (last < cfg.barisAwal) return cfg.barisAkhir;
  const b = src.getRange(cfg.barisAwal, 1, last - cfg.barisAwal + 1, 2).getValues();
  for (let i = 0; i < b.length; i++) {
    const label = String(b[i][1]).trim().toUpperCase();
    if (label === 'OUT' || label === 'IN') {
      let j = i - 1;
      while (j >= 0 && String(b[j][0]).trim() === '' && String(b[j][1]).trim() === '') j--;
      return cfg.barisAwal + j;
    }
  }
  return cfg.barisAkhir;
}

/** True kalau formula lama merujuk persis kolom grup (format lama: IN warna k di kolom 4+2k) di barisnya sendiri. */
function formulaLamaStandar_(f, kolomHarap, baris) {
  const kiri = String(f).replace(/\*[^*]*$/, '');
  const refs = [];
  const re = /([A-Z]+)(\d+)/g;
  let m;
  while ((m = re.exec(kiri))) refs.push([kolomAngka_(m[1]), Number(m[2])]);
  return refs.length === kolomHarap.length && refs.every((x, i) => x[0] === kolomHarap[i] && x[1] === baris);
}

/** Harga dari formula lama, mis. "=(D4+F4+H4+J4+L4)*281000" → 281000. */
function hargaDariFormula_(f) {
  const m = String(f).match(/\*\s*\(?\s*(\d+(?:\.\d+)?)\s*\)?\s*$/);
  return m ? Number(m[1]) : null;
}

function emailUser_(e) {
  try {
    if (e.user && e.user.getEmail && e.user.getEmail()) return e.user.getEmail();
  } catch (err) { /* tidak tersedia untuk sebagian akun */ }
  try {
    const m = Session.getActiveUser().getEmail();
    if (m) return m;
  } catch (err) { /* idem */ }
  return '';
}

function hapusProteksiLama_(sh) {
  sh.getProtections(SpreadsheetApp.ProtectionType.SHEET).forEach(p => {
    if (p.getDescription() === KONFIG.DESKRIPSI_PROTEKSI) p.remove();
  });
}

/** Pola resmi Google: pastikan diri sendiri editor dulu, baru hapus editor lain. */
function batasiKePemilik_(p, me) {
  p.addEditor(me);
  p.removeEditors(p.getEditors());
  if (p.canDomainEdit()) p.setDomainEdit(false);
}

function kolomAngka_(h) {
  let n = 0;
  for (let i = 0; i < h.length; i++) n = n * 26 + h.charCodeAt(i) - 64;
  return n;
}

function huruf_(c) {
  let s = '';
  while (c > 0) {
    const m = (c - 1) % 26;
    s = String.fromCharCode(65 + m) + s;
    c = Math.floor((c - 1) / 26);
  }
  return s;
}
