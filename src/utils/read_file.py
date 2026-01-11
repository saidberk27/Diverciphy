from dotenv import load_dotenv
import os

def read_file(file_path: str) -> bytes:
    try:
        if not os.path.exists(file_path):
             print(f"File not found: {file_path}")
             return None

        with open(file_path, 'rb') as f:
            return f.read()

    except Exception as e:
        print(f"Error reading file: {e}")
        return None