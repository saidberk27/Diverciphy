import random
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend

class Shred:
    def __init__(self):
        self.public_key = None

    def load_public_key_from_bytes(self, key_bytes: bytes):
        """
        Loads a public key from raw bytes (PEM format).
        """
        try:
            self.public_key = serialization.load_pem_public_key(
                key_bytes,
                backend=default_backend()
            )
            print("[Core] Public key loaded successfully.")
            return True
        except Exception as e:
            print(f"[Core Error] Failed to load public key: {e}")
            return False

    def encrypt_payload(self, payload: str) -> bytes:
        """
        Encrypts the string payload using the loaded Public Key.
        """
        if self.public_key is None:
            print("[Core Error] Public key is not loaded. Cannot encrypt.")
            return None
        
        try:
            encrypted_data = self.public_key.encrypt(
                payload.encode('utf-8'),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return encrypted_data
        except Exception as e:
            print(f"[Core Error] Encryption failed: {e}")
            return None

    def encrypt_metadata(self, metadata_str: str) -> bytes:
        """
        Encrypts metadata (position info) separately.
        """
        return self.encrypt_payload(metadata_str)

    def shred_data(self, encrypted_data: bytes, num_parts: int) -> tuple[dict, bytes]:
        """
        Splits the encrypted data into 'num_parts'.
        Returns:
            - shreds_map: Dict {original_index: data_chunk_bytes}
            - encrypted_metadata: Bytes containing the shuffled order info.
        """
        total_len = len(encrypted_data)
        chunk_size = total_len // num_parts
        
        parts_with_index = []
        start = 0
        for i in range(num_parts):
            if i == num_parts - 1:
                part = encrypted_data[start:]
            else:
                end = start + chunk_size
                part = encrypted_data[start:end]
                start = end
            parts_with_index.append((i, part))

        #random.shuffle(parts_with_index)

        shreds_map = {} 
        indices = []
        
        final_shreds = [] 

        for original_index, part in parts_with_index:
            final_shreds.append((original_index, part))
            indices.append(str(original_index))

        metadata_str = "POSITION-" + ",".join(indices)
        encrypted_metadata = self.encrypt_metadata(metadata_str)

        return final_shreds, encrypted_metadata