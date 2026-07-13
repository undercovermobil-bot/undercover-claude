# Auto-commit & push kode/dokumen proyek Undercover ke GitHub tiap akhir hari kerja.
# Dijalankan otomatis oleh Windows Task Scheduler (task: Undercover-AutoCommitPush).
# Data besar (xlsx, gambar, banner, dll) TIDAK disentuh script ini - itu ditangani
# oleh sync real-time Google Drive for Desktop, bukan git.

$repoPath = "C:\Users\chand\Documents\Undercover"
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

$pushOutput = git push origin main 2>&1
if ($LASTEXITCODE -eq 0) {
    Add-Content -Path $logFile -Value "$timestamp - Commit & push berhasil: $commitMsg"
} else {
    Add-Content -Path $logFile -Value "$timestamp - GAGAL push. Detail: $pushOutput"
}
