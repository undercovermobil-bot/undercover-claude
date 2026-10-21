# Sistem Stok Otomatis — Google Sheets

Untuk file **Stock Opname** (Google Sheet), 2 sheet:

| Sheet | Sheet lama | Sheet baru (urutan 100 SKU terlaris) | Total & rekap harian (baru) |
|---|---|---|---|
| **Stok Cover UC** | baris 4–196 (193 produk) | 181 produk, baris 4–184 | baris 186–187 |
| **Stok Cover STP** | baris 4–107 (104 produk), **+ warna Orange** | 126 produk, baris 4–129 | baris 131–132 |

Batas baris sheet lama dicari otomatis saat migrasi (baris terakhir sebelum label "OUT"/"IN" di kolom B). Urutan dan isi sheet baru mengikuti sheet **Urutan UC / Urutan STP** (lihat "Daftar urutan produk").
Kode: [`Kode.gs`](Kode.gs).

## Mulai di sini: 3 file dan urutan pasang

**Hanya 3 file yang dibutuhkan.** Data stok tidak butuh file lain: dibaca langsung dari sheet "Stok Cover UC / STP" yang sudah ada di Google Sheet Stock Opname.

| File | Fungsi | Dipakai di mana |
|---|---|---|
| `Kode.gs` | Script sistem stok | **Extensions → Apps Script**, ditempel lalu Ctrl+S |
| `Urutan Stok UC STP.xlsx` | Daftar urutan 100 SKU terlaris + Kode SKU (tab **Urutan UC**, **Urutan STP**, **Tidak masuk**) | **File → Import → Insert new sheet(s)** di Google Sheet Stock Opname |
| `PANDUAN.md` | Panduan ini | dibaca |

Folder `uji/` (simulasi untuk menguji kode) tidak perlu dipakai.

**Urutan ringkas** (rincian tiap langkah ada di bagian "Pasang"):
1. **Akhir hari**, minta semua staf **menutup file**. Pastikan IN sudah final (dipakai apa adanya sebagai stok awal) dan OUT sudah dikosongkan.
2. **File → Make a copy** sebagai cadangan.
3. **File → Import → Upload** `Urutan Stok UC STP.xlsx` → **Insert new sheet(s)**. **Sekali saja** (impor ulang membuat "Urutan UC 1" dan migrasi ditolak sampai dirapikan).
4. **Extensions → Apps Script** → tempel isi `Kode.gs` → **Ctrl+S**.
5. Refresh spreadsheet (F5) → menu **📦 Sistem Stok → 1a** (UC) → **Yes**, lalu **1b** (STP) → **Yes**.
6. **2. Aktifkan input otomatis** (sekali, dari **satu akun** saja, sebaiknya pemilik file). Cek di Apps Script → ikon jam **Triggers**: harus ada 3 trigger, penyapu "Every 15 minutes" dan rekap harian "Day timer".
7. Tes langkah 12–14 di bagian "Pasang", juga dari aplikasi Sheets di HP.
8. Opsional: **3. Kunci kolom STOK**. Sheet Log boleh disembunyikan. **Sheet yang sudah pernah dimigrasi** (bukan migrasi baru): jalankan menu **4** sebelum langkah 6 (lihat "Memasang versi kode baru").
9. 1–3 hari pertama: pantau **Executions** (lihat "Biaya").

## Daftar urutan produk (100 SKU terlaris)

Urutan produk sheet baru **tidak sama dengan sheet lama**. Urutan, nama, dan Kode SKU diambil dari sheet **Urutan UC** dan **Urutan STP** (satu baris per produk). Isinya dibuat dari file `Urutan Stok UC STP.xlsx` (sumber data di repo: `uji/daftar-urutan.js`) dan harus **diimpor ke Google Sheet sebelum menu 1a / 1b**.

Susunan (sama untuk UC dan STP; rinciannya beda karena isi sheet lama beda):
1. **Bagian 1, hijau**: produk yang namanya berwarna hijau di sheet lama, urutan sheet lama dipertahankan (UC 38, STP 27).
2. **Bagian 2, top-100**: produk 100 SKU terlaris (ranking 4 toko gabungan, `RANKING_TOP_100_PER_SKU.xlsx`) urut peringkat 1 → 100. Satu baris per **kode generasi** (mis. Civic Sedan G5–G11). Yang belum ada di sheet lama = **BARU**, stok kosong, supaya tinggal diisi lewat IN.
3. **Bagian 3, sisa stok**: produk di luar top-100 yang masih ada stok, urutan sheet lama. Produk di luar top-100 dengan stok 0 **tidak ikut** (tetap ada di sheet "(lama)").

Kode SKU tiap baris: `MEREK-MODEL-TOKO-R-GENERASI` (UC = toko `UA`, STP = toko `SP`), mis. `TYT-AVZ-SP-R-G3`. Kode generasi mengikuti listing Shopee Undercover (1 Okt 2026) dan aturan Total Formula. Baris bagian 3 tidak punya kode (seperti sheet lama).

Aturan khusus yang sudah diputuskan: baris sheet lama berkode sama **digabung dan stoknya dijumlah** (mis. Triton, X-Over + S-Cross). Satu sel boleh berisi 2 kode kalau satu formula (HiAce Commuter / Premio, Starlet Kotak / Kapsul, STP Hardtop / Land Cruiser). Santa Fe dan Stargazer punya baris G1 dan G2; Mini Cooper 3P dan 5P; Livina X-Gear 5S dan 7S.

**Kolom di sheet Urutan** (judul di baris 1; script mencarinya lewat judul, urutan kolom bebas):

| Kolom | Dipakai script? | Isi |
|---|---|---|
| Nama Produk | ya | nama di sheet baru |
| Kode SKU | ya | kode di sheet baru |
| Baris lama | ya | nomor baris sheet lama asal stok. Beberapa nomor dipisah koma = digabung, stok dijumlah per warna. Kosong = produk baru |
| Nama di sheet lama | ya, **wajib** | nama baris-baris tadi, dipisah tanda garis tegak \| (satu nama per nomor). Dipakai script memastikan nomor baris masih benar |
| Harga dari baris | ya | khusus produk baru: baris sheet lama yang harga Value-nya ditiru (model sama, atau harga standar sheet) |
| No, Stok sekarang, Bagian, Peringkat, Status, Catatan | tidak | informasi untuk dibaca |

