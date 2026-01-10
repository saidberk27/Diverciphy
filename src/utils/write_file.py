import os

def write_file(file_path: str, data: str, timestamp: str = None, set_secure: bool = False):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        content = f'"{timestamp}","{data}"' if timestamp else data
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        if set_secure:
            os.chmod(file_path, 0o600)
            
        print(f"File successfully saved to: {file_path}")
        return True
    except Exception as e:
        print(f"Error writing file at {file_path}: {e}")
        return False