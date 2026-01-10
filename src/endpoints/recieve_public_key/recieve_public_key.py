from flask import Flask, request, jsonify
import os
from src.utils.write_file import write_file
app = Flask(__name__) #TODO: Create global architecture for app object.

@app.route('/recieve_public_key', methods=['POST'])
def recieve_public_key():
    data = request.get_json(silent=True)

    print(f"Public Key Recieved: {data['public_key']}")

    if not data:
        return jsonify({"hata": "JSON gövdesi boş veya hatalı!"}), 400
    write_file(file_path = '../../keys/recieved_keys/recieved_key.pem', data = data['public_key'])
    return jsonify({"durum": "basarili"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)
        