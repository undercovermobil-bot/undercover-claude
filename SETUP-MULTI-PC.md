# Setup 2 Komputer (Marketing + E-commerce) — Satu Akun Claude

Proyek Undercover dipakai di **2 komputer** dengan **akun Claude yang sama**, tapi
sisi kerjanya dipisah ke **2 repo GitHub berbeda** supaya konteks (memory Claude)
tidak tercampur dan akses tiap sisi bisa dikelola sendiri.

## Pembagian

| PC | Fungsi | Repo GitHub | Folder yang dibuka di Claude Code |
|----|--------|-------------|-----------------------------------|
| **PC 1** | Digital Marketing (social media & website) | [`undercover-digital-marketing`](https://github.com/undercovermobil-bot/undercover-digital-marketing) | folder clone repo marketing |
| **PC 2** | E-commerce (SKU Sync, Shopee monitor, katalog) | `undercover-claude` (repo ini) | folder clone repo ini |

## Kenapa 2 repo terpisah?

Memory Claude Code di-scope **per path folder project**. Karena tiap PC membuka
folder clone repo yang berbeda, keduanya otomatis dapat namespace memory yang
**terpisah** — aturan SKU / katalog e-commerce tidak bocor ke sesi marketing, dan
sebaliknya. Selain itu, repo marketing yang berdiri sendiri memudahkan kalau nanti
mau memberi akses ke orang/tim marketing tanpa membuka data e-commerce.

## Setup per PC

- **PC 2 — E-commerce (repo ini):** ikuti [`SETUP-DEVICE-BARU.md`](SETUP-DEVICE-BARU.md).
- **PC 1 — Marketing:** ikuti `SETUP-DEVICE-BARU.md` di repo
  [`undercover-digital-marketing`](https://github.com/undercovermobil-bot/undercover-digital-marketing).

## Google Drive (aset besar)

Tetap 1 akun Drive (`under.covermobil@gmail.com`), tapi **pisahkan folder** aset
besar per sisi supaya rapi:

- Folder Drive **e-commerce** (xlsx katalog, foto produk) — lihat `SETUP-DEVICE-BARU.md`.
- Folder Drive **marketing** (video, banner, aset brand) — folder terpisah, mis.
  `Undercover/Marketing`.

Aset besar tidak masuk git di kedua repo (lihat masing-masing `.gitignore`).

## Sinkronisasi git

Karena 2 repo, tiap sisi punya alur git sendiri (`git pull` sebelum kerja, commit &
push sesudah) dan — kalau mau — task auto-commit hariannya masing-masing. Lihat
Langkah 4 di `SETUP-DEVICE-BARU.md` tiap repo.
