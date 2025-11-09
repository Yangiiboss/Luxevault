from flask import Flask, send_from_directory, jsonify, request
import os

# Fix: __name__ (double underscores)
app = Flask(__name__, static_folder='templates')  # or '.' if files are in root

# Serve index.html at root
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')  # works if index.html is in root

# Serve all other static files (JS, images, manifest, etc.)
@app.route('/<path:path>')
def serve_static(path):
    # Prevent directory traversal attacks
    if '..' in path or path.startswith('/'):
        return jsonify({"error": "Access denied"}), 403
    return send_from_directory('.', path)

# NFC verification endpoint
@app.route('/verify-nfc', methods=['POST'])
def verify_nfc():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"verified": False, "error": "No JSON received"}), 400

        nfc = data.get('nfc', '').strip().upper()

        if not nfc:
            return jsonify({"verified": False, "error": "NFC tag missing"}), 400

        # DEMO LOGIC: Real luxury brands
        if nfc.startswith("04"):
            return jsonify({
                "verified": True,
                "brand": "Louis Vuitton",
                "model": "Neverfull MM",
                "year": "2024"
            })
        elif nfc.startswith("05"):
            return jsonify({
                "verified": True,
                "brand": "Gucci",
                "model": "Dionysus Mini",
                "year": "2024"
            })
        elif nfc.startswith("06"):
            return jsonify({
                "verified": True,
                "brand": "Chanel",
                "model": "Classic Flap",
                "year": "2024"
            })
        else:
            return jsonify({
                "verified": False,
                "message": "Unknown or fake NFC tag"
            })

    except Exception as e:
        print(f"Error in verify-nfc: {e}")
        return jsonify({"verified": False, "error": "Server error"}), 500

# Optional: Serve tonconnect-manifest.json correctly
@app.route('/tonconnect-manifest.json')
def serve_manifest():
    return send_from_directory('.', 'tonconnect-manifest.json')

# Fix: __name__ == '__main__'
if __name__ == '__main__':
    # Use port for Render/Vercel
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)  # debug=False in production