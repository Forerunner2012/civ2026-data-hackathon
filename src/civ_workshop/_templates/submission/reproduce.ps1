param(
    [Parameter(Mandatory = $true)]
    [string]$Dataset
)

$Workspace = Split-Path -Parent $MyInvocation.MyCommand.Path
civ detect (Join-Path $Workspace "detector/detector.yaml") $Dataset --output $Workspace
