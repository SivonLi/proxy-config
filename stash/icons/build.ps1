param(
    [string]$Magick = 'magick'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Invoke-Magick {
    param([string[]]$Arguments)
    & $Magick @Arguments
    if ($LASTEXITCODE -ne 0) { throw 'IMAGEMAGICK_FAILED' }
}

$sources = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'sources.json') -Raw -Encoding utf8 | ConvertFrom-Json
$workDirectory = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..\.work\icon-sources'))
$outputDirectory = Join-Path $PSScriptRoot 'rounded'
New-Item -ItemType Directory -Force -Path $workDirectory, $outputDirectory | Out-Null

# 全部图标共用画布、底板、圆角和标志区域。
$canvasSize = 256
$tileInset = 12
$cornerRadius = 52
$symbolSize = 176
$tileEnd = $canvasSize - $tileInset - 1
$canvasGeometry = "${canvasSize}x${canvasSize}"
$symbolGeometry = "${symbolSize}x${symbolSize}"
$maskPath = Join-Path $workDirectory 'rounded-mask.png'
Invoke-Magick -Arguments @(
    '-size', $canvasGeometry, 'xc:none', '-fill', 'white',
    '-draw', "roundrectangle $tileInset,$tileInset $tileEnd,$tileEnd $cornerRadius,$cornerRadius",
    '-strip', $maskPath
)

foreach ($source in $sources) {
    if ($source.id -notmatch '^[a-z]+(?:-[a-z]+)*$') { throw "ICON_ID_INVALID: $($source.id)" }
    $uri = [Uri]$source.url
    if ($uri.Scheme -ne 'https') { throw "ICON_SOURCE_NOT_HTTPS: $($source.id)" }
    $extension = if ($uri.AbsolutePath.EndsWith('.svg')) { '.svg' } else { '.image' }
    $sourcePath = Join-Path $workDirectory ($source.id + $extension)
    $symbolPath = Join-Path $workDirectory ($source.id + '-symbol.png')
    $outputPath = Join-Path $outputDirectory ($source.id + '.png')
    Invoke-WebRequest -Uri $uri -OutFile $sourcePath -TimeoutSec 45

    $cropArguments = @()
    if ($source.PSObject.Properties.Name -contains 'crop') {
        $cropArguments = @('-crop', $source.crop, '+repage')
    }

    # 等比例缩放原图，整理边缘空白，保留标志的颜色和构图。
    $prepareArguments = @('-background', 'white', $sourcePath) + $cropArguments + @(
        '-alpha', 'remove', '-alpha', 'off',
        '-fuzz', '2%', '-trim', '+repage', '-filter', 'Lanczos',
        '-resize', $symbolGeometry, '-colorspace', 'sRGB', '-strip', $symbolPath
    )
    Invoke-Magick -Arguments $prepareArguments
    Invoke-Magick -Arguments @(
        $maskPath, '-colorspace', 'sRGB', '-type', 'TrueColorAlpha',
        $symbolPath, '-gravity', 'center', '-compose', 'over', '-composite',
        '-colorspace', 'sRGB', '-depth', '8', '-strip', "PNG32:$outputPath"
    )
    Write-Output "已生成 $($source.name): $outputPath"
}
