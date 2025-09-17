@echo off
title Street View Downloader - Versione Semplice
echo ================================================
echo    STREET VIEW PANORAMA DOWNLOADER
echo    Versione Semplice - Avvio in corso...
echo ================================================
echo.

REM Controlla se Python è installato
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRORE: Python non trovato!
    echo Installa Python da: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Controlla se il file esiste
if not exist "simple_downloader.py" (
    echo ERRORE: File simple_downloader.py non trovato!
    echo Assicurati di essere nella cartella corretta.
    pause
    exit /b 1
)

REM Avvia l'applicazione
echo Avvio Street View Downloader Semplice...
echo.
python simple_downloader.py

REM Se l'applicazione termina con errore
if errorlevel 1 (
    echo.
    echo ================================================
    echo    APPLICAZIONE TERMINATA CON ERRORE
    echo ================================================
    echo Potrebbero mancare delle dipendenze.
    echo Prova ad eseguire: pip install requests pillow
    echo.
    pause
) else (
    echo.
    echo ================================================
    echo    APPLICAZIONE CHIUSA CORRETTAMENTE
    echo ================================================
)

pause
