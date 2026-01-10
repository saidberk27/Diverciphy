import os
import socket
from dotenv import load_dotenv
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from src.utils.clear_memory import clear_memory
from src.utils.timestamp_consistency_checker import is_timestamp_consistent
import requests

class Assemble:
    def __init__(self, components):
        self.components = components
        self.__key_name = "generated"
        self.key_path = f"../../keys/generated_keys/{self.__key_name}"
        os.makedirs(os.path.dirname(self.key_path), exist_ok=True)

    @clear_memory
    def generate_and_save_keys(self, password: str, file_path: str = None):
        if file_path is None:
            file_path = self.key_path

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

    @clear_memory
    def receive_metadata(self):
        pass
    
    @clear_memory
    def receive_encrypted_data_parts(self):
        distributors = os.getenv("ASSEMBLER_ADRESSES")
        
        if not distributors:
            print("Error: any assembler adress did not found.")
            return

        encrypted_parts = {}
        timestamp_average = 0
        #TODO: Make here more ACID compliant by adding retries and timeouts.
        for addr in eval(distributors):
            addr_final = f"{addr}/last"
            try:
                response = requests.get(addr_final)
                if response.status_code == 200:
                    encrypted_part = response.content
                    distributor_index = response.headers.get("Distributor-Index", "Unknown")
                    timestamp = response.headers.get("Timestamp", "Unknown")
                    encrypted_parts.update({distributor_index: [encrypted_part, timestamp]})
                    print(f"Success: Data received from {addr} length: {len(encrypted_part)} bytes")
                    
                else:
                    print(f"Error: Data could not received from {addr} status code: {response.status_code}")
            except Exception as e:
                print(f"Error: Exception occurred while receiving data from {addr}. {e}")

    @clear_memory
    def assemble_encrypted_data(self):
        metadata = self.receive_metadata()
        encrypted_parts = self.receive_encrypted_data_parts()

        timestamps = []
        for i in metadata: # [3,4,1,0,2]
            part_index = metadata[i]
            part_data = encrypted_parts.get(part_index)
            if part_data:
                encrypted = part_data[0]
                encrypted_data += encrypted
                timestamp = part_data[1]
                timestamps.append(int(timestamp))
            else:
                print(f"ACID Error: Part {part_index} not found in received parts.") # Metadata and received parts mismatch. 

        print("ACID Info: Checking timestamp consistency...")
        

        if(utils.is_timestamp_consistent(timestamps)):
            print("ACID Info: Timestamps are consistent. Encypted data assembled successfully.")
            return encrypted_data

        else:
            print("ACID Error: Timestamps are not consistent. Aborting assembly.")
            return None

    def decrypt_data(self, encrypted_data: bytes, password: str):
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
    assemble.receive_encrypted_data_parts()