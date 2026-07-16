param(
    [string]$Destination
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$RepositoryRoot = Split-Path -Parent $PSScriptRoot
if (-not $Destination) {
    $Destination = Join-Path $RepositoryRoot "sources\upstream"
}
$ManifestPath = Join-Path $RepositoryRoot "sources\manifest.json"
$Manifest = Get-Content -Raw -LiteralPath $ManifestPath | ConvertFrom-Json
$Downloaded = Join-Path $Destination "downloaded"
$Extracted = Join-Path $Destination "extracted"
New-Item -ItemType Directory -Force -Path $Destination, $Downloaded, $Extracted | Out-Null

foreach ($SourceRepository in $Manifest.repositories) {
    $Target = Join-Path $Destination $SourceRepository.name
    if (-not (Test-Path -LiteralPath (Join-Path $Target ".git"))) {
        git clone $SourceRepository.url $Target
    }
    git -C $Target fetch --all --tags
    git -C $Target checkout --detach $SourceRepository.commit
    $ActualCommit = git -C $Target rev-parse HEAD
    if ($ActualCommit.Trim() -ne $SourceRepository.commit) {
        throw "Commit verification failed for $($SourceRepository.name)"
    }
}

foreach ($SourceFile in $Manifest.files) {
    $Target = Join-Path $Downloaded $SourceFile.name
    if (-not (Test-Path -LiteralPath $Target)) {
        Invoke-WebRequest -Uri $SourceFile.url -OutFile $Target
    }
    $ActualHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $Target).Hash
    if ($ActualHash -ne $SourceFile.sha256) {
        throw "SHA256 verification failed for $($SourceFile.name)"
    }
    if ([IO.Path]::GetExtension($Target) -eq ".zip") {
        $FolderName = [IO.Path]::GetFileNameWithoutExtension($Target)
        $ExtractTarget = Join-Path $Extracted $FolderName
        if (-not (Test-Path -LiteralPath $ExtractTarget)) {
            Expand-Archive -LiteralPath $Target -DestinationPath $ExtractTarget
        }
    }
}

Write-Host "Pinned sources are present and verified under $Destination"
