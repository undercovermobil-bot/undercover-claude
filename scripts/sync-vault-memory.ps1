# Sinkron memory e-commerce antara vault Obsidian (lokal) dan folder claude-memory/ di repo ini.
# Hanya file project-undercover-*, feedback-undercover-*, user-undercover-* yang disinkron;
# catatan lain di vault (chat, digital marketing, dll) tidak pernah masuk repo.
#
#   -Mode pull : repo -> vault saja (dipakai saat sesi Claude lokal dimulai)
#   -Mode both : dua arah (dipakai auto-commit-push.ps1 sebelum commit)
#
# Cara kerja: hash tiap file saat sinkron terakhir disimpan di <vault>\.claude-sync-state.json.
# Sisi yang berubah sejak sinkron terakhir menang. Kalau dua sisi sama-sama berubah, versi
# vault dipertahankan dan versi repo disimpan ke "00 Inbox\KONFLIK <nama>" untuk dicek manual.
# File yang dihapus di salah satu sisi TIDAK ikut dihapus di sisi lain.

param(
    [ValidateSet("pull", "both")] [string]$Mode = "both",
    [string]$VaultPath = (Join-Path $env:USERPROFILE "Documents\Undercover Claude")
)

$repoPath = Split-Path -Parent $PSScriptRoot
$memDir = Join-Path $repoPath "claude-memory"
$statePath = Join-Path $VaultPath ".claude-sync-state.json"
$logFile = Join-Path $repoPath "auto-commit-log.txt"
$utf8 = New-Object System.Text.UTF8Encoding $false
$patterns = "project-undercover-*.md", "feedback-undercover-*.md", "user-undercover-*.md"
# Folder tujuan di vault untuk file baru dari repo
$defaultDir = @{ "project" = "10 Projects\Undercover"; "feedback" = "30 Knowledge"; "user" = "40 Bisnis" }

function Get-NormText($path) { ([IO.File]::ReadAllText($path) -replace "`r`n", "`n").TrimEnd() }
function Get-NormHash($path) {
    $bytes = $utf8.GetBytes((Get-NormText $path))
    [BitConverter]::ToString([Security.Cryptography.SHA256]::Create().ComputeHash($bytes)).Replace("-", "")
}
function Write-Log($msg) { Add-Content -Path $logFile -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - sync: $msg" }

if (-not (Test-Path $VaultPath)) { Write-Log "vault tidak ditemukan ($VaultPath), lewati."; exit 0 }

$state = @{}
if (Test-Path $statePath) {
    (Get-Content -Raw $statePath | ConvertFrom-Json).PSObject.Properties | ForEach-Object { $state[$_.Name] = $_.Value }
}

# Kumpulkan file per nama di kedua sisi (vault: abaikan arsip, template, inbox)
$repoFiles = @{}
foreach ($p in $patterns) { Get-ChildItem $memDir -Filter $p -File | ForEach-Object { $repoFiles[$_.Name] = $_.FullName } }
$vaultFiles = @{}
foreach ($p in $patterns) {
    Get-ChildItem $VaultPath -Recurse -Filter $p -File |
        Where-Object { $_.FullName -notmatch '\\(99 Archive|90 Templates|00 Inbox)\\' } |
        ForEach-Object { if (-not $vaultFiles.ContainsKey($_.Name)) { $vaultFiles[$_.Name] = $_.FullName } }
}

$changes = @()
$newInRepo = @()
foreach ($name in (@($repoFiles.Keys) + @($vaultFiles.Keys) | Sort-Object -Unique)) {
    $r = $repoFiles[$name]; $v = $vaultFiles[$name]
    $hr = if ($r) { Get-NormHash $r }; $hv = if ($v) { Get-NormHash $v }

    if ($r -and -not $v) {
        $dir = Join-Path $VaultPath $defaultDir[$name.Split("-")[0]]
        New-Item -ItemType Directory -Force $dir | Out-Null
        Copy-Item $r (Join-Path $dir $name)
        $state[$name] = $hr; $changes += "repo->vault BARU $name"; continue
    }
    if ($v -and -not $r) {
        if ($Mode -eq "pull") { continue }
        Copy-Item $v (Join-Path $memDir $name)
        $state[$name] = $hv; $changes += "vault->repo BARU $name"; $newInRepo += $name; continue
    }
    if ($hr -eq $hv) { $state[$name] = $hr; continue }

    # Belum pernah disinkron: anggap versi repo sebagai titik awal
    $base = if ($state.ContainsKey($name)) { $state[$name] } else { $hr }
    $repoChanged = $hr -ne $base; $vaultChanged = $hv -ne $base

    if ($repoChanged -and -not $vaultChanged) {
        Copy-Item $r $v -Force; $state[$name] = $hr; $changes += "repo->vault $name"
    } elseif ($vaultChanged -and -not $repoChanged) {
        if ($Mode -eq "pull") { continue }
        Copy-Item $v $r -Force; $state[$name] = $hv; $changes += "vault->repo $name"
    } else {
        $inbox = Join-Path $VaultPath "00 Inbox"
        New-Item -ItemType Directory -Force $inbox | Out-Null
        Copy-Item $r (Join-Path $inbox "KONFLIK $(Get-Date -Format 'yyyy-MM-dd') $name") -Force
        $changes += "KONFLIK $name (versi repo disimpan di 00 Inbox, vault dipertahankan)"
    }
}

# File baru dari vault juga didaftarkan di indeks claude-memory/MEMORY.md
$indexPath = Join-Path $memDir "MEMORY.md"
foreach ($name in $newInRepo) {
    $text = Get-NormText (Join-Path $memDir $name)
    $desc = if ($text -match '(?m)^description:\s*"?(.+?)"?\s*$') { $Matches[1] } elseif ($text -match '(?m)^#\s+(.+)$') { $Matches[1] } else { $name }
    # [char]0x2014 = tanda pisah panjang, ditulis begini supaya file .ps1 tetap ASCII (PowerShell 5.1)
    Add-Content -Path $indexPath -Value "- [$($name -replace '\.md$','')]($name) $([char]0x2014) $desc" -Encoding UTF8
}

$json = $state | ConvertTo-Json
[IO.File]::WriteAllText($statePath, $json, $utf8)
if ($changes.Count -gt 0) { Write-Log ($changes -join "; ") }
$changes
