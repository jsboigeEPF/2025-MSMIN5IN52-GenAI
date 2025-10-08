@echo off
REM Script de nettoyage de l'arborescence pour Windows

echo 🧹 Nettoyage de l'arborescence du projet...

REM Supprimer les dossiers __pycache__
echo Suppression des dossiers __pycache__...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

REM Supprimer les fichiers bytecode Python
echo Suppression des fichiers .pyc...
del /s /q *.pyc >nul 2>&1
del /s /q *.pyo >nul 2>&1

REM Supprimer les fichiers temporaires
echo Suppression des fichiers temporaires...
del /s /q *~ >nul 2>&1
del /s /q *.swp >nul 2>&1
del /s /q *.swo >nul 2>&1

REM Supprimer les fichiers de log
echo Suppression des fichiers de log...
del /s /q *.log >nul 2>&1

echo ✅ Nettoyage terminé!
pause