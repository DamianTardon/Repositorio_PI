@echo off
title Compilador PyInstaller - Analizador de Impulsos
echo ========================================================
echo Iniciando compilacion PyInstaller
echo ========================================================

REM 1. Nombre de la carpeta contenedora.
set "FOLDER=PyInstaller_Build"

REM 2. Limpiar la carpeta anterior.
if exist %FOLDER% rd /s /q %FOLDER%

echo.
echo Compilando...
echo.

REM 3. Ejecutar.
pyinstaller --noconfirm --onefile --console ^
 --name "Analizador_Impulsos_v2_pyinstaller" ^
 --distpath "./%FOLDER%/dist" ^
 --workpath "./%FOLDER%/build" ^
 --specpath "./%FOLDER%" ^
 --collect-all pyvisa_py ^
 --collect-all pyvisa ^
 --collect-all serial ^
 --hidden-import serial ^
 --hidden-import pyvisa_py.protocols.usbtmc ^
 main.py

echo.
echo ========================================================
echo Proceso finalizado. 
echo El .exe está en: %FOLDER%/dist
echo ========================================================
pause