**Pengaman saat menu 1a / 1b** (kalau ada yang tidak cocok: muncul pesan dan **tidak ada yang diubah**):
- Kolom "Nama di sheet lama" wajib ada dan terisi untuk setiap baris yang punya "Baris lama". Nama di baris yang ditunjuk harus sama dengan isinya. Kalau sheet lama sudah bergeser (baris disisip/dihapus), script mencari nama itu di baris lain (hanya kalau cuma ada satu), memetakan stok **dan harga produk baru** ke baris yang benar, dan menyebutnya di dialog (bukan diam-diam). Kalau nama di baris itu sekadar **diganti** sejak daftar dibuat (mis. salah ketik "Toyota Swift" dibetulkan jadi "Suzuki Swift") dan masih ada kata yang sama, baris itu dianggap produk yang sama dan nama sheet baru ikut nama sekarang; ini juga disebut di dialog. Kalau diganti total, ditolak dengan petunjuk: ubah "Nama di sheet lama" (dan Nama Produk) di sheet Urutan.
- Nama Produk baru harus masih berkaitan dengan nama baris lamanya (minimal satu kata sama). Kalau tidak, biasanya kolom daftar terlepas (mis. Data → Sort pada sebagian kolom saja): ditolak. **Jangan sort sebagian kolom di sheet Urutan.**
- Satu baris lama tidak boleh dipakai dua baris daftar (stok jadi dobel). Baris tanpa "Baris lama" **dan** tanpa Kode SKU (mis. baris TOTAL/catatan) ditolak.
- Baris sheet lama yang **tidak disebut daftar**: stok 0 → tidak ikut; **berstok, atau isi IN-nya aneh → otomatis ditaruh di paling bawah** dan disebut di dialog, jadi tidak ada yang hilang diam-diam.
- Sel IN berisi angka berformat teks (mis. `'6`) dibaca sebagai angka dan disebut di dialog. Isi lain yang bukan angka (huruf, tanggal) dikosongkan dan dilaporkan dengan nomor baris.
- Hanya satu sheet daftar per toko: kalau ada sheet lain bernama mirip (mis. "Urutan UC 1" hasil impor ganda), ditolak sampai dirapikan.
- Total stok sheet baru harus sama dengan sheet lama; kalau tidak, dibatalkan. Sesudah sheet baru jadi, data sheet lama dibaca ulang dan dibandingkan; kalau ada yang berubah selama proses (staf masih mengedit), dibatalkan. **Minta semua staf menutup file saat migrasi.**
- Sheet baru dibangun dulu dengan nama sementara "Stok Cover UC (baru)"; sheet lama baru diganti nama di langkah paling akhir. Kalau terhenti di tengah, sheet lama tetap utuh (hapus sheet "(baru)" yang tersisa lalu ulangi).
- Produk baru tanpa harga di sheet lama: kolom Value dikosongkan dan disebut di catatan.

**Cara impor** (dari tampilan Google bahasa Inggris). Mengunggah file ke Google Drive saja **tidak cukup**: isinya harus masuk sebagai tab di Google Sheet Stock Opname. Buka Google Sheet itu → **File → Import → Upload** → pilih `Urutan Stok UC STP.xlsx` → **Import location: Insert new sheet(s)** → **Import data**. Muncul tab **Urutan UC**, **Urutan STP**, dan **Tidak masuk** di deretan tab bawah (cek juga lewat menu **Cek status**) (daftar baris stok 0 yang dibuang, hanya informasi; boleh dihapus). Kalau mengimpor ulang, **hapus dulu** sheet Urutan yang lama: Google menamai sheet duplikat "Urutan UC 1" dan script akan menolak sampai tinggal satu.

**Mengubah daftar sebelum migrasi**: edit langsung di sheet Urutan UC / Urutan STP: ganti nama, pindahkan **baris utuh** (klik nomor baris, drag; jangan sort sebagian kolom), hapus baris, atau tambah produk baru dengan "Baris lama" kosong dan Kode SKU terisi. Jangan sisakan dua baris yang "Baris lama"-nya sama. Setelah migrasi, sheet Urutan boleh dihapus.

Setelah migrasi, urutan sudah ada di sheet baru: tambah / hapus produk dikerjakan langsung di sana (lihat "Aturan pakai"), bukan lewat sheet Urutan.

## Cara kerja

Tiap warna jadi 3 kolom: **STOK | IN | OUT**.

| Aksi staf | Hasil otomatis (beberapa detik) |
|---|---|
| Ketik `5` di **IN**, Enter | STOK +5, sel IN kosong lagi (beberapa detik), tercatat di Log sheet itu (UC → "Log Stok UC", STP → "Log Stok STP") |
| Ketik `2` di **OUT**, Enter | STOK −2, sel OUT kosong lagi, tercatat |
| OUT lebih besar dari STOK | **Ditolak**: sel merah + catatan, STOK tidak berubah |
| Ketik huruf / desimal / minus | Ditolak oleh validasi sheet; kalau validasi tidak terpasang (Google menolak aturannya), ditolak script: sel merah + catatan. **Minus sengaja tidak dipakai** |
| **Salah ketik hari ini**: ketik `B1` (B + jumlah) di sel IN/OUT yang sama | Membatalkan 1 unit dari entri HARI INI: salah OUT → STOK naik, salah IN → STOK turun. Tercatat di Log (Jenis tetap IN/OUT, Qty **negatif**, keterangan "BATAL OUT/IN"); rekap hari ini otomatis bersih |
| Admin ketik langsung di **STOK** | Diterima, tercatat sebagai `KOREKSI` (untuk opname) |

Tidak ada lagi langkah "kurangi IN manual" dan "hapus OUT akhir hari".

**Revisi salah ketik (pembatalan "B").** Contoh: seharusnya OUT 2 tapi terketik 3. Ketik **`B1`** di sel OUT yang sama (huruf kecil dan spasi boleh: `b 1`, `B 1`). Aturannya:
- Hanya boleh membatalkan sampai sejumlah entri **hari ini** (WIB) untuk produk **dan** warna **dan** jenis (IN/OUT) yang sama, dihitung dari Log. Lebih dari itu, atau produk/warna/jenis lain, atau entri hari lain: **ditolak** (sel merah, catatan "DITOLAK: ...", tercatat DITOLAK di Log) dan stok tidak berubah.
- Membatalkan **IN** juga butuh STOK yang cukup (stok tidak boleh jadi minus).
- Pengecekan per **produk + warna + jenis**, bukan per baris. Kalau dua baris sheet punya nama dan SKU yang sama, `B` di baris yang salah tetap diterima (totalnya benar, stok per baris tertukar): hindari baris ganda.
- Kalau nama produk atau SKU diubah di hari yang sama dengan entrinya, `B` ditolak ("tercatat 0") karena dianggap produk lain. Jalan keluarnya: koreksi STOK oleh admin.
- Sel yang ditolak lalu dibiarkan berisi teks bisa membuat Sheets menyarankan isian otomatis (mis. `B1` jadi `B10`). Hapus sel yang merah sebelum mengetik lagi.
- **Salah catat di hari lain**: minta admin mengoreksi **STOK** langsung (opname; tercatat `KOREKSI`). Rekap hari yang sudah lewat sengaja tidak diubah.
- Kenapa bukan angka minus: `OUT -3` mudah terbaca staf sebagai "kurangi stok 3", padahal artinya menaikkan stok. Huruf B tidak mungkin terketik tanpa sengaja. Minus tetap ditolak dengan petunjuk "ketik B1".
- Matikan fitur ini dengan `IZINKAN_PEMBATALAN = false` di kode (B1 lalu ditolak seperti teks biasa).
- Kolom IN/OUT hanya menerima `B` + angka bila validasi barunya terpasang (migrasi baru: otomatis; sheet yang sudah dimigrasi: menu **4**).

