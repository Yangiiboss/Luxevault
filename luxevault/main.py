from flask import Flask, send_from_directory, jsonify, request
import os

# Flask looks for this variable
app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

@app.route('/verify-nfc', methods=['POST'])
def verify_nfc():
    data = request.get_json() or {}
    nfc = data.get('nfc', '').upper().replace(':', '')
    
    if nfc.startswith('04'):
        return jsonify({"verified": True, "brand": "Louis Vuitton"})
    elif nfc.startswith('05'):
        return jsonify({"verified": True, "brand": "Gucci"})
    elif nfc.startswith('06'):
        return jsonify({"verified": True, "brand": "Chanel"})
    else:
        return jsonify({"verified": False})

# REQUIRED FOR RENDER
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

