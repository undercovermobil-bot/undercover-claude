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
3. **Opsi auto-sync berkelanjutan:** di Google Drive for Desktop, fitur
   **"Back up folder from computer"** SEHARUSNYA bikin folder itu ke-upload
   otomatis real-time tiap disave. **Tapi ini TIDAK terverifikasi jalan**
   (dicoba & gagal di PC utama 2026-07-15 — file yang diedit lokal jam 11:44
   & 13:57 masih belum naik ke Drive saat dicek jam ~14:00; ternyata
   kecocokan timestamp yang dikira "bukti auto-sync" sebelumnya cuma
   kebetulan dari upload manual sekali-jalan). **Jangan asumsikan folder ini
   auto-sync — selalu verifikasi dulu** (bandingkan size/timestamp file lokal
   vs `G:\My Drive\...`) sebelum mengandalkannya.
4. **Kalau auto-sync ternyata tidak aktif, solusi yang terbukti jalan:**
   Google Drive for Desktop biasanya me-mount Drive sebagai drive letter lokal
   (mis. `G:\My Drive\...`). Kalau Claude (atau siapa pun) punya akses
   terminal ke device itu, copy/tulis file **langsung ke path itu** (`cp`/
   `Copy-Item`, bukan drag-drop browser) — ini file I/O lokal biasa, BEDA
   mekanisme dari upload API/MCP yang gagal (lihat catatan di bawah), dan
   Drive Desktop yang mendeteksi + upload sendiri di background. Bisa
   diverifikasi naik ke cloud (bukan cuma ke mount lokal) dalam hitungan
   detik lewat Drive API/MCP tool `get_file_metadata`.
5. Pastikan hasil sync-nya berdampingan dengan folder hasil clone git di
   langkah 1 — idealnya digabung jadi satu folder `Undercover` yang sama
   supaya path yang direferensikan di memory Claude tetap cocok.

**Catatan tambahan (ditemukan 2026-07-15):** ada **DUA folder "List Produk
SKU"** berbeda di Drive akun ini — satu kanonik langsung di root folder
Drive di atas, satu lagi duplikat di dalam subfolder `Export Undercover ke
Akun Claude Lain\`. Duplikat ini muncul karena drag-and-drop browser (opsi
cepat di atas) tidak merge kalau folder tujuan sudah ada isinya, malah bikin
folder baru. Kerja sync SKU sepanjang Juli 2026 pakai folder yang **di dalam
`Export Undercover ke Akun Claude Lain\`** (itu yang punya subfolder `Update
via Claude\`). Kalau bingung file "hilang", cek dulu apa kamu lihat folder
kanonik yang stale atau folder aktif ini.

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
**15:45**. Task ini:

- Cek apakah ada perubahan (`git status --porcelain`) — kalau tidak ada,
  langsung berhenti tanpa commit kosong.
- Kalau ada, otomatis `git add -A` + commit dengan pesan
  `Auto-commit akhir hari kerja <tanggal>` + `git push origin main`.
- Catat hasilnya (berhasil/gagal) ke `auto-commit-log.txt` di root repo
  (file ini sengaja di-`.gitignore`, jadi hanya ada lokal).

**Syarat supaya jalan:** device harus **hidup & login** jam 15:45 (Task
Scheduler tidak bisa menyalakan PC dari kondisi mati total, tapi task ini
sudah diset `WakeToRun` — bisa membangunkan dari sleep — dan
`StartWhenAvailable` — kalau jam 15:45 PC lagi mati, task akan otomatis
jalan begitu PC berikutnya menyala).

Kalau mau setup task yang sama di device lain, jalankan ini di PowerShell
(sesuaikan `$repoPath` dan jam kalau perlu):

```powershell
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument '-NoProfile -ExecutionPolicy Bypass -File "<path-ke-repo>\scripts\auto-commit-push.ps1"'
$trigger = New-ScheduledTaskTrigger -Daily -At 15:45
$settings = New-ScheduledTaskSettingsSet -WakeToRun -StartWhenAvailable -DontStopOnIdleEnd
Register-ScheduledTask -TaskName "Undercover-AutoCommitPush" -Action $action -Trigger $trigger -Settings $settings -Description "Auto commit+push proyek Undercover ke GitHub tiap akhir hari kerja"
```

(Ingat sesuaikan path `$repoPath` di dalam `auto-commit-push.ps1` itu sendiri
juga kalau lokasi repo di device itu berbeda.)

Data besar tidak pakai automation git — tapi JANGAN asumsikan itu berarti
"tidak perlu apa-apa". Lihat Langkah 2 poin 3-4: verifikasi dulu apakah
Google Drive for Desktop auto-sync beneran aktif di device itu; kalau tidak,
perlu copy manual (atau minta Claude yang punya akses terminal device itu
copy) ke path `G:\My Drive\...` tiap ada perubahan data besar.

## Alur kerja harian singkat

```
git pull                 # ambil update kode/dokumen terbaru
# ...kerja data besar: cek dulu apa Drive folder ini auto-sync (Langkah 2
#    poin 3) — kalau tidak, copy manual ke G:\My Drive\... tiap selesai edit...
# ...git add/commit/push otomatis tiap 15:45 lewat Task Scheduler (Langkah 4)...
# atau manual kapan saja:
git add -A
git commit -m "..."
git push
```
