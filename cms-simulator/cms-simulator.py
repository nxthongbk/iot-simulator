import json
import random
import time
import requests
from datetime import datetime
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
 
# ===== TOKEN =====
token_EMP = os.getenv("TOKEN")
print(token_EMP)
 
# ===== CẤU HÌNH =====
base_power = 120          # W
interval_sec = 5
energy_wh = 15000.0
 
# ===== PUSH TELEMETRY =====
def push_telemetry(token, payload):
    url = "https://cms.tmainnovation.com.vn/api/device/telemetry/noauth/%s" % token
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

    try:
        payload = json.dumps({
            "fa_signal": random.randint(10, 30),
            "data_percentBat": random.randint(90, 100),
            "data_isPower": True
            })

        res = push_telemetry(token, payload)

    except Exception as e:
        print("Push error:", e)
 
    time.sleep(interval_sec)