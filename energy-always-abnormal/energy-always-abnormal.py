import json
import random
import time
import requests
from datetime import datetime
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
 
# ===== TOKEN =====
token_EMP = os.getenv("TOKEN_EMP")
print(token_EMP)
 
# ===== CẤU HÌNH =====
base_power = 120          # W
interval_sec = 5
energy_wh = 15000.0
 
# ===== PUSH TELEMETRY =====
def push_telemetry(token, payload):
    url = "https://scity-dev.innovation.com.vn/api/device/telemetry/noauth/%s" % token
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(
        url,
        headers=headers,
        data=payload,
        verify=False,
        timeout=10
    )
    return response
 
# ===== MAIN LOOP =====
while True:
    now = datetime.now()
 
    # ===== POWER STABLE =====
    power = base_power + random.randint(-2, 2)
 
    # ===== POWER FACTOR STABLE =====
    power_factor = round(random.uniform(0.81, 0.92), 2)
 
    # ===== ENERGY TĂNG ĐỀU =====
    #energy_wh += power * interval_sec / 3600
 
    timestamp = int(datetime.now().timestamp())
 
    energy_wh = int(timestamp / 11)
 
 
    # ===== PAYLOAD =====
    payload = json.dumps({
        "Timestamp": int(now.timestamp() * 1000),
        "TotalActivePower": int(power),
        "TotalActiveEnergy": int(energy_wh),
        "PowerFactor": power_factor,
        "Schedule": "NORMAL"
    })
 
    # ===== PUSH =====
    try:
        res = push_telemetry(token_EMP, payload)
        print(f"[{now.strftime('%H:%M:%S')}] "
              f"Power={power}W | Energy={int(energy_wh)}Wh | "
              f"PF={power_factor} | Status={res.status_code}")
    except Exception as e:
        print("Push error:", e)
 
    time.sleep(interval_sec)