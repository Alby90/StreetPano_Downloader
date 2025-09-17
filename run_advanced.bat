@echo off
title Street View Downloader - Versione Avanzata
echo ================================================
echo    STREET VIEW PANORAMA DOWNLOADER
echo    Versione Avanzata - Avvio in corso...
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
if not exist "advanced_downloader.py" (
    echo ERRORE: File advanced_downloader.py non trovato!
    echo Assicurati di essere nella cartella corretta.
    pause
    exit /b 1
)

REM Installa dipendenze se mancanti
echo Verifica dipendenze...
python -c "import requests, PIL, tkinter" >nul 2>&1
if errorlevel 1 (
    echo Installazione dipendenze mancanti...
    pip install requests pillow
    if errorlevel 1 (
        echo ERRORE: Impossibile installare le dipendenze!
        echo Prova manualmente: pip install requests pillow
        pause
        exit /b 1
    )
)

REM Controlla dipendenze opzionali
echo Verifica dipendenze opzionali per performance...
python -c "import numpy" >nul 2>&1
if errorlevel 1 (
    echo NumPy non trovato - installazione opzionale per performance migliorate
    echo Puoi installare con: pip install numpy
) else (
    echo NumPy trovato - performance migliorate disponibili
)

echo.
echo ================================================
echo    AVVIO APPLICAZIONE AVANZATA
echo ================================================
echo.
echo Funzionalità disponibili:
echo - Download Street View con anteprima
echo - Conversione file locali equirect/cubemap  
echo - Download multipli e batch processing
echo - 3 tab specializzati per diverse operazioni
echo.

REM Avvia l'applicazione
python advanced_downloader.py

REM Se l'applicazione termina con errore
if errorlevel 1 (
    echo.
    echo ================================================
    echo    APPLICAZIONE TERMINATA CON ERRORE
    echo ================================================
    echo.
    echo Possibili soluzioni:
    echo 1. Installa dipendenze: pip install requests pillow
    echo 2. Verifica Python 3.7+ installato
    echo 3. Controlla connessione internet
    echo 4. Esegui test: python test_functionality.py
    echo.
    pause
) else (
    echo.
    echo ================================================
    echo    APPLICAZIONE CHIUSA CORRETTAMENTE
    echo ================================================
)

pause
