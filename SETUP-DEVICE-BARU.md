# Setup Undercover di Device Baru

Panduan ini untuk menyalakan proyek Undercover (SKU Sync, Shopee Price Monitor, dll)
di komputer/akun Claude baru, lengkap dengan konteks memory yang sudah dipelajari
Claude sebelumnya.

Proyek ini dipecah ke 2 tempat penyimpanan:

- **GitHub (privat)** — kode `.py`, dokumen `.md`/`.docx` kecil, dan snapshot memory Claude.
  Repo: https://github.com/undercovermobil-bot/undercover-claude
- **Google Drive** — semua data besar: `.xlsx` katalog/SKU, foto, banner, video, file zip export.
  Folder: https://drive.google.com/drive/folders/168snWOIoROx-isBH3DWdECwSiYVgFHqK

Keduanya perlu digabung lagi di device baru supaya Claude bisa kerja normal.

## Langkah 1 — Clone repo dari GitHub

```
git clone https://github.com/undercovermobil-bot/undercover-claude.git "Undercover"
```

Taruh di lokasi yang sama dengan device lama kalau bisa, misalnya
`Documents\Undercover`, biar konsisten.

## Langkah 2 — Sync data besar dari Google Drive

Data besar (xlsx, banner, foto, zip) **tidak ada di GitHub** — itu sengaja
(lihat `.gitignore`) karena file-file itu terlalu besar/binary untuk git.
Datanya ada di Google Drive: https://drive.google.com/drive/folders/168snWOIoROx-isBH3DWdECwSiYVgFHqK
(folder "Claude", akun `under.covermobil@gmail.com`).

**Catatan: upload/download data besar ini harus manual** (drag-and-drop atau
lewat Google Drive for Desktop) — Claude tidak bisa upload file besar secara
otomatis lewat chat/API, sudah dicoba dan mentok di batas ukuran konten per
panggilan tool bahkan untuk file kecil sekalipun (lihat riwayat percakapan
2026-07-13). Jadi transfer data besar selalu perlu dilakukan manual oleh
manusia, baik di setup awal maupun kalau butuh restore ulang.

Cara setup:

1. Install Google Drive for Desktop, login dengan akun yang punya akses ke
   folder Undercover di atas (`under.covermobil@gmail.com`).
2. **Opsi cepat (sekali jalan):** buka folder Drive itu di browser, lalu
   drag folder-folder ini dari File Explorer ke jendela browser:
   `List Produk SKU`, `Banner`, `Otonation`, `Otopro`, `Smartpro`, `Undercover`.
3. **Opsi auto-sync berkelanjutan (direkomendasikan):** di Google Drive for
   Desktop, aktifkan fitur **"Back up folder from computer"** dan pilih
   folder-folder data di atas. Dengan ini, setiap kali file di-edit/di-save,
   otomatis ke-upload ke Drive real-time — tidak perlu dijadwalkan, beda
   dengan git yang butuh commit diskrit (lihat Langkah 4).
4. Pastikan hasil sync-nya berdampingan dengan folder hasil clone git di
   langkah 1 — idealnya digabung jadi satu folder `Undercover` yang sama
   supaya path yang direferensikan di memory Claude tetap cocok.

## Langkah 3 — Restore memory Claude

Folder [`claude-memory/`](claude-memory/) di repo ini adalah salinan dari memory
Claude (isi `MEMORY.md` + semua file `*.md` pendukung) per tanggal commit terakhir.
Ini yang membuat Claude "ingat" aturan SKU, status tiap toko, dan pelajaran dari
sesi-sesi sebelumnya tanpa perlu diulang dari nol.

Di device baru:

1. Buka Claude Code di folder project ini (`Undercover`) minimal sekali —
   ini akan otomatis membuat folder memory kosong di:
   `~/.claude/projects/<hash-folder-project>/memory/`
   (nama persis folder `<hash-folder-project>` tergantung path lengkap
   project di device itu — biasanya nama path dengan `/` diganti `-`).
2. Salin **isi** folder `claude-memory/` dari repo ini ke folder memory
   yang baru terbentuk itu (timpa `MEMORY.md` kosong dengan yang dari repo).
3. Mulai sesi baru — Claude akan otomatis membaca `MEMORY.md` dan
   konteks lama langsung tersedia.

## Menjaga memory tetap sinkron ke depan

Setiap kali Claude menyimpan memory baru/update di satu device, jalankan ini
sesekali (atau minta Claude melakukannya) supaya device lain ikut update:

```
# dari folder project Undercover
cp ~/.claude/projects/<hash-folder-project>/memory/*.md claude-memory/
git add claude-memory/
git commit -m "Update snapshot memory Claude"
git push
```

Lalu di device lain, `git pull` dan salin ulang isi `claude-memory/` ke folder
memory lokalnya (langkah 3 di atas).

## Langkah 4 — (Opsional) Auto-commit & push harian

Di device utama (per 2026-07-13: PC Windows ini), sudah ada Windows Task
Scheduler task bernama **`Undercover-AutoCommitPush`** yang menjalankan
[`scripts/auto-commit-push.ps1`](scripts/auto-commit-push.ps1) tiap hari jam
**16:15** (15 menit setelah jam kerja terakhir user, 16:00). Task ini:

- Cek apakah ada perubahan (`git status --porcelain`) — kalau tidak ada,
  langsung berhenti tanpa commit kosong.
- Kalau ada, otomatis `git add -A` + commit dengan pesan
  `Auto-commit akhir hari kerja <tanggal>` + `git push origin main`.
- Catat hasilnya (berhasil/gagal) ke `auto-commit-log.txt` di root repo
  (file ini sengaja di-`.gitignore`, jadi hanya ada lokal).

**Syarat supaya jalan:** device harus **hidup & login** jam 16:15 (Task
Scheduler tidak bisa menyalakan PC dari kondisi mati total, tapi task ini
sudah diset `WakeToRun` — bisa membangunkan dari sleep — dan
`StartWhenAvailable` — kalau jam 16:15 PC lagi mati, task akan otomatis
jalan begitu PC berikutnya menyala).

Kalau mau setup task yang sama di device lain, jalankan ini di PowerShell
(sesuaikan `$repoPath` dan jam kalau perlu):

```powershell
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument '-NoProfile -ExecutionPolicy Bypass -File "<path-ke-repo>\scripts\auto-commit-push.ps1"'
$trigger = New-ScheduledTaskTrigger -Daily -At 16:15
$settings = New-ScheduledTaskSettingsSet -WakeToRun -StartWhenAvailable -DontStopOnIdleEnd
Register-ScheduledTask -TaskName "Undercover-AutoCommitPush" -Action $action -Trigger $trigger -Settings $settings -Description "Auto commit+push proyek Undercover ke GitHub tiap akhir hari kerja"
```

(Ingat sesuaikan path `$repoPath` di dalam `auto-commit-push.ps1` itu sendiri
juga kalau lokasi repo di device itu berbeda.)

Data besar tidak perlu automation git karena sudah ditangani real-time oleh
Google Drive for Desktop (lihat Langkah 2, opsi "Back up folder from computer").

## Alur kerja harian singkat

```
git pull                 # ambil update kode/dokumen terbaru
# ...kerja seperti biasa, data besar otomatis sinkron real-time lewat Google Drive...
# ...git add/commit/push otomatis tiap 16:15 lewat Task Scheduler (Langkah 4)...
# atau manual kapan saja:
git add -A
git commit -m "..."
git push
```
