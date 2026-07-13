# Setup 2 Komputer (Marketing + E-commerce) — Satu Akun Claude

Dokumen ini menjelaskan cara memakai proyek Undercover di **2 komputer sekaligus**
dengan **akun Claude yang sama**, tapi tetap menjaga konteks (memory) tiap PC
terpisah supaya tidak tercampur.

## Pembagian tugas

| PC | Fungsi | Folder project yang dibuka di Claude Code |
|----|--------|-------------------------------------------|
| **PC 1** | Digital Marketing (social media & website) | `Undercover/marketing/` |
| **PC 2** | E-commerce (SKU Sync, Shopee monitor, katalog) | `Undercover/` (root repo) |

Keduanya login akun Claude yang sama dan pakai **1 repo GitHub yang sama**
(`undercover-claude`) — hanya membuka **subfolder yang berbeda** sebagai project
root Claude Code.

## Kenapa subfolder, bukan 2 repo?

Memory Claude Code di-scope **per path folder project**, bukan per akun login.
Setiap folder project punya namespace memory sendiri di
`~/.claude/projects/<hash-path-folder>/memory/`. Karena `Undercover/marketing/`
dan `Undercover/` (root) adalah path yang berbeda, keduanya otomatis dapat
namespace memory yang **terpisah** — jadi:

- Memory e-commerce (aturan SKU, status tiap toko) **tidak** bocor ke sesi marketing.
- Memory marketing (nada brand, kalender konten, dsb) **tidak** bocor ke sesi e-commerce.

Sekaligus, karena masih **1 repo / 1 clone**, cukup **satu** `git pull`/`git push`
dan **satu** task auto-commit untuk sinkronkan kedua sisi — lebih hemat daripada
mengurus 2 repo terpisah.

> **PENTING (PC 1 / Marketing):** buka folder **`Undercover/marketing/`** sebagai
> project root di Claude Code — **bukan** folder `Undercover/` root. Kalau salah
> buka root, Claude akan memuat memory e-commerce, bukan marketing.

## Langkah singkat per PC

### PC 2 — E-commerce (yang sudah ada sekarang)
Tidak ada perubahan. Tetap ikuti [`SETUP-DEVICE-BARU.md`](SETUP-DEVICE-BARU.md)
dan buka folder `Undercover/` root seperti biasa. Memory e-commerce tetap di
[`claude-memory/`](claude-memory/) (root).

### PC 1 — Marketing (komputer baru ini)
1. Clone repo yang sama (kalau belum):
   ```
   git clone https://github.com/undercovermobil-bot/undercover-claude.git "Undercover"
   ```
2. Buka folder **`Undercover/marketing/`** di Claude Code sebagai project root.
3. Ikuti [`marketing/SETUP-DEVICE-BARU.md`](marketing/SETUP-DEVICE-BARU.md) untuk
   restore memory marketing + sync aset besar dari Google Drive.

## Google Drive (aset besar)

Tetap 1 akun Drive (`under.covermobil@gmail.com`), tapi **pisahkan folder** aset
besar per fungsi supaya rapi:

- Folder Drive **e-commerce** (xlsx katalog, foto produk) — sudah ada, lihat
  `SETUP-DEVICE-BARU.md`.
- Folder Drive **marketing** (video, banner, aset brand) — buat folder baru,
  mis. `Undercover/Marketing`, dan hubungkan lewat Google Drive for Desktop.

Aset besar tetap **tidak** masuk git (lihat [`.gitignore`](.gitignore)) — sama
seperti sisi e-commerce.

## Sinkronisasi git (berlaku untuk kedua PC)

Karena 1 repo, alurnya sama seperti biasa — `git pull` sebelum kerja, commit &
push sesudah. Auto-commit harian (Windows Task Scheduler, lihat Langkah 4 di
`SETUP-DEVICE-BARU.md`) yang jalan di PC mana pun akan meng-commit **seluruh isi
repo**, termasuk folder `marketing/`, jadi cukup satu task saja. Kalau kedua PC
sama-sama aktif, biasakan `git pull` dulu sebelum mulai supaya tidak bentrok.
