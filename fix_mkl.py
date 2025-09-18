"""
Fix automatico per problemi Intel MKL con NumPy
"""

import os
import sys
import subprocess


def fix_mkl_issue():
    """Risolve problemi Intel MKL"""
    print("🔧 RISOLUZIONE PROBLEMI INTEL MKL")
    print("=" * 50)
    
    # Test se il problema esiste
    try:
        import numpy as np
        print("✅ NumPy si importa correttamente")
        return True
    except Exception as e:
        if "mkl" in str(e).lower() or "intel" in str(e).lower():
            print("❌ Errore Intel MKL rilevato!")
            print(f"Errore: {e}")
            return fix_mkl_numpy()
        else:
            print(f"❌ Errore NumPy diverso: {e}")
            return False


def fix_mkl_numpy():
    """Fix specifico per NumPy con MKL Intel"""
    print("\n🔄 Applicazione fix Intel MKL...")
    
    solutions = [
        ("Opzione 1: Reinstalla NumPy senza MKL", reinstall_numpy_nomkl),
        ("Opzione 2: Downgrade NumPy stabile", downgrade_numpy),
        ("Opzione 3: Usa OpenBLAS invece di MKL", install_openblas_numpy),
        ("Opzione 4: Fix variabili ambiente", fix_environment_vars)
    ]
    
    for i, (description, fix_func) in enumerate(solutions, 1):
        print(f"\n{i}. {description}")
        
        response = input(f"Vuoi provare questa soluzione? (s/n): ").lower().strip()
        if response in ['s', 'si', 'y', 'yes']:
            try:
                success = fix_func()
                if success:
                    print("✅ Fix applicato! Testando...")
                    if test_numpy_import():
                        print("🎉 PROBLEMA RISOLTO!")
                        return True
                    else:
                        print("❌ Fix non riuscito, proviamo il successivo...")
                else:
                    print("❌ Fix fallito, proviamo il successivo...")
            except Exception as e:
                print(f"❌ Errore durante fix: {e}")
    
    print("\n❌ Nessun fix automatico riuscito")
    print("💡 Suggerimenti manuali:")
    print("   1. Riavvia il computer")
    print("   2. Usa Python system invece di conda")
    print("   3. Installa Visual Studio C++ Redistributables")
    return False


def reinstall_numpy_nomkl():
    """Reinstalla NumPy senza MKL"""
    print("Disinstallazione NumPy...")
    subprocess.run([sys.executable, "-m", "pip", "uninstall", "numpy", "-y"], 
                  capture_output=True)
    
    print("Installazione NumPy senza MKL...")
    result = subprocess.run([sys.executable, "-m", "pip", "install", 
                           "numpy", "--no-binary", "numpy"], 
                          capture_output=True, text=True)
    
    return result.returncode == 0


def downgrade_numpy():
    """Downgrade a versione NumPy stabile"""
    print("Disinstallazione NumPy attuale...")
    subprocess.run([sys.executable, "-m", "pip", "uninstall", "numpy", "-y"], 
                  capture_output=True)
    
    print("Installazione NumPy 1.24.3 (stabile)...")
    result = subprocess.run([sys.executable, "-m", "pip", "install", "numpy==1.24.3"], 
                          capture_output=True, text=True)
    
    return result.returncode == 0


def install_openblas_numpy():
    """Installa NumPy con OpenBLAS invece di MKL"""
    print("Disinstallazione NumPy attuale...")
    subprocess.run([sys.executable, "-m", "pip", "uninstall", "numpy", "-y"], 
                  capture_output=True)
    
    print("Installazione NumPy con OpenBLAS...")
    result = subprocess.run([sys.executable, "-m", "pip", "install", 
                           "numpy", "--prefer-binary", "--extra-index-url", 
                           "https://pypi.anaconda.org/scipy-wheels-nightly/simple"], 
                          capture_output=True, text=True)
    
    return result.returncode == 0


def fix_environment_vars():
    """Fix variabili ambiente per MKL"""
    print("Impostazione variabili ambiente MKL...")
    
    # Variabili che possono risolvere problemi MKL
    env_vars = {
        'MKL_NUM_THREADS': '1',
        'OMP_NUM_THREADS': '1',
        'MKL_THREADING_LAYER': 'GNU',
        'KMP_DUPLICATE_LIB_OK': 'TRUE'
    }
    
    for var, value in env_vars.items():
        os.environ[var] = value
        print(f"  {var} = {value}")
    
    return True


def test_numpy_import():
    """Testa import NumPy"""
    try:
        # Forza reload per testare
        if 'numpy' in sys.modules:
            del sys.modules['numpy']
        
        import numpy as np
        print(f"✅ NumPy {np.__version__} importato correttamente")
        
        # Test operazione base
        arr = np.array([1, 2, 3])
        result = np.sum(arr)
        print(f"✅ Test operazione NumPy: {result}")
        
        return True
    except Exception as e:
        print(f"❌ Import NumPy ancora fallisce: {e}")
        return False


def create_mkl_free_environment():
    """Crea script per ambiente senza MKL"""
    script_content = '''@echo off
echo Avvio Street View Downloader in modalità MKL-free...

REM Imposta variabili ambiente per evitare MKL
set MKL_NUM_THREADS=1
set OMP_NUM_THREADS=1
set MKL_THREADING_LAYER=GNU
set KMP_DUPLICATE_LIB_OK=TRUE

REM Avvia applicazione
python advanced_downloader.py

pause
'''
    
    with open('run_advanced_nomkl.bat', 'w') as f:
        f.write(script_content)
    
    print("✅ Creato launcher run_advanced_nomkl.bat per ambiente MKL-free")


if __name__ == "__main__":
    print("🛠️ FIX AUTOMATICO INTEL MKL per Street View Downloader")
    print("=" * 60)
    
    # Test iniziale
    print("📊 Diagnostica problema...")
    
    # Crea sempre il launcher MKL-free
    create_mkl_free_environment()
    
    # Tenta fix automatico
    if fix_mkl_issue():
        print("\n🎉 PROBLEMA RISOLTO!")
        print("✅ Street View Downloader dovrebbe funzionare normalmente")
    else:
        print("\n⚠️ Fix automatico non riuscito")
        print("💡 SOLUZIONE ALTERNATIVA:")
        print("   Usa: run_advanced_nomkl.bat")
        print("   Questo avvia l'app senza dipendenze MKL")
    
    print(f"\n{'='*60}")
    print("📱 Prova ad avviare l'applicazione:")
    print("   • run_advanced.bat (normale)")
    print("   • run_advanced_nomkl.bat (MKL-free)")
    print("="*60)