**Mengetik cepat di banyak sel.** Google bisa melewatkan atau menunda satu kejadian edit kalau diketik cepat, sehingga angka IN/OUT sempat tertinggal di sel. Pengamannya:
1. Tiap kali sebuah edit diproses, script menyapu **semua** sel IN/OUT di sheet itu (bukan hanya sel yang diedit), lalu **mengulang** sampai tidak ada yang tersisa (maks. `PUTARAN_MAKS` = 3 putaran), sebelum melepas kunci. Angka yang diketik selagi script berjalan ikut terbawa. Sel hasil sapuan dicatat di Log dengan keterangan "Diproses penyapuan otomatis" dan kolom User **kosong** (pemilik angkanya tidak diketahui).
2. Trigger edit yang kalah giliran **tidak menunggu lama** (3 detik; untuk koreksi STOK manual 25 detik). Pemegang kunci sudah menyapu semuanya, jadi menunggu hanya menghabiskan kuota.
3. **Penyapu waktu** tiap `SAPU_MENIT` = 15 menit, hanya pada jam `SAPU_JAM` (06.00–19.00 WIB; penyapu terakhir jalan sebelum 19.00), memproses angka yang masih tertinggal walau tidak ada edit baru. Dipasang bersama trigger edit oleh menu **2. Aktifkan input otomatis**.
4. Kalau IN dan OUT warna yang sama tertunda bersamaan, **OUT diperiksa lebih dulu** terhadap stok yang ada (OUT yang tak muat ditolak, tidak lolos karena IN yang baru diketik).
5. Kalau layanan Google error di tengah proses, sel yang STOK-nya sudah naik dikosongkan dan dicatat di Log, lalu galatnya muncul di **Executions**. Sel yang belum sempat diproses tetap menunggu penyapuan berikutnya, jadi tidak ada yang dihitung dua kali.

**Kapan angka tertinggal diproses:** langsung di edit berikutnya pada sheet yang sama; kalau tidak ada edit, oleh penyapu paling lambat ±15 menit (Google tidak menjamin menit tepatnya) pada jam 06.00–19.00 WIB. Di luar jam itu menunggu edit berikutnya atau penyapu pertama setelah 06.00. Mau tidak menunggu: ketik satu angka di sel mana pun pada sheet itu, edit itu menyapu semuanya.

Sel yang **ditolak** (merah, ada catatan, mis. OUT melebihi stok) tidak disentuh penyapuan: tunggu staf menghapus atau mengetik ulang. Kalau sistem sibuk, angka IN/OUT **tidak** ditandai merah: angkanya tetap di sel dan diproses pemegang kunci atau penyapu. **Jangan ketik ulang** angka yang masih ada di sel. Tanda merah buatan script yang tertinggal di sel yang sudah kosong dibersihkan otomatis oleh penyapuan; catatan buatan staf tidak disentuh (dan sel berangka yang punya catatan staf tidak ikut disapu). Edit di luar area IN/OUT/STOK (mis. kolom Value) tidak memicu penyapuan.

**Sebelum menempel kode ini di file yang sudah dipakai:** pastikan **tidak ada angka tertinggal** di kolom IN/OUT kedua sheet. Edit pertama sesudahnya akan memprosesnya. Kalau angka itu sebenarnya sudah kamu masukkan manual ke STOK, hapus dulu angkanya, kalau tidak stok jadi dobel.

**Biaya (dari Executions file ini, 12 Okt):** satu proses edit memakan 4–9 detik, penyapu yang tidak menemukan apa-apa 8–10 detik, dan rangkaian ±14 edit beruntun sebelum perbaikan lock memakan 7–29 detik **per proses** (waktu tunggu kunci ikut dihitung) ≈ 4 menit kuota. **Ukuran 15 Okt (kode terbaru; 22 edit beruntun dalam 49 detik, semuanya Completed):** 6–9,4 detik per eksekusi (median ±7; 9 dari 18 di bawah 7 detik, kemungkinan yang kalah giliran lock dan berhenti setelah menunggu 3 detik), 4 eksekusi pertama 14,5–18,8 detik (penyebab belum jelas: antrean lock atau tempel banyak sel); total 3,3 menit ≈ 3,6% dari 90 menit. Pegangan kasar: ±9 detik kuota per entri yang diketik cepat. Kuota yang relevan: **total waktu semua trigger per hari** (Google: 90 menit untuk akun Gmail biasa, 6 jam untuk Workspace; angka dari sumber pihak ketiga, cek halaman kuota Apps Script). Habis kuota → trigger berhenti sampai kuota pulih (±24 jam), gejalanya sama dengan angka tertinggal. Pantau **Extensions → Apps Script → Executions** 1–3 hari: jumlahkan durasi sehari (waspada di atas 45 menit), cari status Failed / "too much computer time". Kalau mendekati, naikkan `SAPU_MENIT` (30) atau persempit `SAPU_JAM`, lalu **Matikan** dan **Aktifkan input otomatis** sekali lagi (interval trigger hanya berubah lewat dua langkah itu). Sejak 2026-10-13 bawaannya sudah 15 menit dan jam 06–19, dan sel IN/OUT yang diterima tidak lagi di-reset tampilannya kalau tidak punya catatan (±4 panggilan lebih sedikit per entri; sel yang ditempel dari sel berwarna ikut menyimpan warnanya, pakai **Ctrl+Shift+V** / tempel nilai saja). Perkiraan, belum diukur di Google: pemakaian penyapu ±8–10 menit per hari (sebelumnya ±14–16). Jumlah baris Log sehari kira-kira sama dengan jumlah edit sehari.

**Perkiraan volume** (dari Histori versi file lama, 6–12 Okt: tiga hari lengkap 49, 75, dan 90 "edit", rata-rata ±71; hari lain punya 4–5 versi yang totalnya belum terbaca, 6 Okt kemungkinan paling sibuk; satu "edit" di Histori versi = blok sel berdekatan, bukan satu sel, jadi entri sebenarnya bisa lebih banyak): pemakaian sehari ±20–60% dari 90 menit (±70 entri ≈ 21%, ±300 entri ≈ 59%), **belum terukur di Google**. Ukuran sebenarnya hanya dari Executions.

**Kalau kuota habis** (trigger berhenti, angka IN/OUT tetap di sel): paling aman **menunggu** kuota pulih (±24 jam); angka diproses sendiri dan tercatat di Log. Kalau tidak bisa menunggu: **hapus dulu angka IN/OUT sampai selnya kosong, baru ubah STOK secara manual** (STOK baru = STOK lama + IN − OUT). Jangan sebaliknya: kalau STOK diubah selagi angka masih di sel, angka itu diproses lagi saat trigger pulih dan stok jadi dobel. Perubahan STOK manual saat trigger mati **tidak tercatat di Log** (catat sendiri). Aturan staf: angka yang tidak hilang dalam ±1 menit **jangan diketik ulang** dan STOK jangan diubah; lapor admin. **Cadangan** (belum diuji): akun Google kedua dengan izin edit file bisa menjalankan menu 2 sementara, kuotanya kemungkinan terpisah (kalau kolom STOK dikunci, tambahkan akun itu sebagai pengecualian proteksi dulu; matikan lagi setelah kuota akun utama pulih, satu akun saja). Di Apps Script → **Triggers**, atur *Failure notification settings* ke *Notify me immediately* supaya ada email saat eksekusi gagal (belum pasti apakah kuota habis ikut memicunya). Pengaturan kode (`SAPU_MENIT`, `SAPU_JAM`) boleh diubah kapan saja tanpa migrasi ulang; **Matikan input otomatis** adalah rem darurat (sheet lama tetap utuh tapi basi, tidak ikut terisi). **Rencana awal yang disarankan:** migrasi UC dulu (menu 1a), ukur 2–3 hari di Executions, baru STP (1b); sheet yang belum dimigrasi hanya memicu eksekusi singkat ±1–2 detik per edit.

