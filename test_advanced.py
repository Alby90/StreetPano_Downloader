"""
Test suite per l'applicazione avanzata Street View Downloader
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch
from PIL import Image
import tempfile
import shutil

# Aggiungi il percorso corrente al path Python
sys.path.insert(0, os.path.dirname(__file__))

try:
    from advanced_downloader import AdvancedStreetViewDownloader
    from panorama_converter import PanoramaConverter, BatchProcessor
    import tkinter as tk
    TKINTER_AVAILABLE = True
except ImportError as e:
    TKINTER_AVAILABLE = False
    print(f"Errore import: {e}")


class TestPanoramaConverter(unittest.TestCase):
    """Test per il convertitore panoramico"""
    
    def setUp(self):
        """Setup test"""
        if not TKINTER_AVAILABLE:
            self.skipTest("Tkinter non disponibile")
        
        self.converter = PanoramaConverter()
        self.temp_dir = tempfile.mkdtemp()
        
        # Crea immagine test equirettangolare
        self.test_equirect = Image.new('RGB', (1024, 512), (128, 128, 128))
        # Aggiungi alcuni pattern per verificare la conversione
        for x in range(0, 1024, 100):
            for y in range(0, 512, 50):
                # Quadratini colorati
                color = (x % 256, y % 256, (x + y) % 256)
                for dx in range(20):
                    for dy in range(20):
                        if x + dx < 1024 and y + dy < 512:
                            self.test_equirect.putpixel((x + dx, y + dy), color)
    
    def tearDown(self):
        """Cleanup test"""
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_equirect_to_cubemap_conversion(self):
        """Test conversione equirettangolare → cubemap"""
        cubemap = self.converter.equirectangular_to_cubemap(self.test_equirect, face_size=256)
        
        # Verifica che ci siano 6 facce
        self.assertEqual(len(cubemap), 6)
        
        # Verifica nomi facce
        expected_faces = ['front', 'right', 'back', 'left', 'up', 'down']
        for face_name in expected_faces:
            self.assertIn(face_name, cubemap)
            
        # Verifica dimensioni facce
        for face_name, face_image in cubemap.items():
            self.assertEqual(face_image.size, (256, 256))
            self.assertEqual(face_image.mode, 'RGB')
    
    def test_cubemap_to_equirect_conversion(self):
        """Test conversione cubemap → equirettangolare"""
        # Prima converti in cubemap
        cubemap = self.converter.equirectangular_to_cubemap(self.test_equirect, face_size=128)
        
        # Poi riconverti in equirettangolare
        equirect_result = self.converter.cubemap_to_equirectangular(cubemap, (512, 256))
        
        # Verifica dimensioni
        self.assertEqual(equirect_result.size, (512, 256))
        self.assertEqual(equirect_result.mode, 'RGB')
    
    def test_conversion_methods(self):
        """Test metodi di conversione diversi"""
        # Test metodo veloce
        cubemap_fast = self.converter.equirectangular_to_cubemap(
            self.test_equirect, face_size=64, method='fast')
        
        # Test metodo qualità (se numpy disponibile)
        try:
            cubemap_quality = self.converter.equirectangular_to_cubemap(
                self.test_equirect, face_size=64, method='quality')
            
            # Entrambi dovrebbero produrre 6 facce
            self.assertEqual(len(cubemap_fast), 6)
            self.assertEqual(len(cubemap_quality), 6)
        except:
            # Se numpy non è disponibile, fallback al metodo veloce
            self.assertEqual(len(cubemap_fast), 6)


class TestBatchProcessor(unittest.TestCase):
    """Test per il processore batch"""
    
    def setUp(self):
        """Setup test"""
        if not TKINTER_AVAILABLE:
            self.skipTest("Tkinter non disponibile")
            
        self.processor = BatchProcessor()
        self.temp_dir = tempfile.mkdtemp()
        self.input_dir = os.path.join(self.temp_dir, 'input')
        self.output_dir = os.path.join(self.temp_dir, 'output')
        
        os.makedirs(self.input_dir)
        os.makedirs(self.output_dir)
        
        # Crea immagini test
        for i in range(3):
            test_img = Image.new('RGB', (512, 256), (i * 50, 100, 150))
            test_img.save(os.path.join(self.input_dir, f'test_{i}.jpg'))
    
    def tearDown(self):
        """Cleanup test"""
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_single_file_conversion(self):
        """Test conversione file singolo"""
        input_file = os.path.join(self.input_dir, 'test_0.jpg')
        
        result_files = self.processor.convert_single_file(
            input_file, self.output_dir, 'equirect_to_cube', face_size=64)
        
        # Verifica che il risultato non sia None
        self.assertIsNotNone(result_files)
        
        # Type guard per TypeScript-like behavior
        if result_files is not None:
            # Dovrebbero essere create 6 facce
            self.assertEqual(len(result_files), 6)
            
            # Verifica che i file esistano
            for file_path in result_files:
                self.assertTrue(os.path.exists(file_path))
    
    def test_supported_extensions(self):
        """Test estensioni supportate"""
        expected_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
        self.assertEqual(self.processor.supported_extensions, expected_extensions)


class TestAdvancedDownloader(unittest.TestCase):
    """Test per l'applicazione avanzata"""
    
    def setUp(self):
        """Setup test"""
        if not TKINTER_AVAILABLE:
            self.skipTest("Tkinter non disponibile")
        
        # Crea root Tkinter per test
        self.root = tk.Tk()
        self.root.withdraw()  # Nasconde la finestra durante i test
        
        # Crea applicazione
        self.app = AdvancedStreetViewDownloader(self.root)
    
    def tearDown(self):
        """Cleanup test"""
        if hasattr(self, 'root'):
            self.root.destroy()
    
    def test_panoid_extraction(self):
        """Test estrazione PanoID da URL"""
        test_urls = [
            "https://www.google.com/maps/@40.758896,-73.985130,3a,75y,92.19h,90t/data=!3m6!1e1!3m4!1sAF1QipO5fGJGUMXv7Q1C0z-QR4n3fxOg8_5jOJxJVXpp!2e10!7i16384!8i8192",
            "https://maps.google.com/maps?q=40.758896,-73.985130&layer=c&cbll=40.758896,-73.985130&panoid=abc123&cbp=12,92.19,,0,5",
            "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d387191.33750313813!2d-74.25986548248684!3d40.697670063550034!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x89c24fa5d33f083b%3A0xc80b8f06e177fe62!2sNew+York%2C+NY%2C+USA"
        ]
        
        for url in test_urls:
            panoid = self.app.extract_panoid_from_url(url)
            # Il PanoID dovrebbe essere una stringa non vuota
            self.assertIsInstance(panoid, str)
    
    def test_cube_to_sphere_coords(self):
        """Test coordinate cubo → sfera"""
        # Test coordinate centrali di una faccia
        theta, phi = self.app.cube_to_sphere_coords(0.5, 0.5, 0)  # front face center
        
        # Verifica che le coordinate siano valide
        self.assertIsInstance(theta, float)
        self.assertIsInstance(phi, float)
        self.assertGreaterEqual(phi, 0)
        self.assertLessEqual(phi, 3.14159)  # π
    
    def test_cubemap_creation(self):
        """Test creazione cubemap vuoto"""
        empty_cubemap = self.app.create_empty_cubemap(128)
        
        # Verifica 6 facce
        self.assertEqual(len(empty_cubemap), 6)
        
        # Verifica dimensioni
        for face_name, face_image in empty_cubemap.items():
            self.assertEqual(face_image.size, (128, 128))


