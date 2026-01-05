import os
import socket
from dotenv import load_dotenv
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from src.utils.clear_memory import clear_memory

class Assemble:
    def __init__(self, components):
        self.components = components
        self.__key_name = "assemble_key"
        self.key_path = f"keys/{self.__key_name}"
        os.makedirs(os.path.dirname(self.key_path), exist_ok=True)

    @clear_memory
    def generate_and_save_keys(self, password: str):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        encryption = serialization.BestAvailableEncryption(password.encode())


        with open(f"{self.key_path}_private.pem", "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=encryption
            ))
        
        self.__save_public_key(private_key)

        print(f"[!] {self.__key_name}_private.pem güvenli şekilde oluşturuldu.")
    
    @clear_memory
    def __save_public_key(self, private_key):
        public_key = private_key.public_key()
        with open(f"{self.key_path}_public.pem", "wb") as f:
            f.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))
        print(f"[!] {self.__key_name}_public.pem güvenli şekilde oluşturuldu.")


    @clear_memory
    def __load_private_key(self, password: str):
        try:
            with open(f"keys/{self.__key_name}_private.pem", "rb") as f:
                key_data = f.read()

            private_key = serialization.load_pem_private_key(
                key_data,
                password=password.encode()
            )
            return private_key
        except Exception as e:
            print(f"Hata: Anahtar yüklenemedi. Şifre yanlış olabilir. {e}")
            return None

    def send_public_key(self):
        """
        Public key always being transmitted as a pem file.
        Public key always being transmitted from B1 -> A1 (Assembler1 Node to Distributor1 Node)
        """
        try:
            with open(f"keys/{self.__key_name}_public.pem", "rb") as f:
                public_key_data = f.read()

            #TODO: socket logic will be here to send the public key to Distributor1 Node using k8s service.
            return public_key_data
        except Exception as e:
            print(f"Hata: Genel anahtar yüklenemedi. {e}")
            return None

    
    def receive_encrypted_data_parts(self, encrypted_parts: list[bytes], password: str):
        # Different parts received from different distributors will be merged here.
        pass

    def decrypted_data(self, encrypted_data: bytes, password: str):
        private_key = self.__load_private_key(password)
        if not private_key:
            print("Hata: Özel anahtar yüklenemedi, şifre yanlış olabilir.")
            return None

        try:
            decrypted_data = private_key.decrypt(
                encrypted_data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return decrypted_data
            
        except Exception as e:
            print(f"Hata: Veri çözülemedi. {e}")
            return None

if __name__ == "__main__":
    load_dotenv()
    password = os.getenv("FILE_PASSWORD")
    assemble = Assemble(components=[])
    assemble.generate_and_save_keys(password = password)