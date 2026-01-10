from flask import Flask, request, jsonify
from src.core.assemble import Assemble
from dotenv import load_dotenv
import os
app = Flask(__name__) #TODO: Create global architecture for app object.

def read_public_key_from_file(file_path: str):
    try:
        with open(file_path, 'rb') as f:
            return f.read().decode('utf-8')
    except Exception as e:
        try:
            print(f"Error reading public key from file: {e}")
            load_dotenv()
            assembler = Assemble(components=[])
            assembler.generate_and_save_keys(password=os.environ.get("FILE_PASSWORD"), file_path=file_path)
            with open(file_path, 'rb') as f:
                return f.read().decode('utf-8')
        except Exception as e:
            print(f"Error generating new keys and reading public key: {e}")
            return None

    except Exception as e:
        print(f"Error reading public key from file: {e}")
        return None

@app.route('/send_public_key', methods=['GET'])
def send_public_key():
    public_key = read_public_key_from_file('../../keys/generated_keys/generated_public.pem')
    if not public_key:
        return jsonify({"hata": "Public key okunamadı!"}), 500
    return jsonify({"public_key": public_key}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
        