**Satu akun saja** yang menjalankan menu 2: dua akun menggandakan trigger edit dan penyapu (biaya dua kali). Jangan menyisip atau menghapus baris produk selagi staf sedang mengetik.

Baris bawah tabel:
- **TOTAL STOK**: total per warna + total unit (kolom C) + total value.
- **MASUK / KELUAR HARI INI**: jumlah IN/OUT hari ini per warna, dari Log. Di **kolom C baris itu = total KELUAR hari ini** (semua warna, mis. "Keluar 4 unit"), dan **di bawahnya**, berurutan: total MASUK hari ini, **Keluar kemarin**, **Keluar 7 hari** (hari ini + 6 hari sebelumnya), **Keluar bulan ini** (tanggal 1 sampai hari ini). Staf tidak perlu pindah sheet. Semuanya rumus langsung ke Log, jadi bersih setelah pembatalan (B1), tanpa trigger dan tanpa kuota tambahan. Konsekuensi: angka "kemarin/7 hari/bulan ini" ikut hilang bila baris Log dipindah ke arsip (menu Arsipkan log bulan lalu). Angka bulan lalu dan sebelumnya tetap ada di **Rekap Harian**.
- **Kapan angka hari ini reset:** tengah malam WIB. Artinya angkanya masih ada pada jam 19.00 dan tetap ada sampai tengah malam. Syarat: **zona waktu file = Asia/Jakarta** (menu "Setel zona waktu file ke WIB"; kalau tidak, resetnya terjadi di jam lain, mis. 14.00 WIB di zona Pacific) dan **File → Settings → Calculation = "On change and every hour"** supaya hari berganti walau tidak ada yang mengedit. Mau menyimpan angka sebelum reset: lihat "Rekap harian".

Kolom **Value** memakai harga per baris dari formula lama, tapi sekarang menghitung dari kolom STOK.

## Rekap harian (disimpan per hari)

Sheet **Rekap Harian UC** dan **Rekap Harian STP** (satu per sheet stok): satu baris per hari, terbaru di atas, nilai **tetap** (bukan rumus) supaya bertahan walau Log diarsipkan. Kolom: Tanggal | Masuk (unit) | Keluar (unit) | Selisih | Entri | Dibatalkan IN (unit) | Dibatalkan OUT (unit) | Opname STOK (entri) | Selisih opname (unit) | Ditolak (entri) | Dihitung | Status | Catatan. Masuk/Keluar sudah **bersih** setelah pembatalan; "Entri" menghitung entri IN/OUT biasa (bukan pembatalan). Kolom **Catatan** boleh Anda isi sendiri (ikut tersimpan per tanggal). Kolom O2 = kapan terakhir dihitung.

Cara kerja:
- Sumber kebenaran = **Log + sheet arsip log**. Rekap dihitung ulang dari sana, bukan diperbarui per entri, jadi tidak menambah kuota di jalur input.
- **Otomatis tiap malam** (trigger ketiga "rekap harian", sekitar 00.30 WIB; dipasang menu **2**): menghitung ulang hari ini dan 3 hari sebelumnya (lebih jauh bila ada hari yang terlewat). Hari kemarin jadi final.
- **Hari ini belum final sampai tengah malam.** Mau menyimpan angka hari ini pada jam 19.00: menu **Perbarui rekap harian sekarang** (angka live ada juga di kolom C di bawah TOTAL STOK).
- **Bangun ulang rekap harian dari Log (semua hari)**: menghitung seluruh riwayat dari Log + arsip dan boleh menurunkan angka lama (dengan konfirmasi). Dipakai bila ada yang tidak cocok.
- Pengaman: hari yang barisnya sudah tidak ada di Log/arsip **tidak pernah dihapus atau dinolkan**. Kalau sumber sebuah hari kini lebih sedikit dari yang tersimpan (mis. Log dipotong), angka lama dipertahankan dan Status berbunyi "SUMBER BERKURANG" (hanya "Bangun ulang" yang boleh menurunkan). Baris Log yang Waktu-nya tak terbaca atau Qty-nya bukan angka tidak dihitung; peringatannya muncul di dialog menu, di sel **O3** sheet Rekap, dan di **Cek status**.
- Rekap membaca seluruh Log sekali per malam (±5–20 detik kuota). Batas `REKAP_BATAS_BARIS` = 60.000 baris (Log + arsip) berlaku untuk "Bangun ulang"; trigger malam memakai batas 3× lebih longgar. **Memindahkan baris ke arsip tidak mengurangi hitungan ini** (arsip ikut dibaca); kalau sampai terlewati, naikkan `REKAP_BATAS_BARIS` di kode. Trigger malam juga membaca arsip bulan yang memuat jendela 4 hari terakhir, jadi hari yang sempat pindah ke arsip sebelum dihitung final tetap benar.
- Tabel Rekap **ditulis ulang seluruhnya** tiap kali dihitung: rumus, warna sorot, atau catatan-sel yang Anda taruh di dalam tabel tidak dijamin bertahan. Hanya kolom **Catatan** (M) yang dibawa per tanggal. Taruh rumus/analisis Anda di sheet lain yang merujuk ke Rekap.
- Ada satu hal yang bisa membuat satu hari terlihat salah: entri yang diproses **setelah** tengah malam (mis. angka tertinggal yang baru diproses penyapu keesokan paginya) dicatat di hari proses, bukan hari ketik.
- Sheet rekap ikut dikunci oleh menu **3**. Cek status menampilkan jumlah hari tersimpan dan kapan terakhir dihitung (peringatan bila lebih dari 26 jam).

## Log Stok (satu per sheet)

- **Stok Cover UC** mencatat ke **Log Stok UC**, **Stok Cover STP** ke **Log Stok STP**.
- **Terbaru di paling atas** (baris 2). Header tetap di baris 1 dan ikut membeku saat scroll.
- Kolom: Waktu (WIB), Sheet, Baris, Produk, Kode SKU, Warna, Jenis (IN / OUT / KOREKSI / DITOLAK), Qty, Stok Sebelum, Stok Sesudah, User, Keterangan.

**Cari / saring riwayat.** Aman. Pakai **Data → Filter views → Create new filter view** (bukan "Create a filter"): filter view hanya berlaku di layar kamu, tidak mengubah tampilan staf lain, dan tidak mengganggu script. Contoh: filter kolom Produk = Honda Brio, atau Jenis = DITOLAK, atau Waktu pada rentang tertentu. Script tetap mencatat mutasi baru walaupun filter sedang aktif (baris disisipkan di atas dan tersimpan, hanya mungkin belum terlihat sampai filter diterapkan ulang). Hindari **Data → Sort sheet** langsung di log: urutannya berlaku untuk semua orang. Urutan tetap kembali terbaru-di-atas untuk mutasi berikutnya.

