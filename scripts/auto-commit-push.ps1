# Auto-commit & push kode/dokumen proyek Undercover ke GitHub tiap akhir hari kerja.
# Dijalankan otomatis oleh Windows Task Scheduler (task: Undercover-AutoCommitPush).
# Data besar (xlsx, gambar, banner, dll) TIDAK disentuh script ini - itu ditangani
# oleh sync real-time Google Drive for Desktop, bukan git.

# Lokasi repo diambil dari letak script ini (scripts\..), jadi jalan di device mana pun.
$repoPath = Split-Path -Parent $PSScriptRoot
$logFile = Join-Path $repoPath "auto-commit-log.txt"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

Set-Location $repoPath

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
