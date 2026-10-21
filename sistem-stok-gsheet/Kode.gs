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
 * Urutan produk sheet baru diambil dari sheet "Urutan UC" / "Urutan STP" (diimpor dari file daftar urutan).
 * Pasang: lihat PANDUAN.md di folder yang sama.
 *
 * PENTING: jangan buat fungsi bernama onEdit di project ini.
 * Handler sengaja bernama prosesInputStok dan dipasang sebagai
 * trigger installable (menu "2. Aktifkan input otomatis").
 */

const KONFIG = {
  // nama  : sheet yang dipakai staf (setelah migrasi berformat STOK|IN|OUT)
  // arsip : nama baru untuk sheet lama saat migrasi (isinya tidak diubah)
  // urutan: sheet berisi daftar produk sheet baru (urutan, nama, kode SKU, baris lama asal stoknya)
  // log   : sheet riwayat mutasi khusus sheet ini (terbaru di baris 2, paling atas)
  // rekap : sheet rekap per hari (dihitung script dari Log + arsip log; terbaru di atas)
  // barisAkhir hanya cadangan; migrasi mencari sendiri baris produk terakhir
  //   (baris sebelum label "OUT"/"IN" di kolom B).
  // tanpaValue: grup yang memang tidak dijual di toko itu (tidak dilaporkan "tanpa harga").
  // warnaTambahan: warna baru yang belum ada di sheet lama. Dibuat kosong (stok 0) saat migrasi,
  //   diletakkan setelah warna `setelah`, ikut grup Value warna itu (harga per baris sama).
  SISTEM: [
    { nama: 'Stok Cover UC', arsip: 'Stok Cover UC (lama)', urutan: 'Urutan UC', log: 'Log Stok UC', rekap: 'Rekap Harian UC', barisAwal: 4, barisAkhir: 196,
      tanpaValue: [], warnaTambahan: [] },
    { nama: 'Stok Cover STP', arsip: 'Stok Cover STP (lama)', urutan: 'Urutan STP', log: 'Log Stok STP', rekap: 'Rekap Harian STP', barisAwal: 4, barisAkhir: 107,
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
  SAPU_MENIT: 15,               // trigger waktu penyapu input tertinggal (1, 5, 10, 15, atau 30). Tiap jalan ±8-10 detik dari kuota harian
  SAPU_JAM: { awal: 6, akhir: 19 },   // penyapu hanya bekerja pada jam ini (WIB), di luar jam itu langsung berhenti
  TUNGGU_LOCK_MS: 3000,         // lama trigger edit menunggu lock. Singkat: yang kalah giliran berhenti, pemegang lock sudah menyapu semua sel
  IZINKAN_PEMBATALAN: true,     // sel IN/OUT boleh berisi "B" + jumlah (mis. B1): membatalkan sebagian entri HARI INI untuk produk x warna x jenis yang sama
  BATAS_BACA_BATAL: 3000,       // baris teratas Log yang dibaca untuk memeriksa pembatalan (hanya saat ada entri B)
  REKAP_JAM: 0,                 // trigger rekap harian berjalan sekitar jam ini (WIB) + REKAP_MENIT. Mengubahnya: Matikan lalu Aktifkan input otomatis
  REKAP_MENIT: 30,
  REKAP_HARI_ULANG: 4,          // tiap malam rekap menghitung ulang hari ini + (n-1) hari sebelumnya (lebih jauh bila ada hari yang terlewat)
  REKAP_BATAS_BARIS: 60000,     // Log + arsip lebih panjang dari ini: rekap berhenti dengan pesan "arsipkan log dulu"
  REKAP_BATAS_MS: 240000,       // batas waktu membaca sumber rekap (eksekusi maks. 6 menit); lewat ini rekap dibatalkan sebelum menulis apa pun
  PUTARAN_MAKS: 3,              // pemegang lock mengulang penyapuan sampai tidak ada yang tersisa (maks. putaran ini)
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

// Judul kolom sheet "Urutan ..." (baris 1). Kolom lain (Bagian, Peringkat, Status, Catatan, dst.) diabaikan.
const KET_SAPU = 'Diproses penyapuan otomatis (angka tertinggal di sel)';   // keterangan Log untuk sel di luar area yang diedit
const CATATAN_SIBUK = 'Sistem sibuk';   // awal catatan sel yang tertunda karena lock; dicoba lagi otomatis

const KOLOM_URUTAN = { nama: 'nama produk', sku: 'kode sku', baris: 'baris lama', namaLama: 'nama di sheet lama', harga: 'harga dari baris' };

const HEADER_LOG = ['Waktu', 'Sheet', 'Baris', 'Produk', 'Kode SKU', 'Warna', 'Jenis',
  'Qty', 'Stok Sebelum', 'Stok Sesudah', 'User', 'Keterangan'];

// Rekap harian: satu baris per hari (nomor hari WIB), nilai statis hasil hitung script dari Log + arsip. Kolom O2 = waktu hitung terakhir.
const HEADER_REKAP = ['Tanggal', 'Masuk (unit)', 'Keluar (unit)', 'Selisih', 'Entri', 'Dibatalkan IN (unit)', 'Dibatalkan OUT (unit)',
  'Opname STOK (entri)', 'Selisih opname (unit)', 'Ditolak (entri)', 'Dihitung', 'Status', 'Catatan'];
const KOLOM_REKAP_STATUS = 15;
const FORMAT_TOTAL_KELUAR = '"Keluar "#,##0" unit";"Keluar -"#,##0" unit"';
const FORMAT_TOTAL_MASUK = '"Masuk "#,##0" unit";"Masuk -"#,##0" unit"';
const TEKS_BANNER_LAMA = 'STOK dihitung otomatis. Isi angka di kolom IN / OUT lalu Enter. Jangan ketik di kolom STOK.';
const TEKS_BANNER_BARU = 'STOK dihitung otomatis. Isi angka di kolom IN / OUT lalu Enter. Salah ketik hari ini? Ketik B + jumlah (mis. B1) di sel yang sama untuk membatalkan. Jangan ketik di kolom STOK.';

// ---------------------------------------------------------------- menu

function onOpen() {
  SpreadsheetApp.getUi().createMenu('📦 Sistem Stok')
    .addItem('1a. Susun "' + KONFIG.SISTEM[0].nama + '" ke format STOK/IN/OUT (ikut "' + KONFIG.SISTEM[0].urutan + '")', 'migrasiStokUC')
    .addItem('1b. Susun "' + KONFIG.SISTEM[1].nama + '" ke format STOK/IN/OUT (ikut "' + KONFIG.SISTEM[1].urutan + '")', 'migrasiStokSTP')
    .addItem('2. Aktifkan input otomatis', 'aktifkanInputOtomatis')
    .addItem('3. Kunci kolom STOK (opsional, pemilik file)', 'kunciKolomStok')
    .addItem('4. Perbarui sheet yang sudah dimigrasi (total harian, rekap, pembatalan B)', 'perbaruiSheetLama')
    .addSeparator()
    .addItem('Cek status', 'cekStatus')
    .addItem('Arsipkan log bulan lalu (opsional)', 'arsipkanLogBulanLalu')
    .addItem('Perbarui rekap harian sekarang', 'perbaruiRekapSekarang')
    .addItem('Bangun ulang rekap harian dari Log (semua hari)', 'bangunUlangRekap')
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
 *
 * Tiap eksekusi juga MENYAPU seluruh sel IN/OUT sheet itu (bukan hanya sel yang diedit): kalau staf mengetik cepat
 * dan Google melewatkan satu kejadian edit, atau pembacaan sel sempat ketinggalan, angka yang tertinggal diproses
 * oleh eksekusi berikutnya. Sel yang ditolak (ada catatan merah) tidak disentuh sampai staf menghapus/mengetik ulang.
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
  if (!peta.labelAda) return;   // label "TOTAL STOK" hilang: jangan proses apa pun (lihat bacaPeta_)
  const barisAwal = Math.max(r0, KONFIG.BARIS_DATA);
  const barisAkhir = Math.min(r1, peta.barisTotal - 1);
  const kolomAkhir = Math.min(c1, peta.kolomTerakhir);
  if (barisAwal > barisAkhir || c0 > kolomAkhir) return;
  let relevan = false;
  for (let c = c0; c <= kolomAkhir; c++) if (peta.kolom[c]) relevan = true;
  if (!relevan) return;

  // Menunggu lock memakan kuota trigger harian (waktu tunggu ikut dihitung). IN/OUT: tunggu sebentar saja, yang kalah giliran
  // berhenti karena pemegang lock menyapu SEMUA sel (dan memeriksa ulang sebelum melepas lock). Koreksi STOK manual tidak ikut
  // disapu, jadi untuknya tunggu lebih lama.
  let adaStok = false;
  for (let c = c0; c <= kolomAkhir; c++) if (peta.kolom[c] && peta.kolom[c].jenis === 'STOK') adaStok = true;
  const lock = LockService.getDocumentLock();
  if (!lock.tryLock(adaStok ? 25000 : KONFIG.TUNGGU_LOCK_MS)) {
    // Sel IN/OUT sengaja TIDAK ditandai merah: pemegang lock bisa saja sudah memprosesnya (dan menghapus tandanya) sebelum
    // tanda ini terpasang, sehingga sel kosong tertinggal merah. Angka yang belum hilang diproses pemegang lock / penyapu.
    const isi = sheet.getRange(barisAwal, c0, barisAkhir - barisAwal + 1, kolomAkhir - c0 + 1).getValues();
    for (let r = barisAwal; r <= barisAkhir; r++) {
      for (let c = c0; c <= kolomAkhir; c++) {
        const info = peta.kolom[c];
        if (info && info.jenis === 'STOK' && isi[r - barisAwal][c - c0] !== '') {
          tandaiError_(sheet.getRange(r, c), 'Sistem sibuk: koreksi STOK ini belum tercatat di Log. Ketik ulang angkanya.');
        }
      }
    }
    return;
  }

  try {
    const ss = e.source || SpreadsheetApp.getActiveSpreadsheet();
    prosesBlok_(ss, sheet, cfg, peta, { r0: barisAwal, r1: barisAkhir, c0: c0, c1: kolomAkhir, satu: r0 === r1 && c0 === c1 }, e);
  } finally {
    lock.releaseLock();
  }
}

/**
 * Jaring pengaman (trigger waktu, tiap KONFIG.SAPU_MENIT menit): proses sel IN/OUT yang masih tertinggal di sheet sistem.
 * Dipasang menu "2. Aktifkan input otomatis" bersama trigger edit.
 */
function sapuInputStok() {
  const jam = Number(Utilities.formatDate(new Date(), KONFIG.ZONA_WAKTU, 'HH'));
  if (jam < KONFIG.SAPU_JAM.awal || jam >= KONFIG.SAPU_JAM.akhir) return;   // di luar jam kerja: hemat kuota
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const galat = [];
  KONFIG.SISTEM.forEach(cfg => {
    try {
      const sheet = ss.getSheetByName(cfg.nama);
      if (!sheet) return;
      const peta = bacaPeta_(sheet);
      if (!Object.keys(peta.kolom).length || !peta.labelAda) return;
      const lock = LockService.getDocumentLock();
      if (!lock.tryLock(10000)) return;   // sibuk: giliran berikutnya
      try {
        prosesBlok_(ss, sheet, cfg, peta, null, null);
      } finally {
        lock.releaseLock();
      }
    } catch (err) {
      galat.push(cfg.nama + ': ' + err.message);   // sheet berikutnya tetap disapu
    }
  });
  if (galat.length) throw new Error('Penyapu gagal: ' + galat.join(' | '));
}

/**
 * Inti pemrosesan. Lock sudah dipegang pemanggil.
 * edit = { r0, r1, c0, c1 } area yang diedit staf (sel STOK di area ini = koreksi manual; sel kosong di area ini
 * dikembalikan ke tampilan normal), atau null untuk penyapuan murni.
 * Sel IN/OUT berisi angka di luar area edit ikut diproses, kecuali yang punya catatan (ditolak sebelumnya).
 */
function prosesBlok_(ss, sheet, cfg, peta, edit, e) {
  if (!peta.labelAda || peta.barisTotal - 1 < KONFIG.BARIS_DATA || peta.kolomTerakhir < 1) return;
  // Rekap "hari ini" memakai TODAY() menurut zona file, jam Log memakai WIB: samakan.
  if (ss.getSpreadsheetTimeZone() !== KONFIG.ZONA_WAKTU) ss.setSpreadsheetTimeZone(KONFIG.ZONA_WAKTU);
  // Ulangi penyapuan selama masih ada yang diproses: sel yang diketik staf selagi putaran sebelumnya berjalan ikut terbawa,
  // sehingga trigger yang kalah giliran lock tidak meninggalkan angka. Putaran ke-2 dst. hanya menyapu (tanpa area edit).
  for (let putaran = 1; putaran <= KONFIG.PUTARAN_MAKS; putaran++) {
    const n = prosesPutaran_(ss, sheet, cfg, peta, putaran === 1 ? edit : null, putaran === 1 ? e : null);
    if (!n) break;
  }
}

/** Satu putaran penyapuan. Mengembalikan jumlah sel IN/OUT yang berhasil diproses. */
function prosesPutaran_(ss, sheet, cfg, peta, edit, e) {
  const namaSheet = sheet.getName();
  const baris0 = KONFIG.BARIS_DATA;
  const baris1 = peta.barisTotal - 1;
  const kol1 = peta.kolomTerakhir;
  const bacaBlok = () => sheet.getRange(baris0, 1, baris1 - baris0 + 1, kol1).getValues();
  const blok = bacaBlok();
  const diEdit = (r, c) => !!edit && r >= edit.r0 && r <= edit.r1 && c >= edit.c0 && c <= edit.c1;
  const satuSel = !!edit && edit.satu === true;   // rentang ASLI satu sel (bukan rentang yang terpotong ke area produk)
  // Penyapuan murni: kalau tidak ada sel IN/OUT berisi, selesai di sini (tanpa membaca catatan). Pada edit, catatan dibaca
  // untuk membersihkan tanda merah basi di sel yang sudah kosong.
  if (!edit) {
    let ada = false;
    for (let r = baris0; r <= baris1 && !ada; r++) {
      for (let c = 1; c <= kol1; c++) {
        const inf = peta.kolom[c];
        if (inf && inf.jenis !== 'STOK' && angkaInput_(blok[r - baris0][c - 1]) !== null) { ada = true; break; }
      }
    }
    if (!ada) return 0;
  }
  const catatan = sheet.getRange(baris0, 1, baris1 - baris0 + 1, kol1).getNotes();
  // Urutan kolom: per warna STOK, lalu OUT, lalu IN. Kalau IN dan OUT warna yang sama tertunda bersamaan, OUT diperiksa lebih
  // dulu terhadap stok yang ada (lebih aman: OUT yang tak muat ditolak terlihat, bukan lolos karena IN yang baru diketik).
  const urutKolom = Object.keys(peta.kolom).map(Number).sort((a, b) => {
    const ia = peta.kolom[a], ib = peta.kolom[b];
    if (ia.kolomStok !== ib.kolomStok) return ia.kolomStok - ib.kolomStok;
    const rank = j => (j === 'STOK' ? 0 : j === 'OUT' ? 1 : 2);
    return rank(ia.jenis) - rank(ib.jenis);
  });
  // Jangan menandai merah sel yang isinya sudah berubah/terhapus sejak dibaca (staf bisa menghapus selagi diproses).
  const tandai = (sel, nilai, pesanError) => (sel.getValue() === nilai ? tandaiError_(sel, pesanError) : false);
  const user = emailUser_(e || {});
  const waktu = waktuSerial_(new Date());   // jam WIB sebagai angka, tidak tergantung zona waktu file/script
  const log = [];
  const pesan = [];
  const selesai = [];   // sel IN/OUT yang sudah diproses, dikosongkan setelah dicek ulang
  // Net IN/OUT hari ini per produk x warna x jenis (dari Log). Dibaca malas: hanya bila ada entri pembatalan "B n" di putaran ini.
  let netBatal = null;
  const ambilNet = () => netBatal || (netBatal = netHariIni_(ss, cfg, Math.floor(waktu), log));

  try {
  for (let r = baris0; r <= baris1; r++) {
    const baris = blok[r - baris0];
    const produk = String(baris[1]).trim();
    const sku = String(baris[2]).trim();

    for (let k = 0; k < urutKolom.length; k++) {
      const c = urutKolom[k];
      const info = peta.kolom[c];
      const dalam = diEdit(r, c);
      const nilai = baris[c - 1];

      // Admin mengetik langsung di kolom STOK (opname / koreksi).
      // Tulisan script sendiri tidak memicu onEdit, jadi ini pasti edit manusia. Hanya untuk sel yang diedit.
      if (info.jenis === 'STOK') {
        if (!dalam) continue;
        const sel = sheet.getRange(r, c);
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

      const batal = batalInput_(nilai);   // jumlah pembatalan ("B n"), null = bukan pembatalan, NaN = B tak valid
      const qty = batal === null ? angkaInput_(nilai) : batal;
      const catatanSel = catatan[r - baris0][c - 1];
      if (qty === null) {               // sel kosong
        // Di area edit: kembalikan ke tampilan normal. Di luar area edit: bersihkan tanda merah buatan script yang tertinggal
        // di sel yang sudah kosong (mis. staf menghapus angkanya tapi kejadian hapus terlewat).
        // Tanda merah selalu disertai catatan: sel kosong tanpa catatan sudah tampil normal, tidak perlu 4 panggilan reset (kuota).
        if (catatanSel !== '' && (dalam || catatanSistem_(catatanSel))) resetSel_(sheet.getRange(r, c), info.jenis, info.warna);
        continue;
      }
      const sel = sheet.getRange(r, c);
      if (!dalam) {
        // Penyapuan: sel di luar edit ini yang masih berisi angka. Yang ditolak sebelumnya (ada catatan) dibiarkan;
        // yang hanya tertunda karena sistem sibuk dicoba lagi.
        if (catatanSel !== '' && catatanSel.indexOf(CATATAN_SIBUK) !== 0) continue;
      }
      // Sel di luar area edit: pemilik angkanya tidak diketahui (bukan yang menjalankan eksekusi ini), jadi User dikosongkan.
      const pelaku = dalam ? user : '';
      const ket = dalam ? '' : KET_SAPU;
      if (!produk) {
        tandai(sel, nilai, 'Baris ini tanpa nama produk, input tidak diproses.');
        continue;
      }
      if (isNaN(qty)) {
        tandai(sel, nilai, 'Isi angka bulat 1–' + KONFIG.MAKS_QTY +
          (KONFIG.IZINKAN_PEMBATALAN ? '. Salah ketik hari ini? Ketik B + jumlah yang dibatalkan, mis. B1 (minus tidak dipakai).' : '.'));
        continue;
      }
      const sebelum = angkaStok_(baris[info.kolomStok - 1]);
      if (sebelum === null) {
        tandai(sel, nilai, 'Kolom STOK warna ini berisi bukan angka. Perbaiki STOK dulu.');
        continue;
      }
      let sesudah;
      let qtyLog = qty;
      let ketBatal = '';
      if (batal !== null) {
        // Pembatalan: hanya sebagian entri HARI INI untuk produk x warna x jenis yang sama (net dari Log), supaya salah arah/salah sel/salah hari
        // tidak jadi mutasi sah. Salah catat di hari lain: admin koreksi STOK (opname). Dicatat di Log sebagai Qty NEGATIF, jenis tetap IN/OUT,
        // sehingga rumus rekap (SUMIFS atas Qty) otomatis menghitung bersih.
        const kunci = kunciBatal_(produk, sku, info.warna, info.jenis);
        const net = ambilNet();
        const tersedia = net.get(kunci) || 0;
        let alasan = '';
        if (tersedia < batal) {
          alasan = 'batal ' + info.jenis + ' ' + batal + ' melebihi ' + info.jenis + ' HARI INI untuk produk/warna ini (tercatat ' + tersedia +
            '). Salah catat di hari lain? Minta admin mengoreksi STOK (opname).';
        } else if (info.jenis === 'IN' && sebelum < batal) {
          alasan = 'batal IN ' + batal + ' melebihi stok ' + sebelum + '. Stok tidak berubah.';
        }
        if (alasan) {
          if (tandai(sel, nilai, 'DITOLAK: ' + alasan)) {
            log.push([waktu, namaSheet, r, produk, sku, info.warna, 'DITOLAK', batal, sebelum, sebelum, pelaku,
              'Pembatalan ditolak: ' + alasan + (ket ? '; ' + ket : '')]);
          }
          continue;
        }
        sesudah = info.jenis === 'IN' ? sebelum - batal : sebelum + batal;
        qtyLog = -batal;
        ketBatal = 'BATAL ' + info.jenis;
        net.set(kunci, tersedia - batal);
      } else {
        sesudah = info.jenis === 'IN' ? sebelum + qty : sebelum - qty;
        if (sesudah < 0 && !KONFIG.IZINKAN_STOK_MINUS) {
          const pesanTolak = 'DITOLAK: OUT ' + qty + ' melebihi stok ' + sebelum +
            '. Stok tidak berubah. Cek fisik barang, lalu hapus/ketik ulang.';
          if (tandai(sel, nilai, pesanTolak)) {
            log.push([waktu, namaSheet, r, produk, sku, info.warna, 'DITOLAK', qty, sebelum, sebelum, pelaku,
              'OUT melebihi stok' + (ket ? '; ' + ket : '')]);
          }
          continue;
        }
      }

      sheet.getRange(r, info.kolomStok).setValue(sesudah);
      baris[info.kolomStok - 1] = sesudah;
      selesai.push({ r: r, c: c, nilai: nilai, sel: sel, jenis: info.jenis, warna: info.warna, catatan: catatanSel });
      baris[c - 1] = '';
      log.push([waktu, namaSheet, r, produk, sku, info.warna, info.jenis, qtyLog, sebelum, sesudah, pelaku, [ketBatal, ket].filter(Boolean).join('; ')]);
      pesan.push((ketBatal ? ketBatal + ' ' + batal + ' · ' : '') + produk + ' ' + info.warna + ': ' + sebelum + ' → ' + sesudah);
    }
  }

  if (selesai.length) {
    // Staf bisa mengetik ulang di sel yang sama selagi script berjalan: sel yang isinya sudah berubah
    // jangan dihapus; ketikan baru diproses putaran berikutnya.
    const terkini = bacaBlok();
    selesai.forEach(x => {
      if (terkini[x.r - baris0][x.c - 1] === x.nilai) {
        x.sel.clearContent();
        // Sel yang diterima tanpa catatan tidak pernah diberi tanda merah: tampilannya sudah normal (hemat 4 panggilan per sel).
        if (x.catatan !== '') resetSel_(x.sel, x.jenis, x.warna);
      }
    });
  }
  if (log.length) tulisLog_(ss, cfg, log);
  } catch (err) {
    // Galat sementara dari layanan Sheets di tengah proses: STOK sebagian sel sudah naik. Pulihkan sebisanya supaya sel itu tidak
    // tertinggal berisi angka (penyapu akan menghitungnya lagi = stok dobel), lalu catat ke Log, lalu lempar ulang galatnya.
    selesai.forEach(x => { try { x.sel.clearContent(); } catch (e2) { /* sudah mentok */ } });
    // Jangan menulis dua kali kalau tulisLog_ sudah berhasil di server (galat bisa datang sesudahnya, mis. timeout): cek puncak Log dulu.
    try { if (log.length && !logSudahAda_(ss, cfg, log)) tulisLog_(ss, cfg, log); } catch (e3) { /* sudah mentok */ }
    throw err;
  }
  SpreadsheetApp.flush();   // wajib sebelum lock dilepas, supaya eksekusi berikutnya baca nilai terbaru
  if (pesan.length) {
    ss.toast(pesan.slice(0, 5).join('\n') + (pesan.length > 5 ? '\n+' + (pesan.length - 5) + ' lainnya' : ''),
      'Stok diperbarui', 5);
  }
  return selesai.length;
}

// ---------------------------------------------------------------- migrasi

function migrasiStokUC() {
  migrasi_(KONFIG.SISTEM[0]);
}

function migrasiStokSTP() {
  migrasi_(KONFIG.SISTEM[1]);
}

/**
 * Sheet lama diganti nama jadi cfg.arsip (isinya tidak diubah).
 * Sheet baru dibangun dulu dengan nama sementara; hanya kalau semuanya berhasil, sheet lama diganti nama dan sheet baru
 * memakai nama asli di posisi tab yang sama. Urutan dan isi produk mengikuti sheet cfg.urutan; stok tiap produk diambil
 * dari baris sheet lama yang ditunjuk daftar itu.
 */
function migrasi_(cfg) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const ui = SpreadsheetApp.getUi();
  const sementara = cfg.nama + ' (baru)';
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
  if (ss.getSheetByName(sementara)) {
    ui.alert('Ada sheet "' + sementara + '" sisa migrasi yang terhenti. Sheet "' + cfg.nama + '" masih utuh. ' +
      'Hapus sheet "' + sementara + '" dulu, lalu ulangi.');
    return;
  }

  const W = KONFIG.JUMLAH_WARNA;
  const namaWarna = src.getRange(2, 4, 1, 2 * W).getValues()[0]
    .filter((_, i) => i % 2 === 0).map(v => String(v).trim());
  const labelValue = src.getRange(3, 4 + 2 * W, 1, GRUP_VALUE.length + 1).getValues()[0]
    .map((v, i) => String(v).trim() || (i < GRUP_VALUE.length ? GRUP_VALUE[i].nama : 'Total Value'));
  // Rencana dibuat beberapa kali: untuk dialog, lagi dengan data terbaru setelah user setuju (dialog bisa terbuka lama,
  // staf lain mungkin mengubah sheet lama atau daftar), dan sekali lagi sesudah sheet baru jadi (pemeriksaan akhir).
  const rencanakan = () => {
    const barisAkhir = cariBarisAkhir_(src, cfg);
    const n = barisAkhir - cfg.barisAwal + 1;
    const lama = src.getRange(cfg.barisAwal, 1, n, 3 + 2 * W).getValues();
    const fLama = src.getRange(cfg.barisAwal, 4 + 2 * W, n, GRUP_VALUE.length + 1).getFormulas();
    const r = susunUrutan_(cfg, bacaDaftarUrutan_(ss, cfg), lama, fLama, namaWarna, labelValue);
    r.barisAkhir = barisAkhir;
    return r;
  };
  const sidik = r => JSON.stringify([r.barisAkhir, r.entri.map(e => [e.nama, e.sku, e.sumber, e.stok, e.harga, e.adaTotal])]);
  let daftar;
  let rencana;
  try {
    daftar = susunWarna_(namaWarna, cfg);
    rencana = rencanakan();
  } catch (err) {
    ui.alert(err.message);
    return;
  }

  const namaTampil = x => '"' + x.nama + '" (baris ' + x.r + ', stok ' + x.stok + ')';
  const awalAkhir = rencana.entri.length ? ' (dari "' + rencana.entri[0].nama + '" sampai "' + rencana.entri[rencana.entri.length - 1].nama + '")' : '';
  let tanya = 'Produk "' + cfg.nama + '" disusun ulang mengikuti sheet "' + cfg.urutan + '"' + awalAkhir + ': ' + rencana.entri.length +
    ' produk (' + rencana.dariLama + ' dari sheet lama' + (rencana.digabung ? ', ' + rencana.digabung + ' di antaranya gabungan beberapa baris lama' : '') +
    ', ' + rencana.baru + ' baris BARU dengan stok kosong).\n\n' +
    '• Sheet lama (baris ' + cfg.barisAwal + '–' + rencana.barisAkhir + ') diganti nama jadi "' + cfg.arsip + '" (isinya tidak diubah, termasuk bagian di bawah baris ' +
    rencana.barisAkhir + ').\n• Sheet baru bernama "' + cfg.nama + '".\n• STOK awal = angka kolom IN sekarang (baris gabungan dijumlahkan). ' +
    'Total ' + rencana.stokBaru + ' unit, sama dengan sheet lama.';
  if (rencana.geser.length) {
    tanya += '\n• ' + rencana.geser.length + ' nomor "Baris lama" di daftar sudah tidak cocok dengan sheet lama (baris bergeser?). Stoknya dicari lewat nama baris, mis. ' +
      rencana.geser.slice(0, 3).map(g => g.nama + ' (baris ' + g.dari + ' → ' + g.ke + ')').join('; ') + '.';
  }
  if (rencana.diganti.length) {
    tanya += '\n• ' + rencana.diganti.length + ' nama baris lama sudah diganti sejak daftar dibuat, mis. ' +
      rencana.diganti.slice(0, 3).map(g => '"' + g.dari + '" → "' + g.ke + '" (baris ' + g.baris + ')').join('; ') + '. Barisnya sama, jadi dianggap produk yang sama.';
  }
  if (rencana.teksAngka) tanya += '\n• ' + rencana.teksAngka + ' sel IN berisi angka berformat teks; dibaca sebagai angka.';
  if (rencana.bukanAngka) tanya += '\n• PERHATIAN: ' + rencana.bukanAngka + ' sel IN bukan angka (teks/tanggal); stoknya dikosongkan, daftar sel ada di catatan setelah selesai.';
  if (rencana.dibuang.length) {
    tanya += '\n• ' + rencana.dibuang.length + ' baris sheet lama tidak ikut karena tidak ada di daftar dan stoknya 0 (tetap ada di sheet "' + cfg.arsip + '").';
  }
  if (rencana.ditambah.length) {
    tanya += '\n• PERHATIAN: ' + rencana.ditambah.length + ' baris sheet lama BERSTOK tapi tidak ada di daftar. Supaya stoknya tidak hilang, ditaruh di bagian paling bawah: ' +
      rencana.ditambah.slice(0, 5).map(namaTampil).join(', ') + (rencana.ditambah.length > 5 ? ', …' : '') + '.';
  }
  daftar.forEach((w, i) => {
    if (w.kSumber === null) {
      tanya += '\n• Warna baru: ' + w.nama + ' (setelah ' + daftar[i - 1].nama + ', stok awal kosong, value ikut harga ' +
        labelValue[w.gi] + ').';
    }
  });
  if (rencana.outTerisi.length) {
    tanya += '\n\nPERHATIAN: ' + rencana.outTerisi.length + ' sel OUT masih terisi. Sistem menganggap IN sudah dikurangi OUT ' +
      '(sesuai alur lama). Kalau belum, batalkan dan rapikan dulu.\n' +
      rencana.outTerisi.slice(0, 8).join('\n') + (rencana.outTerisi.length > 8 ? '\n…' : '');
  }
  const zonaLama = ss.getSpreadsheetTimeZone();
  if (zonaLama !== KONFIG.ZONA_WAKTU) {
    tanya += '\n• Zona waktu file diubah dari ' + zonaLama + ' ke ' + KONFIG.ZONA_WAKTU +
      ' (supaya jam Log Stok dan rekap "hari ini" sesuai WIB). Isi sheet lain tidak berubah.';
  }
  tanya += '\n\nMinta semua staf menutup file ini selama migrasi (±1 menit). Lanjutkan?';
  if (ui.alert('Migrasi ' + cfg.nama, tanya, ui.ButtonSet.YES_NO) !== ui.Button.YES) return;

  const logSudahAda = !!ss.getSheetByName(cfg.log);
  let sh = null;
  let infoBangun = { catatan: [] };
  try {
    rencana = rencanakan();   // data terbaru setelah dialog
    siapkanLog_(ss, cfg.log);
    sh = ss.insertSheet(sementara, src.getIndex() - 1);
    infoBangun = bangunSheet_(sh, cfg, { daftar, labelValue, entri: rencana.entri });
    if (sidik(rencanakan()) !== sidik(rencana)) {
      throw new Error('Sheet lama atau daftar berubah selama migrasi (ada yang masih mengedit?). Minta semua staf menutup file ini, lalu ulangi.');
    }
    src.setName(cfg.arsip);
    sh.setName(cfg.nama);
  } catch (err) {
    // Sheet lama baru diganti nama di langkah paling akhir, jadi biasanya masih utuh. Bersihkan sisa.
    const sisa = [];
    if (src.getName() === cfg.arsip) { try { src.setName(cfg.nama); } catch (e2) { sisa.push('nama sheet lama harus dikembalikan manual ke "' + cfg.nama + '"'); } }
    if (sh) { try { ss.deleteSheet(sh); } catch (e3) { sisa.push('hapus sheet "' + sementara + '"'); } }
    const lg = !logSudahAda && ss.getSheetByName(cfg.log);
    if (lg) { try { ss.deleteSheet(lg); } catch (e4) { sisa.push('hapus sheet "' + cfg.log + '" yang kosong'); } }
    ui.alert('Migrasi GAGAL. Sheet "' + cfg.nama + '" tidak diubah.' + (sisa.length ? '\nBersihkan manual: ' + sisa.join('; ') + '.' : '') + '\n\n' + err.message);
    return;
  }
  if (zonaLama !== KONFIG.ZONA_WAKTU) ss.setSpreadsheetTimeZone(KONFIG.ZONA_WAKTU);

  // Sheet rekap harian disiapkan SESUDAH sheet baru resmi (gagal di sini hanya jadi catatan; tidak membatalkan migrasi).
  const catatanRekap = [];
  try {
    siapkanRekap_(ss, cfg.rekap);
    if (logSudahAda) denganKunciRekap_(() => perbaruiRekapSatu_(ss, cfg, { semua: true, paksa: false }));
  } catch (err) {
    catatanRekap.push('Sheet "' + cfg.rekap + '" belum siap (' + err.message + '). Jalankan menu 4 nanti.');
  }

  const peringatan = rencana.peringatan.concat(infoBangun.catatan, catatanRekap);
  const BATAS = 25;
  let selesai = 'Sheet "' + cfg.nama + '" siap: ' + rencana.entri.length + ' produk. Sheet lama: "' + cfg.arsip + '".' +
    '\n\nLangkah berikutnya: menu 📦 Sistem Stok → 2. Aktifkan input otomatis (cukup sekali untuk semua sheet).';
  if (peringatan.length) {
    selesai += '\n\nCatatan (' + peringatan.length + '):\n' + peringatan.slice(0, BATAS).join('\n') +
      (peringatan.length > BATAS ? '\n… (' + (peringatan.length - BATAS) + ' catatan lain ada di log eksekusi: Extensions → Apps Script → Executions)' : '');
  }
  console.log(selesai + (peringatan.length > BATAS ? '\n\nSemua catatan:\n' + peringatan.join('\n') : ''));
  ui.alert('Migrasi selesai', selesai, ui.ButtonSet.OK);
}

/**
 * Baca sheet cfg.urutan. Baris 1 = judul kolom (KOLOM_URUTAN); kolom lain diabaikan.
 * Tiap baris berikutnya = 1 produk sheet baru, sesuai urutan: nama, kode SKU, "Baris lama" (nomor baris sheet lama
 * yang stoknya dipindah; boleh lebih dari satu, dipisah koma = stok dijumlahkan; kosong = produk baru, stok kosong),
 * "Nama di sheet lama" (WAJIB: nama baris-baris itu dipisah "|", untuk memastikan baris yang ditunjuk masih benar),
 * "Harga dari baris" (opsional: baris sheet lama yang harga Value-nya dipakai, untuk produk baru).
 */
function bacaDaftarUrutan_(ss, cfg) {
  const sh = ss.getSheetByName(cfg.urutan);
  const kembar = ss.getSheets().map(x => x.getName()).filter(n => n !== cfg.urutan && n.indexOf(cfg.urutan) === 0);
  if (!sh) {
    throw new Error('Sheet "' + cfg.urutan + '" tidak ditemukan di spreadsheet ini. Tidak ada yang diubah.\n\n' +
      (kembar.length ? 'Yang ada: ' + kembar.map(n => '"' + n + '"').join(', ') + '. Ganti namanya jadi persis "' + cfg.urutan + '".\n\n' : '') +
      'File xlsx yang hanya ada di Google Drive belum cukup: isinya harus masuk sebagai TAB di spreadsheet ini (deretan tab di bagian bawah layar). ' +
      'Caranya: buka spreadsheet ini → menu File → Import → Upload (atau tab My Drive) → pilih file → Import location: "Insert new sheet(s)" → Import data. ' +
      'Lihat PANDUAN.md bagian "Daftar urutan produk".');
  }
  if (kembar.length) {
    throw new Error('Ada sheet lain yang namanya mirip "' + cfg.urutan + '": ' + kembar.map(n => '"' + n + '"').join(', ') +
      '. Mungkin hasil impor ganda. Hapus sheet daftar yang tidak dipakai, sisakan satu bernama persis "' + cfg.urutan + '". Tidak ada yang diubah.');
  }
  const lastRow = sh.getLastRow();
  const lastCol = sh.getLastColumn();
  if (lastRow < 2 || lastCol < 1) throw new Error('Sheet "' + cfg.urutan + '" kosong. Tidak ada yang diubah.');
  const isi = sh.getRange(1, 1, lastRow, lastCol).getValues();
  const kolom = {};
  isi[0].forEach((v, c) => {
    const k = normNama_(v);
    Object.keys(KOLOM_URUTAN).forEach(f => { if (KOLOM_URUTAN[f] === k && kolom[f] === undefined) kolom[f] = c; });
  });
  const hilang = ['nama', 'sku', 'baris', 'namaLama'].filter(f => kolom[f] === undefined);
  if (hilang.length) {
    throw new Error('Sheet "' + cfg.urutan + '": baris 1 harus berisi judul kolom ' +
      hilang.map(f => '"' + KOLOM_URUTAN[f] + '"').join(', ') + '. Tidak ada yang diubah.');
  }
  const hasil = [];
  const masalah = [];
  for (let i = 1; i < isi.length; i++) {
    const row = isi[i];
    const nama = String(row[kolom.nama]).trim();
    const sku = String(row[kolom.sku]).trim();
    const mentahBaris = row[kolom.baris];
    if (!nama && !sku && String(mentahBaris).trim() === '') continue;   // baris kosong
    const ket = 'baris ' + (i + 1) + (nama ? ' (' + nama + ')' : '');
    if (!nama) { masalah.push(ket + ': Nama Produk kosong'); continue; }
    if (nama.charAt(0) === '=' || sku.charAt(0) === '=') { masalah.push(ket + ': nama/kode SKU tidak boleh diawali tanda "="'); continue; }
    const sumber = parseBaris_(mentahBaris);
    if (sumber === null) {
      masalah.push(ket + ': "Baris lama" harus berisi nomor baris saja, dipisah koma dan spasi, mis. 76, 125 (isi terbaca: "' + mentahBaris + '")');
      continue;
    }
    const unik = sumber.filter((r, j) => sumber.indexOf(r) === j);
    const namaLama = String(row[kolom.namaLama]).split('|').map(x => x.trim()).filter(x => x !== '');
    if (unik.length && namaLama.length !== sumber.length) {
      masalah.push(ket + ': "Nama di sheet lama" harus berisi nama untuk tiap nomor di "Baris lama" (' + sumber.length + ' nomor, ' +
        namaLama.length + ' nama; pisahkan nama dengan |)');
      continue;
    }
    if (!unik.length && !sku) {
      masalah.push(ket + ': tidak punya "Baris lama" maupun Kode SKU. Kalau ini baris catatan/TOTAL, hapus; kalau produk baru, isi Kode SKU');
      continue;
    }
    let hargaDari = null;
    if (kolom.harga !== undefined && String(row[kolom.harga]).trim() !== '') {
      const h = parseBaris_(row[kolom.harga]);
      if (h === null || h.length !== 1) { masalah.push(ket + ': "Harga dari baris" harus satu nomor baris (isi: "' + row[kolom.harga] + '")'); continue; }
      hargaDari = h[0];
    }
    hasil.push({ nama: nama, sku: sku, sumber: unik, namaLama: unik.length === sumber.length ? namaLama : unik.map(r => namaLama[sumber.indexOf(r)]), hargaDari: hargaDari, barisDaftar: i + 1 });
  }
  if (masalah.length) {
    throw new Error('Sheet "' + cfg.urutan + '" bermasalah (' + masalah.length + '). Tidak ada yang diubah.\n' +
      masalah.slice(0, 10).join('\n') + (masalah.length > 10 ? '\n…' : ''));
  }
  if (!hasil.length) throw new Error('Sheet "' + cfg.urutan + '" tidak berisi produk. Tidak ada yang diubah.');
  return hasil;
}

/** "76, 125" / 76 → [76, 125]; kosong → []; selain nomor baris → null. */
function parseBaris_(v) {
  if (v === '' || v === null || v === undefined) return [];
  if (typeof v === 'number') return isFinite(v) && Math.floor(v) === v && v > 0 ? [v] : null;
  const bagian = String(v).split(/[\s,;+|]+/).filter(x => x !== '');
  const hasil = [];
  for (let j = 0; j < bagian.length; j++) {
    if (!/^\d+$/.test(bagian[j]) || Number(bagian[j]) < 1) return null;
    hasil.push(Number(bagian[j]));
  }
  return hasil;
}

/** Catatan yang dipasang script sendiri pada sel IN/OUT/STOK yang bermasalah (bukan catatan buatan staf). */
function catatanSistem_(n) {
  return /^(DITOLAK:|Sistem sibuk|Isi angka bulat|Baris ini tanpa nama produk|Kolom STOK warna ini berisi|STOK harus angka)/.test(String(n));
}

function normNama_(s) {
  return String(s).toLowerCase().replace(/\s+/g, ' ').trim();
}

/** Kata-kata (huruf/angka, min. 2 karakter) dari nama, untuk memeriksa nama baru masih "nyambung" dengan nama lamanya. */
function kataNama_(s) {
  return String(s).toLowerCase().replace(/[^a-z0-9]+/g, ' ').split(' ').filter(x => x.length >= 2);
}

/** Isi sel IN sheet lama: { n: angka atau null, teks: true kalau angka berformat teks, salah: true kalau isi bukan angka }. */
function bacaIN_(v) {
  if (typeof v === 'number') return { n: v, teks: false, salah: false };
  if (v === '' || v === null || v === undefined) return { n: null, teks: false, salah: false };
  if (typeof v === 'string') {
    if (v.trim() === '') return { n: null, teks: false, salah: false };
    if (/^\s*\d+\s*$/.test(v)) return { n: Number(v), teks: true, salah: false };
  }
  return { n: null, teks: false, salah: true };
}

/**
 * Susun produk sheet baru dari daftar urutan + isi sheet lama. Tidak menulis apa pun.
 * lama / fLama = isi baris produk sheet lama mulai cfg.barisAwal (nilai dan formula kolom Value).
 * Melempar Error (pesan siap tampil) kalau daftar tidak cocok dengan sheet lama, supaya tidak ada stok yang salah tempat.
 */
function susunUrutan_(cfg, mentah, lama, fLama, namaWarna, labelValue) {
  const W = KONFIG.JUMLAH_WARNA;
  const G = GRUP_VALUE.length;
  const awal = cfg.barisAwal;
  const akhir = awal + lama.length - 1;
  const kritis = [];   // catatan yang perlu dibaca user
  const info = [];     // catatan biasa
  const salah = [];
  const perNama = {};
  lama.forEach((row, i) => {
    const k = normNama_(row[1]);
    if (k) (perNama[k] = perNama[k] || []).push(awal + i);
  });
  const dalamRentang = r => r >= awal && r <= akhir;
  const namaBaris = r => String(lama[r - awal][1]).trim();

  // 1. Baris lama untuk tiap produk daftar. Nomor baris selalu dicocokkan dengan namanya; kalau sheet lama sudah bergeser,
  //    dicari lewat nama (hanya kalau namanya unik). Satu baris lama tidak boleh dipakai dua kali.
  const dipakai = {};
  const asal = {};   // nomor baris yang tertulis di daftar → baris lama yang benar-benar dipakai
  const geser = [];
  const diganti = [];   // nama baris lama sudah diganti sejak daftar dibuat, barisnya tetap
  const diharapkan = {};
  mentah.forEach(m => m.namaLama.forEach(n => { diharapkan[normNama_(n)] = true; }));
  const entri = mentah.map(m => {
    const ket = 'Daftar "' + cfg.urutan + '" baris ' + m.barisDaftar + ' (' + m.nama + ')';
    const sumber = [];
    let namaProduk = m.nama;
    m.sumber.forEach((r, j) => {
      const harap = m.namaLama[j];
      let pakai = r;
      if (!dalamRentang(r) || normNama_(namaBaris(r)) !== normNama_(harap)) {
        const cocok = perNama[normNama_(harap)] || [];
        const kini = dalamRentang(r) ? 'bernama "' + namaBaris(r) + '"' : 'di luar daftar produk sheet lama (baris ' + awal + '–' + akhir + ')';
        if (cocok.length === 1) {
          pakai = cocok[0];
          geser.push({ nama: m.nama, dari: r, ke: pakai });
        } else if (dalamRentang(r) && cocok.length === 0 && !diharapkan[normNama_(namaBaris(r))] &&
          kataNama_(namaBaris(r)).some(k => kataNama_(harap).indexOf(k) >= 0)) {
          // Nama di baris ini sudah diganti (mis. salah ketik dibetulkan): bukan nama produk lain di daftar, nama lama tidak ada
          // di baris lain, dan masih ada kata yang sama. Dianggap produk yang sama.
          diganti.push({ nama: m.nama, baris: r, dari: harap, ke: namaBaris(r) });
          if (m.sumber.length === 1 && normNama_(m.nama) === normNama_(harap)) namaProduk = namaBaris(r);
        } else {
          salah.push(ket + ': baris lama ' + r + ' ' + kini + ', daftar menulis "' + harap + '"; nama itu ' +
            (cocok.length ? 'ada di ' + cocok.length + ' baris' : 'tidak ditemukan') + ' di sheet lama.' +
            (dalamRentang(r) && cocok.length === 0 ? ' Kalau nama baris itu memang sudah diganti, ubah kolom "Nama di sheet lama" (dan Nama Produk) di daftar menjadi "' + namaBaris(r) + '".' : ''));
          return;
        }
      }
      asal[r] = pakai;
      if (dipakai[pakai]) {
        salah.push(ket + ': baris lama ' + pakai + ' sudah dipakai oleh baris daftar ' + dipakai[pakai] + ' (stok akan terhitung dua kali).');
        return;
      }
      dipakai[pakai] = m.barisDaftar;
      sumber.push(pakai);
    });
    // Nama baru harus masih berkaitan dengan nama lamanya (mencegah kolom daftar yang terlepas, mis. Sort sebagian kolom).
    const kataBaru = kataNama_(m.nama);
    const kataLama = [];
    sumber.forEach(r => kataNama_(namaBaris(r)).forEach(k => kataLama.push(k)));
    if (sumber.length && kataBaru.length && kataLama.length && !kataBaru.some(k => kataLama.indexOf(k) >= 0)) {
      salah.push(ket + ': nama baru sama sekali beda dari nama baris lama ' + sumber.join('+') + ' ("' + sumber.map(namaBaris).join('" + "') +
        '"). Kolom daftar mungkin terlepas (mis. habis Sort sebagian kolom). Kalau memang sengaja diganti, sisakan minimal satu kata yang sama.');
    }
    return { nama: namaProduk, sku: m.sku, sumber: sumber, hargaDari: m.hargaDari, tambahan: false };
  });
  // "Harga dari baris" ikut dipetakan lewat baris-baris yang sudah dicocokkan namanya.
  entri.forEach((e, idx) => {
    if (e.hargaDari === null) return;
    const asli = e.hargaDari;
    if (asal[asli] !== undefined) {
      e.hargaDari = asal[asli];
    } else if (!dalamRentang(asli)) {
      salah.push('Daftar "' + cfg.urutan + '" baris ' + mentah[idx].barisDaftar + ' (' + e.nama + '): "Harga dari baris" ' + asli +
        ' di luar daftar produk sheet lama (baris ' + awal + '–' + akhir + ').');
    } else if (geser.length) {
      kritis.push('Harga "' + e.nama + '" diambil dari baris lama ' + asli + ' (' + namaBaris(asli) + ') tanpa verifikasi nama, padahal ada baris yang bergeser. Cek hargamu.');
    }
  });
  if (salah.length) {
    throw new Error('Daftar "' + cfg.urutan + '" tidak cocok dengan sheet "' + cfg.nama + '" (' + salah.length + ' masalah). Tidak ada yang diubah.\n' +
      salah.slice(0, 10).join('\n') + (salah.length > 10 ? '\n…' : ''));
  }

  // 2. Baris lama yang tidak disebut daftar: stok 0 → tidak ikut; berstok (atau isi IN yang tak terbaca) → ditaruh di bawah
  //    supaya tidak ada yang hilang diam-diam.
  const dalamIN = row => { const o = []; for (let k = 0; k < W; k++) o.push(bacaIN_(row[3 + 2 * k])); return o; };
  const jumlahN = arr => arr.reduce((a, x) => a + (x.n === null ? 0 : x.n), 0);
  const dibuang = [];
  const ditambah = [];
  lama.forEach((row, i) => {
    const r = awal + i;
    if (dipakai[r]) return;
    const sel = dalamIN(row);
    const stok = jumlahN(sel);
    const nama = String(row[1]).trim();
    if (stok !== 0 || sel.some(x => x.salah)) {
      entri.push({ nama: nama, sku: String(row[2]).trim(), sumber: [r], hargaDari: null, tambahan: true });
      ditambah.push({ r: r, nama: nama, stok: stok });
      const kembar = entri.find(e => !e.sumber.length && !e.tambahan && normNama_(e.nama) === normNama_(nama));
      kritis.push('Baris lama ' + r + ' "' + nama + '" berstok / isi IN tak terbaca tapi tidak ada di daftar: ditambahkan di bagian bawah.' +
        (kembar ? ' Namanya sama dengan produk BARU "' + kembar.nama + '" di daftar; stoknya tidak digabung otomatis, pindahkan manual.' : ''));
    } else if (nama) {
      dibuang.push({ r: r, nama: nama });
    }
  });

  // 3. Stok per warna: jumlah kolom IN semua baris lama yang digabung. Angka berformat teks dibaca sebagai angka;
  //    isi lain yang bukan angka dikosongkan (diberi catatan).
  let teksAngka = 0;
  let bukanAngka = 0;
  entri.forEach(e => {
    e.stok = [];
    for (let k = 0; k < W; k++) {
      let total = null;
      e.sumber.forEach(r => {
        const v = lama[r - awal][3 + 2 * k];
        const x = bacaIN_(v);
        if (x.n !== null) {
          total = (total === null ? 0 : total) + x.n;
          if (x.teks) teksAngka++;
        } else if (x.salah) {
          bukanAngka++;
          kritis.push('Baris ' + r + ' ' + namaWarna[k] + ': IN bukan angka ("' + v + '"), dikosongkan.');
        }
      });
      e.stok.push(total === null ? '' : total);
    }
  });
  const jumlah = arr => arr.reduce((a, v) => a + (v === '' ? 0 : v), 0);
  const stokLama = lama.reduce((a, row) => a + jumlahN(dalamIN(row)), 0);
  const stokBaru = entri.reduce((a, e) => a + jumlah(e.stok), 0);
  if (Math.abs(stokLama - stokBaru) > 1e-6) {
    throw new Error('Pemeriksaan total stok gagal (sheet lama ' + stokLama + ' unit, hasil susunan ' + stokBaru + ' unit). Tidak ada yang diubah.');
  }

  // 4. Harga Value tiap produk: dari formula baris sumbernya (yang pertama punya harga), atau dari "Harga dari baris".
  const memo = {};
  const hargaBaris = (r, lapor) => {
    if (memo[r]) return memo[r];
    const f = fLama[r - awal];
    memo[r] = GRUP_VALUE.map((g, gi) => {
      if (!f[gi]) return { harga: null, rusak: false };
      const harga = hargaDariFormula_(f[gi]);
      if (harga === null) {
        if (lapor) kritis.push('Baris ' + r + ' ' + namaBaris(r) + ': formula ' + labelValue[gi] + ' lama rusak (' + f[gi] + '), dikosongkan. Isi harga manual.');
        return { harga: null, rusak: true };
      }
      if (lapor && !formulaLamaStandar_(f[gi], g.warna.map(k => 4 + 2 * k), r)) {
        kritis.push('DIPERBAIKI baris ' + r + ' ' + namaBaris(r) + ': formula ' + labelValue[gi] + ' lama ' + f[gi] +
          ' → sekarang semua warna ' + labelValue[gi] + ' baris ini × ' + harga + ' (sama seperti baris lain).');
      }
      return { harga: harga, rusak: false };
    });
    return memo[r];
  };
  entri.forEach(e => e.sumber.forEach(r => hargaBaris(r, true)));
  const tanpaHarga = GRUP_VALUE.map(() => []);
  entri.forEach((e, idx) => {
    const kandidat = e.hargaDari === null ? e.sumber : e.sumber.concat([e.hargaDari]);
    e.harga = [];
    GRUP_VALUE.forEach((g, gi) => {
      const dariSumber = e.sumber.map(r => hargaBaris(r, false)[gi].harga).filter(h => h !== null);
      if (new Set(dariSumber).size > 1) {
        kritis.push('Baris lama ' + e.sumber.join('+') + ' "' + e.nama + '": harga ' + labelValue[gi] + ' beda antar baris yang digabung (' +
          dariSumber.join(' / ') + '), dipakai ' + dariSumber[0] + '.');
      }
      const harga = kandidat.map(r => hargaBaris(r, false)[gi].harga).filter(h => h !== null)[0];
      e.harga.push(harga === undefined ? null : harga);
      if (harga === undefined && !e.sumber.some(r => hargaBaris(r, false)[gi].rusak)) tanpaHarga[gi].push(KONFIG.BARIS_DATA + idx);
    });
    e.adaTotal = kandidat.some(r => !!fLama[r - awal][G]);
  });
  tanpaHarga.forEach((rows, gi) => {
    if (rows.length && (cfg.tanpaValue || []).indexOf(labelValue[gi]) < 0) {
      info.push(labelValue[gi] + ': ' + rows.length + ' baris tanpa formula harga, value kosong' +
        (rows.length <= 15 ? ' (baris sheet baru ' + rows.join(', ') + ')' : '') + '.');
    }
  });
  const baru = entri.filter(e => !e.sumber.length);
  if (baru.length) {
    info.push(baru.length + ' produk BARU memakai harga Value dari baris sheet lama yang disebut daftar (model sama atau harga standar). ' +
      'Cek kalau harganya perlu beda.');
  }

  // 5. OUT yang masih terisi: menurut alur lama, IN biasanya SUDAH dikurangi OUT.
  const outTerisi = [];
  entri.forEach(e => e.sumber.forEach(r => {
    for (let k = 0; k < W; k++) {
      const o = lama[r - awal][4 + 2 * k];
      if (typeof o === 'number' && o !== 0) outTerisi.push('baris ' + r + ' ' + namaBaris(r) + ' – ' + namaWarna[k] + ': OUT ' + o);
    }
  }));

  diganti.forEach(g => kritis.push('Nama baris lama ' + g.baris + ' sudah diganti sejak daftar dibuat: "' + g.dari + '" → "' + g.ke +
    '". Dianggap produk yang sama, stok diambil dari baris itu' + (g.dari === g.nama ? ' dan nama di sheet baru ikut nama sekarang.' : '.')));
  const ringkasGeser = geser.length
    ? ['' + geser.length + ' nomor "Baris lama" di daftar sudah bergeser; stok diambil lewat nama baris. Contoh: ' +
      geser.slice(0, 5).map(g => g.nama + ' (' + g.dari + ' → ' + g.ke + ')').join('; ') + '.']
    : [];
  return {
    entri: entri, peringatan: kritis.concat(ringkasGeser, info), dibuang: dibuang, ditambah: ditambah, outTerisi: outTerisi,
    stokLama: stokLama, stokBaru: stokBaru, geser: geser, diganti: diganti, teksAngka: teksAngka, bukanAngka: bukanAngka,
    dariLama: entri.filter(e => e.sumber.length).length, baru: baru.length, digabung: entri.filter(e => e.sumber.length > 1).length,
  };
}

function teksBanner_() {
  return KONFIG.IZINKAN_PEMBATALAN ? TEKS_BANNER_BARU : TEKS_BANNER_LAMA;
}

/** Total IN atau OUT HARI INI (semua warna) langsung dari Log. Sama dengan rumus per warna di baris rekap, tanpa kriteria warna; bersih (Qty negatif = pembatalan). */
function rumusTotalHarian_(logNama, jenis) {
  const q = "'" + logNama + "'!";
  return '=SUMIFS(' + q + '$H:$H,' + q + '$G:$G,"' + jenis + '",' + q + '$A:$A,">="&TODAY(),' + q + '$A:$A,"<"&(TODAY()+1))';
}

function bangunSheet_(sh, cfg, d) {
  const W = d.daftar.length;
  const n = d.entri.length;
  const kolStok = k => 4 + 3 * k;
  const kolValue = 4 + 3 * W;
  const totalKolom = kolValue + GRUP_VALUE.length;   // 4 grup + Total Value
  const barisDataAkhir = KONFIG.BARIS_DATA + n - 1;
  const barisTotal = barisDataAkhir + 2;
  const barisMutasi = barisTotal + 1;
  pastikanUkuran_(sh, barisMutasi + 1, totalKolom);   // +1: baris total MASUK hari ini di bawah baris rekap

  // Header
  sh.getRange(1, 1).setValue('No');
  sh.getRange(1, 2).setValue('Nama Produk');
  sh.getRange(1, 3).setValue('Kode SKU');
  sh.getRange(1, 4).setValue(teksBanner_());
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
  const data = d.entri.map((e, i) => {
    const out = [i + 1, e.nama, e.sku];
    for (let k = 0; k < W; k++) {
      const w = d.daftar[k];
      out.push(w.kSumber === null ? '' : e.stok[w.kSumber], '', '');
    }
    return out;
  });
  sh.getRange(KONFIG.BARIS_DATA, 1, n, 3 + 3 * W).setValues(data);

  // Value: harga per baris diambil dari formula lama, referensi diganti ke kolom STOK.
  const fBaru = d.entri.map((e, i) => {
    const r = KONFIG.BARIS_DATA + i;
    const hasil = GRUP_VALUE.map((g, gi) => {
      if (e.harga[gi] === null) return '';
      const refs = [];
      d.daftar.forEach((w, k) => { if (w.gi === gi) refs.push(huruf_(kolStok(k)) + r); });
      return '=(' + refs.join('+') + ')*' + e.harga[gi];
    });
    hasil.push(e.adaTotal ? '=SUM(' + huruf_(kolValue) + r + ':' + huruf_(kolValue + GRUP_VALUE.length - 1) + r + ')' : '');
    return hasil;
  });
  sh.getRange(KONFIG.BARIS_DATA, kolValue, n, GRUP_VALUE.length + 1).setFormulas(fBaru);

  // Total + mutasi hari ini. SUM sengaja sampai baris kosong di bawah produk: produk baru ditambah dengan
  // "Insert row above" pada baris kosong itu, sehingga rentang SUM ikut melebar.
  const akhirStok = huruf_(kolValue - 1);
  const q = "'" + cfg.log + "'!";
  const fTotal = ['=SUMIF($D$3:$' + akhirStok + '$3,"STOK",D' + barisTotal + ':' + akhirStok + barisTotal + ')'];
  const fMutasi = [rumusTotalHarian_(cfg.log, 'OUT')];   // C: total KELUAR hari ini (semua warna), langsung dari Log
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
  sh.getRange(barisMutasi + 1, 3).setFormulas([[rumusTotalHarian_(cfg.log, 'IN')]]);   // total MASUK hari ini
  sh.getRange(barisMutasi, 3).setNumberFormat(FORMAT_TOTAL_KELUAR);
  sh.getRange(barisMutasi + 1, 3).setNumberFormat(FORMAT_TOTAL_MASUK);

  // Format
  sh.getRange(1, 1, 3, totalKolom).setFontWeight('bold').setHorizontalAlignment('center')
    .setVerticalAlignment('middle').setWrap(true);
  sh.getRange(1, 4, 1, 3 * W).setBackground(KONFIG.WARNA_SEL.BANNER_BG).setFontColor(KONFIG.WARNA_SEL.BANNER_FG);
  const hasilValidasi = [];
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
    hasilValidasi.push(pasangValidasi_(sh.getRange(KONFIG.BARIS_DATA, c, n, 1), huruf_(c) + KONFIG.BARIS_DATA, 'stok'));
    hasilValidasi.push(pasangValidasi_(sh.getRange(KONFIG.BARIS_DATA, c + 1, n, 2), huruf_(c + 1) + KONFIG.BARIS_DATA, 'inout'));
  }
  sh.getRange(KONFIG.BARIS_DATA, 4, barisMutasi - KONFIG.BARIS_DATA + 1, 3 * W).setHorizontalAlignment('center');
  sh.getRange(KONFIG.BARIS_DATA, 4, n, 3 * W).setNumberFormat(KONFIG.FORMAT_ANGKA);   // angka bulat; cegah format tanggal menempel
  for (let k = 0; k < W; k++) sh.getRange(KONFIG.BARIS_DATA, kolStok(k), n, 1).setNumberFormat(KONFIG.FORMAT_STOK);   // STOK 0 tampil kosong
  sh.getRange(KONFIG.BARIS_DATA, kolValue, barisMutasi - KONFIG.BARIS_DATA + 1, totalKolom - kolValue + 1)
    .setNumberFormat('#,##0');
  sh.getRange(barisTotal, 3).setNumberFormat('#,##0" unit"');
  sh.getRange(barisTotal, 1, 3, totalKolom).setFontWeight('bold');
  sh.setColumnWidth(1, 40);
  sh.setColumnWidth(2, 190);
  sh.setColumnWidth(3, 130);
  sh.setColumnWidths(4, 3 * W, 48);
  sh.setColumnWidths(kolValue, totalKolom - kolValue + 1, 110);
  sh.setFrozenRows(3);
  sh.setFrozenColumns(2);
  // Hanya kasus yang mengubah perilaku dilaporkan (varian rumus berkoma / titik koma bekerja sama).
  const catatan = [];
  const tanpa = hasilValidasi.filter(x => x === null).length;
  const sederhana = hasilValidasi.filter(x => x === 'rentang').length;
  // Catatan tambahan di dialog akhir: lihat migrasi_ (infoBangun.catatan).
  if (tanpa) {
    catatan.push('Validasi angka TIDAK terpasang di ' + tanpa + ' dari ' + hasilValidasi.length + ' bagian kolom (Google menolak aturannya). ' +
      'Script tetap menolak isian yang salah dengan tanda merah + catatan, tapi sel tidak menahan ketikan huruf.');
  }
  if (sederhana) {
    catatan.push('Validasi angka memakai aturan sederhana "angka antara" di ' + sederhana + ' dari ' + hasilValidasi.length +
      ' bagian kolom (rumus ditolak Google): desimal lolos ke sel, lalu ditolak script dengan tanda merah.');
  }
  return { catatan: catatan };
}

// ---------------------------------------------------------------- trigger & proteksi

function aktifkanInputOtomatis() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const ui = SpreadsheetApp.getUi();
  const trigger = fn => ScriptApp.getProjectTriggers().filter(t => t.getHandlerFunction() === fn);
  const adaEdit = trigger('prosesInputStok');
  const adaSapu = trigger('sapuInputStok');
  const adaRekap = trigger('rekapHarianOtomatis');
  if (adaEdit.length && adaSapu.length && adaRekap.length) {
    ui.alert('Input otomatis sudah aktif (' + adaEdit.length + ' trigger edit + ' + adaSapu.length + ' penyapu + ' + adaRekap.length +
      ' rekap harian milik akun ini).');
    return;
  }
  // Melengkapi yang kurang tanpa menggandakan: instalasi lama (edit + penyapu) hanya ditambah trigger rekap harian.
  const ditambah = [];
  if (!adaEdit.length) { ScriptApp.newTrigger('prosesInputStok').forSpreadsheet(ss).onEdit().create(); ditambah.push('trigger edit'); }
  if (!adaSapu.length) { ScriptApp.newTrigger('sapuInputStok').timeBased().everyMinutes(KONFIG.SAPU_MENIT).create(); ditambah.push('penyapu'); }
  if (!adaRekap.length) {
    ScriptApp.newTrigger('rekapHarianOtomatis').timeBased().everyDays(1).atHour(KONFIG.REKAP_JAM).nearMinute(KONFIG.REKAP_MENIT).inTimezone(KONFIG.ZONA_WAKTU).create();
    ditambah.push('rekap harian');
  }
  if (ss.getSpreadsheetTimeZone() !== KONFIG.ZONA_WAKTU) ss.setSpreadsheetTimeZone(KONFIG.ZONA_WAKTU);
  let pesan = 'Input otomatis AKTIF (trigger edit + penyapu tiap ' + KONFIG.SAPU_MENIT + ' menit untuk angka yang tertinggal + rekap harian tiap malam ±' +
    ('0' + KONFIG.REKAP_JAM).slice(-2) + '.' + ('0' + KONFIG.REKAP_MENIT).slice(-2) + ' WIB). Ditambahkan sekarang: ' + ditambah.join(', ') +
    '.\nTrigger berjalan atas nama akun: ' + Session.getEffectiveUser().getEmail() +
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
    if (['prosesInputStok', 'sapuInputStok', 'rekapHarianOtomatis'].indexOf(t.getHandlerFunction()) >= 0) {
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
    ss.getSheets().filter(x => x.getName() === cfg.log || x.getName() === cfg.rekap || x.getName().indexOf('Arsip ' + cfg.log + ' ') === 0).forEach(log => {
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
  const sapu = ScriptApp.getProjectTriggers().filter(x => x.getHandlerFunction() === 'sapuInputStok').length;
  const rekapT = ScriptApp.getProjectTriggers().filter(x => x.getHandlerFunction() === 'rekapHarianOtomatis').length;
  const baris = ['Trigger edit aktif (akun ini): ' + t + (t > 1 ? '  ← lebih dari 1, hapus lewat menu Matikan lalu aktifkan lagi' : '') +
    '\nPenyapu angka tertinggal (tiap ' + KONFIG.SAPU_MENIT + ' menit): ' + sapu +
    (t && !sapu ? '  ← belum ada, jalankan menu 2. Aktifkan input otomatis sekali lagi' : '') +
    '\nRekap harian (tiap malam ±' + ('0' + KONFIG.REKAP_JAM).slice(-2) + '.' + ('0' + KONFIG.REKAP_MENIT).slice(-2) + ' WIB): ' + rekapT +
    (t && !rekapT ? '  ← belum ada, jalankan menu 2. Aktifkan input otomatis sekali lagi' : '') +
    '\n(Angka "tiap … menit" hanya nilai di kode; interval trigger sebenarnya dilihat di Apps Script → Triggers.)'];
  KONFIG.SISTEM.forEach(cfg => {
    const sh = ss.getSheetByName(cfg.nama);
    let status = 'TIDAK ADA';
    if (sh) {
      const peta = bacaPeta_(sh);
      if (!Object.keys(peta.kolom).length) {
        status = 'format lama (belum dimigrasi); daftar urutan "' + cfg.urutan + '" ' +
          (ss.getSheetByName(cfg.urutan) ? 'sudah ada' : 'BELUM ada (impor dulu, lihat PANDUAN)');
      } else {
        status = 'format STOK/IN/OUT (aktif)';
        if (!peta.labelAda) {
          status += '  ← label "' + KONFIG.LABEL_TOTAL + '" di kolom B HILANG: sheet ini TIDAK diproses sampai labelnya dikembalikan';
        } else {
          // rekap "hari ini" (baris di bawah TOTAL STOK, kolom IN warna pertama) harus merujuk log sheet ini
          const rumus = sh.getRange(peta.barisTotal + 1, 5).getFormula();
          if (rumus.indexOf("'" + cfg.log + "'!") < 0) {
            status += '  ← rekap per warna masih merujuk log versi lama (lihat PANDUAN, "Memasang versi kode baru")';
          }
          if (!sh.getRange(peta.barisTotal + 1, 3).getFormula()) status += '  ← total harian (kolom C) belum ada: jalankan menu 4';
        }
      }
    }
    baris.push('"' + cfg.nama + '": ' + status);
  });
  KONFIG.SISTEM.forEach(cfg => {
    const log = ss.getSheetByName(cfg.log);
    baris.push('"' + cfg.log + '": ' + (log ? Math.max(log.getLastRow() - 1, 0) + ' baris mutasi' : 'BELUM ada'));
  });
  const zona = ss.getSpreadsheetTimeZone();
  KONFIG.SISTEM.forEach(cfg => {
    const rk = ss.getSheetByName(cfg.rekap);
    if (!rk) { baris.push('"' + cfg.rekap + '": BELUM ada (migrasi baru membuatnya; sheet yang sudah dimigrasi: menu 4)'); return; }
    const w = waktuNomor_(rk.getRange(2, KOLOM_REKAP_STATUS).getValue(), zona);
    // getLastRow ikut menghitung sel status (O2): hitung hari dari kolom A saja.
    const nHari = rk.getLastRow() > 1 ? rk.getRange(2, 1, rk.getLastRow() - 1, 1).getValues().filter(x => x[0] !== '').length : 0;
    let teks = nHari + ' hari tersimpan; ';
    if (w === null) {
      teks += 'belum pernah dihitung' + (rekapT ? ' (trigger malam pertama atau menu "Perbarui rekap harian sekarang")' : '');
    } else {
      teks += 'terakhir dihitung ' + Utilities.formatDate(new Date(Math.round(w * 86400000) + Date.UTC(1899, 11, 30)), 'UTC', 'dd/MM/yyyy HH:mm') + ' WIB';
      if (rekapT && waktuSerial_(new Date()) - w > 26 / 24) teks += '  ← lebih dari 26 jam lalu: cek Executions (trigger rekap gagal atau kuota habis?)';
    }
    baris.push('"' + cfg.rekap + '": ' + teks);
  });
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
  let labelAda = false;
  if (lastRow >= KONFIG.BARIS_DATA) {
    const b = sheet.getRange(KONFIG.BARIS_DATA, 2, lastRow - KONFIG.BARIS_DATA + 1, 1).getValues();
    for (let i = 0; i < b.length; i++) {
      if (String(b[i][0]).trim().toUpperCase() === KONFIG.LABEL_TOTAL) {
        barisTotal = KONFIG.BARIS_DATA + i;
        labelAda = true;
        break;
      }
    }
  }
  // labelAda=false (label "TOTAL STOK" terhapus/diubah): batas produk tidak diketahui. Baris total dan rekap (isinya rumus) akan terbaca
  // sebagai produk dan angkanya diproses sebagai input, jadi pemrosesan berhenti (lihat prosesInputStok/prosesBlok_/sapuInputStok).
  return { kolom: kolom, barisTotal: barisTotal, kolomTerakhir: kolomTerakhir, labelAda: labelAda };
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

/**
 * Mutasi terbaru ditaruh di baris 2 (paling atas), tepat di bawah header; dalam satu batch, yang diproses
 * paling akhir ada paling atas. Baris disisipkan SETELAH baris 2 lalu isi baris 2 disalin ke bawah:
 * rumus/aturan buatan staf yang rentangnya berawal di baris 2 (mis. G2:G) ikut melebar, tidak bergeser.
 * Salinan memakai copyTo (nilai + format apa adanya), bukan getValues, supaya jam tidak terkonversi ulang.
 */
function tulisLog_(ss, cfg, rows) {
  const sh = siapkanLog_(ss, cfg.log);
  const n = rows.length;
  const lebar = HEADER_LOG.length;
  if (sh.getMaxRows() < 3) sh.insertRowsAfter(sh.getMaxRows(), 3 - sh.getMaxRows());
  sh.insertRowsBefore(3, n);
  sh.getRange(2, 1, 1, lebar).copyTo(sh.getRange(n + 2, 1, 1, lebar));
  sh.getRange(2, 1, n, lebar).clearFormat();   // baris baru bisa mewarisi format dari baris di atasnya
  sh.getRange(2, 1, n, 1).setNumberFormat(KONFIG.FORMAT_WAKTU);
  sh.getRange(2, 1, n, lebar).setValues(rows.slice().reverse());
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

// ---------------------------------------------------------------- rekap harian (disimpan per hari; dihitung dari Log + arsip)
//
// Sumber kebenaran = Log (dan sheet arsip bulanannya). Rekap TIDAK dihitung dari selisih per entri dan tidak dipanggil dari jalur edit:
// satu eksekusi per malam (trigger rekapHarianOtomatis) atau menu. Hasilnya nilai statis supaya bertahan walau Log diarsipkan.
// Aturan: hari yang tidak punya baris di sumber TIDAK pernah dinolkan/dihapus; hari yang sumbernya kini lebih sedikit tidak diturunkan
// otomatis (Status "SUMBER BERKURANG"); hanya menu "Bangun ulang" yang boleh menurunkan.

function siapkanRekap_(ss, nama) {
  let sh = ss.getSheetByName(nama);
  if (sh) return sh;
  sh = ss.insertSheet(nama);
  pastikanUkuran_(sh, 2, KOLOM_REKAP_STATUS);
  sh.getRange(1, 1, 1, HEADER_REKAP.length).setValues([HEADER_REKAP]).setFontWeight('bold').setBackground(KONFIG.WARNA_SEL.HEADER);
  sh.getRange(1, KOLOM_REKAP_STATUS).setValue('Terakhir dihitung (WIB)').setFontWeight('bold').setBackground(KONFIG.WARNA_SEL.HEADER);
  sh.setFrozenRows(1);
  [100, 90, 90, 70, 60, 110, 120, 110, 120, 90, 120, 260, 200, 30, 150].forEach((w, i) => sh.setColumnWidth(i + 1, w));
  return sh;
}

/** Baca seluruh Log (dan arsipnya bila semuaSumber) dalam satu getValues per sheet. Waktu (kolom A) diubah ke nomor seri WIB; null = tak terbaca. */
function kumpulkanBarisLog_(ss, cfg, semuaSumber) {
  const zona = ss.getSpreadsheetTimeZone();
  const log = ss.getSheetByName(cfg.log);
  if (!log) throw new Error('Sheet "' + cfg.log + '" tidak ada.');
  const sumber = [log];
  if (semuaSumber) {
    const pola = new RegExp('^Arsip ' + cfg.log.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ' \\d{4}-\\d{2}$');
    ss.getSheets().forEach(sh => { if (pola.test(sh.getName())) sumber.push(sh); });
  }
  const total = sumber.reduce((a, sh) => a + Math.max(0, sh.getLastRow() - 1), 0);
  if (total > KONFIG.REKAP_BATAS_BARIS) {
    throw new Error('Log + arsip terlalu besar (' + total + ' baris, batas ' + KONFIG.REKAP_BATAS_BARIS +
      '). Arsipkan log lama dulu (menu "Arsipkan log bulan lalu"), lalu ulangi.');
  }
  const t0 = Date.now();
  const unik = sumber.length > 1 ? new Map() : null;   // baris yang sama di Log dan arsip (arsip terhenti sebelum menghapus) dihitung sekali
  const hasil = [];
  sumber.forEach(sh => {
    if (Date.now() - t0 > KONFIG.REKAP_BATAS_MS) {
      throw new Error('Waktu eksekusi hampir habis saat membaca sumber; belum ada yang ditulis. Arsipkan log lama atau jalankan lagi.');
    }
    const n = sh.getLastRow() - 1;
    if (n < 1) return;
    const nilai = sh.getRange(2, 1, n, 10).getValues();
    const ubah = konversiKolomWaktu_(nilai.map(b => b[0]), zona);
    const lokal = unik ? new Map() : null;
    nilai.forEach(b => {
      b[0] = ubah(b[0]);
      if (!unik) { hasil.push(b); return; }
      const k = b[0] === null ? 'x|' + b.join('|') : kunciBaris_(b);
      const e = lokal.get(k);
      if (e) e.n++; else lokal.set(k, { baris: b, n: 1 });
    });
    if (unik) lokal.forEach((e, k) => { const g = unik.get(k); if (!g || g.n < e.n) unik.set(k, e); });
  });
  if (unik) unik.forEach(e => { for (let i = 0; i < e.n; i++) hasil.push(e.baris); });
  return hasil;
}

/** Jumlahkan baris Log (kolom A sudah nomor seri) per nomor hari WIB. dari/sampai = nomor hari (null = tanpa batas bawah). */
function agregasiBaris_(baris, dari, sampai) {
  const hari = {};
  const info = { dibaca: baris.length, tidakTerbaca: 0, qtyRusak: 0, masaDepan: 0 };
  baris.forEach(b => {
    if (b[0] === null || b[0] === undefined) { info.tidakTerbaca++; return; }
    const h = Math.floor(b[0]);
    if (dari !== null && h < dari) return;
    if (h > sampai) { info.masaDepan++; return; }
    const a = hari[h] || (hari[h] = { masuk: 0, keluar: 0, entri: 0, batalIN: 0, batalOUT: 0, opnameEntri: 0, opnameSelisih: 0, ditolak: 0 });
    const jenis = String(b[6]);
    if (jenis === 'IN' || jenis === 'OUT') {
      const q = Number(b[7]);
      if (b[7] === '' || !isFinite(q)) { info.qtyRusak++; return; }
      if (jenis === 'IN') a.masuk += q; else a.keluar += q;
      if (q > 0) a.entri++;
      else if (q < 0) { if (jenis === 'IN') a.batalIN -= q; else a.batalOUT -= q; }
    } else if (jenis === 'KOREKSI') {
      a.opnameEntri++;
      const sb = Number(b[8]);
      const sd = Number(b[9]);
      if (b[8] !== '' && b[9] !== '' && isFinite(sb) && isFinite(sd)) a.opnameSelisih += sd - sb;
    } else if (jenis === 'DITOLAK') {
      a.ditolak++;
    }
  });
  return { hari: hari, info: info };
}

/** Tabel rekap yang ada: baris per hari ({hari, nilai}) + baris bertanggal tak terbaca (dipertahankan). Tanggal ganda digabung (Entri terbesar menang). */
function bacaTabelRekap_(sh, zona) {
  const hasil = { baris: [], lain: [] };
  const n = sh.getLastRow() - 1;
  if (n < 1) return hasil;
  const nilai = sh.getRange(2, 1, n, HEADER_REKAP.length).getValues();
  const ubahA = konversiKolomWaktu_(nilai.map(b => b[0]), zona);
  const ubahK = konversiKolomWaktu_(nilai.map(b => b[10]), zona);
  const peta = new Map();
  nilai.forEach(b => {
    if (b.every(x => x === '')) return;
    const w = ubahA(b[0]);
    if (w === null) { hasil.lain.push(b); return; }
    const h = Math.floor(w);
    const baris = b.slice();
    baris[0] = h;
    const hitung = ubahK(b[10]);
    if (hitung !== null) baris[10] = hitung;
    const ada = peta.get(h);
    if (!ada) { peta.set(h, baris); return; }
    const unggul = Number(baris[4]) > Number(ada[4]) ? baris : ada;
    const kalah = unggul === baris ? ada : baris;
    unggul[12] = [unggul[12], kalah[12]].filter((x, i, a) => String(x).trim() !== '' && a.indexOf(x) === i).join(' | ');
    peta.set(h, unggul);
  });
  peta.forEach((v, h) => hasil.baris.push({ hari: h, nilai: v }));
  return hasil;
}

function gabungRekap_(lama, baru, paksa, sekarang) {
  const peta = new Map(lama.baris.map(x => [x.hari, x.nilai]));
  let ditulis = 0;
  let dipertahankan = 0;
  Object.keys(baru).forEach(k => {
    const h = Number(k);
    const a = baru[k];
    const ada = peta.get(h);
    if (!ada || paksa || a.entri >= Number(ada[4] || 0)) {
      peta.set(h, [h, a.masuk, a.keluar, a.masuk - a.keluar, a.entri, a.batalIN, a.batalOUT, a.opnameEntri, a.opnameSelisih, a.ditolak,
        sekarang, 'OK', ada ? ada[12] : '']);
      ditulis++;
    } else {
      const tetap = ada.slice();
      tetap[11] = 'SUMBER BERKURANG: Log/arsip kini ' + a.entri + ' entri, tersimpan ' + ada[4] +
        '. Angka lama dipertahankan; pakai "Bangun ulang rekap harian" bila memang benar.';
      peta.set(h, tetap);
      dipertahankan++;
    }
  });
  const baris = Array.from(peta.keys()).sort((x, y) => y - x).map(h => peta.get(h));
  return { baris: baris.concat(lama.lain), ditulis: ditulis, dipertahankan: dipertahankan };
}

function tulisTabelRekap_(sh, baris, sekarang) {
  if (baris.length) {
    pastikanUkuran_(sh, baris.length + 1, KOLOM_REKAP_STATUS);
    sh.getRange(2, 1, baris.length, HEADER_REKAP.length).setValues(baris);
    sh.getRange(2, 1, baris.length, 1).setNumberFormat('dd/MM/yyyy');
    sh.getRange(2, 2, baris.length, 9).setNumberFormat('#,##0');
    sh.getRange(2, 11, baris.length, 1).setNumberFormat('dd/MM/yyyy HH:mm');
  }
  sh.getRange(2, KOLOM_REKAP_STATUS).setValue(sekarang).setNumberFormat('dd/MM/yyyy HH:mm');
}

/**
 * Hitung ulang rekap satu sheet. opsi.semua: seluruh hari dari Log + arsip; selain itu hanya jendela terakhir (hari ini + REKAP_HARI_ULANG-1
 * hari sebelumnya, atau mulai sehari sebelum hari tersimpan terakhir kalau ada hari yang terlewat) dari Log. opsi.paksa: boleh menurunkan.
 */
function perbaruiRekapSatu_(ss, cfg, opsi) {
  const sh = ss.getSheetByName(cfg.rekap);
  if (!sh) throw new Error('Sheet "' + cfg.rekap + '" belum ada (jalankan menu 4).');
  const sekarang = waktuSerial_(new Date());
  const hariIni = Math.floor(sekarang);
  const lama = bacaTabelRekap_(sh, ss.getSpreadsheetTimeZone());
  let dari = null;
  let semuaSumber = true;
  if (!opsi.semua && lama.baris.length) {
    const terakhir = Math.max.apply(null, lama.baris.map(x => x.hari));
    dari = Math.min(hariIni - (KONFIG.REKAP_HARI_ULANG - 1), terakhir - 1);
    semuaSumber = false;
  }
  const agr = agregasiBaris_(kumpulkanBarisLog_(ss, cfg, semuaSumber), dari, hariIni);
  const gabung = gabungRekap_(lama, agr.hari, !!opsi.paksa, sekarang);
  tulisTabelRekap_(sh, gabung.baris, sekarang);
  return { ditulis: gabung.ditulis, dipertahankan: gabung.dipertahankan, info: agr.info, semuaSumber: semuaSumber };
}

/** Serialkan rekap dengan rekap lain (trigger vs menu). Lock skrip terpisah dari lock dokumen yang dipakai edit, jadi tidak menghalangi staf. */
function denganKunciRekap_(fn) {
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(30000)) throw new Error('Rekap lain sedang berjalan. Coba lagi sebentar lagi.');
  try {
    return fn();
  } finally {
    lock.releaseLock();
  }
}

function ringkasRekap_(cfg, h) {
  return cfg.rekap + ': ' + h.ditulis + ' hari ditulis' + (h.dipertahankan ? ', ' + h.dipertahankan + ' hari dipertahankan (sumber berkurang)' : '') +
    '; ' + h.info.dibaca + ' baris Log dibaca' + (h.semuaSumber ? ' (Log + arsip)' : '') +
    (h.info.tidakTerbaca ? '; PERIKSA: ' + h.info.tidakTerbaca + ' baris Waktu tak terbaca diabaikan' : '') +
    (h.info.qtyRusak ? '; PERIKSA: ' + h.info.qtyRusak + ' baris Qty bukan angka diabaikan' : '') +
    (h.info.masaDepan ? '; PERIKSA: ' + h.info.masaDepan + ' baris bertanggal masa depan diabaikan' : '') + '.';
}

/**
 * Trigger harian (±00.30 WIB): hitung ulang jendela terakhir dari Log. Tidak membuat sheet, tidak memakai UI. Satu sheet gagal tidak
 * menghentikan yang lain; galat dilempar di akhir supaya eksekusi berstatus Failed di Executions.
 */
function rekapHarianOtomatis() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const galat = [];
  denganKunciRekap_(() => {
    KONFIG.SISTEM.forEach(cfg => {
      try {
        if (!ss.getSheetByName(cfg.rekap) || !ss.getSheetByName(cfg.log)) return;   // belum dimigrasi / belum disiapkan (menu 4)
        perbaruiRekapSatu_(ss, cfg, { semua: false, paksa: false });
      } catch (err) {
        galat.push(cfg.nama + ': ' + err.message);
      }
    });
  });
  if (galat.length) throw new Error('Rekap harian gagal: ' + galat.join(' | '));
}

/** Menu: hitung ulang jendela terakhir sekarang (termasuk hari ini, yang belum final). */
function perbaruiRekapSekarang() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const lapor = [];
  try {
    denganKunciRekap_(() => {
      KONFIG.SISTEM.forEach(cfg => {
        if (!ss.getSheetByName(cfg.rekap)) { lapor.push(cfg.rekap + ': belum ada (jalankan menu 4 atau migrasi dulu).'); return; }
        try { lapor.push(ringkasRekap_(cfg, perbaruiRekapSatu_(ss, cfg, { semua: false, paksa: false }))); } catch (err) { lapor.push(cfg.rekap + ': GAGAL (' + err.message + ')'); }
      });
    });
  } catch (err) {
    lapor.push(err.message);
  }
  SpreadsheetApp.getUi().alert('Rekap harian diperbarui', lapor.join('\n') + '\n\nHari ini belum final sampai tengah malam; angka live ada di kolom C di bawah TOTAL STOK.', SpreadsheetApp.getUi().ButtonSet.OK);
}

/** Menu: hitung ulang SELURUH riwayat dari Log + arsip; boleh menurunkan angka lama. */
function bangunUlangRekap() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const ui = SpreadsheetApp.getUi();
  if (ui.alert('Bangun ulang rekap harian',
    'Hitung ulang SEMUA hari dari Log + sheet arsip dan timpa angka rekap yang tersimpan (catatan manual tetap). ' +
    'Hari yang barisnya sudah tidak ada di Log/arsip tidak disentuh. Lanjutkan?', ui.ButtonSet.YES_NO) !== ui.Button.YES) return;
  const lapor = [];
  try {
    denganKunciRekap_(() => {
      KONFIG.SISTEM.forEach(cfg => {
        if (!ss.getSheetByName(cfg.rekap)) { lapor.push(cfg.rekap + ': belum ada (jalankan menu 4 atau migrasi dulu).'); return; }
        try { lapor.push(ringkasRekap_(cfg, perbaruiRekapSatu_(ss, cfg, { semua: true, paksa: true }))); } catch (err) { lapor.push(cfg.rekap + ': GAGAL (' + err.message + ')'); }
      });
    });
  } catch (err) {
    lapor.push(err.message);
  }
  ui.alert('Rekap harian dibangun ulang', lapor.join('\n'), ui.ButtonSet.OK);
}

// ---------------------------------------------------------------- menu 4: perbarui sheet yang SUDAH dimigrasi

/**
 * Menaikkan versi sheet UC/STP yang sudah berformat STOK/IN/OUT tanpa migrasi ulang: validasi IN/OUT menerima "B1", total harian di kolom C
 * (di bawah TOTAL STOK), teks banner, sheet "Rekap Harian ..." beserta riwayatnya. Tidak menyentuh STOK, isi IN/OUT, Log, catatan, atau
 * warna sel data. Tiap langkah dicek sebelum menulis dan dilaporkan; aman diulang (hasil sama).
 */
function perbaruiSheetLama() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const ui = SpreadsheetApp.getUi();
  const tanya = 'Perbarui sheet yang SUDAH dimigrasi (tanpa migrasi ulang)?\n\n' +
    '• Kolom IN/OUT menerima "B" + jumlah (mis. B1) untuk membatalkan salah ketik hari ini.\n' +
    '• Di bawah TOTAL STOK, baris "' + KONFIG.LABEL_MUTASI + '": kolom C = total KELUAR hari ini, di bawahnya total MASUK hari ini.\n' +
    '• Teks banner baris 1, dan sheet "' + KONFIG.SISTEM.map(c => c.rekap).join('" / "') + '" (riwayat per hari dari Log + arsip).\n\n' +
    'STOK, isi IN/OUT, Log, dan warna sel data tidak diubah. Aman diulang. Jalankan dari akun pemilik file dan minta staf menutup file ±1 menit. Lanjutkan?';
  if (ui.alert('Perbarui sheet', tanya, ui.ButtonSet.YES_NO) !== ui.Button.YES) return;
  const lapor = [];
  KONFIG.SISTEM.forEach(cfg => {
    try {
      perbaruiSatu_(ss, cfg).forEach(x => lapor.push(x));
    } catch (err) {
      lapor.push('"' + cfg.nama + '": GAGAL (' + err.message + '). Aman diulang.');
    }
  });
  const tr = h => ScriptApp.getProjectTriggers().filter(t => t.getHandlerFunction() === h).length;
  if (!tr('rekapHarianOtomatis')) lapor.push('Trigger rekap harian BELUM terpasang: jalankan menu 2. Aktifkan input otomatis (melengkapi tanpa menggandakan).');
  ui.alert('Perbarui selesai', lapor.join('\n'), ui.ButtonSet.OK);
}

function perbaruiSatu_(ss, cfg) {
  const nama = '"' + cfg.nama + '"';
  const sh = ss.getSheetByName(cfg.nama);
  if (!sh) return [nama + ': tidak ada, dilewati.'];
  const peta = bacaPeta_(sh);
  if (!Object.keys(peta.kolom).length) return [nama + ': belum berformat STOK/IN/OUT (jalankan menu 1 dulu), dilewati.'];
  if (!peta.labelAda) return [nama + ': label "' + KONFIG.LABEL_TOTAL + '" di kolom B tidak ditemukan, dilewati. Kembalikan labelnya dulu.'];
  const log = ss.getSheetByName(cfg.log);
  if (!log) return [nama + ': sheet "' + cfg.log + '" tidak ada, dilewati (menu Cek status menjelaskan).'];
  const terkunci = [sh, log, ss.getSheetByName(cfg.rekap)].filter(Boolean).filter(x => !bisaEdit_(x));
  if (terkunci.length) {
    return [nama + ': DILEWATI. Sheet dikunci (' + terkunci.map(x => x.getName()).join(', ') + '); jalankan menu ini dari akun pemilik file.'];
  }
  // Baris rekap harian dicari lewat labelnya (bukan alamat tetap): staf bisa menambah produk sehingga barisnya bergeser.
  let barisMutasi = 0;
  const sisa = Math.min(5, sh.getMaxRows() - peta.barisTotal);
  if (sisa > 0) {
    const b = sh.getRange(peta.barisTotal + 1, 2, sisa, 1).getValues();
    for (let i = 0; i < b.length; i++) {
      if (String(b[i][0]).trim().toUpperCase() === KONFIG.LABEL_MUTASI) { barisMutasi = peta.barisTotal + 1 + i; break; }
    }
  }
  if (!barisMutasi) return [nama + ': baris "' + KONFIG.LABEL_MUTASI + '" tidak ditemukan di bawah TOTAL STOK, dilewati.'];

  const lapor = [];
  const awal = nama + ': ';

  // 1. validasi kolom IN/OUT (STOK tidak berubah)
  try {
    if (!KONFIG.IZINKAN_PEMBATALAN) {
      lapor.push(awal + 'validasi IN/OUT tidak diubah (IZINKAN_PEMBATALAN = false).');
    } else {
      const nBaris = peta.barisTotal - 1 - KONFIG.BARIS_DATA;
      const hasil = [];
      Object.keys(peta.kolom).map(Number).sort((a, b) => a - b).forEach(c => {
        if (peta.kolom[c].jenis !== 'STOK') return;
        if (!peta.kolom[c + 1] || peta.kolom[c + 1].jenis !== 'IN' || !peta.kolom[c + 2] || peta.kolom[c + 2].jenis !== 'OUT') return;
        hasil.push(pasangValidasi_(sh.getRange(KONFIG.BARIS_DATA, c + 1, nBaris, 2), huruf_(c + 1) + KONFIG.BARIS_DATA, 'inout'));
      });
      const ok = hasil.filter(x => x !== null);
      lapor.push(awal + 'validasi IN/OUT diperbarui di ' + ok.length + ' dari ' + hasil.length + ' warna' +
        (ok.length ? ' (rumus ' + ok[0] + ')' : '') +
        (ok.length < hasil.length ? '. Sisanya DITOLAK Google: validasinya dikosongkan supaya B1 bisa diketik; script tetap menolak isian salah dengan tanda merah' : '') + '.');
    }
  } catch (err) {
    lapor.push(awal + 'validasi GAGAL (' + err.message + '). Aman diulang.');
  }

  // 2. total harian di kolom C (baris rekap harian dan satu baris di bawahnya)
  try {
    pastikanUkuran_(sh, barisMutasi + 1, 3);
    const f = sh.getRange(barisMutasi, 3, 2, 1).getFormulas();
    const v = sh.getRange(barisMutasi, 3, 2, 1).getValues();
    const rencana = [['OUT', FORMAT_TOTAL_KELUAR], ['IN', FORMAT_TOTAL_MASUK]];
    const ditulis = [];
    rencana.forEach((rc, i) => {
      const r = barisMutasi + i;
      const kosong = f[i][0] === '' && v[i][0] === '';
      const milikKita = f[i][0].indexOf("=SUMIFS('" + cfg.log + "'!") === 0;
      if (!kosong && !milikKita) {
        lapor.push(awal + 'sel C' + r + ' berisi sesuatu yang bukan rumus total harian; TIDAK ditimpa. Kosongkan dulu bila memang mau diganti.');
        return;
      }
      sh.getRange(r, 3).setFormulas([[rumusTotalHarian_(cfg.log, rc[0])]]).setNumberFormat(rc[1]);
      sh.getRange(r, 3).setFontWeight('bold');
      ditulis.push('C' + r + ' (' + (rc[0] === 'OUT' ? 'Keluar' : 'Masuk') + ')');
    });
    if (ditulis.length) lapor.push(awal + 'total harian ' + ditulis.join(', ') + '.');
  } catch (err) {
    lapor.push(awal + 'total harian GAGAL (' + err.message + '). Aman diulang.');
  }

  // 3. banner baris 1
  try {
    const sel = sh.getRange(1, 4);
    const teks = String(sel.getValue());
    if (!KONFIG.IZINKAN_PEMBATALAN || teks === teksBanner_()) {
      lapor.push(awal + 'banner sudah sesuai.');
    } else if (teks === TEKS_BANNER_LAMA) {
      sel.setValue(teksBanner_());
      lapor.push(awal + 'banner diperbarui.');
    } else {
      lapor.push(awal + 'banner D1 sudah diubah manual; tidak diganti (tambahkan sendiri: "Salah ketik hari ini? Ketik B + jumlah (mis. B1) untuk membatalkan").');
    }
  } catch (err) {
    lapor.push(awal + 'banner GAGAL (' + err.message + ').');
  }

  // 4. sheet rekap harian + riwayat dari Log dan arsip
  try {
    const sudahAda = !!ss.getSheetByName(cfg.rekap);
    const rk = siapkanRekap_(ss, cfg.rekap);
    const judul = rk.getRange(1, 1, 1, HEADER_REKAP.length).getValues()[0];
    if (sudahAda && HEADER_REKAP.some((x, i) => String(judul[i]).trim() !== x)) {
      lapor.push(awal + 'sheet "' + cfg.rekap + '" sudah ada dengan judul kolom berbeda; TIDAK disentuh. Ganti namanya lalu ulangi.');
    } else {
      lapor.push(awal + ringkasRekap_(cfg, denganKunciRekap_(() => perbaruiRekapSatu_(ss, cfg, { semua: true, paksa: false }))));
    }
  } catch (err) {
    lapor.push(awal + 'rekap GAGAL (' + err.message + '). Aman diulang.');
  }

  // pemeriksaan akhir: rumus total harian tidak boleh menampilkan galat
  try {
    SpreadsheetApp.flush();
    sh.getRange(barisMutasi, 3, 2, 1).getValues().forEach((x, i) => {
      if (/^#/.test(String(x[0]))) lapor.push(awal + 'PERIKSA: C' + (barisMutasi + i) + ' menampilkan ' + x[0] + '.');
    });
  } catch (err) { /* hanya pemeriksaan */ }
  return lapor;
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

/** Bisa menulis ke sheet ini? (false kalau sheet dikunci dan akun ini bukan editor proteksi.) */
function bisaEdit_(sh) {
  return sh.getProtections(SpreadsheetApp.ProtectionType.SHEET).every(p => p.canEdit());
}

/** Kunci baris untuk mencegah baris yang sama diarsipkan dua kali (waktu dibulatkan ke detik). */
function kunciBaris_(r) {
  return r.map((v, i) => i === 0 ? String(Math.round((typeof v === 'number' ? v : 0) * 86400)) : String(v)).join('|');
}

/** Rencana arsip: per log, indeks baris (0 = baris 2) yang jamnya sebelum bulan ini + barisnya per bulan. */
function rencanaArsip_(ss, zona, bulanIni) {
  const rencana = [];
  KONFIG.SISTEM.forEach(cfg => {
    const log = ss.getSheetByName(cfg.log);
    if (!log || log.getLastRow() < 2) return;
    const n = log.getLastRow() - 1;
    const indeks = [];
    const pindah = {};
    log.getRange(2, 1, n, HEADER_LOG.length).getValues().forEach((row, i) => {
      const w = waktuNomor_(row[0], zona);
      if (w === null) return;   // jam tak terbaca: dibiarkan di Log
      const b = bulanDariNomor_(w);
      if (b >= bulanIni) return;
      row[0] = w;
      indeks.push(i);
      (pindah[b] = pindah[b] || []).push(row);
    });
    if (indeks.length) rencana.push({ cfg: cfg, n: n, indeks: indeks, pindah: pindah, log: log });
  });
  return rencana;
}

/**
 * Pindahkan baris Log sebelum bulan ini ke sheet "Arsip <nama log> <yyyy-MM>" (satu sheet per bulan,
 * terbaru di atas), lalu hapus baris itu dari Log. Aman diulang: baris yang sudah ada di arsip tidak
 * digandakan, jadi kalau proses terhenti di tengah cukup jalankan lagi. Rekap "hari ini" tidak terpengaruh.
 */
function arsipkanLogBulanLalu() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const ui = SpreadsheetApp.getUi();
  const zona = ss.getSpreadsheetTimeZone();
  const bulanIni = bulanDariNomor_(waktuSerial_(new Date(), KONFIG.ZONA_WAKTU));

  const rencana = rencanaArsip_(ss, zona, bulanIni);
  if (!rencana.length) {
    ui.alert('Tidak ada log bulan sebelum ' + bulanIni + '.');
    return;
  }
  let tanya = 'Pindahkan log sebelum bulan ini (' + bulanIni + ') ke sheet arsip per bulan?\n';
  rencana.forEach(p => {
    tanya += '\n' + p.cfg.log + ':';
    Object.keys(p.pindah).sort().forEach(b => { tanya += '\n  • ' + b + ': ' + p.pindah[b].length + ' baris → "Arsip ' + p.cfg.log + ' ' + b + '"'; });
    tanya += '\n  Tersisa di Log: ' + (p.n - p.indeks.length) + ' baris.';
  });
  if (ui.alert('Arsipkan log', tanya, ui.ButtonSet.YES_NO) !== ui.Button.YES) return;

  const lock = LockService.getDocumentLock();
  if (!lock.tryLock(25000)) {
    ui.alert('Sistem sibuk, coba lagi sebentar lagi.');
    return;
  }
  let hasil = [];
  try {
    // Baca ulang setelah lock didapat: dialog bisa terbuka lama dan log terus bertambah.
    rencanaArsip_(ss, zona, bulanIni).forEach(p => {
      const nama = p.cfg.log;
      try {
        const bulan = Object.keys(p.pindah).sort();
        // Periksa hak edit SEBELUM menulis apa pun, supaya tidak berhenti separuh jalan.
        const arsipAda = bulan.map(b => ss.getSheetByName('Arsip ' + nama + ' ' + b)).filter(Boolean);
        if (!bisaEdit_(p.log) || !arsipAda.every(bisaEdit_)) {
          hasil.push(nama + ': DILEWATI. Sheet dikunci; jalankan menu ini sebagai pemilik file.');
          return;
        }
        bulan.forEach(b => {
          const arsip = siapkanLog_(ss, 'Arsip ' + nama + ' ' + b);
          const ada = arsip.getLastRow() > 1
            ? arsip.getRange(2, 1, arsip.getLastRow() - 1, HEADER_LOG.length).getValues().map(r => {
              const w = waktuNomor_(r[0], zona);
              if (w !== null) r[0] = w;   // waktu tak terbaca (teks) dibiarkan apa adanya
              return r;
            })
            : [];
          const sudah = {};
          ada.forEach(r => { const k = kunciBaris_(r); sudah[k] = (sudah[k] || 0) + 1; });
          const baru = p.pindah[b].filter(r => {
            const k = kunciBaris_(r);
            if (sudah[k] > 0) { sudah[k]--; return false; }   // sudah ada di arsip (jalan ulang)
            return true;
          });
          if (!baru.length) return;
          const gabung = ada.concat(baru).sort((x, y) => (typeof y[0] === 'number' ? y[0] : 0) - (typeof x[0] === 'number' ? x[0] : 0));
          pastikanUkuran_(arsip, gabung.length + 1, HEADER_LOG.length);
          arsip.getRange(2, 1, gabung.length, 1).setNumberFormat(KONFIG.FORMAT_WAKTU);
          arsip.getRange(2, 1, gabung.length, HEADER_LOG.length).setValues(gabung);
        });
        SpreadsheetApp.flush();
        // Hapus hanya baris yang sudah diarsipkan (dari bawah ke atas); baris lain di Log tidak disentuh.
        const grup = [];
        p.indeks.forEach(i => {
          const g = grup[grup.length - 1];
          if (g && i === g.akhir + 1) g.akhir = i; else grup.push({ awal: i, akhir: i });
        });
        pastikanUkuran_(p.log, p.n + 2, HEADER_LOG.length);   // sisakan minimal satu baris non-beku
        grup.reverse().forEach(g => p.log.deleteRows(g.awal + 2, g.akhir - g.awal + 1));
        hasil.push(nama + ': ' + p.indeks.length + ' baris diarsipkan, ' + (p.n - p.indeks.length) + ' baris tersisa.');
      } catch (err) {
        hasil.push(nama + ': GAGAL (' + err.message + '). Aman diulang: baris yang sudah masuk arsip tidak digandakan.');
      }
    });
    SpreadsheetApp.flush();
  } finally {
    lock.releaseLock();
  }
  if (!hasil.length) hasil.push('Tidak ada yang dipindahkan (log berubah selama dialog).');
  ui.alert('Arsip selesai', hasil.join('\n') + '\n\nSheet arsip baru belum dikunci: jalankan menu 3 lagi bila log dikunci.', ui.ButtonSet.OK);
}

// ---------------------------------------------------------------- pembatalan salah ketik ("B" + jumlah)

/**
 * Isi sel IN/OUT berbentuk "B" + jumlah (mis. "B1", "b 2") = membatalkan sebagian entri HARI INI untuk produk x warna x jenis yang sama.
 * Minus sengaja TIDAK dipakai: "OUT -3" mudah terbaca staf sebagai "kurangi stok 3" padahal artinya kebalikannya.
 * null = bukan pembatalan; NaN = berbentuk B tapi jumlahnya tidak valid (B0, B99999).
 */
function batalInput_(v) {
  if (!KONFIG.IZINKAN_PEMBATALAN || typeof v !== 'string') return null;
  const m = /^\s*[Bb]\s*(\d+)\s*$/.exec(v);
  if (!m) return null;
  const n = Number(m[1]);
  return n >= 1 && n <= KONFIG.MAKS_QTY ? n : NaN;
}

function kunciBatal_(produk, sku, warna, jenis) {
  return [sku, produk, warna].map(normNama_).concat(jenis).join('|');
}

function adalahTanggal_(v) {
  return Object.prototype.toString.call(v) === '[object Date]' && !isNaN(v.getTime());
}

/**
 * Pengubah nilai kolom Waktu (angka, atau Date kalau sel berformat tanggal) ke nomor seri WIB. Memakai zona FILE (Sheets membuat Date
 * menurut zona file). Zona WIB tidak punya DST, jadi selisihnya cukup dihitung sekali (dicek di sampel pertama dan terakhir) tanpa
 * Utilities.formatDate per baris; zona lain memakai jalur lambat yang selalu benar. Mengembalikan fungsi (nilai) => nomor seri | null.
 */
function konversiKolomWaktu_(nilai, zona) {
  let awal = null;
  let akhir = null;
  for (let i = 0; i < nilai.length; i++) {
    if (adalahTanggal_(nilai[i])) { if (awal === null) awal = nilai[i]; akhir = nilai[i]; }
  }
  const epoch = Date.UTC(1899, 11, 30);
  let selisih = null;
  if (awal !== null && zona === KONFIG.ZONA_WAKTU) {
    const s1 = waktuSerial_(awal, zona) * 86400000 + epoch - awal.getTime();
    const s2 = waktuSerial_(akhir, zona) * 86400000 + epoch - akhir.getTime();
    if (Math.abs(s1 - s2) < 1) selisih = s1;
  }
  return v => {
    if (typeof v === 'number' && isFinite(v)) return v;
    if (!adalahTanggal_(v)) return null;
    return selisih !== null ? (v.getTime() + selisih - epoch) / 86400000 : waktuSerial_(v, zona);
  };
}

/**
 * Net IN/OUT hari ini (nomor hari WIB `hari`) per produk x warna x jenis: baris teratas Log (terbaru di atas; paling banyak
 * KONFIG.BATAS_BACA_BATAL baris, kalau Log diurutkan lain hasilnya bisa kurang = pembatalan ditolak, arah yang aman)
 * ditambah baris putaran berjalan yang belum tertulis (logJalan). Qty negatif (pembatalan sebelumnya) ikut mengurangi.
 */
function netHariIni_(ss, cfg, hari, logJalan) {
  const net = new Map();
  const tambah = b => {
    const jenis = String(b[6]);
    if (jenis !== 'IN' && jenis !== 'OUT') return;
    const q = Number(b[7]);
    if (b[7] === '' || !isFinite(q)) return;
    const k = kunciBatal_(b[3], b[4], b[5], jenis);
    net.set(k, (net.get(k) || 0) + q);
  };
  const sh = ss.getSheetByName(cfg.log);
  if (sh && sh.getLastRow() >= 2) {
    const n = Math.min(sh.getLastRow() - 1, KONFIG.BATAS_BACA_BATAL);
    const baris = sh.getRange(2, 1, n, 8).getValues();
    const ubah = konversiKolomWaktu_(baris.map(b => b[0]), ss.getSpreadsheetTimeZone());
    baris.forEach(b => {
      const w = ubah(b[0]);
      if (w !== null && Math.floor(w) === hari) tambah(b);
    });
  }
  (logJalan || []).forEach(b => { if (Math.floor(b[0]) === hari) tambah(b); });
  return net;
}

/** Sudah adakah baris-baris ini di puncak Log? Dipakai jalur penyelamatan supaya tidak menulis dobel kalau tulisLog_ sebenarnya sudah berhasil. */
function logSudahAda_(ss, cfg, rows) {
  const sh = ss.getSheetByName(cfg.log);
  if (!sh || sh.getLastRow() < rows.length + 1) return false;
  const zona = ss.getSpreadsheetTimeZone();
  const atas = sh.getRange(2, 1, rows.length, HEADER_LOG.length).getValues();
  const harap = rows.slice().reverse();
  return atas.every((r, i) => {
    const w = waktuNomor_(r[0], zona);
    return w !== null && kunciBaris_([w].concat(r.slice(1))) === kunciBaris_(harap[i]);
  });
}

function pastikanUkuran_(sh, baris, kolom) {
  if (sh.getMaxRows() < baris) sh.insertRowsAfter(sh.getMaxRows(), baris - sh.getMaxRows() + 500);
  if (sh.getMaxColumns() < kolom) sh.insertColumnsAfter(sh.getMaxColumns(), kolom - sh.getMaxColumns());
}

let VARIAN_VALIDASI_ = null;   // varian rumus yang diterima Google di eksekusi ini ('koma' | 'titik koma'); dicoba lebih dulu di area berikutnya

/**
 * Pasang validasi angka pada `range`; `sel` = sel pertama range (mis. "D4"), dipakai rumus relatif. jenis: 'stok' (bulat >= 0) atau
 * 'inout' (bulat > 0, plus "B" + digit bila IZINKAN_PEMBATALAN).
 * Google membaca rumus validasi dengan pemisah argumen sesuai LOKAL file (koma di en_US; titik koma di id_ID dan banyak lokal lain),
 * beda dengan rumus sel (setFormulas) yang selalu berbahasa Inggris. Rumus berkoma di file berlokal Indonesia ditolak Google
 * ("Argumen aturan validasi data ... tidak valid") dan dulu menggagalkan migrasi. Urutan percobaan:
 *   1. rumus berkoma   2. rumus bertitik koma   3. aturan "angka antara" (tanpa rumus; tidak dipakai untuk IN/OUT yang menerima "B1",
 *   karena aturan itu menolak teks B1 diam-diam)
 * Kalau semuanya ditolak, validasi dilewati (aturan lama pada IN/OUT dihapus supaya "B1" bisa diketik): script sendiri menolak isian
 * salah dengan tanda merah + catatan, jadi ini tidak boleh menggagalkan migrasi. Mengembalikan 'koma' | 'titik koma' | 'rentang' | null.
 */
function pasangValidasi_(range, sel, jenis) {
  const stok = jenis === 'stok';
  const maks = KONFIG.MAKS_QTY;
  const batalOk = !stok && KONFIG.IZINKAN_PEMBATALAN;
  const bantuan = stok ? 'STOK: angka bulat 0–' + maks
    : 'Isi angka bulat 1–' + maks + ' lalu Enter.' + (batalOk ? ' Salah ketik hari ini? Ketik B + jumlah yang dibatalkan, mis. B1.' : '');
  const angka = p => 'AND(' + ['ISNUMBER(' + sel + ')', sel + (stok ? '>=0' : '>0'), sel + '<=' + maks, sel + '=INT(' + sel + ')'].join(p) + ')';
  const teksB = p => 'AND(' + ['ISTEXT(' + sel + ')', 'REGEXMATCH(' + [sel, '"^[Bb][0-9]+$"'].join(p) + ')'].join(p) + ')';
  const rumus = p => '=' + (batalOk ? 'OR(' + [angka(p), teksB(p)].join(p) + ')' : angka(p));
  const pisah = { 'koma': ',', 'titik koma': ';' };
  const urut = VARIAN_VALIDASI_ === 'titik koma' ? ['titik koma', 'koma'] : ['koma', 'titik koma'];
  const percobaan = urut.map(nama => [nama, b => b.requireFormulaSatisfied(rumus(pisah[nama]))]);
  if (!batalOk) percobaan.push(['rentang', b => b.requireNumberBetween(stok ? 0 : 1, maks)]);
  for (let i = 0; i < percobaan.length; i++) {
    try {
      range.setDataValidation(percobaan[i][1](SpreadsheetApp.newDataValidation()).setAllowInvalid(false).setHelpText(bantuan).build());
      if (percobaan[i][0] !== 'rentang') VARIAN_VALIDASI_ = percobaan[i][0];
      return percobaan[i][0];
    } catch (err) { /* lokal file menolak varian ini: coba berikutnya */ }
  }
  if (batalOk) { try { range.clearDataValidations(); } catch (err) { /* biarkan */ } }
  return null;
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
