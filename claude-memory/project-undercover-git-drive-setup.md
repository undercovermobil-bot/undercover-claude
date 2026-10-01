---
name: project-undercover-git-drive-setup
description: "Setup Git+GitHub (kode/dokumen) dan Google Drive (data besar) untuk proyek Undercover, termasuk auto-commit terjadwal dan sync memory Claude lintas device"
metadata: 
  node_type: memory
  type: project
  originSessionId: 7c593ac5-33d8-4484-b2ce-8b4f3b16cb6e
---

Sejak 2026-07-13, folder `C:\Users\chand\Documents\Undercover` (folder kerja
sebenarnya — bukan `Documents\Undercover Claude` yang kosong, lihat
[[project-undercover-overview]]) adalah git repo yang sinkron ke GitHub +
Google Drive supaya bisa dikerjakan lintas device/akun Claude.

**Pembagian penyimpanan:**
- **GitHub privat**: https://github.com/undercovermobil-bot/undercover-claude
  — kode `.py` (Shopee Price Monitor), dokumen `.md`/`.docx` kecil,
  `.env.example`, dan snapshot memory Claude (folder `claude-memory/` di repo).
- **Google Drive**: https://drive.google.com/drive/folders/168snWOIoROx-isBH3DWdECwSiYVgFHqK
  (folder "Claude", akun under.covermobil@gmail.com) — semua data besar:
  xlsx katalog/SKU, Banner, foto, video, zip export. Di-exclude dari git
  lewat `.gitignore` (pola `*.xlsx`, `*.zip`, gambar, video, dll).
- Panduan lengkap setup device baru: `SETUP-DEVICE-BARU.md` di root repo.

**Automation yang sudah berjalan:**
- Windows Task Scheduler task `Undercover-AutoCommitPush` jalan tiap hari
  **15:45**, menjalankan
  `scripts/auto-commit-push.ps1` — auto `git add`+commit+push kalau ada
  perubahan, log ke `auto-commit-log.txt` (lokal, tidak di-track git).
  Butuh device hidup+login saat itu; sudah diset `WakeToRun` (bangunkan dari
  sleep) + `StartWhenAvailable` (jalan begitu PC nyala lagi kalau jadwal
  kelewat) sebagai jaring pengaman.
- Data besar ke Google Drive sebaiknya pakai fitur **"Back up folder from
  computer"** di Google Drive for Desktop — ini sync real-time tiap file
  disimpan, TIDAK butuh scheduling terpisah seperti git.

**Keterbatasan penting (sudah dicoba & terbukti gagal, 2026-07-13):** Claude
TIDAK BISA upload file besar ke Google Drive secara otomatis lewat tool
chat/MCP — bahkan file xlsx 21 KB pun sudah mentok di batas ukuran konten
base64 per panggilan tool (hasil encode terpotong saat dibaca kembali).
Jangan ulangi eksperimen ini lewat jalur MCP/API.

**TAPI (ditemukan 2026-07-15) ada jalur LAIN yg terbukti jalan** — kalau
sesi Claude berjalan LANGSUNG di PC yg py Google Drive for Desktop aktif
(`G:\My Drive\...` ke-mount): copy/tulis file biasa (Bash/PowerShell `cp`/
`Copy-Item`) ke path `G:\My Drive\...` itu SAMA SEKALI BEDA mekanisme dari
upload via MCP tool call — ini cuma file I/O lokal biasa, Drive Desktop yg
mendeteksi & upload sendiri di background. Diverifikasi jalan (bukan cuma
nulis ke mount lokal, tapi BENERAN naik ke cloud dlm hitungan detik, dicek
via `get_file_metadata` API). Jadi: **kalau sesi Claude py akses terminal
ke device dgn Drive Desktop aktif, TIDAK perlu lagi minta user upload
manual** — tinggal copy ke path `G:\My Drive\...` yg sesuai. Minta manual
ke user cuma perlu kalau (a) sesi Claude tidak py akses filesystem device
itu (mis. sesi cloud/browser-only), atau (b) device itu tidak py Drive
Desktop ke-mount.

