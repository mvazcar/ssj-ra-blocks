param(
    [string]$SourceRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$RepositoryRoot = Split-Path -Parent $PSScriptRoot
if (-not $SourceRoot) {
    $SourceRoot = Join-Path $RepositoryRoot "sources\upstream"
}

$ManifestPath = Join-Path $RepositoryRoot "sources\manifest.json"
$Manifest = Get-Content -Raw -LiteralPath $ManifestPath | ConvertFrom-Json
$Downloaded = Join-Path $SourceRoot "downloaded"

foreach ($SourceRepository in $Manifest.repositories) {
    $Target = Join-Path $SourceRoot $SourceRepository.name
    if (-not (Test-Path -LiteralPath (Join-Path $Target ".git"))) {
        throw "Missing repository: $($SourceRepository.name)"
    }
    $ActualCommit = (git -C $Target rev-parse HEAD).Trim()
    if ($ActualCommit -ne $SourceRepository.commit) {
        throw (
            "Commit mismatch for $($SourceRepository.name): " +
            "expected $($SourceRepository.commit), found $ActualCommit"
        )
    }
}

foreach ($SourceFile in $Manifest.files) {
    $Target = Join-Path $Downloaded $SourceFile.name
    if (-not (Test-Path -LiteralPath $Target)) {
        throw "Missing source file: $($SourceFile.name)"
    }
    $ActualHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $Target).Hash
    if ($ActualHash -ne $SourceFile.sha256) {
        throw (
            "SHA256 mismatch for $($SourceFile.name): " +
            "expected $($SourceFile.sha256), found $ActualHash"
        )
    }
}

Write-Host "All pinned source commits and file checksums are valid under $SourceRoot"
