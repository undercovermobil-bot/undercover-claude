# Sinkron skill Claude "undercover-ecommerce-ops" antara folder skill lokal (~\.claude\skills) dan salinan di repo
# (.claude\skills\ di repo ini, supaya sesi cloud yang meng-clone repo ikut memakainya).
#
#   -Mode pull : repo -> lokal saja (dipakai saat sesi Claude lokal dimulai)
#   -Mode both : dua arah (dipakai auto-commit-push.ps1 sebelum commit)
#
# Cara kerja: hash tiap file (akhir baris dinormalkan) saat sinkron terakhir disimpan di file state.
# Sisi yang berubah sejak sinkron terakhir menang. Bila dua sisi sama-sama berubah, versi lokal dipertahankan dan
# versi repo disimpan di <skill lokal>\_conflicts\ untuk digabung manual. File yang dihapus TIDAK dipropagasi.
# __pycache__, *.pyc, dan folder _conflicts tidak ikut disinkron.
# Menyelesaikan konflik: gabungkan ke file LOKAL, salin file lokal itu ke salinan repo, lalu hapus folder _conflicts.

param(
    [ValidateSet("pull", "both")] [string]$Mode = "both",
    [string]$SkillName = "undercover-ecommerce-ops",
    [string]$LocalRoot = (Join-Path $env:USERPROFILE ".claude\skills"),
    [string]$RepoRoot = (Join-Path (Split-Path -Parent $PSScriptRoot) ".claude\skills"),
    [string]$StatePath = (Join-Path $env:USERPROFILE (".claude\.skill-sync-state-" + $SkillName + ".json")),
    [string]$LogFile = (Join-Path (Split-Path -Parent $PSScriptRoot) "auto-commit-log.txt")
)

$local = Join-Path $LocalRoot $SkillName
$remote = Join-Path $RepoRoot $SkillName
$logFile = $LogFile
$textExt = ".md", ".py", ".ps1", ".json", ".txt", ".yaml", ".yml"

function Write-Log($msg) { Add-Content -Path $logFile -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - skill-sync: $msg" }
function Get-Hash($path) {
    if ($textExt -contains [IO.Path]::GetExtension($path).ToLower()) {
        $bytes = [Text.Encoding]::UTF8.GetBytes(([IO.File]::ReadAllText($path) -replace "`r`n", "`n"))
    } else { $bytes = [IO.File]::ReadAllBytes($path) }
    [BitConverter]::ToString([Security.Cryptography.SHA256]::Create().ComputeHash($bytes)).Replace("-", "")
}
function Get-Files($root) {
    $h = @{}
    if (-not (Test-Path $root)) { return $h }
    Get-ChildItem $root -Recurse -File | Where-Object { $_.FullName -notmatch '\\(__pycache__|_conflicts)\\' -and $_.Extension -ne '.pyc' } |
        ForEach-Object { $h[$_.FullName.Substring($root.Length + 1)] = $_.FullName }
    $h
}

if (-not (Test-Path $local) -and -not (Test-Path $remote)) { exit 0 }
$state = @{}
if (Test-Path $StatePath) {
    (Get-Content -Raw $StatePath | ConvertFrom-Json).PSObject.Properties | ForEach-Object { $state[$_.Name] = $_.Value }
}
$lf = Get-Files $local; $rf = Get-Files $remote
$changes = @()
foreach ($key in (@($lf.Keys) + @($rf.Keys) | Sort-Object -Unique)) {
    $l = $lf[$key]; $r = $rf[$key]
    $lp = Join-Path $local $key; $rp = Join-Path $remote $key
    if ($l -and -not $r) {
        if ($Mode -eq "pull") { continue }
        New-Item -ItemType Directory -Force (Split-Path -Parent $rp) | Out-Null
        Copy-Item $l $rp -Force; $state[$key] = Get-Hash $l; $changes += "lokal->repo BARU $key"; continue
    }
    if ($r -and -not $l) {
        New-Item -ItemType Directory -Force (Split-Path -Parent $lp) | Out-Null
        Copy-Item $r $lp -Force; $state[$key] = Get-Hash $r; $changes += "repo->lokal BARU $key"; continue
    }
    $hl = Get-Hash $l; $hr = Get-Hash $r
    if ($hl -eq $hr) { $state[$key] = $hl; continue }
    $base = if ($state.ContainsKey($key)) { $state[$key] } else { $null }
    if ($null -eq $base) { $localChanged = $true; $repoChanged = $true }
    else { $localChanged = $hl -ne $base; $repoChanged = $hr -ne $base }
    if ($repoChanged -and -not $localChanged) {
        Copy-Item $r $lp -Force; $state[$key] = $hr; $changes += "repo->lokal $key"
    } elseif ($localChanged -and -not $repoChanged) {
        if ($Mode -eq "pull") { continue }
        Copy-Item $l $rp -Force; $state[$key] = $hl; $changes += "lokal->repo $key"
    } else {
        $dest = Join-Path $local ("_conflicts\" + $key)
        New-Item -ItemType Directory -Force (Split-Path -Parent $dest) | Out-Null
        Copy-Item $r $dest -Force
        $changes += "KONFLIK $key (versi repo disimpan di _conflicts, lokal dipertahankan)"
    }
}
New-Item -ItemType Directory -Force (Split-Path -Parent $StatePath) | Out-Null
[IO.File]::WriteAllText($StatePath, ($state | ConvertTo-Json), (New-Object System.Text.UTF8Encoding $false))
if ($changes.Count -gt 0) { Write-Log ($changes -join "; ") }
$changes
