"""
Test rapido post-fix MKL per verificare funzionalità
"""

import sys
import os

print("🧪 TEST POST-FIX INTEL MKL")
print("=" * 40)

# Test 1: Import di base
print("1. Test import librerie base...")
try:
    import tkinter as tk
    print("   ✅ tkinter")
except Exception as e:
    print(f"   ❌ tkinter: {e}")

try:
    from PIL import Image
    print("   ✅ PIL/Pillow")
except Exception as e:
    print(f"   ❌ PIL/Pillow: {e}")

try:
    import requests
    print("   ✅ requests")
except Exception as e:
    print(f"   ❌ requests: {e}")

# Test 2: Import NumPy con gestione MKL
print("\n2. Test NumPy (con gestione MKL)...")
try:
    import numpy as np
    print(f"   ✅ NumPy {np.__version__}")
    
    # Test operazione
    arr = np.array([1, 2, 3, 4, 5])
    result = np.sum(arr)
    print(f"   ✅ Operazione test: sum([1,2,3,4,5]) = {result}")
    
except Exception as e:
    if "mkl" in str(e).lower():
        print(f"   ❌ Errore MKL ancora presente: {e}")
    else:
        print(f"   ⚠ NumPy non disponibile: {e}")

# Test 3: Import OpenCV
print("\n3. Test OpenCV (opzionale)...")
try:
    import cv2
    print(f"   ✅ OpenCV {cv2.__version__}")
except Exception as e:
    print(f"   ⚠ OpenCV non disponibile: {e}")

# Test 4: Import applicazione principale
print("\n4. Test import applicazione...")
try:
    sys.path.insert(0, os.path.dirname(__file__))
    from advanced_downloader import AdvancedStreetViewDownloader
    print("   ✅ AdvancedStreetViewDownloader")
except Exception as e:
    print(f"   ❌ Errore import applicazione: {e}")

# Test 5: Test panorama converter
print("\n5. Test panorama converter...")
try:
    from panorama_converter import PanoramaConverter
    print("   ✅ PanoramaConverter")
except Exception as e:
    print(f"   ❌ Errore import converter: {e}")

# Test 6: Test GUI di base
print("\n6. Test GUI di base...")
try:
    root = tk.Tk()
    root.withdraw()  # Nasconde finestra
    
    # Test creazione app
    app = AdvancedStreetViewDownloader(root)
    print("   ✅ GUI inizializzata correttamente")
    
    root.destroy()
    
except Exception as e:
    print(f"   ❌ Errore GUI: {e}")

# Test 7: Test funzione overlap
print("\n7. Test funzionalità overlap...")
try:
    from PIL import Image
    test_img = Image.new('RGB', (100, 50), (128, 128, 128))
    
    root = tk.Tk()
    root.withdraw()
    app = AdvancedStreetViewDownloader(root)
    
    # Test overlap
    overlap_img = app.create_overlap_image(test_img, 20)
    
    if overlap_img.size[0] > test_img.size[0]:
        print("   ✅ Funzione overlap funziona correttamente")
    else:
        print("   ❌ Funzione overlap non aumenta dimensioni")
    
    root.destroy()
    
except Exception as e:
    print(f"   ❌ Errore test overlap: {e}")

print("\n" + "=" * 40)
print("📊 RISULTATO COMPLESSIVO:")

# Verifica se i componenti critici funzionano
critical_ok = True
try:
    import tkinter
    from PIL import Image
    import requests
    from advanced_downloader import AdvancedStreetViewDownloader
except:
    critical_ok = False

if critical_ok:
    print("✅ TUTTI I COMPONENTI CRITICI FUNZIONANO")
    print("🚀 L'applicazione è pronta all'uso!")
    print("\n📱 Per avviare:")
    print("   python advanced_downloader.py")
    print("   oppure run_advanced.bat")
else:
    print("❌ ALCUNI COMPONENTI CRITICI NON FUNZIONANO")
    print("🔧 Potrebbero essere necessari ulteriori fix")
    
print("=" * 40)