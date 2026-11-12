# Auto-commit & push kode/dokumen proyek Undercover ke GitHub tiap akhir hari kerja.
# Dijalankan otomatis oleh Windows Task Scheduler (task: Undercover-AutoCommitPush).
# Data besar (xlsx, gambar, banner, dll) TIDAK disentuh script ini - itu ditangani
# oleh sync real-time Google Drive for Desktop, bukan git.

# Lokasi repo diambil dari letak script ini (scripts\..), jadi jalan di device mana pun.
$repoPath = Split-Path -Parent $PSScriptRoot
# Task Scheduler kadang jalan dengan PATH lama (tanpa git) - tambahkan lokasi default Git for Windows.
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { $env:Path += ";C:\Program Files\Git\cmd" }
$logFile = Join-Path $repoPath "auto-commit-log.txt"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

Set-Location $repoPath

# Ambil perubahan terbaru dulu, lalu sinkron memory dua arah dengan vault Obsidian lokal
# (lihat sync-vault-memory.ps1) supaya catatan sesi lokal ikut ter-push.
git pull --rebase --autostash origin main 2>&1 | Out-Null
& (Join-Path $PSScriptRoot "sync-vault-memory.ps1") -Mode both | Out-Null
# Skill Claude e-commerce: ~\.claude\skills\undercover-ecommerce-ops <-> .claude\skills\ di repo (lihat sync-skill.ps1).
& (Join-Path $PSScriptRoot "sync-skill.ps1") -Mode both | Out-Null

$status = git status --porcelain
if ([string]::IsNullOrWhiteSpace($status)) {
    Add-Content -Path $logFile -Value "$timestamp - Tidak ada perubahan, lewati commit."
    exit 0
}

git add -A
$commitMsg = "Auto-commit akhir hari kerja $(Get-Date -Format 'yyyy-MM-dd')"
git commit -m $commitMsg | Out-Null

# Sesi Claude lain (cloud/device lain) juga push ke main - ambil dulu supaya push tidak ditolak.
$pullOutput = git pull --rebase origin main 2>&1
if ($LASTEXITCODE -ne 0) {
    git rebase --abort 2>&1 | Out-Null
    Add-Content -Path $logFile -Value "$timestamp - GAGAL pull (commit lokal tetap ada, push manual). Detail: $pullOutput"
    exit 1
}

$pushOutput = git push origin main 2>&1
if ($LASTEXITCODE -eq 0) {
    Add-Content -Path $logFile -Value "$timestamp - Commit & push berhasil: $commitMsg"
} else {
    Add-Content -Path $logFile -Value "$timestamp - GAGAL push. Detail: $pushOutput"
}
