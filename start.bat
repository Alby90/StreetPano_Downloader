@echo off
echo Avvio Google Street View Downloader...
echo.
python simple_downloader.py
if errorlevel 1 (
    echo.
    echo ERRORE: Impossibile avviare il programma.
    echo.
    echo Possibili cause:
    echo - Python non e' installato
    echo - Dipendenze mancanti ^(requests, pillow^)
    echo.
    echo Per installare le dipendenze:
    echo pip install requests pillow
    echo.
    pause
)
