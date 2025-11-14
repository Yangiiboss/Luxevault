from flask import Flask, request, jsonify, render_template, send_file
import os
import hashlib
import json
from datetime import datetime, date, timedelta
import io

app = Flask(__name__)

# Simple in-memory storage (no Redis required)
user_data = {}

class SimpleStorage:
    def get(self, key):
        return user_data.get(key)
    
    def set(self, key, value):
        user_data[key] = value
        return True
    
    def setex(self, key, seconds, value):
        user_data[key] = value
        return True
    
    def incr(self, key):
        current = int(user_data.get(key, 0))
        new_value = current + 1
        user_data[key] = str(new_value)
        return new_value

r = SimpleStorage()

# Luxury brand database
LUXURY_PUBKEYS = {
    "LV01": {"key": "0x1a2b3c", "name": "Louis Vuitton"},
    "GUCC": {"key": "0x4d5e6f", "name": "Gucci"},
    "DIO1": {"key": "0x7g8h9i", "name": "Dior"},
    "HERM": {"key": "0x89ab12", "name": "Hermès"},
    "ROLEX": {"key": "0x34cd56", "name": "Rolex"},
    "HUBLOT": {"key": "0x78ef90", "name": "Hublot"},
    "NIKE": {"key": "0x12gh34", "name": "Nike"},
    "CARTIER": {"key": "0x56ij78", "name": "Cartier"}
}

# Wallet addresses (replace with actual wallets in production)
YOUR_WALLET = "EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c"
TREASURY_WALLET = "EQBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"
LUXE_MINTER = "EQCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC"

# Demo functions (replace with actual TON integration in production)
async def send_ton(to_address: str, amount_nano: int):
    print(f"[DEMO] Sent {amount_nano} nanoTON to {to_address}")
    return True

async def jetton_transfer(minter: str, to: str, amount: int):
    print(f"[DEMO] Transferred {amount} jettons to {to}")
    return True

async def swap_ton_for_luxe(wallet: str, amount_nano: int):
    print(f"[DEMO] Swapped {amount_nano} nanoTON for $LUXE")
    return True

async def lock_tokens(wallet: str, amount: int, days: int):
    print(f"[DEMO] Locked {amount} tokens for {days} days")
    return True

def verify_signature(message: str, signature: str, pubkey: str) -> bool:
    # Demo verification - any NFC starting with "04" is real
    return message.startswith("04") if message else False

def verify_signature_with_any_known_key(nfc_data: str) -> bool:
    # Demo verification logic
    return nfc_data.startswith("04") if nfc_data else False

def detect_brand(nfc_data: str) -> str:
    if not nfc_data:
        return "Unknown"
    
    nfc_prefix = nfc_data[:4]
    brand_data = LUXURY_PUBKEYS.get(nfc_prefix)
    if brand_data:
        return brand_data["name"]
    
    if verify_signature_with_any_known_key(nfc_data):
        return "Independent Luxury"
    
    return "Unknown"

def calculate_luxe_reward(brand: str, streak: int) -> int:
    base_rewards = {
        "Hermès": 50000,
        "Rolex": 30000,
        "Chanel": 15000,
        "Louis Vuitton": 10000,
        "Gucci": 8000,
        "Dior": 7000,
        "Prada": 6000,
        "Independent Luxury": 5000
    }
    base = base_rewards.get(brand, 5000)
    return base * streak

async def pump_price(fee_received: int, referrer: str = None):
    print(f"[DEMO] Price pump activated: {fee_received}")
    if referrer:
        print(f"[DEMO] Referral commission for: {referrer}")
    return True

async def mint_ownership_nft(wallet: str, brand: str, nfc_hash: str):
    nft_id = hashlib.sha256(f"{wallet}{brand}{nfc_hash}".encode()).hexdigest()[:16]
    return f"EQNFT{nft_id}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/verify-nfc', methods=['POST'])
