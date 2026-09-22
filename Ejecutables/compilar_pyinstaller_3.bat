@echo off
cd /d "%~dp0"
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
pyinstaller --noconfirm --onedir --noconsole --clean ^
 --name "Analizador_Impulsos_v3_pyinstaller" ^
 --distpath ".\%FOLDER%\dist" ^
 --workpath ".\%FOLDER%\build" ^
 --specpath ".\%FOLDER%" ^
 --collect-all pyvisa_py ^
 --collect-all pyvisa ^
 --collect-all serial ^
 --hidden-import serial ^
 --hidden-import pyvisa_py.protocols.usbtmc ^
 ..\src\main.py

echo.
echo ========================================================
echo Proceso finalizado. 
echo El ejecutable esta en: %FOLDER%\dist\Analizador_Impulsos_v3_pyinstaller
echo ========================================================
pause