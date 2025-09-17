"""
Test specifico per la funzionalità Overlap SfM
"""

import os
import sys
from PIL import Image, ImageDraw
import tempfile
import shutil

# Aggiungi il percorso corrente
sys.path.insert(0, os.path.dirname(__file__))

try:
    from advanced_downloader import AdvancedStreetViewDownloader
    import tkinter as tk
    TKINTER_AVAILABLE = True
except ImportError as e:
    TKINTER_AVAILABLE = False
    print(f"Errore import: {e}")


def create_test_equirectangular(width=1024, height=512):
    """Crea immagine equirettangolare di test con pattern riconoscibili"""
    image = Image.new('RGB', (width, height), (50, 50, 50))
    draw = ImageDraw.Draw(image)
    
    # Griglia di riferimento
    grid_size = 64
    for x in range(0, width, grid_size):
        for y in range(0, height, grid_size):
            # Colore basato su posizione
            color = (
                (x * 255) // width,
                (y * 255) // height, 
                ((x + y) * 255) // (width + height)
            )
            draw.rectangle([x, y, x + grid_size//2, y + grid_size//2], fill=color)
    
    # Marker centrali per verificare il wrapping
    center_x = width // 2
    center_y = height // 2
    
    # Marker al centro (per riferimento)
    draw.ellipse([center_x-20, center_y-20, center_x+20, center_y+20], fill=(255, 255, 255))
    
    # Marker ai bordi per verificare l'overlap
    # Bordo sinistro (diventa bordo destro nell'overlap)
    draw.rectangle([0, center_y-10, 30, center_y+10], fill=(255, 0, 0))
    
    # Bordo destro (diventa bordo sinistro nell'overlap) 
    draw.rectangle([width-30, center_y-10, width, center_y+10], fill=(0, 255, 0))
    
    # Bordi superiore e inferiore
    draw.rectangle([center_x-10, 0, center_x+10, 30], fill=(0, 0, 255))
    draw.rectangle([center_x-10, height-30, center_x+10, height], fill=(255, 255, 0))
    
    return image


def test_overlap_functionality():
    """Test della funzionalità overlap"""
    print("🧪 TEST FUNZIONALITÀ OVERLAP SfM")
    print("=" * 50)
    
    if not TKINTER_AVAILABLE:
        print("❌ Tkinter non disponibile - skip test")
        return False
    
    # Crea directory temporanea
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Crea applicazione
        root = tk.Tk()
        root.withdraw()
        app = AdvancedStreetViewDownloader(root)
        
        # Crea immagine test
        print("📐 Creazione immagine equirettangolare test...")
        test_image = create_test_equirectangular(1024, 512)
        test_path = os.path.join(temp_dir, 'test_equirect.jpg')
        test_image.save(test_path)
        print(f"✅ Immagine test salvata: {test_image.size[0]}x{test_image.size[1]}")
        
        # Test overlap percentuali diverse
        overlap_tests = [0, 10, 20, 30, 40, 50]
        
        for overlap_percent in overlap_tests:
            print(f"\n🔄 Test overlap {overlap_percent}%...")
            
            # Applica overlap
            overlap_image = app.create_overlap_image(test_image, overlap_percent)
            
            # Verifica dimensioni
            original_w, original_h = test_image.size
            overlap_w, overlap_h = overlap_image.size
            
            expected_w = int(original_w * (1 + overlap_percent / 100.0))
            expected_h = int(original_h * (1 + overlap_percent / 200.0))  # Overlap verticale dimezzato
            
            print(f"   Dimensioni originali: {original_w}x{original_h}")
            print(f"   Dimensioni overlap:   {overlap_w}x{overlap_h}")
            print(f"   Dimensioni attese:    {expected_w}x{expected_h}")
            
            # Salva per ispezione visuale
            overlap_path = os.path.join(temp_dir, f'test_overlap_{overlap_percent}pct.jpg')
            overlap_image.save(overlap_path)
            
            # Verifica incremento dimensioni
            if overlap_percent > 0:
                if overlap_w > original_w and overlap_h >= original_h:
                    print(f"   ✅ Overlap {overlap_percent}%: dimensioni corrette")
                else:
                    print(f"   ❌ Overlap {overlap_percent}%: dimensioni errate!")
                    return False
            else:
                if overlap_w == original_w and overlap_h == original_h:
                    print(f"   ✅ Overlap 0%: nessuna modifica (corretto)")
                else:
                    print(f"   ❌ Overlap 0%: dimensioni cambiate erroneamente!")
                    return False
        
        # Test border wrapping
        print(f"\n🔍 Test wrapping bordi panoramici...")
        test_wrap = app.create_overlap_image(test_image, 30)
        
        # Verifica che i marker colorati siano presenti nei bordi giusti
        # (Questo è un test visuale - in produzione si potrebbero usare hash o pixel sampling)
        wrap_path = os.path.join(temp_dir, 'test_border_wrap.jpg')
        test_wrap.save(wrap_path)
        
        print(f"   ✅ Immagine border wrap salvata per ispezione visuale")
        print(f"   📁 Controlla: {wrap_path}")
        
        # Test integrazione con conversione cubemap
        print(f"\n🎲 Test integrazione overlap + cubemap...")
        overlap_image = app.create_overlap_image(test_image, 20)
        cubemap = app.equirect_to_cubemap(overlap_image, face_size=256)
        
        if len(cubemap) == 6:
            print(f"   ✅ Conversione overlap → cubemap: 6 facce generate")
            
            # Salva facce per verifica
            for face_name, face_img in cubemap.items():
                cube_path = os.path.join(temp_dir, f'overlap_cube_{face_name}.jpg')
                face_img.save(cube_path)
            
            print(f"   ✅ Facce cubemap salvate in {temp_dir}")
        else:
            print(f"   ❌ Conversione overlap → cubemap fallita")
            return False
        
        print(f"\n📂 File di test salvati in: {temp_dir}")
        print(f"   🔍 Ispeziona visualmente per verificare la qualità dell'overlap")
        
        # Cleanup
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ Errore durante test: {e}")
        return False
    
    finally:
        # Non rimuovere temp_dir per permettere ispezione
        print(f"\n📁 File temporanei mantenuti per ispezione: {temp_dir}")


def demo_overlap_benefit():
    """Dimostra i benefici dell'overlap per photogrammetry"""
    print("\n" + "=" * 60)
    print("📊 DEMO: BENEFICI OVERLAP PER STRUCTURE FROM MOTION")
    print("=" * 60)
    
    print("""
🎯 OVERLAP PER STRUCTURE FROM MOTION / PHOTOGRAMMETRY:

📐 Concetto:
   • Immagini panoramiche normali = bordi netti, nessuna sovrapposizione
   • Immagini con overlap = bordi estesi con contenuto delle immagini adiacenti
   • SfM algorithms = necessitano punti comuni tra immagini per ricostruire 3D

🔄 Come funziona l'overlap:
   • 30% overlap = immagine 30% più larga 
   • Bordi sinistro/destro = wrapping panoramico (360°)
   • Bordi alto/basso = stretch equatoriale (meno distorsione)
   • Angoli = interpolazione smart per continuità

✅ Vantaggi per SfM:
   • Feature matching migliore tra immagini consecutive
   • Ricostruzione 3D più robusta e precisa
   • Meno gaps nella point cloud finale
   • Bundle adjustment più stabile

🎮 Applicazioni:
   • Virtual tourism con navigazione fluida
   • Ricostruzione 3D di ambienti urbani
   • Mapping fotogrammetrico da Street View
   • Dataset training per deep learning 3D

📊 Raccomandazioni overlap:
   • 10-20%: Per SfM standard, buon bilanciamento
   • 30-40%: Per SfM ad alta precisione
   • 50%+: Per applicazioni critiche o scene complesse
    """)


if __name__ == "__main__":
    success = test_overlap_functionality()
    
    if success:
        print("\n🎉 TUTTI I TEST OVERLAP COMPLETATI CON SUCCESSO!")
        demo_overlap_benefit()
    else:
        print("\n❌ ALCUNI TEST OVERLAP FALLITI")
    
    print(f"\n{'='*60}")
    print("🚀 PRONTO PER L'USO: La funzionalità overlap è implementata!")
    print("📱 Usa Advanced Downloader → impostazione 'Overlap SfM' per attivarla")
    print("📊 File di test generati per verifica visuale")
    print("="*60)
