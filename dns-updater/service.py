from flask import Flask, request, jsonify
import os
import subprocess
app = Flask(__name__)
UPLOAD_FOLDER = "/etc/named"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/zone', methods=['POST'])
def receive_zone_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    try:
        file.save(file_path)
        subprocess.run(["sudo", "systemctl", "restart", "named"], check=True)
        return jsonify({"message": f"File {file.filename} saved and named service restarted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6363)

