@echo off
title Digest de Noticias - Servidor local
cd /d "C:\Users\Usuario\Desktop\noticias"

echo Iniciando servidor Flask en http://localhost:5000 ...
echo Cierra esta ventana para detener el servidor.
echo.

start "" "http://localhost:5000"
python app.py
