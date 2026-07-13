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
  **16:15** (15 menit setelah jam kerja terakhir user, ~16:00), menjalankan
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
Jangan ulangi eksperimen ini; transfer data besar ke Drive selalu harus
manual oleh user (drag-and-drop browser, atau Google Drive for Desktop).

**Sinkronisasi memory Claude lintas device:** folder `claude-memory/` di
repo adalah snapshot manual dari
`~/.claude/projects/<hash-folder-project>/memory/*.md`. Kalau ada memory
baru/update di satu device, copy ulang ke `claude-memory/` lalu commit
(auto-commit 16:15 akan otomatis push-kan kalau sudah ke-copy sebelum jam
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
