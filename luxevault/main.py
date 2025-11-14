from flask import Flask, request, jsonify, render_template, send_file
import os
import hashlib
import json
from datetime import date, datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import io

app = Flask(__name__)

# Simple in-memory storage (replace with Redis later)
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

# Use simple storage (upgrade to Redis when you have 1000+ users)
r = SimpleStorage()

# Rest of your Luxe Vault code remains exactly the same...
# [Keep all your LUXURY_PUBKEYS, wallet functions, verification logic]

@app.route('/streak', methods=['POST'])
def get_streak():
    data = request.get_json()
    wallet = data.get('wallet')
    
    if not wallet:
        return jsonify({"error": "Wallet required"}), 400
        
    today = date.today().isoformat()
    streak_key = f"streak:{wallet}"
    count_key = f"count:{wallet}"
    
    last_scan = r.get(streak_key)
    streak = 1
    
    if last_scan and last_scan == today:
        streak = int(r.get(count_key) or 1)
    else:
        if last_scan:
            try:
                last_date = datetime.strptime(last_scan, '%Y-%m-%d').date()
                if last_date == date.today() - timedelta(days=1):
                    streak = int(r.incr(count_key))
                else:
                    streak = 1
                    r.set(count_key, "1")
            except:
                streak = 1
                r.set(count_key, "1")
        else:
            r.set(count_key, "1")
        
        r.set(streak_key, today)
    
    multiplier = min(streak, 50)
    return jsonify({"streak": streak, "multiplier": multiplier})

# All other routes remain the same...