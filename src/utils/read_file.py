from dotenv import load_dotenv
import os
from src.core.assemble import Assemble

def read_file(file_path: str):
    try:
        load_dotenv()
        assembler = Assemble(components=[])
        assembler.generate_and_save_keys(password=os.environ.get("FILE_PASSWORD"), file_path=file_path)
        
        with open(file_path, 'rb') as f:
            return f.read().decode('utf-8')

    except Exception as e:
        print(f"Error reading public key from file: {e}")
        return None
