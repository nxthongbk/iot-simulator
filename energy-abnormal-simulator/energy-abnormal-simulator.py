import json
import random
import time
import requests
from datetime import datetime
import urllib3
 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
 
# ===== TOKEN =====
token_EMP = "EM000013"
print(token_EMP)
 
# ===== CẤU HÌNH =====
base_power = 120            # W ban ngày
night_spike_power = (500, 900)
interval_sec = 30
Schedule = ["NORMAL", "NIGHT"]
 
energy_wh = 15000.0         # điện năng khởi tạo
 
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
    hour = now.hour
 
    # ===== POWER LOGIC =====
    if 22 <= hour or hour < 6:
        # Ban đêm → có spike
        if random.random() < 0.2:
            power = random.randint(*night_spike_power)
        else:
            power = base_power + random.randint(-5, 5)
        schedule = "NIGHT"
    else:
        # Ban ngày → ổn định
        power = base_power + random.randint(-3, 3)
        schedule = "NORMAL"
 
    # ===== POWER FACTOR =====
    if power > 400:
        power_factor = round(random.uniform(0.5, 0.7), 2)
    else:
        power_factor = round(random.uniform(0.92, 0.98), 2)
 
    # ===== ENERGY =====
    timestamp = int(datetime.now().timestamp())
 
    energy_wh = int(timestamp / 13)
 
    # ===== PAYLOAD =====
    payload = json.dumps({
        "Timestamp": int(now.timestamp() * 1000),
        "TotalActivePower": int(power),
        "TotalActiveEnergy": int(energy_wh),
        "PowerFactor": power_factor,
        "Schedule": schedule
    })
 
    # ===== PUSH =====
    try:
        res = push_telemetry(token_EMP, payload)
        print(f"[{now.strftime('%H:%M:%S')}] "
              f"Power={power}W | Energy={int(energy_wh)}Wh | "
              f"PF={power_factor} | {schedule} | "
              f"Status={res.status_code}")
    except Exception as e:
        print("Push error:", e)
 
    time.sleep(interval_sec)