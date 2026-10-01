Add-Type -AssemblyName System.Drawing
$bitmap = [System.Drawing.Bitmap]::new(1200, 630)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
$bg = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(8, 19, 28))
$cyan = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(139, 228, 238))
$white = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(243, 246, 248))
$muted = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(170, 184, 196))
$line = [System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(26, 51, 64), 2)
$accent = [System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(139, 228, 238), 5)
$titleFont = [System.Drawing.Font]::new('Segoe UI', 82, [System.Drawing.FontStyle]::Bold, [System.Drawing.GraphicsUnit]::Pixel)
$smallFont = [System.Drawing.Font]::new('Segoe UI', 27, [System.Drawing.FontStyle]::Bold, [System.Drawing.GraphicsUnit]::Pixel)
$bodyFont = [System.Drawing.Font]::new('Segoe UI', 31, [System.Drawing.FontStyle]::Regular, [System.Drawing.GraphicsUnit]::Pixel)
try {
    $graphics.FillRectangle($bg, 0, 0, 1200, 630)
    for ($x = 80; $x -lt 1200; $x += 80) { $graphics.DrawLine($line, $x, 0, $x, 630) }
    for ($y = 70; $y -lt 630; $y += 70) { $graphics.DrawLine($line, 0, $y, 1200, $y) }
    $graphics.DrawLine($accent, 88, 90, 260, 90)
    $graphics.DrawString('HAIDER GAMES PRESENTS', $smallFont, $cyan, 88, 115)
    $graphics.DrawString('WAVE', $titleFont, $white, 80, 210)
    $graphics.DrawString('SURVIVOR', $titleFont, $cyan, 80, 300)
    $graphics.DrawString('A SCI-FI FPS FOR 1–3 PLAYERS', $bodyFont, $white, 88, 455)
    $graphics.DrawString('STORY  /  ENDLESS  /  OFFLINE  /  CO-OP', $smallFont, $muted, 88, 535)
    $bitmap.Save((Join-Path $PSScriptRoot 'docs\assets\og-card.png'), [System.Drawing.Imaging.ImageFormat]::Png)
}
finally {
    $titleFont.Dispose(); $smallFont.Dispose(); $bodyFont.Dispose()
    $bg.Dispose(); $cyan.Dispose(); $white.Dispose(); $muted.Dispose()
    $line.Dispose(); $accent.Dispose(); $graphics.Dispose(); $bitmap.Dispose()
}