**Dibagi per bulan?** Tidak wajib. Satu log per sheet lebih mudah dicari dengan filter. Kalau log mulai berat (kira-kira di atas 30–50 ribu baris; perkiraan, bukan batas Google), jalankan menu **📦 Sistem Stok → Arsipkan log bulan lalu**:
- Baris sebelum bulan ini dipindah ke sheet **"Arsip Log Stok UC 2026-09"**, **"Arsip Log Stok STP 2026-09"**, dst. (satu sheet per bulan, terbaru di atas).
- Log hanya menyisakan bulan ini. Rekap "hari ini" tidak terpengaruh.
- Ada dialog konfirmasi yang menampilkan jumlah baris per bulan. Baris yang jamnya tidak terbaca dibiarkan di Log.
- Sheet arsip baru belum dikunci: jalankan menu **3. Kunci kolom STOK** lagi bila memakai kunci.
- Cukup dijalankan sebulan sekali (awal bulan) oleh **pemilik file**. Kalau Log sudah dikunci (menu 3) dan akun lain menjalankannya, menu berhenti dengan pesan "DILEWATI" sebelum menulis apa pun.
- **Aman diulang.** Kalau proses terhenti di tengah (mis. koneksi putus), jalankan lagi: baris yang sudah masuk arsip tidak digandakan, dan hanya baris yang sudah diarsipkan yang dihapus dari Log.
- Baris Log yang kolom Waktu-nya tidak terbaca (mis. teks) tidak dipindah.

**Rumus buatan sendiri di log** (mis. `COUNTIF`, `QUERY`): aman mulai dari baris 2 karena script menyisip baris baru di bawah baris data pertama, sehingga rentang seperti `G2:G` ikut melebar. Paling aman tetap memakai kolom penuh (`G:G`) atau `G2:G`. Dalam satu kali input yang memproses beberapa sel (mis. paste), yang diproses paling akhir ada paling atas.

Kalau di file trial masih ada sheet **"Log Stok"** lama (satu log bersama dari versi sebelumnya), hapus saja; script tidak memakainya lagi.

## Memasang versi kode baru (sheet sudah pernah dimigrasi)

Tempel kode baru di Apps Script lalu simpan (Ctrl+S) cukup untuk **logika input** (validasi, zona waktu, log baru, arsip, penyapuan input cepat). **Trigger baru (penyapu 15 menit) baru terpasang setelah menu 2. Aktifkan input otomatis dijalankan sekali lagi** (aman: trigger edit yang sudah ada tidak digandakan). Kalau penyapu lama (mis. 10 menit) sudah terpasang, menu 2 tidak menggantinya: jalankan **Matikan input otomatis** lalu **Aktifkan input otomatis** supaya interval jadi 15 menit. Jam kerja penyapu (`SAPU_JAM`) dibaca dari kode, jadi cukup tempel kode + Ctrl+S. Menu **Cek status** menunjukkan **jumlah** trigger yang terpasang; angka "tiap … menit" di dialognya hanya membaca nilai di kode, bukan interval trigger yang sebenarnya. Interval sebenarnya dilihat di Apps Script → ikon jam **Triggers** (penyapu harus bertulisan "Every 15 minutes"). Tampilan yang dibuat saat migrasi (warna, format STOK 0 kosong, rumus rekap harian, log per sheet) **tidak berubah otomatis** di sheet yang sudah dimigrasi. Menu **Cek status** memberi peringatan bila rekap harian masih merujuk log versi lama.

- **File trial**: boleh migrasi ulang. Hapus sheet "Stok Cover UC" / "Stok Cover STP" baru dan semua sheet "Log Stok…", ganti nama "(lama)" kembali ke nama asli, lalu jalankan menu 1a dan 1b (sheet Urutan UC / Urutan STP harus masih ada). Mutasi yang sudah dicatat di sheet baru ikut hilang.
- **File asli yang sudah dipakai sungguhan**: **jangan** migrasi ulang (stok sekarang ada di sheet baru, sheet "(lama)" sudah basi). Naikkan versi dengan menu **4. Perbarui sheet yang sudah dimigrasi** (di bawah).

**Menu 4 (sheet yang sudah dimigrasi, tanpa migrasi ulang).** Memasang fitur pembatalan B dan rekap harian di sheet yang sudah dipakai: validasi kolom IN/OUT (menerima `B1`), total harian di kolom C (baris di bawah TOTAL STOK, dicari lewat label "TOTAL STOK"/"MASUK / KELUAR HARI INI", bukan alamat tetap), teks banner baris 1, dan sheet **Rekap Harian** beserta riwayatnya dari Log + arsip. **Tidak mengubah** STOK, isi IN/OUT, Log, catatan, atau warna sel data. Sebelum menulis, tiap sheet diperiksa: sudah berformat STOK/IN/OUT, label TOTAL STOK ada, Log ada, tidak terkunci untuk akun ini, dan sel total harian kosong atau milik rumus ini (kalau berisi hal lain, **tidak ditimpa** dan dilaporkan); satu sheet yang gagal diperiksa dilewati dengan alasan, tidak menghentikan sheet lain. Laporan per langkah muncul di dialog akhir. **Aman diulang** (hasil sama).

Urutan aman untuk file asli yang sudah dipakai (kerjakan di luar jam kerja, mis. setelah 19.00 saat penyapu sudah berhenti):
1. Semua staf menutup file. Pastikan tidak ada angka tertinggal di IN/OUT dan tidak ada sel merah.
2. **File → Make a copy** sebagai cadangan (di file asli: **File → Version history → Name current version**).
3. Tempel `Kode.gs` baru di Apps Script, Ctrl+S, refresh. **Jangan jalankan menu apa pun dulu**; **Cek status** boleh (hanya membaca).
4. Menu **4** dari akun pemilik (akun yang menjalankan menu 2 dan 3). Baca laporannya: tiap langkah harus "diperbarui"/"ditulis", bukan GAGAL atau DILEWATI.
5. Menu **2. Aktifkan input otomatis**: melengkapi trigger rekap harian tanpa menggandakan trigger lama. Cek di Apps Script → **Triggers**: 3 trigger milik satu akun (edit, penyapu "Every 15 minutes", rekap harian "Day timer", sekitar 00.00–01.00 GMT+7).
6. Kalau menu 3 dipakai, jalankan **ulang** supaya sheet Rekap ikut terkunci.
7. Tes: ketik OUT 1, lalu `B1` di sel yang sama (stok kembali, Log punya 2 baris: OUT 1 dan OUT −1); coba `B1` lagi (harus ditolak). **Pastikan `B1` benar-benar bisa diketik tanpa popup penolakan dari Sheets** (laporan menu 4 hanya membuktikan Google menerima rumusnya, bukan cara kerjanya). Cek kolom C di bawah TOTAL STOK. Tes juga dari HP. Catatan: tes ini tercatat permanen di Log dan Rekap hari itu (Keluar bersih 0, Entri 1, Dibatalkan OUT 1); itu normal. Lebih bersih: coba dulu di salinan file (File → Make a copy).
8. Hari 1–3: pantau Executions dan sheet Rekap (Cek status menampilkan umur rekap).
- **Jalan mundur:** menu **Matikan input otomatis** (ini menghentikan SEMUA pemrosesan input staf; pulihkan dengan menu **2. Aktifkan input otomatis** setelah kode lama ditempel), hapus sheet Rekap Harian, kembalikan banner D1/kolom C secara manual, atau pulihkan dari salinan/Version history. Tempel `Kode.gs` lama bila perlu.
- Ubah `FORMAT_STOK` di kode hanya berlaku untuk migrasi berikutnya.

