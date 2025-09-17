#!/usr/bin/env python3
"""
Launcher per Google Street View Downloader
Esegui questo file per avviare il programma
"""

import sys
import os

# Aggiungi il percorso corrente al PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from streetview_downloader import main
    
    if __name__ == "__main__":
        print("Avvio Google Street View Downloader...")
        main()
        
except ImportError as e:
    print(f"Errore nell'importazione: {e}")
    print("Assicurati che tutti i file necessari siano presenti:")
    print("- streetview_downloader.py")
    print("- streetview_utils.py") 
    print("- config.py")
    
except Exception as e:
    print(f"Errore nell'avvio: {e}")
    import traceback
    traceback.print_exc()