**BACA/UNDUH dari Drive lewat konektor MCP di sesi CLOUD — TERBUKTI JALAN
(2026-10-01).** Beda arah dari upload yg gagal di atas. User minta "baca file
di `G:\My Drive\E-commerce\List Produk SKU\List produk`" (path Drive for
Desktop di PC-nya). Sesi cloud tidak bisa buka drive G:, tapi konektor
Google Drive (`mcp__Google_Drive__*`, akun under.covermobil@gmail.com) bisa:
1. Navigasi folder: `search_files` dgn `parentId = '<id>'` (E-commerce =
   `168snWOIoROx-isBH3DWdECwSiYVgFHqK`, List Produk SKU =
   `1GG8ZHvJjIF5oTfBHDB1iOgPrsdNux_MF`, List produk =
   `1SlX362uY4kLRdlFYle0FgDkA28CGAbjH`). Hasil bisa berhalaman — cek
   `nextPageToken` (file ke-6 baru muncul di halaman 2).
2. `download_file_content` -> kalau hasil > batas token, harness OTOMATIS
   menyimpan JSON `{content: base64, ...}` ke `~/.claude/projects/.../
   tool-results/mcp-Google_Drive-download_file_content-*.txt`; decode pakai
   python `base64.b64decode(json.load(f)['content'])` -> xlsx utuh.
   Diverifikasi byte-exact (Shopee 2.xlsx 101.230 byte = ukuran di Drive).
   **Hati-hati: file KECIL (<~40 KB) TIDAK disimpan ke file, base64-nya
   masuk langsung ke percakapan** (boros konteks, dan tidak bisa di-decode
   tanpa menyalin ulang) — utk file kecil tetap lebih baik minta user upload
   di chat, atau terima saja hasil inline kalau isinya tidak perlu diolah.
3. File hasil tetap perlu `repair_xlsx.py` (bug activePane Shopee sama).
Belum diuji utk file ~2 MB (Lazada/TikTok 1 di folder itu) — mekanisme sama,
kemungkinan jalan. Upload/tulis ke Drive lewat MCP tetap JANGAN dicoba
(lihat catatan gagal di atas).

**Sinkronisasi memory Claude lintas device:** folder `claude-memory/` di
repo adalah snapshot manual dari
`~/.claude/projects/<hash-folder-project>/memory/*.md`. Kalau ada memory
baru/update di satu device, copy ulang ke `claude-memory/` lalu commit
(auto-commit 15:45 akan otomatis push-kan kalau sudah ke-copy sebelum jam
itu). Di device lain, `git pull` lalu salin ulang isi `claude-memory/` ke
folder memory lokalnya. Detail lengkap di `SETUP-DEVICE-BARU.md` bagian
"Restore memory Claude".

Why: dicatat supaya sesi Claude berikutnya (device manapun) langsung tahu
infrastruktur ini sudah ada dan tidak perlu setup ulang, dan supaya tidak
mengulang eksperimen upload Drive otomatis yang sudah terbukti gagal
(lihat [[user-undercover-profile]] soal kerja lintas akun Claude).

How to apply: sebelum menyarankan setup git/Drive baru untuk proyek ini,
cek dulu apakah repo masih ada dan masih dipakai (`git remote -v` di
`Documents\Undercover`, cek `Get-ScheduledTask -TaskName
Undercover-AutoCommitPush`). Kalau user minta bantuan upload file besar ke
Drive, langsung arahkan ke cara manual — jangan coba jalur MCP Drive tool
untuk file di atas beberapa KB.

