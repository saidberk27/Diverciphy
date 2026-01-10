import os
from datetime import datetime
from flask import Flask, request, jsonify
from src.utils.write_file import write_file
from src.utils.auth import Auth

app = Flask(__name__) #TODO: Create global architecture for app object.

#@Auth.login_required
def recieve_shred():
    try:
        data = request.get_json(silent=True)

        if not data or 'shred' not in data or 'timestamp' not in data:
            return jsonify({"error": "Invalid JSON. 'shred' and 'timestamp' are required."}), 400

        incoming_shred = data['shred']
        incoming_time = data['timestamp']

        file_path = f'../../shreds/recieved_shreds/shred_{incoming_time}.pem'

        write_file(file_path=file_path, data=incoming_shred, timestamp=incoming_time)

        return jsonify({
            "status": "success",
            "message": "shred saved with sender timestamp"
        }), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5003)