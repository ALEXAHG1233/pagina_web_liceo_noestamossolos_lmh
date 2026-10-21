# Convierte informe.html en Word (.docx) y, si se puede, en PDF, usando Microsoft Word:
# títulos con estilos de Word, índice automático, "Página X de Y" e imágenes guardadas en el archivo.
# Uso: powershell -ExecutionPolicy Bypass -File convertir_informe.ps1   (deja el detalle en convertir.log)
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$html = Join-Path $dir "informe.html"
$docx = Join-Path $dir "Informe_No_estamos_solos_LMH.docx"
$pdf = Join-Path $dir "Informe_No_estamos_solos_LMH.pdf"
$log = Join-Path $dir "convertir.log"
"" | Set-Content $log -Encoding utf8
function Paso($nombre, [scriptblock]$accion) {
  try { & $accion; Add-Content $log "ok: $nombre" -Encoding utf8 }
  catch { Add-Content $log "ERROR en ${nombre}: $($_.Exception.Message)" -Encoding utf8 }
}

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
$doc = $null
Paso "abrir" { $script:doc = $word.Documents.Open($html) }
Paso "vista de impresión" { $doc.ActiveWindow.View.Type = 3 }
Paso "página carta" {
  $doc.PageSetup.PageWidth = 612; $doc.PageSetup.PageHeight = 792
  $doc.PageSetup.TopMargin = 72; $doc.PageSetup.BottomMargin = 72; $doc.PageSetup.LeftMargin = 72; $doc.PageSetup.RightMargin = 72
}
Paso "imágenes dentro del archivo" {
  # Word 2007 deja enlazadas las imágenes del HTML: se reemplaza cada una por una copia incrustada del mismo tamaño.
  $n = 0
  $formas = @($doc.InlineShapes)
  for ($i = $formas.Count - 1; $i -ge 0; $i--) {
    $forma = $formas[$i]
    $ruta = $null
    try { $ruta = $forma.LinkFormat.SourceFullName } catch {}
    if (-not $ruta) { continue }
    $ancho = $forma.Width; $alto = $forma.Height
    $rango = $forma.Range
    $forma.Delete()
    $nueva = $doc.InlineShapes.AddPicture($ruta, $false, $true, $rango)
    $nueva.Width = $ancho; $nueva.Height = $alto
    $n++
  }
  Add-Content $log "   imágenes incrustadas: $n" -Encoding utf8
}
Paso "índice" {
  $rango = $doc.Content
  if ($rango.Find.Execute("[[INDICE]]")) {
    $rango.Text = ""
    [void]$doc.Fields.Add($rango, 13, '\o "1-2" \h \z \u', $false)   # 13 = campo TOC con los títulos 1 y 2
  } else { throw "no encontré la marca del índice" }
}
Paso "pie de página" {
  $seccion = $doc.Sections.Item(1)
  $seccion.PageSetup.DifferentFirstPageHeaderFooter = $true
  foreach ($k in 1, 2, 3) { try { $seccion.Headers.Item($k).Range.Text = "" } catch {} }
  $pie = $seccion.Footers.Item(1)
  $pie.Range.Text = "Página X de Y"
  $pie.Range.ParagraphFormat.Alignment = 2
  $pie.Range.Font.Name = "Calibri"; $pie.Range.Font.Size = 9
  $r = $pie.Range; if ($r.Find.Execute("X")) { [void]$doc.Fields.Add($r, 33) }    # PAGE
  $r = $pie.Range; if ($r.Find.Execute("Y")) { [void]$doc.Fields.Add($r, 26) }    # NUMPAGES
}
Paso "encabezado de tablas en cada página" { foreach ($t in @($doc.Tables)) { $t.Rows.Item(1).HeadingFormat = -1 } }
Paso "actualizar campos" { [void]$doc.Fields.Update(); foreach ($t in @($doc.TablesOfContents)) { $t.Update() } }
Paso "guardar docx" {
  try { $doc.SaveAs($docx, 12) } catch { $nombre = [object]$docx; $formato = [object]12; $doc.SaveAs([ref]$nombre, [ref]$formato) }
}
Paso "guardar pdf" {
  try { $doc.ExportAsFixedFormat($pdf, 17) } catch { $doc.SaveAs($pdf, 17) }
}
Paso "contar páginas" { Add-Content $log "   páginas: $($doc.ComputeStatistics(2))" -Encoding utf8 }
Paso "cerrar" { $doc.Close([ref]0) }
Paso "salir de Word" { $word.Quit() }
Get-Content $log
