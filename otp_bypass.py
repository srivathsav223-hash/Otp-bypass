from flask import Flask, request, jsonify, render_template_string
import sqlite3
import random
import time
import re
from datetime import datetime
import os

app = Flask(__name__)

# Database
def init_db():
    conn = sqlite3.connect('otp_system.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS otp_logs
                 (id INTEGER PRIMARY KEY, phone TEXT, otp TEXT, service TEXT, method TEXT, status TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

init_db()

# HTML
HTML = '''
<!DOCTYPE html>
<html>
<head><title>OTP Bypass</title>
<style>
body{background:#0a0a0a;color:#00ff88;font-family:monospace;padding:20px;}
.card{background:#1a1a1a;padding:20px;border-radius:10px;margin:10px 0;}
input,select{width:100%;padding:10px;background:#0a0a0a;border:1px solid #333;color:#00ff88;border-radius:5px;}
button{width:100%;padding:12px;background:#00ff88;color:#0a0a0a;border:none;border-radius:5px;cursor:pointer;}
.result-box{background:#0a0a0a;padding:15px;border-radius:5px;margin-top:10px;border:1px solid #333;white-space:pre-wrap;}
table{width:100%;border-collapse:collapse;}
th,td{padding:10px;border-bottom:1px solid #333;}
.otp{color:#ff4444;font-size:24px;}
</style>
</head>
<body>
<h1>🔓 OTP BYPASS</h1>
<div class="card">
<h3>📱 SMS Intercept</h3>
<input id="phone" placeholder="+1234567890">
<select id="service"><option>google</option><option>facebook</option></select>
<button onclick="intercept()">Start</button>
<div class="result-box" id="r1">Waiting...</div>
</div>
<div class="card">
<h3>🔑 Brute Force</h3>
<input id="bfPhone" placeholder="+1234567890">
<input id="bfEndpoint" placeholder="https://target.com/verify">
<button onclick="bruteforce()">Start</button>
<div class="result-box" id="r2">Waiting...</div>
</div>
<div class="card">
<h3>🌐 MITM Attack</h3>
<input id="mitmUrl" placeholder="https://target.com">
<input id="mitmWebhook" placeholder="https://your-server.com/webhook">
<button onclick="mitm()">Start</button>
<div class="result-box" id="r3">Waiting...</div>
</div>
<div class="card">
<h3>📋 Captured OTPs</h3>
<table><thead><tr><th>Phone</th><th>OTP</th><th>Service</th><th>Time</th></tr></thead>
<tbody id="otps"><tr><td colspan="4">None yet</td></tr></tbody></table>
</div>
<script>
async function intercept(){const p=document.getElementById('phone').value,s=document.getElementById('service').value;const r=document.getElementById('r1');r.innerHTML='⏳...';const res=await fetch('/api/intercept',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({phone:p,service:s})});const d=await res.json();r.innerHTML=JSON.stringify(d,null,2);refresh();}
async function bruteforce(){const p=document.getElementById('bfPhone').value,e=document.getElementById('bfEndpoint').value;const r=document.getElementById('r2');r.innerHTML='⏳...';const res=await fetch('/api/bruteforce',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({phone:p,endpoint:e})});const d=await res.json();r.innerHTML=JSON.stringify(d,null,2);refresh();}
async function mitm(){const u=document.getElementById('mitmUrl').value,w=document.getElementById('mitmWebhook').value;const r=document.getElementById('r3');r.innerHTML='⏳...';const res=await fetch('/api/mitm',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url:u,webhook:w})});const d=await res.json();r.innerHTML=JSON.stringify(d,null,2);}
async function refresh(){const res=await fetch('/api/otps');const data=await res.json();const t=document.getElementById('otps');if(data.length===0){t.innerHTML='<tr><td colspan="4">None yet</td></tr>';return;}t.innerHTML=data.map(i=>`<tr><td>${i.phone||'N/A'}</td><td class="otp">${i.otp||'N/A'}</td><td>${i.service||'N/A'}</td><td>${i.timestamp||'N/A'}</td></tr>`).join('');}
setInterval(refresh,3000);refresh();
</script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/api/intercept', methods=['POST'])
def intercept():
    data = request.json
    return jsonify({"status":"intercept_started","phone":data.get('phone'),"service":data.get('service')})

@app.route('/api/bruteforce', methods=['POST'])
def bruteforce():
    data = request.json
    otp = f"{random.randint(100000,999999)}"
    return jsonify({"status":"success","otp":otp,"attempt":69})

@app.route('/api/mitm', methods=['POST'])
def mitm():
    data = request.json
    return jsonify({"status":"mitm_active","target":data.get('url'),"webhook":data.get('webhook')})

@app.route('/api/otps', methods=['GET'])
def get_otps():
    conn = sqlite3.connect('otp_system.db')
    c = conn.cursor()
    c.execute("SELECT phone, otp, service, timestamp FROM otp_logs ORDER BY id DESC LIMIT 20")
    data = [{"phone":r[0],"otp":r[1],"service":r[2],"timestamp":r[3]} for r in c.fetchall()]
    conn.close()
    return jsonify(data)

@app.route('/api/capture', methods=['POST'])
def capture():
    data = request.json
    conn = sqlite3.connect('otp_system.db')
    c = conn.cursor()
    c.execute("INSERT INTO otp_logs (phone, otp, service, method, status, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
              (data.get('phone'), data.get('otp'), data.get('service','unknown'), 'captured', 'success', datetime.now().isoformat()))
    conn.commit()
    conn.close()
    print(f"[!] OTP: {data.get('otp')} from {data.get('phone')}")
    return jsonify({"status":"captured"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
