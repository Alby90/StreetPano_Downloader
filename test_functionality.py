"""
Test delle funzionalità del Google Street View Downloader
"""

import requests
import re
from PIL import Image
from io import BytesIO


def test_panoid_extraction():
    """Testa l'estrazione del PanoID"""
    print("=== Test Estrazione PanoID ===")
    
    # URL di esempio (sostituisci con URL reali per test completi)
    test_urls = [
        "https://www.google.com/maps/@40.748817,-73.985428,3a,75y,90t/data=!3m6!1e1!3m4!1sAF1QipM_test_panoid_here_123456789012345678901234!2e0!7i16384!8i8192",
        "https://maps.google.com/maps?q=40.748817,-73.985428&hl=en&t=k&z=18&layer=c&cbll=40.748817,-73.985428&panoid=test_panoid_here_123456789012345678901234&cbp=12,90,,0,5",
    ]
    
    patterns = [
        r'!1s([a-zA-Z0-9_-]{20,})',
        r'"pano":"([a-zA-Z0-9_-]{20,})"',
        r'panoid=([a-zA-Z0-9_-]{20,})',
    ]
    
    for url in test_urls:
        print(f"URL: {url[:80]}...")
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                panoid = match.group(1)
                print(f"  PanoID trovato con pattern '{pattern}': {panoid}")
                break
        else:
            print("  Nessun PanoID trovato")
        print()


def test_tile_download():
    """Testa il download di una singola tile"""
    print("=== Test Download Tile ===")
    
    # PanoID di esempio (Google ha alcuni PanoID pubblici per test)
    # Questo è un esempio, sostituisci con un PanoID reale
    test_panoid = "F:6Wyk5iqH9okNh4_yCG0Rg"  # Times Square esempio
    
    url = f"https://streetviewpixels-pa.googleapis.com/v1/tile?cb_client=maps_sv.tactile&panoid={test_panoid}&x=0&y=0&zoom=1&nbt=1&fover=2"
    
    try:
        print(f"Test URL: {url}")
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Content Length: {len(response.content)} bytes")
        print(f"Content Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200:
            print("✓ Download riuscito!")
            
            # Verifica che sia un'immagine valida
            try:
                image = Image.open(BytesIO(response.content))
                print(f"✓ Immagine valida: {image.size} pixel, formato: {image.format}")
            except Exception as e:
                print(f"✗ Errore nell'apertura dell'immagine: {e}")
        else:
            print(f"✗ Download fallito: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"✗ Errore di rete: {e}")
    
    print()


def test_zoom_levels():
    """Testa i diversi livelli di zoom"""
    print("=== Test Livelli di Zoom ===")
    
    zoom_config = {
        0: (1, 1, "512×512"),
        1: (2, 1, "1024×512"),
        2: (4, 2, "2048×1024"),
        3: (8, 4, "4096×2048"),
        4: (16, 8, "8192×4096")
    }
    
    for zoom, (tiles_x, tiles_y, resolution) in zoom_config.items():
        total_tiles = tiles_x * tiles_y
        print(f"Zoom {zoom}: {tiles_x}×{tiles_y} tiles = {total_tiles} tiles totali → {resolution}")
    
    print()


def test_url_patterns():
    """Testa vari pattern di URL Google Maps"""
    print("=== Test Pattern URL ===")
    
    test_cases = [
        ("URL Maps standard", "https://www.google.com/maps/@40.748817,-73.985428,3a,75y,90t/data=!3m6!1e1!3m4!1sAF1QipNExample123456789012345678901234!2e0!7i16384!8i8192"),
        ("URL con photosphereId", "https://maps.google.com/maps?q=40.748817,-73.985428&photosphereId=Example123456789012345678901234"),
        ("URL con panoid diretto", "https://maps.google.com/maps?panoid=Example123456789012345678901234&cbp=12,90,,0,5"),
        ("URL JSON-like", '{"pano":"Example123456789012345678901234","location":{"lat":40.748817,"lng":-73.985428}}'),
    ]
    
    patterns = [
        (r'!1s([a-zA-Z0-9_-]{20,})', "Pattern !1s"),
        (r'photosphereId=([a-zA-Z0-9_-]{20,})', "Pattern photosphereId"),
        (r'panoid=([a-zA-Z0-9_-]{20,})', "Pattern panoid"),
        (r'"pano":"([a-zA-Z0-9_-]{20,})"', "Pattern JSON pano"),
    ]
    
    for desc, test_url in test_cases:
        print(f"{desc}:")
        print(f"  URL: {test_url[:80]}...")
        
        found = False
        for pattern, pattern_desc in patterns:
            match = re.search(pattern, test_url)
            if match:
                print(f"  ✓ {pattern_desc}: {match.group(1)}")
                found = True
                break
        
        if not found:
            print("  ✗ Nessun pattern corrispondente")
        print()


def check_dependencies():
    """Verifica le dipendenze"""
    print("=== Verifica Dipendenze ===")
    
    dependencies = [
        ("tkinter", "GUI interface"),
        ("requests", "HTTP requests"),
        ("PIL (Pillow)", "Image processing"),
        ("re", "Regular expressions"),
        ("threading", "Multi-threading"),
    ]
    
    for dep, desc in dependencies:
        try:
            if dep == "PIL (Pillow)":
                import PIL
                print(f"✓ {dep}: {desc}")
            elif dep == "tkinter":
                import tkinter
                print(f"✓ {dep}: {desc}")
            else:
                __import__(dep)
                print(f"✓ {dep}: {desc}")
        except ImportError:
            print(f"✗ {dep}: {desc} - NON DISPONIBILE")
    
    print()


def main():
    """Esegue tutti i test"""
    print("Google Street View Downloader - Test Suite")
    print("=" * 50)
    
    check_dependencies()
    test_zoom_levels()
    test_panoid_extraction()
    test_url_patterns()
    test_tile_download()
    
    print("=" * 50)
    print("Test completati!")
    print("\nPer avviare il programma principale:")
    print("  python simple_downloader.py")
    print("\nOppure esegui:")
    print("  start.bat")


if __name__ == "__main__":
    main()
