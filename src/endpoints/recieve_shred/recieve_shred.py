import os
from datetime import datetime
from flask import Flask, request, jsonify
from src.utils.write_file import write_file
from src.utils.auth import Auth
import base64
from dotenv import load_dotenv

app = Flask(__name__)

# @Auth.login_required
def recieve_shred():
    try:
        load_dotenv()
        data = request.get_json(silent=True)
        if not data or 'shred' not in data or 'timestamp' not in data:
            return jsonify({"error": "Invalid JSON. 'shred' and 'timestamp' are required."}), 400

        incoming_shred = data['shred']
        incoming_time = data['timestamp']

        worker_id = os.getenv("WORKER_INDEX", "unknown")

        file_path = f'../shreds/recieved_shreds/shred_{worker_id}.pem'
       
        write_file(file_path=file_path, data=incoming_shred)

        return jsonify({
            "status": "success",
            "message": f"shred saved by worker {worker_id}",
            "worker_id": worker_id
        }), 200

    except Exception as e:
        print(f"[-] Error: {e}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5003)