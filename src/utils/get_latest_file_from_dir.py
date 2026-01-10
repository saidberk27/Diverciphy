import os
import glob

def get_latest_file(src_relative_path, file_extension='shred_*.pem'):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    full_path = os.path.join(project_root, src_relative_path)
    search_pattern = os.path.join(full_path, file_extension)
    list_of_files = glob.glob(search_pattern)
    
    print(f"[DEBUG] Exact path searching: {search_pattern}")
    
    if not list_of_files:
        print("[!] File not found.")
        return None
    
    latest_file_path = max(list_of_files, key=os.path.getmtime)
    
    return latest_file_path