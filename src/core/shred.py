import os
from dotenv import load_dotenv
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import random

class Shred:
    def __init__(self, payload, assemblers, password : str): #Delete password after testing.
        self.payload = payload
        self.password = password
        self.assemblers = assemblers
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        self.public_key = self.private_key.public_key()
        self.key_name = "assemble_key" #XXX: Delete here after testing.


    def load_public_key(self):
        """
        Geliştirme amaçlı: Yerel dosyadan genel anahtarı yükler.
        Public Key şifreli OLMAZ, bu yüzden password parametresi kaldırıldı.
        """
        try:
            path = f"keys/{self.key_name}_public.pem"
            with open(path, "rb") as f:
                key_data = f.read()

            # Public key yüklenirken password kullanılmaz
            public_key = serialization.load_pem_public_key(key_data)
            
            print(f"Başarılı: {path} yüklendi.")
            return public_key
        except Exception as e:
            print(f"Hata: Anahtar yüklenemedi. {e}")
            return None

    def recieve_public_key(self):
        """ 
        Public key always being transmitted as a pem file.
        Public key always being transmitted from B1 -> A1 (Assembler1 Node to Distributor1 Node)
        Delete after real implementation.
        """     
        # TODO: Public key recieve logic will be implemented here.
        self.public_key = self.load_public_key()
        public_key_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        print(f"Public key received successfully. {public_key_bytes.decode()}")
    
    def encrypt(self, payload : str) -> bytes:
        if(self.public_key is None):
            print("Hata: Public key yüklenemediği için şifreleme yapılamıyor.")
            return None
        
        
        sifreli_metin = self.public_key.encrypt(
            payload.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        print(f"Cyphered Text: {sifreli_metin.hex()}")
        return sifreli_metin

    def shred_encrypted_data(self, encrypted_data: bytes) -> tuple[list[bytes], bytes]:
        """
        Splits and shuffles the encrypted data into n (assembler count) parts,
        then creates and encrypts metadata indicating original positions.
        """
        assembler_count = len(self.assemblers)
        total_len = len(encrypted_data)
        chunk_size = total_len // assembler_count
    
        parts_with_index = []
        start = 0

        for i in range(assembler_count):
            if i == assembler_count - 1: # last takes the remainder
                part = encrypted_data[start:]
            else:
                end = start + chunk_size
                part = encrypted_data[start:end]
                start = end
            
            parts_with_index.append((i, part))

        random.shuffle(parts_with_index)

        shredded_data = []
        indices = []

        for original_index, part in parts_with_index:
            shredded_data.append(part)
            indices.append(str(original_index))

        metadata_str = "POSITION-" + ",".join(indices)
        encrypted_metadata = self.encrypt(metadata_str)

        return shredded_data, encrypted_metadata

if __name__ == "__main__":
    load_dotenv()
    password = os.getenv("FILE_PASSWORD")
    assemblers = os.getenv("ASSEMBLER_ADRESSES").split(",")
    shred = Shred(payload="Sifrele beni", assemblers=assemblers, password=password)
    shred.recieve_public_key()
        