## Tampilan STOK 0

Angka **0** di kolom STOK tidak ditampilkan (sel tampak kosong); nilainya tetap 0 sehingga hitungan, OUT, dan TOTAL tidak berubah. Baris TOTAL STOK tetap menampilkan angka, termasuk 0. Untuk menampilkan 0 lagi: ubah `FORMAT_STOK` di Kode.gs menjadi `'0'` lalu migrasi ulang (lihat bagian di atas), atau ubah format kolom STOK manual lewat **Format → Number**.

## Warna di sheet baru

Mengikuti sheet asli: tiap warna cover diwarnai di **header** dan kolom **STOK**; kolom **IN** dan **OUT** tanpa warna.

| Warna | Header & STOK |
|---|---|
| Abu-abu, Elite/Epic/Warior Abu | abu (#999999), teks hitam |
| Hitam | hitam, teks putih |
| Biru Benhur, Elite/Epic/Warior Biru | biru (#0000FF), teks putih |
| Merah, Elite/Epic/Warior Merah | merah (#FF0000), teks putih |
| Hijau Army | hijau tua (#38761D), teks putih |
| Orange (STP) | oranye (#FF9900), teks hitam |
| Premium / Transparan / Exclusive | abu muda |

Nama produk dan Kode SKU sengaja **tanpa warna** (kuning/hijau di sheet lama ditambah sendiri). Banner "SELAIN ADMIN…" di baris 1 tetap cyan bertulisan merah.
Cell yang ditolak (input salah / OUT melebihi stok) tetap merah muda sampai dihapus. Daftar warna ada di `KONFIG.PALET`; cocok berdasarkan kata di nama warna, jadi warna baru bernama "… Biru" otomatis biru.

## Warna Orange (Stok Cover STP)

Orange = warna **Reguler** ke-6 Smartprotection (SKU `-R-…-ORG`). Sheet lama STP belum punya kolom Orange, jadi migrasi STP otomatis menambahkan blok **Orange: STOK | IN | OUT** tepat setelah Hijau Army:
- Stok awal kosong (0). Isi stok Orange yang ada lewat kolom IN, atau admin ketik langsung di STOK (tercatat `KOREKSI`).
- Value Orange ikut harga **Reguler** per baris (sama dengan Abu-abu, Hitam, dst.).
- Ikut TOTAL STOK, rekap harian, Log, validasi, dan kunci kolom.

Diatur di `KONFIG.SISTEM[1].warnaTambahan`. Warna baru lain bisa ditambah dengan pola yang sama **sebelum migrasi**, mis. `{ nama: 'Silver', setelah: 'Orange' }`. Menambah warna **setelah** sheet aktif dipakai belum didukung script; minta dibuatkan dulu.

## Nama sheet setelah migrasi

| Sebelum | Sesudah |
|---|---|
| Stok Cover UC (format IN/OUT) | **Stok Cover UC** = format baru STOK/IN/OUT, dipakai harian |
| | **Stok Cover UC (lama)** = sheet lama, isi utuh, termasuk Stok Reseller ASTA & ROBY (baris 201+) |
| Stok Cover STP | **Stok Cover STP** (baru) + **Stok Cover STP (lama)** |
| — | **Log Stok UC** dan **Log Stok STP** (baru, satu log per sheet) |

Sheet lain (Resi Keluar Stok, Plan Stok, dll.) tidak disentuh.

## Kenapa butuh Apps Script

Formula biasa tidak bisa "menambah ke dirinya sendiri". `STOK = STOK + IN` adalah referensi melingkar. Angka yang diketik lalu hilang (seperti alur sekarang) hanya bisa lewat script. Apps Script gratis, bawaan Google Sheets, tidak perlu install ekstensi.

## Trial dulu di salinan, baru pasang di file asli

Nama menu di bawah memakai **tampilan Google bahasa Inggris**.

1. Upload `Stock_Opname.xlsx` ke Google Drive.
2. Buka dengan Google Sheets → **File → Save as Google Sheets**. File .xlsx yang dibuka langsung (mode Office) tidak bisa memakai Apps Script.
3. Di file hasil konversi itu, jalankan langkah **Pasang** di bawah. Coba semua skenario di tabel "Cara kerja".
4. Setelah puas: di file trial klik **📦 Sistem Stok → Matikan input otomatis**, lalu ulangi langkah Pasang di Google Sheet asli. Script tidak ikut pindah; tempel ulang di file asli.

Migrasi di file asli memakai data saat itu, bukan data file trial.

**Catatan:** file hasil konversi `.xlsx` memakai lokal Amerika dan zona waktu Pacific, sedangkan Google Sheet asli bisa berlokal Indonesia. Perbedaan lokal pernah menggagalkan migrasi di file asli padahal trial lancar. Uji coba paling mirip kenyataan: **File → Make a copy** dari Google Sheet asli (lokal dan zona waktu ikut tersalin), bukan konversi xlsx.

## Pasang (sekali, oleh pemilik file)

**A. Tempel kode**
1. File asli: **File → Make a copy** dulu sebagai backup. (Untuk file trial tidak perlu.)
2. Di spreadsheet: **Extensions → Apps Script**. Terbuka tab baru "Untitled project". Harus dibuka dari menu spreadsheet ini, bukan dari script.google.com.
3. Buka file `Kode.gs` (Notepad / VS Code) → **Ctrl+A** → **Ctrl+C**.
4. Di Apps Script, panel kiri **Files**:
   - Project baru (cuma ada `Code.gs` berisi `function myFunction() {}`): klik `Code.gs`.
   - Sudah ada script lain: **jangan dihapus**. Klik **+ → Script**, beri nama `SistemStok`, klik file itu. Kalau script lama juga punya `function onOpen`, gabungkan isinya jadi satu fungsi.
5. Klik di area kode → **Ctrl+A** → **Delete** (hapus `function myFunction() {}`) → **Ctrl+V**. Baris pertama harus `/**`, paling bawah `function huruf_(c) {…}` (±1.200 baris).
6. **Ctrl+S** (atau ikon disket "Save project"). Tidak perlu klik **Run** atau **Deploy**.

**B. Impor daftar urutan, lalu jalankan dari spreadsheet**

7. Kembali ke tab spreadsheet → **refresh (F5)**. Tunggu ±5 detik: menu **📦 Sistem Stok** muncul setelah **Help**.
   Impor daftar urutan (cara di bagian "Daftar urutan produk"): sheet **Urutan UC** dan **Urutan STP** harus ada sebelum langkah 8. Menu **Cek status** memberi tahu kalau belum ada.
8. Klik **📦 Sistem Stok → 1a. Susun "Stok Cover UC"…**. Pertama kali muncul izin:
   **Authorization required → OK / Review permissions** → pilih akun → **"Google hasn't verified this app" → Advanced → Go to Untitled project (unsafe) → Allow**. Wajar untuk script buatan sendiri.
   Setelah Allow, kalau tidak terjadi apa-apa, klik menu **1a** sekali lagi.
9. Muncul ringkasan (jumlah produk, produk baru, baris digabung, total stok, OUT yang masih terisi) → **Yes**. Lalu catatan formula Value → **OK**. Tab berubah: "Stok Cover UC" (baru), "Stok Cover UC (lama)", "Log Stok UC". Kalau muncul pesan masalah daftar, tidak ada yang berubah: perbaiki sheet Urutan sesuai pesan, lalu ulangi.
10. **📦 Sistem Stok → 1b. Susun "Stok Cover STP"…** → **Yes** → **OK**. Kolom Orange muncul setelah Hijau Army.
11. **📦 Sistem Stok → 2. Aktifkan input otomatis** → **OK** (sekali, berlaku untuk kedua sheet; memasang 3 trigger: edit, penyapu 15 menit, dan rekap harian tiap malam).

**C. Tes**

12. Stok Cover UC, baris 4 (Honda Brio, produk pertama): ketik `1` di **E4** (IN Abu-abu) → Enter → tunggu 1–2 detik → D4 bertambah 1, E4 kosong lagi, tab "Log Stok UC" ada baris baru di paling atas (baris 2).
13. Ketik `1` di **F4** (OUT Abu-abu) → D4 kembali semula.
14. Ketik `999` di F4 → sel merah + catatan "DITOLAK", D4 tidak berubah. Hapus isi F4 → warna kembali normal.
15. Stok Cover STP: coba kolom Orange (**T** = IN, **U** = OUT, **S** = STOK).
16. Tes juga dari aplikasi Google Sheets di HP.
17. (Opsional) **📦 Sistem Stok → 3. Kunci kolom STOK**, lihat penjelasan di bawah. Tidak perlu saat trial sendirian.

### Untuk apa "Kunci kolom STOK"?

Tanpa kunci, semua editor bisa mengetik apa saja di sel mana pun, termasuk menimpa atau menghapus angka STOK, menghapus baris di Log Stok UC/STP, atau merusak rumus Total/Value. Dengan kunci:
- Staf **hanya** bisa mengisi kolom **IN** dan **OUT** (semua baris produk).
- Kolom **STOK**, header, TOTAL, Value, nama produk, SKU, dan sheet **Log Stok UC / STP** (dan arsipnya) terkunci. Hanya pemilik (dan editor yang ditambahkan di **Data → Protect sheets and ranges**) yang bisa mengubahnya.
- STOK tetap berubah saat staf mengisi IN/OUT, karena trigger berjalan sebagai pemilik file.
- Efek samping: staf tidak bisa koreksi stok langsung (opname) dan tidak bisa menambah produk/baris. Itu dikerjakan pemilik.

Kalau semua pengguna dipercaya dan Log cukup, boleh tidak dikunci. Untuk membuka kunci: **Data → Protect sheets and ranges** → hapus perlindungan bernama "Sistem stok: hanya IN/OUT yang boleh diisi".

**Waktu migrasi terbaik di file asli: akhir hari**, setelah OUT dihapus dan IN sudah final. Script mengambil angka IN apa adanya sebagai STOK awal.

Kalau migrasi error di tengah jalan, sheet lama tidak berubah (script menghapus sheet setengah jadi dan sheet Log kosong yang dibuatnya). Zona waktu file baru diubah setelah migrasi berhasil.

**Migrasi gagal dengan pesan "Argumen aturan validasi data "=AND(ISNUMBER(D4),…" tidak valid"** (kode sebelum 2026-10-20 di file berlokal Indonesia, yang memakai titik koma sebagai pemisah argumen rumus): tempel `Kode.gs` terbaru lalu ulangi menu 1a/1b. Sheet tidak diubah saat migrasi gagal, jadi aman diulang (kalau ada tab sisa bernama "… (baru)", hapus dulu). Kode baru mencoba rumus validasi berkoma, lalu bertitik koma, lalu aturan "angka antara"; kalau semuanya ditolak Google, migrasi tetap selesai tanpa validasi dan menyebutnya di catatan akhir (script tetap menolak isian salah dengan tanda merah + catatan). Lokal file dilihat di **File → Settings → General → Locale**. Cadangan kalau masih gagal: ubah Locale ke United States sementara, jalankan migrasi, lalu kembalikan (rumus ikut menyesuaikan sendiri).

Menu **📦 Sistem Stok** tidak muncul? Cek: kode sudah di-save (Ctrl+S), Apps Script dibuka lewat **Extensions → Apps Script** dari spreadsheet yang sama, file sudah format Google Sheets (bukan .xlsx), lalu refresh lagi.

## Aturan pakai

- **Satu orang saja** yang menekan "Aktifkan input otomatis" (sebaiknya pemilik file). Trigger dari 2 akun tidak menghitung dobel, tapi bikin log penolakan/koreksi tercatat 2×.
- **Jangan buat fungsi bernama `onEdit`** di Apps Script. Bisa memicu proses ganda.
- **Jangan pakai Ctrl+Z** untuk membatalkan input stok. Salah ketik **hari ini**: ketik `B` + jumlah di sel yang sama (mis. `B1`). Salah catat di hari lain: admin mengoreksi STOK (opname). **Jangan** memakai input kebalikan (salah OUT 3 → IN 1): itu membuat rekap Masuk/Keluar hari itu salah. Semua tercatat di Log.
- Tunggu sel IN/OUT kosong lagi (beberapa detik) sebelum mengetik di **sel yang sama**. Mengetik cepat di sel berbeda aman: angka yang tertinggal disapu otomatis (lihat "Mengetik cepat di banyak sel").
- **Jangan ganti nama** sheet "Stok Cover UC", "Stok Cover STP", "Log Stok UC", "Log Stok STP", (sheet "(lama)" boleh dihapus setelah tidak dibutuhkan; migrasi ulang tetap ditolak karena sheet baru sudah berformat STOK/IN/OUT. Pindahkan dulu Stok Reseller ASTA/ROBY di UC (lama) baris 201+ kalau masih dipakai). Kalau perlu ganti nama, ubah juga `KONFIG` di Kode.gs.
- Staf jangan mengisi stok di sheet "(lama)". Isinya tidak lagi diupdate.
- **Tambah produk baru**: klik kanan **baris kosong tepat di atas TOTAL STOK** (setelah migrasi: baris 185 di UC, baris 130 di STP; lihat baris bertuliskan TOTAL STOK) → **Insert 1 row above**. Baris baru jatuh di dalam rumus TOTAL, jadi ikut terhitung. Isi nama, Kode SKU, STOK awal; salin rumus Value dari baris produk di atasnya. Jangan sisip di bawah baris kosong itu: baris tersebut tidak masuk TOTAL.
- Header baris 2 (nama warna) dan baris 3 (STOK/IN/OUT) jadi patokan script. Jangan diubah.
- **Sheet Log boleh disembunyikan** (klik kanan tab → **Hide sheet**; buka lagi lewat **View → Hidden sheets**). Script mencari Log lewat nama, jadi tetap menulis dan rekap harian tetap menghitung. Jangan hapus atau ganti namanya. Sheet arsip bulanan dibuat dalam keadaan terlihat, sembunyikan sendiri kalau perlu.
- **Kolom Value boleh diedit** (diuji: tidak mengubah STOK dan tidak menambah Log). Ubah harga lewat angka setelah tanda `*` di rumus, mis. `=(D5+G5+J5+M5+P5)*277000` jadi `...*300000`. Jangan hapus atau geser kolom STOK (rumus jadi `#REF!`), jangan timpa rumus dengan angka tetap, dan jangan ketik `STOK`, `IN`, atau `OUT` di baris 3 area Value (script membaca baris itu untuk memetakan kolom). Edit di Value memicu satu eksekusi singkat tanpa efek: tempel atau isi sekaligus, jangan satu-satu dalam jumlah ratusan. Kalau kolom STOK dikunci (menu 3), Value ikut terkunci untuk selain pemilik.

## Batasan yang perlu dites sendiri

- **Aplikasi Sheets di HP**: dokumentasi Google tidak menyebut beda perilaku trigger di HP, tapi juga tidak menjamin. Tes langkah 12–14 dari HP sebelum dipakai staf.
- **Jam di Log** selalu WIB (angka jam ditulis script, tidak bergantung zona waktu file). Saat migrasi, script juga mengubah **zona waktu file** ke Asia/Jakarta kalau belum, supaya rekap "MASUK / KELUAR HARI INI" mengikuti tanggal WIB. Perubahan ini disebut di dialog sebelum klik **Yes**. File hasil konversi dari .xlsx bisa berzona waktu Pacific (UTC-7): jam Log tampil 14 jam lebih awal. Menu **Setel zona waktu file ke WIB** memperbaikinya tanpa migrasi ulang (baris Log lama tidak berubah; hapus kalau hanya data uji).
- Kolom **User** di Log bisa kosong.
- **Batas angka**: IN/OUT/STOK 1–9999 per sel (`KONFIG.MAKS_QTY`). Ini juga menolak angka yang tidak sengaja terbaca sebagai tanggal (mis. `1/2`). Zona waktu file dikembalikan ke WIB otomatis begitu input pertama diproses. Untuk akun Gmail biasa, Google sering tidak memberikan email editor ke script.
- Kuota Google untuk trigger terbatas per hari (lihat "Biaya" di bagian Mengetik cepat). Satu input diproses ±6–9 detik menurut Executions file ini (bukan ±1 detik); hasilnya muncul beberapa detik setelah Enter.
- Butuh koneksi internet saat input. Input saat offline belum tentu diproses. Sel IN/OUT yang tetap terisi = belum diproses: hapus, ketik ulang.

## Temuan di data sekarang (dicek dari file unduhan 2026-10-08)

Stok Cover UC:
- **Baris 40 (Gran Max/Luxio) & 41 (Fronx)**: formula Value Premium rusak: `=AF40*AM4441128`, `=AF41*AM4441129`. Mengacu ke sel kosong, jadi value Premium selalu 0. Di sheet baru dikosongkan; isi harga manual.
- **14 baris tanpa formula Value**: 50, 58, 68, 69, 70, 82, 83, 94, 118, 140, 190, 191, 192, 194 (mis. Land Cruiser, Jimny 3P, Mazda Cx9).
- **46 sel OUT masih terisi**. Pastikan IN sudah dikurangi sebelum migrasi.
- Baris 19 tertulis "Toyota Swift" (SKU `SZK-SWF-…`). Kemungkinan salah ketik "Suzuki Swift".

Stok Cover STP:
- **Total lama (baris 109–110) hanya menjumlah sampai baris 104.** X-Over, Soluna, C Class (baris 105–107, 3 unit) tidak ikut total. Sheet baru menjumlah sampai 107: 246 unit (total lama 243).
- **Baris 5, 6, 7, 8, 11 — otomatis DIPERBAIKI saat migrasi**: formula Strip lama tidak menghitung Elite Abu & Warior Abu. Sheet baru menghitung semua 9 warna Strip seperti baris lain, harga tetap. Efek di data sekarang: Veloz (baris 6) value Strip 0 → 257.000.
- **Baris 10 (Innova) — otomatis DIPERBAIKI saat migrasi**: formula Reguler merujuk `L9` (Hijau Army baris 9) bukan `L10`. Sheet baru memakai baris sendiri: value Reguler Innova 514.000 → 0 (Innova memang tidak punya stok Reguler).
- **Exclusive**: Smartprotection tidak menjual varian Exclusive (konfirmasi user 2026-10-08). Kolomnya tetap ada tapi kosong; tidak dilaporkan sebagai masalah.
- Strip baris 4 dan Transparan baris 15 tidak punya harga; 8 baris tanpa formula Value sama sekali (47, 73, 91, 102, 103, 105, 106, 107).
- 1 sel OUT masih terisi (Honda Brio Hitam).

## Sheet lain di file

Dicek dari file unduhan: 11 sheet, 1.443 formula, **0 formula yang merujuk sheet lain** (tidak ada `'Sheet'!A1`, IMPORTRANGE, QUERY, VLOOKUP, INDIRECT). Sheet lain aman dibiarkan. Trigger tetap terpanggil saat sheet lain diedit, tapi langsung berhenti di baris pertama (cek nama sheet).

## Uji

`uji/` berisi simulasi Google Sheets (Node) untuk menguji Kode.gs dengan data asli:

```
cd sistem-stok-gsheet
python3 uji/ekstrak.py "Stock Opname.xlsx" uji/fixture.json   # data tidak di-commit
node uji/uji.js Kode.gs
```

Hasil 2026-10-20: 301/301 lulus (termasuk simulasi lokal titik koma: rumus validasi berkoma ditolak Google). Hasil 2026-10-13: 282/282 lulus. Hasil 2026-10-12: 276/276 lulus (termasuk daftar urutan sungguhan `uji/daftar-urutan.js` terhadap data asli: stok per warna tiap baris, total unit, harga produk baru, pengaman daftar). Hasil 2026-10-08 (sebelum daftar urutan): 189/189 lulus. Kode juga diperiksa 3 reviewer independen + 2 skeptis per temuan (22 kandidat, 9 terbukti, semuanya sudah diperbaiki atau dicatat di atas). Review fitur daftar urutan (4 lensa, tiap temuan dibantah 2 skeptis): 12 temuan bertahan (pengaman nama bisa mati, harga produk baru tidak ikut bergeser, sel IN teks, catatan terpotong, migrasi tidak atomik, dll.), semuanya diperbaiki dan diuji. Formula hasil migrasi juga dihitung ulang di LibreOffice:
- UC: total unit 1.161, value per baris sama persis dengan sheet lama.
- STP (17 warna, + Orange): total unit 246; value per baris sama dengan sheet lama kecuali baris 6 dan 10 (formula lama salah, lihat Temuan). Tes IN Orange 4 di Brio: Value Reguler +924.000 (4 × 231.000), total 250.