**(2026-07-15) Path lokal di PC ini (bukan device asal catatan ini) adalah
`C:\Users\OWNER\Documents\Undercover\Undercover\` (dobel "Undercover",
BUKAN `C:\Users\chand\Documents\Undercover` spt tertulis di atas — itu path
device lain). Selalu verifikasi path aktual per-device, jangan asumsi dari
memory.**

**Ditemukan (2026-07-15): ada DUA folder "List Produk SKU" berbeda di
Drive**, sumber kebingungan user soal "file mana masuk kemana":
1. **Kanonik** — `E-commerce\List Produk SKU\` langsung (folder ID
   `1GG8ZHvJjIF5oTfBHDB1iOgPrsdNux_MF`) — master root di sini SUDAH STALE
   (versi 07-03), tapi subfolder `Hasil Sinkronisasi SKU\` di sini AKTIF
   dipakai (ada file `~$...xlsx` lock artinya lagi dibuka Excel oleh
   seseorang).
2. **Duplikat** — `E-commerce\Export Undercover ke Akun Claude Lain\List
   Produk SKU\` (folder ID `14vfCxdQLqEltZpETXAjesyWoyYPQ9vgm`) — hasil
   drag-and-drop manual folder lokal PC ke browser Drive tgl 13 Juli (lihat
   step "Opsi cepat sekali jalan" di `SETUP-DEVICE-BARU.md` — upload
   browser TIDAK merge, selalu bikin folder baru kalau nama sama). Folder
   ini yg py subfolder `Update via Claude\` — INI yg dimaksud tabel mapping
   "taruh file SYNCED ke sini", BUKAN folder kanonik #1.
   **(Koreksi 2026-07-15 sore) Ternyata BUKAN auto-sync berkelanjutan** —
   dicoba: edit file lokal jam 11:44 & 13:57, dicek lagi jam ~14:00, versi
   di Drive (`G:\My Drive\E-commerce\Export Undercover ke Akun Claude
   Lain\...`) MASIH versi 07-11 (stale, belum ke-update). Kesimpulan
   sebelumnya ("timestamp identik = live sync") salah — itu cuma kebetulan
   dari snapshot upload manual 07-13 yg dilakukan bersamaan. **"Back up
   folder from computer" kemungkinan besar TIDAK aktif untuk folder ini**,
   atau berhenti jalan. Solusi yg terbukti jalan: copy file langsung ke
   path `G:\My Drive\...` (mount lokal biasa, BUKAN lewat MCP/API Drive
   tool) — ini beda mekanisme dari limit ukuran yg didokumentasikan di
   atas (limit itu soal upload via tool call/base64, bukan soal file I/O
   biasa ke drive letter yg di-mount). Setelah copy manual ke `G:\`,
   dikonfirmasi via Drive API (`get_file_metadata`) bahwa file BENERAN naik
   ke cloud (size & modifiedTime cocok) dalam hitungan detik — jadi jalur
   ini reliable, tinggal tidak otomatis, harus di-trigger (copy manual)
   tiap ada perubahan.

Why: user beberapa kali bingung kenapa path yg disebut sesi lain (spt tabel
mapping dari sesi cloud) kelihatannya "tidak ada" waktu dicek manual — root
cause-nya duplikasi folder ini, bukan file yg hilang.

How to apply: kalau user sebut path Drive "List Produk SKU\...", default-kan
ke folder #2 (di dalam "Export Undercover ke Akun Claude Lain") kecuali
konteks eksplisit bilang root/kanonik. Belum digabungkan/dibersihkan —
tawarkan bantuan cleanup kalau relevan, tapi jangan hapus/pindah apa pun di
Drive tanpa konfirmasi eksplisit (banyak file di kanonik sedang aktif
dipakai).

## Lokasi file master SKU (dikonfirmasi via MCP Google Drive, 2026-07-22)

User sempat tidak bisa menemukan file master ("File masternya lokasinya
dimana? kok aku tidak bisa menemukan"). Dikonfirmasi via
`mcp__Google_Drive__search_files`:

- **File master** = `SKU, Price, Tracking Cover Mobil.xlsx`
  (fileId `17PjVhfdNedOYFoDU9-vJB1G4aGYIXU_h`), terakhir diubah **2026-07-03**.
  Lokasi: **E-commerce (folder Drive utama) → List Produk SKU →**
  `SKU, Price, Tracking Cover Mobil.xlsx` — TEPAT DI DALAM folder
  top-level `List Produk SKU`, bukan di subfolder toko manapun.
  1 sheet per merek mobil, format SKU `MEREK-MODEL-TOKO-KAT-GEN-WARNA`.
  Ini file yang sama yang dipakai script-script sesi ini sebagai
  `MASTER_from_drive_20260715.xlsx` secara lokal (nama lokal cuma
  menandai tanggal Claude download/copy filenya ke scratchpad, BUKAN
  tanggal modifikasi Drive-nya — filenya sendiri belum diubah sejak 07-03).
- **Kemungkinan besar sumber kebingungan**: ada folder BERNAMA SAMA
  `List Produk SKU` di DUA tempat berbeda:
  1. `E-commerce/List Produk SKU/` — folder asli, isinya file master +
     4 subfolder per toko (`List Produk Undercover/Otonation/Otopro/Smartpro`)
     + `Hasil Sinkronisasi SKU/` + `Ekspor SKU Gudang/` + `Impor SKU Gudang/`.
  2. `E-commerce/Export Undercover ke Akun Claude Lain/List Produk SKU/` —
     folder staging **untuk Claude edit** sesuai aturan kerja "jangan edit
     file asli langsung, copy dulu ke sini" (lihat
     [[feedback-undercover-update-folder-workflow]]). Ini BUKAN master,
     cuma copy kerja.
  Kalau user mencari "file master" dan membuka folder kedua ini duluan,
  wajar bingung karena tidak ada file master aslinya di situ (cuma ada
  file/script project Shopee Price Monitor yang nyasar — lihat bagian
  cleanup di bawah).
- **Penting**: revisi nama model master (18 rename, 1.997 baris, lihat
  entri sinkronisasi SKU tertanggal 2026-07-21 di
  [[project-undercover-sku-sync-status]]) masih HANYA ada di scratchpad
  sesi lokal (`MASTER Produk - Nama Model Disesuaikan Listing
  (2026-07-21).xlsx`), BELUM di-upload user ke Drive — jadi file master
  di Drive saat ini masih versi lama (pre-rename). Perlu transfer manual
  oleh user kalau mau versi master di Drive ikut ter-update.

## Survei folder E-commerce di Drive (2026-07-22) — kandidat beres-beres

Disurvei via `mcp__Google_Drive__search_files` (belum ada file yang
dihapus — ini cuma daftar temuan untuk dikonfirmasi user dulu):

**Aman dihapus (junk sistem, bukan data):**
- File `.DS_Store` — ditemukan di `List Produk SKU/` dan
  `List Produk SKU/Hasil Sinkronisasi SKU/` (kemungkinan ada di folder
  lain juga). File metadata Finder macOS, tidak ada isi berguna.

**Kandidat redundant/superseded (perlu konfirmasi user sebelum hapus):**
- `List Produk SKU/SKU, Price, Tracking Cover Mobil (backup sebelum
  revisi generasi 2026-07-03).xlsx` — backup pre-revisi dari hari yang
  sama dengan master saat ini; kemungkinan sudah tidak perlu tapi bisa
  jadi jaring pengaman.
- `List Produk SKU/Ekspor SKU Gudang/` berisi 3 file
  `SKU_Gudang20260701230231581(1/2/3).xlsx` + 1 file
  `SKU_Match_20260701230448884(8).zip` — nama file auto-generated
  BigSeller bertanggal 2026-07-01, kemungkinan sudah digantikan oleh
  proses sinkronisasi yang lebih baru (Toyota pilot 07-01, rollout semua
  merek dst) — perlu dicek apakah masih dipakai referensi atau sudah usang.
- `Export Undercover ke Akun Claude Lain/` (folder staging edit Claude)
  berisi file-file project **Shopee Price Monitor** yang nyasar
  (`scraperapi_backend.py`, `utils.py`, `discovery.py`, `my_products.csv`,
  `shops.txt`) — bukan bagian dari SKU Sync, membingungkan karena
  tercampur di folder yang seharusnya khusus staging edit SKU listing.
- `Export Undercover ke Akun Claude Lain/Dari Downloads (di luar folder
  proyek asli)/` — namanya sendiri menandakan "file lepas di luar
  struktur asli"; isinya `MOBIL TERLARIS (1).xlsx` dan
  `SKU Produk - 100 Mobil Terlaris.xlsx` (laporan turunan, bukan sumber).
- Google Sheet bernama generik **"Report"** di folder `Report/` berisi
  campuran log komplain customer (tab "Cahyo") DAN entri yang sama
  sekali tidak nyambung ke bisnis cover mobil (tab "Fajar" — soal
  pendant/anting/kalung perak) — kemungkinan sheet template/contoh yang
  ketiban isi salah, layak dicek user apakah ini memang dokumen yang
  dimaksud atau nyasar.

Why: user eksplisit minta bantu cari lokasi master + rapikan folder
e-commerce karena kebanyakan file bikin bingung. Belum ada aksi hapus
yang dieksekusi (perlu konfirmasi eksplisit dulu, sesuai kebijakan
"jangan hapus file Drive user tanpa izin").

How to apply: kalau user mau lanjut hapus/pindah file-file di atas,
konfirmasi per-item dulu (bukan hapus massal), lalu jalankan via Google
Drive (manual oleh user, atau via MCP Drive tool kalau tersedia
fungsi delete/trash-nya — belum dicek di sesi ini).
