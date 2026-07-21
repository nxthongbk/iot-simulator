import json
import os
import random
import time
from datetime import datetime

DATA_DIR = "data"
STATE_FILE = os.path.join(DATA_DIR, "state.json")

DEVICE_IDS = [
    "ESG001",
    "ESG002",
    "ESG003"
]

SAVE_INTERVAL = 30      # ghi file mỗi 30 giây
SEND_INTERVAL = 1       # mô phỏng mỗi 1 giây

os.makedirs(DATA_DIR, exist_ok=True)


def create_default_state():
    devices = {}

    now = datetime.now()

    for device in DEVICE_IDS:
        devices[device] = {
            "voltage": 0,
            "current": 0,
            "power": 0,
            "pf": 0,
            "frequency": 50,
            "energy_total": 0,
            "energy_today": 0,
            "energy_month": 0,
            "day": now.strftime("%Y-%m-%d"),
            "month": now.strftime("%Y-%m"),
            "last_update": ""
        }

    return {"devices": devices}


def load_state():

    if not os.path.exists(STATE_FILE):
        state = create_default_state()
        save_state(state)
        return state

    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):

    tmp = STATE_FILE + ".tmp"

    with open(tmp, "w") as f:
        json.dump(state, f, indent=4)

    os.replace(tmp, STATE_FILE)


state = load_state()

last_save = time.time()

while True:

    now = datetime.now()

    today = now.strftime("%Y-%m-%d")
    month = now.strftime("%Y-%m")

    for device, data in state["devices"].items():

        # reset daily
        if data["day"] != today:
            data["energy_today"] = 0
            data["day"] = today

        # reset monthly
        if data["month"] != month:
            data["energy_month"] = 0
            data["month"] = month

        #####################################
        # simulate
        #####################################

        voltage = round(random.uniform(220, 235), 1)

        current = round(random.uniform(2, 8), 2)

        pf = round(random.uniform(0.90, 0.99), 2)

        power = voltage * current * pf

        # kWh trong 1 giây
        delta = power / 1000 / 3600

        data["voltage"] = voltage
        data["current"] = current
        data["pf"] = pf
        data["frequency"] = 50.0
        data["power"] = round(power, 2)

        data["energy_total"] += delta
        data["energy_today"] += delta
        data["energy_month"] += delta

        data["last_update"] = now.isoformat()

        print(
            device,
            f"P={power:.1f}W",
            f"Today={data['energy_today']:.3f}",
            f"Month={data['energy_month']:.3f}",
            f"Total={data['energy_total']:.3f}"
        )

    if time.time() - last_save >= SAVE_INTERVAL:
        save_state(state)
        last_save = time.time()
        print("State saved.")

    time.sleep(SEND_INTERVAL)