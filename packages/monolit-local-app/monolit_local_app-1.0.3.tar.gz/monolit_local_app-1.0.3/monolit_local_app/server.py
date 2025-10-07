from flask import Flask, request, jsonify, send_file, send_from_directory
from os.path import dirname
from monolit_local_app.other import sum_paths

class Monolit(Flask):
    index_path = None
    process_request = None

server = Monolit(__name__)

@server.route("/www/index.html")
def index():
    return send_file(server.index_path), 200

@server.route("/www/<path:path>")
def send_anything(path):
    return send_file(sum_paths(dirname(server.index_path), path)), 200
    
@server.route("/process", methods=["POST"])
def process_json_from_client():
    if request.method == 'POST':
        if request.is_json:
            try:
                return server.process_request(request)
            except Exception as e:
                print(f"[SERVER] Can not process JSON: {e}")
                return jsonify({"error": "Can not process JSON"}), 400
        else:
            print(f"[SERVER] Request must be in JSON format")
            return jsonify({"error": "Request must be in JSON format"}), 415
    else:
        print(f"[SERVER] Method not support")
        return jsonify({"error": "Method not support"}), 405