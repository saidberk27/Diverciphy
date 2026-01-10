from flask import Flask, request, jsonify
import os
from src.utils.write_file import write_file
app = Flask(__name__) #TODO: Create global architecture for app object.


def recieve_metadata():
    data = request.get_json(silent=True)

    print(f"Metadata Recieved: {data['metadata']}")

    if not data:
        return jsonify({"hata": "JSON gövdesi boş veya hatalı!"}), 400
    write_file(file_path = '../../metadata/recieved_metadata/recieved_metadata.json', data = data['metadata'])
    return jsonify({"durum": "basarili"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)
        