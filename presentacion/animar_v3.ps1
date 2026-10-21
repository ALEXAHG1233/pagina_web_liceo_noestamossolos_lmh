# Da a la presentación v3 sus animaciones en PowerPoint y la guarda con las letras adentro.
# Cada forma tiene un nombre (fx-circulo, fx-titulo, ...) puesto por crear_presentacion_v3.py.
# Uso: powershell -ExecutionPolicy Bypass -File animar_v3.ps1
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$src = Join-Path $dir "No_estamos_solos_LMH_v3.pptx"
$dst = Join-Path $dir "No_estamos_solos_LMH_v3_PowerPoint.pptx"
$ppt = New-Object -ComObject PowerPoint.Application
$pres = $ppt.Presentations.Open($src, $false, $false, $false)
$total = 0
function Efecto($s, $sh, $tipo, $retraso, $dur, $direccion) {
  $e = $s.TimeLine.MainSequence.AddEffect($sh, $tipo, 0, 2)   # 2 = con la anterior
  $e.Timing.TriggerDelayTime = [single]$retraso
  $e.Timing.Duration = [single]$dur
  if ($direccion) { try { $e.EffectParameters.Direction = $direccion } catch {} }
}
foreach ($s in $pres.Slides) {
  $t = $s.SlideShowTransition; $t.EntryEffect = 3849; $t.Duration = 0.6   # desvanecer suave
  $kt = 0; $kd = 0; $kf = 0; $kc = 0
  foreach ($sh in @($s.Shapes)) {
    switch -Wildcard ($sh.Name) {
      "fondo*"        { continue }
      "fx-circulo"    { Efecto $s $sh 53 ([Math]::Min(0.12 * $kc, 0.4)) 0.8 $null; $kc++; $total++ }   # zoom
      "fx-deco"       { Efecto $s $sh 10 0.3 0.6 $null; $total++ }                                      # desvanecer
      "fx-linea"      { Efecto $s $sh 22 0.35 0.6 4; $total++ }                                         # barrido desde la izquierda
      "fx-titulo"     { Efecto $s $sh 10 0.45 0.7 $null; $total++ }
      "fx-texto"      { Efecto $s $sh 10 ([Math]::Min(0.7 + 0.1 * $kt, 1.8)) 0.6 $null; $kt++; $total++ }
      "fx-diagrama"   { Efecto $s $sh 10 ([Math]::Min(0.6 + 0.07 * $kd, 2.2)) 0.5 $null; $kd++; $total++ }
      "fx-foto"       { Efecto $s $sh 53 (0.5 + 0.15 * $kf) 0.7 $null; $kf++; $total++ }
      "fx-avatar-der" { Efecto $s $sh 2 0.55 0.8 2; $total++ }                                         # entra desde la derecha
      "fx-avatar-izq" { Efecto $s $sh 2 0.55 0.8 4; $total++ }                                         # entra desde la izquierda
    }
  }
}
$pres.SaveAs($dst, 24, -1)
$pres.SaveAs((Join-Path $dir "No_estamos_solos_LMH_v3.pdf"), 32)
$pres.Close(); $ppt.Quit()
"animaciones: $total"
