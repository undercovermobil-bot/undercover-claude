# Proyek Undercover — Konteks untuk Claude

Bahasa respons: **selalu Bahasa Indonesia** (instruksi eksplisit user, 2026-07-09), kecuali kode/SKU/nama variabel yang memang berformat teknis.

## Apa proyek ini

Pemeliharaan katalog produk bisnis cover mobil dengan 4 toko — **Undercover Autocare (UA)**, **Otonation (OT)**, **Otoprotection (OP)**, **Smartprotection (SP)** — di Shopee/TikTok/Lazada. User mengelola ini lintas beberapa akun/device Claude berbeda (bukan 1 sesi berkelanjutan), jadi folder `claude-memory/` di repo ini **adalah snapshot manual** dari memory asli Claude di tiap device (`~/.claude/projects/<hash>/memory/*.md`) — lihat `SETUP-DEVICE-BARU.md` untuk cara restore/sync-nya.

**Sebelum kerja apa pun di proyek ini, baca dulu:**
- [`claude-memory/MEMORY.md`](claude-memory/MEMORY.md) — indeks semua file memory, baca ini duluan
- [`claude-memory/user-undercover-profile.md`](claude-memory/user-undercover-profile.md) — profil & preferensi user
- [`claude-memory/project-undercover-overview.md`](claude-memory/project-undercover-overview.md) — peta sub-proyek + cara verifikasi lokasi file

Tiga sub-proyek:
1. **SKU Sync** (utama) — samakan SKU semua listing ke 1 master. Aturan bisnis final: [`claude-memory/project-undercover-sku-sync-rules.md`](claude-memory/project-undercover-sku-sync-rules.md) — **7 aturan sudah divalidasi berkali-kali, jangan didesain ulang tanpa instruksi eksplisit baru.** Status per toko: `project-undercover-sku-sync-status.md`, `-otonation-status.md`, `-otoprotection-status.md`, `-smartprotection-status.md`. Pelajaran/pola bug berulang: [`claude-memory/feedback-undercover-sku-sync-lessons.md`](claude-memory/feedback-undercover-sku-sync-lessons.md) — **wajib dibaca sebelum investigasi SKU**, banyak jebakan (false positive deteksi bug, skema tier ganda, dll).
2. **Shopee Price Monitor** — mandek karena anti-bot Shopee, sudah pivot ke Apify actor. Detail: `claude-memory/project-undercover-shopee-antibot.md`.
3. **Audit Foto Produk** — selesai 2026-07-06. Detail: `claude-memory/project-undercover-photo-shopee-audit.md`.

## Aturan kerja penting (jangan dilanggar)

- **JANGAN edit file listing/master asli langsung** (sejak 2026-07-10). Selalu copy dulu ke `Export Undercover ke Akun Claude Lain/List Produk SKU/Update via Claude/` (mirror struktur asli), edit copy-nya di sana. Detail: [`claude-memory/feedback-undercover-update-folder-workflow.md`](claude-memory/feedback-undercover-update-folder-workflow.md).
- **Data besar (xlsx, foto, banner, zip) TIDAK ada di git** — sengaja di-`.gitignore`, hidup di Google Drive (akun `under.covermobil@gmail.com`). Jangan coba upload file besar lewat tool/MCP — sudah terbukti gagal (mentok batas ukuran konten). Transfer besar selalu manual oleh user.
- **Sebelum menyarankan setup git/Drive/scheduler baru**, cek dulu yang sudah ada — lihat [`claude-memory/project-undercover-git-drive-setup.md`](claude-memory/project-undercover-git-drive-setup.md). Auto-commit harian sudah jalan via Task Scheduler jam 16:15.
- **Jangan asumsikan path file dari memory/dokumen lama masih benar** — struktur folder bisa berubah antar sesi/export. Glob langsung di sesi berjalan sebelum menyimpulkan file ada/hilang.
- Pertanyaan spot-check user soal 1 produk spesifik ("kenapa produk X begini?") historisnya sering membongkar bug sistemik besar — perlakukan sebagai sinyal investigasi menyeluruh, bukan pertanyaan sepele.

## Menjaga memory tetap sinkron

Kalau kamu (Claude) menyimpan/mengupdate memory native selama sesi ini, salin ke `claude-memory/` dan commit supaya device/sesi lain (termasuk sesi cloud tanpa folder memory native) ikut dapat konteksnya:

```
cp ~/.claude/projects/<hash-folder-project>/memory/*.md claude-memory/
git add claude-memory/
git commit -m "Update snapshot memory Claude"
git push
```

Lihat `SETUP-DEVICE-BARU.md` untuk detail lengkap alur restore/sync memory dan setup device baru.
