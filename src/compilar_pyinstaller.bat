@echo off
title Compilador Organizado - Analizador de Impulsos
echo ========================================================
echo Iniciando compilacion organizada en carpeta /PyInstaller_Build
echo ========================================================

REM 1. Definimos el nombre de la carpeta contenedora
set "FOLDER=PyInstaller_Build"

REM 2. Limpieza de la carpeta anterior para empezar de cero
if exist %FOLDER% rd /s /q %FOLDER%

echo.
echo Compilando... Esto puede tardar un momento.
echo.

REM 3. Ejecucion con rutas personalizadas
pyinstaller --noconfirm --onefile --console ^
 --name "Analizador_Impulsos_v1" ^
 --distpath "./%FOLDER%/dist" ^
 --workpath "./%FOLDER%/build" ^
 --specpath "./%FOLDER%" ^
 --collect-all pyvisa_py ^
 --collect-all pyvisa ^
 --collect-all serial ^
 --hidden-import usb ^
 --hidden-import serial ^
 --hidden-import pyvisa_py.protocols.usbtmc ^
 main.py

echo.
echo ========================================================
echo Proceso finalizado. 
echo El .exe te espera en: %FOLDER%/dist
echo ========================================================
pause