async def verify_nfc_real():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"verified": False, "error": "No data provided"})
            
        user_wallet = data.get('wallet')
        nfc_data = data.get('nfc', '')
        ref = data.get('ref')
        
        if not user_wallet:
            return jsonify({"verified": False, "error": "Wallet address required"})
        
        brand = detect_brand(nfc_data)
        is_real = verify_signature_with_any_known_key(nfc_data)
        
        if is_real:
            # Update user streak
            today = date.today().isoformat()
            streak_key = f"streak:{user_wallet}"
            count_key = f"count:{user_wallet}"
            
            last_scan = r.get(streak_key)
            streak = 1
            
            if last_scan and last_scan != today:
                try:
                    last_date = datetime.strptime(last_scan, '%Y-%m-%d').date()
                    if last_date == date.today() - timedelta(days=1):
                        streak = int(r.get(count_key) or 1) + 1
                    else:
                        streak = 1
                    r.set(count_key, streak)
                except:
                    streak = 1
            
            r.set(streak_key, today)
            streak = min(streak, 50)
            
            luxe_amount = calculate_luxe_reward(brand, streak)
            
            # INSTANT PAYOUT SYSTEM
            await send_ton(user_wallet, 25000000)
            await send_ton(YOUR_WALLET, 25000000)
            await jetton_transfer(LUXE_MINTER, user_wallet, luxe_amount * 10**9)
            await pump_price(50000000, ref)
            nft_address = await mint_ownership_nft(user_wallet, brand, nfc_data)
            
            return jsonify({
                "verified": True,
                "brand": brand,
                "ton_reward": "0.025 TON",
                "luxe_reward": luxe_amount,
                "nft_badge": nft_address,
                "streak": streak,
                "message": "✅ VERIFIED & PAID INSTANTLY!"
            })
        
        else:
            await send_ton(YOUR_WALLET, 50000000)
            return jsonify({
                "verified": False,
                "message": "❌ Counterfeit detected - No reward issued"
            })
            
    except Exception as e:
        return jsonify({
            "verified": False,
            "error": f"Server error: {str(e)}"
        })

@app.route('/streak', methods=['POST'])
def get_streak():
    try:
        data = request.get_json()
        wallet = data.get('wallet')
        
        if not wallet:
            return jsonify({"error": "Wallet required"}), 400
            
        today = date.today().isoformat()
        key = f"streak:{wallet}"
        last = r.get(key)
        
        streak = 1
        if last and last == today:
            streak = int(r.get(f"count:{wallet}") or 1)
            return jsonify({"streak": streak, "multiplier": min(streak, 50)})
        
        if last:
            try:
                last_date = datetime.strptime(last, '%Y-%m-%d').date()
                if last_date == date.today() - timedelta(days=1):
                    streak = int(r.incr(f"count:{wallet}"))
                else:
                    streak = 1
                    r.set(f"count:{wallet}", 1)
            except:
                streak = 1
                r.set(f"count:{wallet}", 1)
        else:
            r.set(f"count:{wallet}", 1)
        
        r.set(key, today)
        multiplier = min(streak, 50)
        return jsonify({"streak": streak, "multiplier": multiplier})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/subscribe', methods=['POST'])
async def subscribe():
    try:
        data = request.get_json()
        wallet = data.get('wallet')
        
        if not wallet:
            return jsonify({"error": "Wallet required"}), 400
        
        await send_ton(YOUR_WALLET, 5000000000)
        r.setex(f"premium:{wallet}", 30*24*3600, "GOLD")
        await lock_tokens(wallet, 5000 * 10**9, 90)
        
        return jsonify({"badge": "GOLD", "status": "PREMIUM_ACTIVATED"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/badge/<wallet>.png')
def generate_badge(wallet):
    try:
        # Import PIL only when needed to avoid deployment issues
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            # Fallback if PIL is not available
            return jsonify({"error": "Image generation not available"}), 500
            
        img = Image.new('RGB', (300, 200), color='black')
        d = ImageDraw.Draw(img)
        
        try:
            font_large = ImageFont.truetype("arial.ttf", 20)
            font_small = ImageFont.truetype("arial.ttf", 14)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        d.text((10, 10), "LUXE VAULT VERIFIED", fill='gold', font=font_large)
        d.text((10, 50), f"Wallet: {wallet[:8]}...{wallet[-6:]}", fill='white', font=font_small)
        d.text((10, 90), "Authentic Luxury Item", fill='gold', font=font_small)
        d.text((10, 130), "On-Chain Proof", fill='white', font=font_small)
        
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png')
        
    except Exception as e:
        return jsonify({"error": f"Badge generation failed: {str(e)}"}), 500

@app.route('/claim-luxe', methods=['POST'])
async def claim_luxe():
    try:
        data = request.get_json()
        wallet = data.get('wallet')
        
        if not wallet:
            return jsonify({"error": "Wallet required"}), 400
        
        await jetton_transfer(LUXE_MINTER, wallet, 500 * 10**9)
        
        return jsonify({"claimed": 500, "message": "500 $LUXE claimed successfully!"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "service": "Luxe Vault"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)