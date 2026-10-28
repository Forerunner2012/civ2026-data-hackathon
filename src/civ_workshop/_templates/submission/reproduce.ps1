param(
    [Parameter(Mandatory = $true)]
    [string]$Dataset,
    [string]$PracticeLabels = "-",
    [string]$NewOutput
)

$ErrorActionPreference = "Stop"
$Workspace = Split-Path -Parent $MyInvocation.MyCommand.Path
$Dataset = (Resolve-Path -LiteralPath $Dataset).Path
if ($PracticeLabels -ne "-") {
    $PracticeLabels = (Resolve-Path -LiteralPath $PracticeLabels).Path
}
$Destination = $Workspace
if ($NewOutput) {
    $Destination = [System.IO.Path]::GetFullPath($NewOutput)
    if (Test-Path -LiteralPath $Destination) { throw "Choose a new output directory." }
    New-Item -ItemType Directory -Path $Destination | Out-Null
    Copy-Item -LiteralPath (Join-Path $Workspace "detector") -Destination $Destination -Recurse
    if (Test-Path -LiteralPath (Join-Path $Workspace "extension")) {
        Copy-Item -LiteralPath (Join-Path $Workspace "extension") -Destination $Destination -Recurse
    }
    Get-ChildItem -LiteralPath $Workspace -File | Where-Object {
        $_.Name -in @("report.md", "reproduce.ps1") -or
        $_.Extension.ToLowerInvariant() -in @(".svg", ".png", ".jpg", ".jpeg", ".webp")
    } | Copy-Item -Destination $Destination
}

civ detect (Join-Path $Destination "detector/detector.yaml") $Dataset --output $Destination
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
civ clip (Join-Path $Destination "events.jsonl") $Dataset
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
if ($PracticeLabels -eq "-") {
    civ score $Destination
} else {
    civ score $Destination --labels $PracticeLabels
}
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
civ report $Destination
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
