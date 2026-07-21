import json
import random
import time
from datetime import datetime

DATA_DIR = "data"
STATE_FILE = os.path.join(DATA_DIR, "state.json")

os.makedirs(DATA_DIR, exist_ok=True)


def create_default_state():
    now = datetime.now()

    return {
        "fa_signal": 25,
        "data_percentBat": 98,
        "data_isPower": True,

        "TotalEnergyConsumption": 12560.0,
        "GridEnergyConsumption": 8200.0,
        "SolarEnergyGeneration": 4360.0,

        "Daily": 85.04,
        "Monthly": 1830.04,
        "Yearly": 25460.04,

        "EquipmentPower": 24.39,
        "SolarPower": 0,
        "GridPower": 24.39,

        "Voltage": 221.4,
        "Current": 110.86,
        "Frequency": 49.96,
        "PowerFactor": 90,

        "VoltageStability": 81,
        "HarmonicDistortion": 93,
        "PhaseImbalance": 85,

        "Temperature": 33.8,
        "Humidity": 47.1,

        "CoalSaved": 1761.44,
        "CO2Reduction": 3706.0,
        "EquivalentTrees": 174,

        "last_day": now.strftime("%Y-%m-%d"),
        "last_month": now.strftime("%Y-%m")
    }

def load_state():
    if not os.path.exists(STATE_FILE):
        state = create_default_state()
        save_state(state)
        return state

    with open(STATE_FILE, "r") as f:
        print(json.load(f))
        return json.load(f)


def save_state(state):

    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)


def update_state(state):

    now = datetime.now()

    today = now.strftime("%Y-%m-%d")
    month = now.strftime("%Y-%m")

    # Reset Daily
    if state["last_day"] != today:
        state["Daily"] = 0
        state["last_day"] = today

    # Reset Monthly
    if state["last_month"] != month:
        state["Monthly"] = 0
        state["last_month"] = month

    #################################
    # Simulate
    #################################

    voltage = round(random.uniform(220, 225), 1)
    current = round(random.uniform(80, 120), 2)
    pf = random.randint(88, 98)

    power = round(voltage * current * pf / 100 / 1000, 2)   # kW

    delta = power / 3600      # kWh / giây

    state["Voltage"] = voltage
    state["Current"] = current
    state["PowerFactor"] = pf
    state["Frequency"] = round(random.uniform(49.95, 50.05), 2)

    state["EquipmentPower"] = power
    state["GridPower"] = power
    state["SolarPower"] = 0

    state["Temperature"] = round(random.uniform(30, 38), 1)
    state["Humidity"] = round(random.uniform(40, 60), 1)

    state["VoltageStability"] = random.randint(80, 100)
    state["HarmonicDistortion"] = random.randint(90, 100)
    state["PhaseImbalance"] = random.randint(80, 100)

    state["fa_signal"] = random.randint(20, 30)
    state["data_percentBat"] = random.randint(95, 100)

    state["TotalEnergyConsumption"] += delta
    state["GridEnergyConsumption"] += delta

    state["Daily"] += delta
    state["Monthly"] += delta
    state["Yearly"] += delta

    state["CoalSaved"] = round(state["TotalEnergyConsumption"] * 0.14, 2)
    state["CO2Reduction"] = round(state["TotalEnergyConsumption"] * 0.295, 2)
    state["EquivalentTrees"] = int(state["CO2Reduction"] / 21.4)

    return state
while True:
   state = load_state()

    # # ============================
    # # STEP 2 : Update
    # # ============================

    # state = update_state(state)

    # # ============================
    # # STEP 3 : Save
    # # ============================

    # save_state(state)
