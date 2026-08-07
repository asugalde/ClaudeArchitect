<#
.SYNOPSIS
  Exports an HTML study guide to PDF using the system's Microsoft Edge in headless mode (zero installs).
.EXAMPLE
  powershell -File herramientas/html-a-pdf.ps1 -HtmlPath "bloques/bloque-4/guia_v1.0.html" -RevealAnswers
.NOTES
  Mermaid diagrams render via CDN, so network access is required during export.
  -RevealAnswers appends ?print=1 so mini-check answers are visible in the PDF.
#>
param(
    [Parameter(Mandatory = $true)][string]$HtmlPath,
    [string]$PdfPath,
    [switch]$RevealAnswers,
    [int]$TimeoutMs = 20000
)

$ErrorActionPreference = "Stop"

# Resolve input file
$html = Resolve-Path -LiteralPath $HtmlPath
if (-not $PdfPath) { $PdfPath = [System.IO.Path]::ChangeExtension($html.Path, ".pdf") }
$pdfFull = [System.IO.Path]::GetFullPath($PdfPath)

# Locate Edge
$edgeCandidates = @(
    (Join-Path ${env:ProgramFiles(x86)} "Microsoft\Edge\Application\msedge.exe"),
    (Join-Path $env:ProgramFiles "Microsoft\Edge\Application\msedge.exe"),
    (Join-Path $env:LOCALAPPDATA "Microsoft\Edge\Application\msedge.exe")
)
$edge = $edgeCandidates | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
if (-not $edge) { throw "msedge.exe not found. Checked: $($edgeCandidates -join '; ')" }

# Build file:/// URI (with optional ?print=1)
$uri = ([System.Uri]$html.Path).AbsoluteUri
if ($RevealAnswers) { $uri += "?print=1" }

Write-Host "Exporting '$($html.Path)' -> '$pdfFull'"
$edgeArgs = @(
    "--headless",
    "--disable-gpu",
    "--no-first-run",
    "--no-pdf-header-footer",
    "--virtual-time-budget=$TimeoutMs",
    "--print-to-pdf=`"$pdfFull`"",
    "`"$uri`""
)
$proc = Start-Process -FilePath $edge -ArgumentList $edgeArgs -Wait -PassThru -WindowStyle Hidden
if ($proc.ExitCode -ne 0) { Write-Warning "Edge exited with code $($proc.ExitCode)" }

if (-not (Test-Path $pdfFull)) { throw "PDF was not created: $pdfFull" }
$size = (Get-Item $pdfFull).Length
if ($size -lt 10KB) { Write-Warning "PDF is suspiciously small ($([math]::Round($size/1KB,1)) KB). Mermaid may not have rendered; retry with a larger -TimeoutMs." }
Write-Host "OK: $pdfFull ($([math]::Round($size/1KB,1)) KB)"
