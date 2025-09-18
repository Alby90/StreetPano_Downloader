@echo off
echo Avvio Street View Downloader in modalità MKL-free...

REM Imposta variabili ambiente per evitare MKL
set MKL_NUM_THREADS=1
set OMP_NUM_THREADS=1
set MKL_THREADING_LAYER=GNU
set KMP_DUPLICATE_LIB_OK=TRUE

REM Avvia applicazione
python advanced_downloader.py

pause
