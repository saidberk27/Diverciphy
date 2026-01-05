import unittest
import os
import shutil
from dotenv import load_dotenv

# Sınıflarını projeden import ediyoruz. 
# Eğer aynı dosyadalar ise import kısmını düzenleyebilirsin.
from src.core.shred import Shred      # Shred sınıfının olduğu dosya yolu
from src.core.assemble import Assemble # Assemble sınıfının olduğu dosya yolu

class TestShredToAssemble(unittest.TestCase):

    def setUp(self):
        """Her testten önce çalışır: Ortam ve Anahtar Hazırlığı"""
        self.password = "SuperSecretPassword123!"
        self.assemblers = ["NodeA", "NodeB", "NodeC"] # 3 Parçaya böleceğiz
        
        # Ortam değişkenlerini simüle et
        os.environ["FILE_PASSWORD"] = self.password
        os.environ["ASSEMBLER_ADRESSES"] = ",".join(self.assemblers)
        
        # Test için geçici key klasörü oluşturma (Gerekirse)
        if not os.path.exists("keys"):
            os.makedirs("keys")

        # 1. ADIM: Assemble tarafı anahtarları üretir (Private & Public)
        self.assemble = Assemble(components=[])
        self.assemble.generate_and_save_keys(password=self.password)

        # 2. ADIM: Shred tarafı (Public key'i yükler)
        self.payload_text = "Bu veri parçalanacak, karıştırılacak ve tekrar birleştirilecek."
        self.shred = Shred(
            payload=self.payload_text, 
            assemblers=self.assemblers, 
            password=self.password
        )
        self.shred.recieve_public_key() # Public key'i yükler

    def tearDown(self):
        """Test bitince temizlik yap"""
        # Oluşturulan anahtarları temizlemek istersen:
        # shutil.rmtree("keys") 
        pass

    def test_shred_and_reassemble_logic(self):
        """
        Test Akışı:
        Encrypt -> Shred (Shuffle) -> Decrypt Metadata -> Reorder -> Merge -> Decrypt Data
        """
        print("\n--- TEST BAŞLIYOR ---")

        # 1. Veriyi Şifrele (Shred sınıfı içindeki metodla)
        encrypted_full_data = self.shred.encrypt(self.payload_text)
        self.assertIsNotNone(encrypted_full_data, "Şifreleme başarısız oldu.")
        
        original_len = len(encrypted_full_data)
        print(f"Orijinal Şifreli Veri Boyutu: {original_len} bytes")

        # 2. Veriyi Parçala ve Karıştır (Shredding)
        # NOT: Shred sınıfındaki encode hatası düzeltilmelidir (Açıklamaya bakınız).
        shredded_parts, encrypted_metadata = self.shred.shred_encrypted_data(encrypted_full_data)

        # KONTROL 1: Parça sayısı assembler sayısına eşit mi?
        self.assertEqual(len(shredded_parts), len(self.assemblers), "Parça sayısı hatalı!")
        
        # KONTROL 2: Parçaların toplam boyutu orijinal veriye eşit mi?
        total_parts_len = sum(len(part) for part in shredded_parts)
        self.assertEqual(total_parts_len, original_len, "Veri kaybı var! Parçaların toplamı orijinale eşit değil.")

        print(f"Parçalar oluşturuldu: {len(shredded_parts)} adet.")

        # 3. Metadata'yı Çöz (Sıralama bilgisini almak için)
        # encrypted_metadata içinde "POSITION-2,0,1" gibi bir bilgi var.
        decrypted_meta_bytes = self.assemble.decrypted_data(encrypted_metadata, self.password)
        self.assertIsNotNone(decrypted_meta_bytes, "Metadata çözülemedi!")
        
        decrypted_meta_str = decrypted_meta_bytes.decode('utf-8')
        print(f"Çözülen Metadata: {decrypted_meta_str}")

        self.assertTrue(decrypted_meta_str.startswith("POSITION-"), "Metadata formatı hatalı!")

        # 4. Sıralamayı Parse Et
        # "POSITION-2,0,1" -> indices = [2, 0, 1]
        # Bu şu demek: 
        # shredded_parts[0] aslında orijinalin 2. parçası
        # shredded_parts[1] aslında orijinalin 0. parçası (ilk parça)
        # shredded_parts[2] aslında orijinalin 1. parçası
        indices_str = decrypted_meta_str.replace("POSITION-", "").split(",")
        indices = [int(i) for i in indices_str]

        # 5. Veriyi Yeniden Birleştir (Reassemble)
        reassembled_list = [None] * len(shredded_parts)

        for i, original_pos in enumerate(indices):
            # shredded_parts[i] -> Elimizdeki karışık listenin i. elemanı
            # original_pos -> Bu parçanın gitmesi gereken gerçek yer
            reassembled_list[original_pos] = shredded_parts[i]

        # Listeyi tek bir byte array haline getir
        reassembled_data = b"".join(reassembled_list)

        # KONTROL 3: Birleştirilen şifreli veri, orijinal şifreli veri ile aynı mı?
        self.assertEqual(reassembled_data, encrypted_full_data, "Birleştirme hatalı! Sıralama yanlış yapıldı.")
        print("Şifreli veri başarıyla orijinal sırasına göre birleştirildi.")

        # 6. Final Çözümleme (Decrypt)
        final_decrypted_bytes = self.assemble.decrypted_data(reassembled_data, self.password)
        final_text = final_decrypted_bytes.decode('utf-8')

        # KONTROL 4: Sonuç metni orijinal payload ile aynı mı?
        self.assertEqual(final_text, self.payload_text, "Veri bozuk çözüldü!")
        
        print(f"BAŞARILI! Çözülen Metin: {final_text}")

if __name__ == "__main__":
    unittest.main()