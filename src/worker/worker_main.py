import os
import argparse
from flask import Flask, jsonify
from dotenv import load_dotenv  # Dotenv kütüphanesini ekledik
from src.utils.get_public_ip import get_public_ip
from src.endpoints import recieve_shred, send_shred

class Worker:
    def __init__(self, app: Flask):
        self.app = app
        
        try:
            self.shredder_address = os.getenv("SHREDDER_ADDRESS", "")
            self.master_address = os.getenv("MASTER_ADDRESS", "")
            self.machine_type = os.getenv("MACHINE_TYPE", "WORKER")
            self.address = get_public_ip()

            if (not self.shredder_address) or (not self.master_address):
                print("[!] Warning: SHREDDER_ADDRESS or MASTER_ADDRESS missing.")
            
            print(f"[!] Worker initialized. IP: {self.address}")
            print(f"[!] Target Master: {self.master_address}")

        except Exception as e:
            print("[-] Error initializing settings:", str(e))

        self._register_routes()

    def _register_routes(self):
        self.app.add_url_rule('/recieve_shred', view_func=recieve_shred.recieve_shred, methods=['POST'])
        self.app.add_url_rule('/send_shred', view_func=send_shred.send_shred, methods=['GET', 'POST'])
        self.app.add_url_rule('/health', view_func=lambda: jsonify({"status": "healthy"}), methods=['GET'])

    def run(self, debug=True, port=5000):
        self.app.run(debug=debug, port=port)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Worker Node Başlatıcı")
    
    parser.add_argument('--port', type=int, default=5555, help='Çalıştırılacak port numarası')
    parser.add_argument('--env', type=str, default='.worker_env1_a', help='Yüklenecek .env dosyasının adı')
    
    args = parser.parse_args()

    if os.path.exists(args.env):
        load_dotenv(dotenv_path=args.env, override=True)
        print(f"[+] Configuration loaded from: {args.env}")
    else:
        print(f"[!] Warning: {args.env} file not found!")

    app = Flask(__name__) 
    worker = Worker(app)
    
    print(f"[*] Worker port {args.port} üzerinde başlatılıyor...")
    worker.run(debug=True, port=args.port)