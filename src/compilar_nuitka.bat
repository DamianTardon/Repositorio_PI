@echo off
title Compilador Nuitka Automático - Analizador de Impulsos
echo ========================================================
echo Iniciando compilacion Nuitka (v1.0-testing)
echo Modo: Unattended (Automatizado)
echo ========================================================

REM 1. Definimos la carpeta para mantener el orden
set "FOLDER=Nuitka_Build"

REM 2. Limpieza de la carpeta anterior
if exist %FOLDER% rd /s /q %FOLDER%

echo.
echo Compilando... Esta operacion es lenta pero eficiente.
echo.

REM 3. Ejecucion de Nuitka
REM --assume-yes-for-downloads: Responde "Yes" a todo automaticamente
REM --output-dir: Guarda build y dist dentro de la carpeta elegida
python -m nuitka --onefile --enable-plugin=pyside6 ^
 --include-package=pyvisa_py ^
 --include-package=serial ^
 --include-package=usb ^
 --include-module=PySide6.QtOpenGL ^
 --include-module=PySide6.QtOpenGLWidgets ^
 --assume-yes-for-downloads ^
 --output-dir=%FOLDER% ^
 --output-filename="Analizador_Impulsos_v1_Nuitka.exe" ^
 main.py

echo.
echo ========================================================
echo Proceso finalizado. 
echo El .exe te espera en: %FOLDER%/Analizador_Impulsos_v1_Nuitka.exe
echo ========================================================
pause