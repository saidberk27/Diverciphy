import os
import sys
import shutil
from unittest.mock import MagicMock

# --- ORTAM AYARLAMASI (MOCKING) ---
# Eğer 'src.utils.clear_memory' modülü yoksa, kodun hata vermemesi için
# geçici bir "dummy" decorator tanımlıyoruz. Bu sayede kodların değişmeden çalışır.
try:
    from src.utils.clear_memory import clear_memory
except ImportError:
    print("[TEST BİLGİSİ] 'src.utils.clear_memory' bulunamadı, test için mocklanıyor...")
    mock_utils = MagicMock()
    # Decorator fonksiyonu (girdiyi olduğu gibi çıktı veren fonksiyon)
    mock_utils.clear_memory = lambda func: func 
    sys.modules["src"] = MagicMock()
    sys.modules["src.utils"] = MagicMock()
    sys.modules["src.utils.clear_memory"] = mock_utils

# --- SINIF IMPORTLARI ---
# Dosya isimlerini kendi kaydettiğin isimlere göre düzenleyebilirsin
try:
    from src.core.assemble import Assemble
    from src.core.shred import Shred
except ImportError as e:
    print(f"[HATA] Sınıf dosyaları bulunamadı. Lütfen dosya adlarını kontrol et: {e}")
    sys.exit(1)

def clean_keys_directory():
    """Test öncesi temiz bir ortam için keys klasörünü temizler."""
    if os.path.exists("src/core/keys"):
        shutil.rmtree("src/core/keys")
    print("[TEST] Keys klasörü temizlendi.")

def integration_test():
    print("\n--- ENTEGRASYON TESTİ BAŞLIYOR ---\n")

    # 1. Test Verileri
    TEST_PAYLOAD = "Test Verisi. 721"
    TEST_PASSWORD = "guclu_bir_sifre_123"
    
    # 2. Assemble (B1 Node) Başlatılıyor
    print(f"[ADIM 1] Assemble (Alıcı) başlatılıyor...")
    assembler = Assemble(components=[])
    
    # 3. Anahtarların Oluşturulması (Generate)
    # Bu adımda keys/assemble_key_private.pem ve keys/assemble_key_public.pem oluşmalı
    assembler.generate_and_save_keys(password=TEST_PASSWORD)
    
    # Kontrol: Dosyalar oluştu mu?
    if not os.path.exists("keys/assemble_key_public.pem"):
        print("[HATA] Public key oluşturulamadı!")
        return

    # 4. Shred (A1 Node / Distributor) Başlatılıyor
    print(f"\n[ADIM 2] Shred (Gönderici) başlatılıyor...")
    shredder = Shred(payload=TEST_PAYLOAD, password=TEST_PASSWORD, assemblers=[])
    
    # 5. Public Key Transferi Simülasyonu
    # Shred sınıfı diskteki public key'i okur (B1 -> A1 transferi simülasyonu)
    shredder.recieve_public_key()
    
    # 6. Şifreleme (Encryption)
    print(f"[ADIM 3] Veri şifreleniyor...")
    encrypted_data = shredder.encrypt(TEST_PAYLOAD)
    
    if not encrypted_data:
        print("[HATA] Şifreleme başarısız oldu.")
        return

    print(f"[BİLGİ] Şifreli veri uzunluğu: {len(encrypted_data)} bytes")

    # 7. Deşifreleme (Decryption - Assemble Tarafı)
    print(f"\n[ADIM 4] Assemble tarafında veri çözülüyor...")
    decrypted_bytes = assembler.decrypted_data(encrypted_data, password=TEST_PASSWORD)
    
    # 8. Doğrulama (Verification)
    if decrypted_bytes:
        decrypted_text = decrypted_bytes.decode('utf-8')
        print(f"\n[SONUÇ] Çözülen Veri: {decrypted_text}")
        
        if decrypted_text == TEST_PAYLOAD:
            print("\nTEST BAŞARILI: Gönderilen ve çözülen veri birebir eşleşiyor.")
        else:
            print("\nTEST BAŞARISIZ: Veriler eşleşmedi.")
            print(f"Beklenen: {TEST_PAYLOAD}")
            print(f"Gelen:    {decrypted_text}")
    else:
        print("\nTEST BAŞARISIZ: Veri çözülemedi (None döndü).")

if __name__ == "__main__":
    # Önceki testlerden kalanları temizle
    clean_keys_directory()
    
    # Testi çalıştır
    integration_test()