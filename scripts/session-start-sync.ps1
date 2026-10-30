# Dipanggil hook SessionStart Claude Code di vault Obsidian lokal:
# tarik update repo dari GitHub, lalu salin memory yang lebih baru dari claude-memory/ ke vault.
# Selalu keluar dengan kode 0 supaya kegagalan (mis. offline) tidak mengganggu sesi.

if (-not (Get-Command git -ErrorAction SilentlyContinue)) { $env:Path += ";C:\Program Files\Git\cmd" }
$repoPath = Split-Path -Parent $PSScriptRoot
Set-Location $repoPath
git pull --rebase --autostash origin main 2>&1 | Out-Null
$changes = & (Join-Path $PSScriptRoot "sync-vault-memory.ps1") -Mode pull
if ($changes) { "Sinkron memory dari repo: " + ($changes -join "; ") }
exit 0
