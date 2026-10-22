@echo off
rem Enciende la pagina "No estamos solos LMH" y la abre en el navegador.
rem Uso: doble clic. No cierres esta ventana negra mientras presentas.
rem Si el servidor se cae, se vuelve a encender solo a los 3 segundos.
title No estamos solos LMH - servidor (no cerrar)
cd /d "%~dp0"
echo.
echo   Encendiendo la pagina... se abrira en el navegador en unos segundos.
echo   Direccion: http://localhost:5000
echo   NO cierres esta ventana mientras uses la pagina.
echo.
start "" cmd /c "timeout /t 6 /nobreak >nul & start http://localhost:5000"
:encender
python app.py
echo.
echo   El servidor se detuvo. Se vuelve a encender en 3 segundos...
timeout /t 3 /nobreak >nul
goto encender
