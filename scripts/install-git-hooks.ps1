$ErrorActionPreference = 'Stop'
$root = git rev-parse --show-toplevel
$hooksDir = Join-Path $root '.git\hooks'
$source = Join-Path $root '.githooks\prepare-commit-msg'
$target = Join-Path $hooksDir 'prepare-commit-msg'

New-Item -ItemType Directory -Force -Path $hooksDir | Out-Null
Copy-Item -Force $source $target
Write-Host "Installed prepare-commit-msg hook -> $target"
