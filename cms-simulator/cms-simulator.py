import requests
import json
import random
import time
from datetime import datetime

tokens = ["ESG001","ESG002","ESG003","ESG004","ESG005","ESG006"]

device_profile = {
    "ESG001": (5, 10),
    "ESG002": (8, 15),
    "ESG003": (10, 18),
    "ESG004": (15, 25),
    "ESG005": (20, 35),
    "ESG006": (30, 50),
}




# ==========================
# Initial Value
# ==========================
TotalEnergyConsumption = 12560.0    # kWh
GridEnergyConsumption = 8200.0      # kWh
SolarEnergyGeneration = 4360.0      # kWh

Daily = 85.0                        # kWh
Monthly = 1830.0                    # kWh
Yearly = 25460.0                    # kWh

last_day = datetime.now().day
last_month = datetime.now().month
last_year = datetime.now().year

INTERVAL = 5    # seconds

def push_telemetry(token, payload):
    url = "https://cms.tmainnovation.com/api/device/telemetry/noauth/%s"%token
    print(url)
    headers = {
      'Content-Type': 'application/json'
    }
    response = requests.request("POST", url,headers=headers,  data=payload, verify = False)
    return response

while True:
    for token in tokens:
        try:
            
            d = devices[token]
            now = datetime.now()



            # --------------------------
            # Reset Counter
            # --------------------------
            if now.day != last_day:
                Daily = 0
                last_day = now.day

            if now.month != last_month:
                Monthly = 0
                last_month = now.month

            if now.year != last_year:
                Yearly = 0
                last_year = now.year

            # --------------------------
            # Simulate Equipment Power
            # --------------------------
            # equipment_power = round(random.uniform(8, 25), 2)  # kW

            min_power, max_power = device_profile[token]
            equipment_power = round(random.uniform(min_power, max_power), 2)



            # Solar production during daytime
            if 6 <= now.hour <= 17:
                solar_power = round(random.uniform(1, 12), 2)
            else:
                solar_power = 0

            # Grid power
            grid_power = max(equipment_power - solar_power, 0)

            # Energy generated during INTERVAL
            equipment_energy = equipment_power * INTERVAL / 3600
            solar_energy = solar_power * INTERVAL / 3600
            grid_energy = grid_power * INTERVAL / 3600

            # --------------------------
            # Accumulate Energy
            # --------------------------
            # TotalEnergyConsumption += equipment_energy
            # GridEnergyConsumption += grid_energy
            # SolarEnergyGeneration += solar_energy

            # Daily += equipment_energy
            # Monthly += equipment_energy
            # Yearly += equipment_energy


            d["TotalEnergyConsumption"] += equipment_energy
            d["GridEnergyConsumption"] += grid_energy
            d["SolarEnergyGeneration"] += solar_energy

            d["Daily"] += equipment_energy
            d["Monthly"] += equipment_energy
            d["Yearly"] += equipment_energy




            # --------------------------
            # Build Payload
            # --------------------------
            payload = json.dumps({
                # Device
                "fa_signal": random.randint(20, 30),
                "data_percentBat": random.randint(90, 100),
                "data_isPower": True,

                # Energy
                # "TotalEnergyConsumption": round(TotalEnergyConsumption, 0),
                # "GridEnergyConsumption": round(GridEnergyConsumption, 0),
                # "SolarEnergyGeneration": round(SolarEnergyGeneration, 0),

                "TotalEnergyConsumption": round(d["TotalEnergyConsumption"], 0),
                "GridEnergyConsumption": round(d["GridEnergyConsumption"], 0),
                "SolarEnergyGeneration": round(d["SolarEnergyGeneration"], 0),

                "Daily": round(d["Daily"], 2),
                "Monthly": round(d["Monthly"], 2),
                "Yearly": round(d["Yearly"], 2),


                # Instant Power
                "EquipmentPower": equipment_power,
                "SolarPower": solar_power,
                "GridPower": round(grid_power, 2),

                # Electrical
                "Voltage": round(random.uniform(219, 231), 1),
                "Current": round(equipment_power * 1000 / 220, 2),
                "Frequency": round(random.uniform(49.95, 50.05), 2),
                "PowerFactor": random.randint(70, 100),

                # Power Quality
                "VoltageStability": random.randint(70, 100),
                "HarmonicDistortion": random.randint(70, 100),
                "PhaseImbalance": random.randint(70, 100),

                # Environment
                "Temperature": round(random.uniform(28, 38), 1),
                "Humidity": round(random.uniform(45, 75), 1),

                # Sustainability
                "CoalSaved": round(d["SolarEnergyGeneration"] * 0.404, 2),
                "CO2Reduction": round(d["SolarEnergyGeneration"] * 0.85, 2),
                "EquivalentTrees": int(d["SolarEnergyGeneration"] * 0.04),

            })

            print(payload)
            push_telemetry(token, payload)

            # TODO: Publish MQTT
            # client.publish(topic, payload)

            time.sleep(5)
        except Exception as e:
            print(e)
