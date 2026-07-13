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

1. Install Google Drive for Desktop, login dengan akun yang punya akses ke
   folder Undercover di atas.
2. Sync/mirror folder tersebut, lalu pastikan isinya (`List Produk SKU`,
   `Banner`, `Otonation`, `Otopro`, `Smartpro`, `Undercover`, dsb) ada
   berdampingan dengan folder hasil clone git di langkah 1 — idealnya
   digabung jadi satu folder `Undercover` yang sama supaya path yang
   direferensikan di memory Claude tetap cocok.

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

## Alur kerja harian singkat

```
git pull                 # ambil update kode/dokumen terbaru
# ...kerja seperti biasa, data besar otomatis sinkron lewat Google Drive...
git add -A
git commit -m "..."
git push                 # kirim update kode/dokumen
```
