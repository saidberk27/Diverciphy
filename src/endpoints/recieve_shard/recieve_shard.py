import os
from datetime import datetime
from flask import Flask, request, jsonify
from src.utils.write_file import write_file

app = Flask(__name__) #TODO: Create global architecture for app object.
@app.route('/recieve_shard', methods=['POST'])
def recieve_shard():
    data = request.get_json(silent=True)

    if not data or 'shard' not in data or 'timestamp' not in data:
        return jsonify({"error": "Invalid JSON. 'shard' and 'timestamp' are required."}), 400

    incoming_shard = data['shard']
    incoming_time = data['timestamp']

    file_path = f'../../shards/recieved_shards/shard_{incoming_time}.pem'

    write_file(file_path=file_path, data=incoming_shard, timestamp=incoming_time)

    return jsonify({
        "status": "success",
        "message": "Shard saved with sender timestamp"
    }), 200