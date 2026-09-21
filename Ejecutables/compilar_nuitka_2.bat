@echo off
cd /d "%~dp0"
title Compilador Nuitka - Analizador de Impulsos
echo ========================================================
echo Iniciando compilacion Nuitka
echo ========================================================

REM 1. Nombre de la carpeta contenedora.
set "FOLDER=Nuitka_Build"

REM 2. Limpiar la carpeta anterior
if exist %FOLDER% rd /s /q %FOLDER%

echo.
echo Compilando...
echo.

REM 3. Ejecutar
python -m nuitka --standalone --disable-console --enable-plugin=pyside6 ^
--include-package=pyvisa_py ^
--include-package=serial ^
--include-module=PySide6.QtOpenGL ^
--include-module=PySide6.QtOpenGLWidgets ^
--assume-yes-for-downloads ^
--output-dir=%FOLDER% ^
--output-filename="Analizador_Impulsos_v3_Nuitka.exe" ^
..\src\main.py

echo.
echo ========================================================
echo Proceso finalizado.
echo El ejecutable estara dentro de la carpeta "main.dist" en: %FOLDER%
echo ========================================================
pause