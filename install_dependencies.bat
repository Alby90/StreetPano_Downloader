@echo off
title Installazione Dipendenze - Street View Downloader
echo ================================================================
echo    STREET VIEW PANORAMA DOWNLOADER
echo    Installazione Automatica Dipendenze
echo ================================================================
echo.

REM Controlla se Python è installato
echo [1/5] Verifica installazione Python...
python --version
if errorlevel 1 (
    echo.
    echo ERRORE: Python non trovato nel PATH!
    echo.
    echo Soluzioni:
    echo 1. Installa Python da: https://www.python.org/downloads/
    echo 2. Durante l'installazione, seleziona "Add Python to PATH"
    echo 3. Riavvia il computer dopo l'installazione
    echo.
    pause
    exit /b 1
)

echo [2/5] Aggiornamento pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ATTENZIONE: Impossibile aggiornare pip, continuo comunque...
)

echo.
echo [3/5] Installazione dipendenze base (obbligatorie)...
python -m pip install requests pillow
if errorlevel 1 (
    echo ERRORE: Installazione dipendenze base fallita!
    pause
    exit /b 1
)

echo.
echo [4/5] Installazione dipendenze opzionali (performance)...
echo Installazione numpy per conversioni più veloci...
python -m pip install numpy
if errorlevel 1 (
    echo ATTENZIONE: NumPy non installato - le conversioni saranno più lente
)

echo Installazione OpenCV per elaborazioni avanzate...
python -m pip install opencv-python
if errorlevel 1 (
    echo ATTENZIONE: OpenCV non installato - alcune funzioni avanzate non disponibili
)

echo.
echo [5/5] Test dipendenze installate...
python -c "import requests; print('✓ requests:', requests.__version__)"
python -c "import PIL; print('✓ PIL/Pillow:', PIL.__version__)"
python -c "import tkinter; print('✓ tkinter: OK')" 2>nul || echo "⚠ tkinter: Problemi rilevati"

echo.
echo Test dipendenze opzionali...
python -c "import numpy; print('✓ numpy:', numpy.__version__)" 2>nul || echo "⚠ numpy: non installato"
python -c "import cv2; print('✓ opencv:', cv2.__version__)" 2>nul || echo "⚠ opencv: non installato"

echo.
echo ================================================================
echo    INSTALLAZIONE COMPLETATA
echo ================================================================
echo.
echo Dipendenze base installate con successo!
echo.
echo Prossimi passi:
echo 1. Per app semplice: doppio click su run_simple.bat
echo 2. Per app avanzata: doppio click su run_advanced.bat  
echo 3. Per test: python test_functionality.py
echo.
echo Documentazione completa in: USAGE_GUIDE.md
echo.

pause
