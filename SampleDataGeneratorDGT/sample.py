import time
import random
import base64
import json
import requests


tokens = ["OKURA001","OKURA002"]
# tokens = ["OKURA003","OKURA004","OKURA005","OKURA006","OKURA007","OKURA008","OKURA009"]
tokens2 = ["OKURA001"]


token_motor = ["MOTOR001"]

i= 1000
while True:
    try:
        i = i+1
        for token in tokens:
            url = "https://dgt.tmainnovation.com/api/device/telemetry/noauth/"+ str(token)
            print(url)
            payload = json.dumps(
                {
                    "fa_signal": 20,
                    "data_percentBat": 100,
                    "data_isPower": True,
                    "oee": 85.2,
                    "availability": 92.1,
                    "quality": 99.2,
                    "idleTime": 15.4,
                    "downtime": 12.2,
                    "maintenanceTime": 8.9,
                    "operationTime": 2.7,
                    "productionTarget": 10000,
                    "productionActual": i,
                    "performance": int(i/100),
                }
            )
            headers = {
                'Content-Type': 'application/json'
            }


            response = requests.request("POST", url, headers=headers, data=payload, verify = False)

            print(response.json())

        time.sleep(3)

        for token in token_motor:
            url = "https://dgt.tmainnovation.com/api/device/telemetry/noauth/"+ str(token)
            print(url)
            payload = json.dumps(
                {
                    "fa_signal": 20,
                    "data_percentBat": 100,
                    "data_isPower": True,
                    "voltage": round(random.uniform(375, 385), 1),
                    "current": round(random.uniform(8, 15), 2),
                    "power": round(random.uniform(3.5, 7.5), 2),
                    "data_health":random.randint(0, 100),
                    "speed": random.randint(1040, 3000),
                    "temperature": round(random.uniform(35, 70), 1),
                    "vibration": round(random.uniform(0.2, 2.5), 2),
                    "runtime": 52375,
                    "alarm": False,
                    "faultCode": 000
                }
            )
            headers = {
                'Content-Type': 'application/json'
            }


            response = requests.request("POST", url, headers=headers, data=payload, verify = False)

            print(response.json())

            time.sleep(3)

        # if i == 10000:
        #     i =1 
        # for token in tokens2:
        
        #     url = "https://dgt.tmainnovation.com/api/device/alarm/noauth/"+ str(token)
        #     print(url)
        #     with open("alarm.jpg", "rb") as image_file:
        #         encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

        #         payload = json.dumps({
        #             "type": "RestrictedZone",
        #             "detail": "RestrictedZone",
        #             "image": encoded_string,
        #             "alarm": True,

        #         })
        #         headers = {
        #             'Content-Type': 'application/json'
        #         }
        #         # print(payload)

        #         response = requests.request("POST", url, headers=headers, data=payload, verify = False)

        #         print(response.json())

        #     time.sleep(3)
    except Exception as e:
        print(e)

        