import os
import shutil
from flask import Flask, jsonify
# Kendi sınıf yollarını kontrol etmeyi unutma
from src.core.assemble import Assemble
from src.core.shred import Shred

app = Flask(__name__)

def clean_keys_directory():
    paths = ["src/core/keys", "keys"]
    for path in paths:
        if os.path.exists(path):
            shutil.rmtree(path)

def run_internal_test():
    try:
        clean_keys_directory()
        
        TEST_PAYLOAD = "Auto-Health Check Verisi"
        TEST_PASSWORD = "health_check_pass_123"
        
        assembler = Assemble(components=[])
        assembler.generate_and_save_keys(password=TEST_PASSWORD)
        
        shredder = Shred(payload=TEST_PAYLOAD, password=TEST_PASSWORD, assemblers=[])
        shredder.recieve_public_key()
        encrypted_data = shredder.encrypt(TEST_PAYLOAD)
        
        decrypted_bytes = assembler.decrypted_data(encrypted_data, password=TEST_PASSWORD)
        
        if decrypted_bytes and decrypted_bytes.decode('utf-8') == TEST_PAYLOAD:
            return True, "✅ System is healthy. Crypto operations successful."
        return False, "❌ Crypto operation failed: Decrypted data does not match original."
        
    except Exception as e:
        return False, f"Sistem Hatası: {str(e)}"

@app.route('/crypto/health', methods=['GET'])
def check_health():
    success, message = run_internal_test()
    
    if success:
        return jsonify({
            "status": "success",
            "integration_test": "PASSED",
            "message": f"{message}",
            "timestamp": "Aktif" # İstersen buraya datetime ekleyebilirsin
        }), 200
    else:
        return jsonify({
            "status": "danger",
            "integration_test": "FAILED",
            "message": message
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)