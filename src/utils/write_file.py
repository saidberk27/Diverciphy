import os

def write_file(file_path: str, data: bytes, set_secure: bool = False):
    """
    Veriyi diske saf binary olarak yazar. Timestamp eklemesi YAPMAZ.
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)        
        with open(file_path, 'w') as f:
            f.write(data)
        
        if set_secure:
            os.chmod(file_path, 0o600)
            
        print(f"File successfully saved to: {file_path}")
        return True
    except Exception as e:
        print(f"Error writing file at {file_path}: {e}")
        return False