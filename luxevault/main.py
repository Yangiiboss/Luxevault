# app.py
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

# Mock Aura API (we fake it for now)
@app.route("/verify-nfc", methods=["POST"])
def verify_nfc():
    data = request.json
    nfc = data.get("nfc", "").strip()

    # MOCK: Accept any serial that starts with LV, GG, or HB
    if nfc.startswith("LV"):
        return jsonify({"verified": True, "brand": "Louis Vuitton"})
    elif nfc.startswith("GG"):
        return jsonify({"verified": True, "brand": "Gucci"})
    elif nfc.startswith("HB"):
        return jsonify({"verified": True, "brand": "Hermès"})
    else:
        return jsonify({"verified": False}), 400

# Mock Mint (sends fake TON transaction)
@app.route("/mint-nft", methods=["POST"])
def mint_nft():
    wallet = request.json.get("wallet")
    brand = request.json.get("brand")
    
    fake_tx = {
        "validUntil": 9999999999,
        "messages": [{
            "address": "EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c",  # testnet
            "amount": "50000000",  # 0.05 TON
            "payload": f"mint:{brand}:{wallet}"
        }]
    }
    return jsonify({"tx": fake_tx, "success": True})

# Home page
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)