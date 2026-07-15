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
