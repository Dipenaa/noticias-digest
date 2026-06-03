@echo off
title Generando digest...
cd /d "C:\Users\Usuario\Desktop\noticias"

echo Descargando feeds y generando HTML...
python main.py

echo.
echo Listo. Abriendo en el navegador...
pause
