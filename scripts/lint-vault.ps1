# Lint vault Obsidian (pola "LLM Wiki"): cari tautan putus, catatan yatim, catatan yang belum
# terdaftar di 00 Home, dan catatan tanpa frontmatter. Hanya membaca, tidak mengubah apa pun.
#   .\lint-vault.ps1                -> cetak laporan
#   .\lint-vault.ps1 -Json          -> keluaran JSON (untuk diproses lagi)

param(
    [string]$VaultPath = (Join-Path $env:USERPROFILE "Documents\Undercover Claude"),
    [switch]$Json
)

$skipDirs = '\\(99 Archive|90 Templates|\.obsidian|\.claude)\\'
$files = Get-ChildItem $VaultPath -Recurse -Filter *.md -File | Where-Object { $_.FullName -notmatch $skipDirs }

# Peta nama (tanpa .md, huruf kecil) -> path
$byName = @{}
foreach ($f in $files) { $byName[$f.BaseName.ToLower()] = $f.FullName }
# Lampiran/arsip tetap dianggap target sah supaya tautan ke sana tidak ditandai putus
Get-ChildItem $VaultPath -Recurse -File | Where-Object { $_.FullName -match $skipDirs } |
    ForEach-Object { if (-not $byName.ContainsKey($_.BaseName.ToLower())) { $byName[$_.BaseName.ToLower()] = $_.FullName } }

$inbound = @{}; $broken = @(); $noFront = @()
foreach ($f in $files) {
    $text = [IO.File]::ReadAllText($f.FullName)
    if ($text -notmatch '^\s*---\s*\r?\n') { $noFront += $f.FullName.Replace($VaultPath + '\', '') }
    # buang blok kode dan kode inline supaya contoh [[...]] tidak dihitung
    $clean = [regex]::Replace($text, '(?s)```.*?```', '')
    $clean = [regex]::Replace($clean, '`[^`\n]*`', '')
    foreach ($m in [regex]::Matches($clean, '\[\[([^\]\|#\n]+)(?:[#\|][^\]\n]*)?\]\]')) {
        $target = $m.Groups[1].Value.Trim().ToLower()
        if ($byName.ContainsKey($target)) {
            if ($byName[$target] -ne $f.FullName) { $inbound[$target] = 1 + [int]$inbound[$target] }
        } else {
            $broken += [pscustomobject]@{ Dari = $f.FullName.Replace($VaultPath + '\', ''); Tautan = $m.Groups[1].Value.Trim() }
        }
    }
}

$homeText = Get-Content -Raw (Join-Path $VaultPath "00 Home.md") -ErrorAction SilentlyContinue
$skipOrphan = '^(00 home|claude)$'
$orphans = @(); $notInHome = @()
foreach ($f in $files) {
    $n = $f.BaseName.ToLower()
    if ($n -match $skipOrphan -or $f.FullName -match '\\(20 Chats|00 Inbox)\\') { continue }
    if (-not $inbound.ContainsKey($n)) { $orphans += $f.FullName.Replace($VaultPath + '\', '') }
    if ($homeText -notmatch [regex]::Escape("[[$($f.BaseName)")) { $notInHome += $f.FullName.Replace($VaultPath + '\', '') }
}

$result = [pscustomobject]@{
    Catatan = $files.Count
    TautanPutus = $broken
    Yatim = $orphans
    TidakDiHome = $notInHome
    TanpaFrontmatter = $noFront
}
if ($Json) { $result | ConvertTo-Json -Depth 4; exit 0 }

"Catatan diperiksa : $($files.Count)"
"Tautan putus      : $($broken.Count)"; $broken | ForEach-Object { "  $($_.Dari)  ->  [[$($_.Tautan)]]" }
"Yatim (tanpa tautan masuk): $($orphans.Count)"; $orphans | ForEach-Object { "  $_" }
"Ada tautan masuk tapi tidak di 00 Home: $($notInHome.Count)"; $notInHome | ForEach-Object { "  $_" }
"Tanpa frontmatter : $($noFront.Count)"; $noFront | ForEach-Object { "  $_" }
