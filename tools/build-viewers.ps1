# Regenerates the in-browser viewers from the source files.
#
#   .\tools\build-viewers.ps1
#
# Requires Microsoft PowerPoint and Word (Office 2016+). Produces:
#   viewer/deck/slide-NN.png   one image per slide, used by deck.html
#   viewer/deck.pdf            the deck as PDF, for download
#   viewer/report.pdf          the DOCX as PDF, used by report.html

param(
  [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

$ErrorActionPreference = "Stop"

$deck = Join-Path $Root "presentation.pptx"
$docx = Get-ChildItem (Join-Path $Root "*.docx") | Select-Object -First 1
$deckOut = Join-Path $Root "viewer\deck"
$deckPdf = Join-Path $Root "viewer\deck.pdf"
$reportPdf = Join-Path $Root "viewer\report.pdf"

foreach ($f in @($deck, $docx.FullName)) {
  if (-not (Test-Path $f)) { throw "Missing source file: $f" }
}

New-Item -ItemType Directory -Force -Path (Join-Path $Root "viewer") | Out-Null
New-Item -ItemType Directory -Force -Path $deckOut | Out-Null

Write-Host "Exporting deck slides..."
$ppt = New-Object -ComObject PowerPoint.Application
try {
  $pres = $ppt.Presentations.Open($deck, $true, $false, $false)
  $pres.SaveAs($deckPdf, 32) # ppSaveAsPDF
  for ($i = 1; $i -le $pres.Slides.Count; $i++) {
    $name = Join-Path $deckOut ("slide-{0:D2}.png" -f $i)
    $pres.Slides.Item($i).Export($name, "PNG", 1600, 900)
  }
  Write-Host ("  {0} slides" -f $pres.Slides.Count)
  $pres.Close()
} finally {
  $ppt.Quit()
}

Write-Host "Exporting report..."
$word = New-Object -ComObject Word.Application
try {
  $word.Visible = $false
  $doc = $word.Documents.Open($docx.FullName, $false, $true)
  $doc.SaveAs2($reportPdf, 17) # wdFormatPDF
  Write-Host ("  {0} pages" -f $doc.ComputeStatistics(2))
  $doc.Close($false)
} finally {
  $word.Quit()
}

Write-Host "Done."
