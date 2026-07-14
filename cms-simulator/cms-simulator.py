# import requests
# import json
# import time
# import random
# from datetime import datetime
# import warnings
# warnings.filterwarnings("ignore")
# tokens = [
# "ESG001","ESG002","ESG003","ESG004","ESG005","ESG006"
# ]
# # token_EMPs = [
# # "EM000011",
# # "EM000012",
# # "EM000013",
# # "EM000014",
# # "EM000015",
# # "EM000016"
# # ]
# Schedule = ["Scheduled","Auto","AlwaysOn","Manual","Smart"]
# def push_telemetry(token, payload):
#     url = "https://cms.tmainnovation.com/api/device/telemetry/noauth/%s"%token
#     print(url)
#     headers = {
#       'Content-Type': 'application/json'
#     }
#     response = requests.request("POST", url,headers=headers,  data=payload, verify = False)
#     return response
# while True:
#     for token in tokens:
#         try:
#             GridEnergyConsumption = random.randint(1000, 3000)
#             SolarEnergyGeneration = random.randint(1000, 3000)
#             TotalEnergyConsumption = GridEnergyConsumption + SolarEnergyGeneration
#             Daily = random.randint(600, 1000)
#             Monthly = Daily *30
#             Yearly = Monthly *12
 
#             payload = json.dumps({
#                 "fa_signal": random.randint(10, 30),
#                 "data_percentBat": random.randint(90, 100),
#                 "data_isPower": True,
#                 "TotalEnergyConsumption": TotalEnergyConsumption,
#                 "GridEnergyConsumption": GridEnergyConsumption,
#                 "SolarEnergyGeneration": SolarEnergyGeneration,
#                 "Daily": Daily,
#                 "Monthly":Monthly,
#                 "Yearly":Yearly,
#                 "Equipment": random.randint(1000, 3000),
#                 "PowerFactor": random.randint(0, 100),
#                 "VoltageStability": random.randint(0, 100),
#                 "HarmonicDistortion": random.randint(0, 100),
#                 "PhaseImbalance": random.randint(0, 100),
#                 "Coal": random.randint(90, 100),
#                 "Co2": random.randint(1000, 3000),
#                 "Trees": random.randint(1000, 3000)
#             })
#             push_telemetry(token, payload)
#             print(payload)
#             time.sleep(5)
#         except Exception as e:
#             print(e)
 
#     # for token_EMP in token_EMPs:
#     #     payload = json.dumps({
#     #         "TotalActiveEnergy": int(datetime.now().timestamp() *1000),
#     #         "TotalActivePower" : random.randint(100, 120),
#     #         "PowerFactor": random.randint(70, 100),
#     #         "Schedule": random.choice(Schedule)
#     #     })
#     #     push_telemetry(token_EMP, payload)
#     #     print(payload)
#     #     time.sleep(10)

import json
import random
import time
from datetime import datetime

tokens = ["ESG001","ESG002","ESG003","ESG004","ESG005","ESG006"]

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
            equipment_power = round(random.uniform(8, 25), 2)  # kW

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
            TotalEnergyConsumption += equipment_energy
            GridEnergyConsumption += grid_energy
            SolarEnergyGeneration += solar_energy

            Daily += equipment_energy
            Monthly += equipment_energy
            Yearly += equipment_energy

            # --------------------------
            # Build Payload
            # --------------------------
            payload = json.dumps({
                # Device
                "fa_signal": random.randint(20, 30),
                "data_percentBat": random.randint(90, 100),
                "data_isPower": True,

                # Energy
                "TotalEnergyConsumption": round(TotalEnergyConsumption, 2),
                "GridEnergyConsumption": round(GridEnergyConsumption, 2),
                "SolarEnergyGeneration": round(SolarEnergyGeneration, 2),

                "Daily": round(Daily, 2),
                "Monthly": round(Monthly, 2),
                "Yearly": round(Yearly, 2),

                # Instant Power
                "EquipmentPower": equipment_power,
                "SolarPower": solar_power,
                "GridPower": round(grid_power, 2),

                # Electrical
                "Voltage": round(random.uniform(219, 231), 1),
                "Current": round(equipment_power * 1000 / 220, 2),
                "Frequency": round(random.uniform(49.95, 50.05), 2),
                "PowerFactor": round(random.uniform(0.95, 0.99), 2),

                # Power Quality
                "VoltageStability": round(random.uniform(97, 100), 1),
                "HarmonicDistortion": round(random.uniform(1.5, 3.5), 2),
                "PhaseImbalance": round(random.uniform(0.2, 1.5), 2),

                # Environment
                "Temperature": round(random.uniform(28, 38), 1),
                "Humidity": round(random.uniform(45, 75), 1),

                # Sustainability
                "CoalSaved": round(SolarEnergyGeneration * 0.404, 2),
                "CO2Reduction": round(SolarEnergyGeneration * 0.85, 2),
                "EquivalentTrees": int(SolarEnergyGeneration * 0.04)
            })

            print(payload)
            push_telemetry(token, payload)

            # TODO: Publish MQTT
            # client.publish(topic, payload)

            time.sleep(5)
        except Exception as e:
            print(e)
