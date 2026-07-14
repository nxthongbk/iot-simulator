import requests
import json
import time
import random
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")
tokens = [
"ESG001","ESG002","ESG003","ESG004","ESG005","ESG006"
]
# token_EMPs = [
# "EM000011",
# "EM000012",
# "EM000013",
# "EM000014",
# "EM000015",
# "EM000016"
# ]
Schedule = ["Scheduled","Auto","AlwaysOn","Manual","Smart"]
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
            GridEnergyConsumption = random.randint(1000, 3000)
            SolarEnergyGeneration = random.randint(1000, 3000)
            TotalEnergyConsumption = GridEnergyConsumption + SolarEnergyGeneration
            Daily = random.randint(600, 1000)
            Monthly = Daily *30
            Yearly = Monthly *12
 
            payload = json.dumps({
                "fa_signal": random.randint(10, 30),
                "data_percentBat": random.randint(90, 100),
                "data_isPower": True
                "TotalEnergyConsumption": TotalEnergyConsumption,
                "GridEnergyConsumption": GridEnergyConsumption,
                "SolarEnergyGeneration": SolarEnergyGeneration,
                "Daily": Daily,
                "Monthly":Monthly,
                "Yearly":Yearly,
                "Equipment": random.randint(1000, 3000),
                "PowerFactor": random.randint(0, 100),
                "VoltageStability": random.randint(0, 100),
                "HarmonicDistortion": random.randint(0, 100),
                "PhaseImbalance": random.randint(0, 100),
                "Coal": random.randint(90, 100),
                "Co2": random.randint(1000, 3000),
                "Trees": random.randint(1000, 3000)
            })
            push_telemetry(token, payload)
            print(payload)
            time.sleep(10)
        except Exception as e:
            print(e)
 
    # for token_EMP in token_EMPs:
    #     payload = json.dumps({
    #         "TotalActiveEnergy": int(datetime.now().timestamp() *1000),
    #         "TotalActivePower" : random.randint(100, 120),
    #         "PowerFactor": random.randint(70, 100),
    #         "Schedule": random.choice(Schedule)
    #     })
    #     push_telemetry(token_EMP, payload)
    #     print(payload)
    #     time.sleep(10)