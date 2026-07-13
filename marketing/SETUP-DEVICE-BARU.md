# Setup Marketing di Device Baru (PC 1)

Panduan menyalakan sisi **Digital Marketing** (social media & website) di komputer
baru, lengkap dengan konteks memory Claude khusus marketing.

> Baca dulu [`../SETUP-MULTI-PC.md`](../SETUP-MULTI-PC.md) untuk gambaran besar
> kenapa marketing & e-commerce dipisah per subfolder tapi tetap 1 repo.

Penyimpanan dipecah ke 2 tempat (sama polanya dengan e-commerce):

- **GitHub (privat)** — teks kecil: draft `.md`, copy, catatan, snapshot memory Claude.
  Repo: https://github.com/undercovermobil-bot/undercover-claude (folder `marketing/`)
- **Google Drive** — aset besar: video, banner, gambar, file desain.
  Buat folder Drive khusus marketing, mis. `Undercover/Marketing`
  (akun `under.covermobil@gmail.com`).

## Langkah 1 — Clone repo dari GitHub

Kalau di device ini belum ada clone-nya:

```
git clone https://github.com/undercovermobil-bot/undercover-claude.git "Undercover"
```

Lalu **buka folder `Undercover/marketing/`** di Claude Code sebagai project root
(bukan folder root `Undercover/`).

## Langkah 2 — Sync aset besar dari Google Drive

Aset besar (video, banner, gambar, desain) **tidak ada di GitHub** — sengaja
(lihat `.gitignore` di root repo) karena terlalu besar/binary untuk git.

**Catatan: upload/download aset besar harus manual** (drag-and-drop atau lewat
Google Drive for Desktop). Claude tidak bisa upload file besar otomatis lewat
chat/API (sudah terbukti mentok di batas ukuran konten per panggilan tool).

Cara setup:

1. Install Google Drive for Desktop, login dengan `under.covermobil@gmail.com`.
2. Buat/siapkan folder Drive khusus marketing (mis. `Undercover/Marketing`).
3. Aktifkan **"Back up folder from computer"** untuk folder aset marketing lokal
   supaya tiap file di-save otomatis ke-upload real-time.
4. Pastikan hasil sync-nya berdampingan dengan folder `marketing/` hasil clone git,
   supaya path yang direferensikan di memory Claude tetap cocok.

## Langkah 3 — Restore memory Claude (khusus marketing)

Folder [`claude-memory/`](claude-memory/) di sini adalah snapshot memory Claude
untuk sisi marketing — **terpisah** dari `claude-memory/` root (yang punya e-commerce).

Di device baru:

1. Buka Claude Code di folder **`Undercover/marketing/`** minimal sekali — ini
   otomatis membuat folder memory kosong di
   `~/.claude/projects/<hash-path-marketing>/memory/`.
   (`<hash-path-marketing>` diturunkan dari path lengkap folder `marketing/`,
   jadi otomatis beda dari namespace e-commerce.)
2. Salin **isi** folder `marketing/claude-memory/` ke folder memory yang baru
   terbentuk itu (timpa `MEMORY.md` kosong dengan yang dari repo).
3. Mulai sesi baru — Claude akan membaca `MEMORY.md` dan konteks marketing lama
   langsung tersedia.

## Menjaga memory tetap sinkron ke depan

Setiap kali Claude menyimpan/meng-update memory marketing di device ini, jalankan
sesekali (atau minta Claude melakukannya):

```
# dari folder Undercover/marketing
cp ~/.claude/projects/<hash-path-marketing>/memory/*.md claude-memory/
git add claude-memory/
git commit -m "Update snapshot memory marketing"
git push
```

Lalu di device lain: `git pull` dan salin ulang isi `marketing/claude-memory/` ke
folder memory lokalnya (Langkah 3).

## Langkah 4 — Auto-commit & push harian

Auto-commit repo ini (Windows Task Scheduler, lihat Langkah 4 di
[`../SETUP-DEVICE-BARU.md`](../SETUP-DEVICE-BARU.md)) meng-commit **seluruh isi
repo**, termasuk folder `marketing/`. Jadi kalau task itu sudah aktif di salah
satu PC, folder marketing **ikut ter-backup otomatis** — tidak perlu task
terpisah. Kalau mau task khusus di PC marketing ini, pakai script/instruksi yang
sama, cukup sesuaikan `$repoPath` ke lokasi clone di device ini.

## Alur kerja harian singkat

```
git pull                 # ambil update terbaru (termasuk perubahan dari PC e-commerce)
# ...kerja konten seperti biasa, aset besar otomatis sinkron lewat Google Drive...
# ...git add/commit/push otomatis lewat Task Scheduler, atau manual:
git add -A
git commit -m "..."
git push
```
