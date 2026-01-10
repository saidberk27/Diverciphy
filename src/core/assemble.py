import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from src.utils.clear_memory import clear_memory

class Assemble:
    def __init__(self, components=None):
        self.components = components or []
        self.__key_name = "generated"
        # Path to save keys
        self.key_path = os.path.join(os.getcwd(), "keys", "generated_keys", self.__key_name)
        os.makedirs(os.path.dirname(self.key_path), exist_ok=True)

    @clear_memory
    def generate_and_save_keys(self, password: str, file_path: os.path.join(os.getcwd(), "keys", "generated_keys", "generated")):
        """Generates RSA Key pair and saves them to disk."""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        encryption = serialization.BestAvailableEncryption(password.encode())

        # Save Private Key
        with open(f"{self.key_path}_private.pem", "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=encryption
            ))
        
        # Save Public Key
        self.__save_public_key(private_key)
        print(f"[Core] {self.__key_name} keys generated successfully.")
    
    @clear_memory
    def __save_public_key(self, private_key):
        public_key = private_key.public_key()
        with open(f"{self.key_path}_public.pem", "wb") as f:
            f.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))

    @clear_memory
    def __load_private_key(self, password: str):
        """Loads the private key from disk."""
        try:
            priv_path = f"{self.key_path}_private.pem"
            if not os.path.exists(priv_path):
                print(f"[Core Error] Private key not found at: {priv_path}")
                return None

            with open(priv_path, "rb") as f:
                key_data = f.read()

            private_key = serialization.load_pem_private_key(
                key_data,
                password=password.encode()
            )
            return private_key
        except ValueError:
            print("[Core Error] Incorrect password.")
            return None
        except Exception as e:
            print(f"[Core Error] Could not load key: {e}")
            return None

    def decrypt_data(self, encrypted_data: bytes, password: str):
        """Decrypts the provided encrypted byte data."""
        private_key = self.__load_private_key(password)
        if not private_key:
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
            print(f"[Core Error] Decryption failed: {e}")
            return None