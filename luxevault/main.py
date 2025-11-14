from flask import Flask, request, jsonify, render_template, send_file
import asyncio
import hashlib
import redis
from datetime import date, datetime, timedelta
import os
from PIL import Image, ImageDraw, ImageFont
import io
import requests
import base64

app = Flask(__name__)

# For Redis - use environment variable for production
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
r = redis.Redis.from_url(REDIS_URL, decode_responses=True)

# Luxury brand public keys database (simplified for demo)
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

# Your wallet addresses (REPLACE WITH ACTUAL WALLETS)
YOUR_WALLET = "EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c"
TREASURY_WALLET = "EQBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"
LUXE_MINTER = "EQCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC"

# Simplified TON sending function (for demo - replace with actual implementation)
async def send_ton(to_address: str, amount_nano: int):
    """
    Simplified TON transfer function
    In production, integrate with actual TON wallet
    """
    print(f"[DEMO] Sending {amount_nano} nanoTON to {to_address}")
    # TODO: Integrate with actual TON wallet/smart contract
    return True

async def jetton_transfer(minter: str, to: str, amount: int):
    """
    Simplified jetton transfer function
    """
    print(f"[DEMO] Transferring {amount} jettons from {minter} to {to}")
    # TODO: Integrate with actual jetton contract
    return True

async def swap_ton_for_luxe(wallet: str, amount_nano: int):
    """
    Auto-buy $LUXE from DEX
    """
    print(f"[DEMO] Swapping {amount_nano} nanoTON for $LUXE to {wallet}")
    return True

async def lock_tokens(wallet: str, amount: int, days: int):
    """
    Token locking mechanism
    """
    print(f"[DEMO] Locking {amount} tokens for {wallet} for {days} days")
    return True

def verify_signature(message: str, signature: str, pubkey: str) -> bool:
    """
    Simplified signature verification
    In production, implement actual cryptographic verification
    """
    # Demo logic: Any NFC starting with "04" is considered real
    return message.startswith("04") if message else False

def verify_signature_with_any_known_key(nfc_data: str) -> bool:
    """
    Try all known brand keys
    """
    if not nfc_data:
        return False
    
    # Demo verification logic
    return nfc_data.startswith("04")

def detect_brand(nfc_data: str) -> str:
    if not nfc_data:
        return "Unknown"
    
    nfc_prefix = nfc_data[:4]
    brand_data = LUXURY_PUBKEYS.get(nfc_prefix)
    if brand_data:
        return brand_data["name"]
    
    # Unknown brand but valid signature
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
    """
    Automatic price pump mechanism
    """
    treasury_share = int(fee_received * 0.10)   # 10%
    burn_share = int(fee_received * 0.05)       # 5%
    
    print(f"[DEMO] Price pump: Treasury={treasury_share}, Burn={burn_share}")
    
    # 1. Treasury buys $LUXE
    await swap_ton_for_luxe(TREASURY_WALLET, treasury_share)
    
    # 2. Burn $LUXE (simplified)
    burn_amount = burn_share // 200
    if burn_amount > 0:
        await jetton_transfer(LUXE_MINTER, "EQ0000000000000000000000000000000000000000000000", burn_amount)
    
    # 3. Lock referral rewards
    if referrer:
        referral_amount = int(fee_received * 0.25)  # 25% commission
        await lock_tokens(referrer, referral_amount, days=30)

async def mint_ownership_nft(wallet: str, brand: str, nfc_hash: str):
    """
    Simplified NFT minting function
    """
    nft_id = hashlib.sha256(f"{wallet}{brand}{nfc_hash}".encode()).hexdigest()[:16]
    nft_address = f"EQNFT{nft_id}"
    
    print(f"[DEMO] Minted NFT for {wallet}: {nft_address}")
    return nft_address

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
        
        # Auto-detect brand
        brand = detect_brand(nfc_data)
        
        # Verify authenticity
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
            streak = min(streak, 50)  # Cap at 50x
            
            # Calculate rewards
            luxe_amount = calculate_luxe_reward(brand, streak)
            
            # INSTANT PAYOUT SYSTEM (DEMO MODE)
            print(f"[DEMO] Real item verified: {brand}")
            print(f"[DEMO] Rewards: {luxe_amount} $LUXE + 0.025 TON")
            
            # 1. User reward TON (simulated)
            await send_ton(user_wallet, 25000000)  # 0.025 TON
            
            # 2. Your profit (simulated)
            await send_ton(YOUR_WALLET, 25000000)  # 0.025 TON
            
            # 3. $LUXE airdrop (simulated)
            await jetton_transfer(LUXE_MINTER, user_wallet, luxe_amount * 10**9)
            
            # 4. Treasury & burn (price pump)
            await pump_price(50000000, ref)
            
            # 5. NFT badge
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
            # FAKE ITEM - Keep full fee
            print(f"[DEMO] Fake item detected: {nfc_data}")
            await send_ton(YOUR_WALLET, 50000000)  # Keep 0.05 TON
            return jsonify({
                "verified": False,
                "message": "❌ Counterfeit detected - No reward issued"
            })
            
    except Exception as e:
        print(f"Error in verify_nfc: {str(e)}")
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
        
        # In production, verify the payment first
        print(f"[DEMO] Premium subscription for {wallet}")
        
        # Set premium status for 30 days
        r.setex(f"premium:{wallet}", 30*24*3600, "GOLD")
        
        # Lock 5000 $LUXE for 90 days
        await lock_tokens(wallet, 5000 * 10**9, 90)
        
        return jsonify({"badge": "GOLD", "status": "PREMIUM_ACTIVATED"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/badge/<wallet>.png')
def generate_badge(wallet):
    try:
        # Generate dynamic verification badge
        img = Image.new('RGB', (300, 200), color='black')
        d = ImageDraw.Draw(img)
        
        # Simple font (system default)
        try:
            font_large = ImageFont.truetype("arial.ttf", 20)
            font_small = ImageFont.truetype("arial.ttf", 14)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Add wallet address and verification info
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
        
        # Airdrop 500 $LUXE tokens (demo)
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