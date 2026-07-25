$ErrorActionPreference = "Stop"

$source = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$targetRoot = "D:\learn\lover"
$target = Join-Path $targetRoot "LangChain-LLM-Journey"

New-Item -ItemType Directory -Force -Path $target | Out-Null
Copy-Item -Path (Join-Path $source "*") -Destination $target -Recurse -Force

Write-Host "Migrated project to: $target"
Write-Host "Run demo:"
Write-Host "  cd /d $target"
Write-Host "  scripts\start_demo.bat"

