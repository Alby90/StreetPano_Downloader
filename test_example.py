"""
Script di esempio per testare le funzionalità del downloader Street View
"""

from streetview_utils import StreetViewUtils, PanoIDExtractor
import requests
from PIL import Image
import os

def test_panoid_extraction():
    """Testa l'estrazione del PanoID da vari tipi di URL"""
    print("=== Test estrazione PanoID ===")
    
    extractor = PanoIDExtractor()
    
    # URL di esempio (sostituisci con URL reali)
    test_urls = [
        "https://www.google.com/maps/@40.748817,-73.985428,3a,75y,90t/data=!3m6!1e1!3m4!1sAF1QipM...",
        "https://www.google.com/maps/place/@40.748817,-73.985428,3a,75y,90t/data=!3m6!1e1!3m4!1s...",
        "https://maps.google.com/?q=loc:40.748817,-73.985428&z=15&t=k&hl=it"
    ]
    
    for url in test_urls:
        panoid = extractor.extract_from_url(url)
        print(f"URL: {url[:50]}...")
        print(f"PanoID estratto: {panoid}")
        
        if panoid:
            is_valid = extractor.validate_panoid(panoid)
            print(f"PanoID valido: {is_valid}")
        print("-" * 50)

def test_panorama_info():
    """Testa l'ottenimento di informazioni su un panorama"""
    print("\n=== Test informazioni panorama ===")
    
    # Usa un PanoID di esempio (sostituisci con uno reale)
    test_panoid = "YourTestPanoIDHere"
    
    if test_panoid != "YourTestPanoIDHere":
        info = StreetViewUtils.get_panorama_info(test_panoid)
        print(f"PanoID: {info['panoid']}")
        print(f"Zoom disponibili: {info['available_zooms']}")
        print(f"Risoluzione massima: {info['max_resolution']}")
        print(f"Dimensioni stimate: {info['estimated_size']}")
    else:
        print("Inserisci un PanoID valido per testare questa funzione")

def test_tile_download():
    """Testa il download di una singola tile"""
    print("\n=== Test download tile ===")
    
    # Usa un PanoID di esempio
    test_panoid = "YourTestPanoIDHere"
    
    if test_panoid != "YourTestPanoIDHere":
        url = f"https://streetviewpixels-pa.googleapis.com/v1/tile?cb_client=maps_sv.tactile&panoid={test_panoid}&x=0&y=0&zoom=1&nbt=1&fover=2"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print("Download tile riuscito!")
                print(f"Dimensione: {len(response.content)} bytes")
                
                # Salva la tile di test
                with open("test_tile.jpg", "wb") as f:
                    f.write(response.content)
                print("Tile salvata come 'test_tile.jpg'")
            else:
                print(f"Errore nel download: {response.status_code}")
        except Exception as e:
            print(f"Errore: {e}")
    else:
        print("Inserisci un PanoID valido per testare questa funzione")

def test_image_enhancement():
    """Testa il miglioramento dell'immagine"""
    print("\n=== Test miglioramento immagine ===")
    
    if os.path.exists("test_tile.jpg"):
        try:
            # Carica l'immagine di test
            original = Image.open("test_tile.jpg")
            print(f"Immagine originale: {original.size}")
            
            # Applica miglioramenti
            enhanced = StreetViewUtils.enhance_equirectangular(original)
            print(f"Immagine migliorata: {enhanced.size}")
            
            # Salva l'immagine migliorata
            enhanced.save("test_tile_enhanced.jpg", quality=95)
            print("Immagine migliorata salvata come 'test_tile_enhanced.jpg'")
            
        except Exception as e:
            print(f"Errore nel miglioramento: {e}")
    else:
        print("Nessuna immagine di test disponibile. Esegui prima test_tile_download()")

def demo_complete_workflow():
    """Dimostra un workflow completo"""
    print("\n=== Demo workflow completo ===")
    
    # Esempio di URL Street View (sostituisci con uno reale)
    example_url = "https://www.google.com/maps/@40.748817,-73.985428,3a,75y,90t/data=!3m6!1e1"
    
    print(f"1. URL di partenza: {example_url}")
    
    # Estrazione PanoID
    extractor = PanoIDExtractor()
    panoid = extractor.extract_from_url(example_url)
    
    if panoid:
        print(f"2. PanoID estratto: {panoid}")
        
        # Validazione
        is_valid = extractor.validate_panoid(panoid)
        print(f"3. PanoID valido: {is_valid}")
        
        if is_valid:
            # Informazioni panorama
            info = StreetViewUtils.get_panorama_info(panoid)
            print(f"4. Zoom disponibili: {info['available_zooms']}")
            print(f"5. Risoluzione consigliata: {info['max_resolution']}")
            
            print("\n>>> A questo punto puoi usare l'interfaccia grafica per il download completo <<<")
        else:
            print("4. PanoID non valido, impossibile procedere")
    else:
        print("2. Impossibile estrarre il PanoID dall'URL")

if __name__ == "__main__":
    print("Street View Downloader - Script di Test")
    print("=" * 50)
    
    # Esegui tutti i test
    test_panoid_extraction()
    test_panorama_info()
    test_tile_download()
    test_image_enhancement()
    demo_complete_workflow()
    
    print("\n" + "=" * 50)
    print("Test completati!")
    print("Per usare l'interfaccia grafica, esegui: python streetview_downloader.py")