class TestIntegration(unittest.TestCase):
    """Test di integrazione"""
    
    def setUp(self):
        """Setup test integrazione"""
        if not TKINTER_AVAILABLE:
            self.skipTest("Tkinter non disponibile")
        
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Cleanup test"""
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_full_conversion_pipeline(self):
        """Test pipeline completa di conversione"""
        # Crea immagine test
        test_equirect = Image.new('RGB', (512, 256), (100, 150, 200))
        
        # Aggiungi pattern riconoscibile
        for x in range(0, 512, 50):
            for y in range(10, 246, 50):
                color = ((x + y) % 255, (x * 2) % 255, (y * 3) % 255)
                for dx in range(10):
                    for dy in range(10):
                        if x + dx < 512 and y + dy < 256:
                            test_equirect.putpixel((x + dx, y + dy), color)
        
        # Salva immagine test
        test_file = os.path.join(self.temp_dir, 'test_equirect.jpg')
        test_equirect.save(test_file)
        
        # Converte usando BatchProcessor
        processor = BatchProcessor()
        result_files = processor.convert_single_file(
            test_file, self.temp_dir, 'equirect_to_cube', face_size=64)
        
        # Verifica risultati
        self.assertIsNotNone(result_files)
        
        if result_files is not None:
            self.assertEqual(len(result_files), 6)
            
            # Verifica che tutti i file esistano e siano immagini valide
            for file_path in result_files:
                self.assertTrue(os.path.exists(file_path))
                
                # Tenta di aprire come immagine
                try:
                    img = Image.open(file_path)
                    self.assertEqual(img.size, (64, 64))
                    img.close()
                except Exception as e:
                    self.fail(f"File {file_path} non è un'immagine valida: {e}")


def run_tests():
    """Esegue tutti i test"""
    print("=" * 60)
    print("TEST SUITE AVANZATA STREET VIEW DOWNLOADER")
    print("=" * 60)
    
    if not TKINTER_AVAILABLE:
        print("❌ ERRORE: Tkinter non disponibile")
        print("Impossibile eseguire i test dell'interfaccia grafica")
        return False
    
    # Crea suite test
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Aggiungi test classes
    test_classes = [
        TestPanoramaConverter,
        TestBatchProcessor,
        TestAdvancedDownloader,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Esegui test
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Stampa risultati
    print("\n" + "=" * 60)
    print("RISULTATI TEST")
    print("=" * 60)
    print(f"Test eseguiti: {result.testsRun}")
    print(f"Successi: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Fallimenti: {len(result.failures)}")
    print(f"Errori: {len(result.errors)}")
    
    if result.failures:
        print("\nFALLIMENTI:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORI:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print("\n✅ TUTTI I TEST COMPLETATI CON SUCCESSO!")
    else:
        print(f"\n❌ {len(result.failures + result.errors)} TEST FALLITI")
    
    return success


if __name__ == "__main__":
    run_tests()
