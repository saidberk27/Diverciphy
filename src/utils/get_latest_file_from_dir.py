import os
import glob
def get_latest_file(directory, file_extension : str = 'shard_*.pem'):
    
    list_of_files = glob.glob(os.path.join(directory, file_extension))
    
    if not list_of_files:
        return None
    
    latest_file = max(list_of_files, key=os.path.getmtime)
    return latest_file