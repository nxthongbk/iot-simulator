import paho.mqtt.client as mqtt
import json
import time
import random
import ssl
# =========================
# MQTT Configuration
# =========================
broker_address = "sfscm.net"
port = 8883

device_id = "DEV-260923-000000003"


gas_price=0
electric_price=0

telemetry_topic = f"device/{device_id}/telemetry"
attribute_topic = f"device/{device_id}/attribute/downlink"

cert_file = "DEV-260923-000000003.crt"
key_file = "DEV-260923-000000003.key"
ca_file = "sfscm.pem"



# =========================
# MQTT Callbacks
# =========================
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT Connected successfully")

        # Subscribe nếu server/device cần nhận message
        # client.subscribe(attribute_topic)

        print("Subscribed:", attribute_topic)

    else:
        print("MQTT connection failed, rc =", rc)


def on_message(client, userdata, msg):
    # print("Received:")
    # print("  Topic:", msg.topic)
    # print("  Payload:", msg.payload.decode())
    message =  msg.payload.decode()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}", flush=True)




def on_disconnect(client, userdata, rc):
    print("MQTT disconnected, rc =", rc)


# =========================
# Create MQTT Client
# =========================
client = mqtt.Client(client_id=device_id)

# =========================
# mTLS
# =========================
client.tls_set(
    ca_certs=ca_file,          # CA dùng để verify MQTT Broker
    certfile=cert_file,        # Client certificate
    keyfile=key_file,          # Client private key
    cert_reqs=ssl.CERT_REQUIRED,
    tls_version=ssl.PROTOCOL_TLS_CLIENT
)

# Không bỏ qua việc verify certificate
client.tls_insecure_set(False)


client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect


# =========================
# Connect
# =========================
print(f"Connecting to {broker_address}:{port} ...")

client.connect(
    broker_address,
    port,
    keepalive=60
)

client.loop_start()


# =========================
# Telemetry Data
# =========================
def generate_telemetry_data():

    telemetry_data = {
        "lora_sensors": [
            {
                "id": 1,
                "temp": round(random.uniform(-4.0, 4.0), 1),
                "hum": round(random.uniform(60.0, 90.0), 1),
                "rssi": random.randint(-90, -70),
                "bat": random.randint(6, 90),
                "type":"outdoor",
                "floor":"0"

            },
            {
                "id": 2,
                "temp": round(random.uniform(23.0, 24.0), 1),
                "hum": round(random.uniform(60.0, 90.0), 1),
                "rssi": random.randint(-90, -70),
                "bat": random.randint(6, 90),
                "type":"indoor",
                "floor":"1"
            },
            {
                "id": 3,
                "temp": round(random.uniform(24.0, 25.0), 1),
                "hum": round(random.uniform(60.0, 90.0), 1),
                "rssi": random.randint(-90, -70),
                "bat": random.randint(6, 90),
                "type":"indoor",
                "floor":"5"
            },
            {
                "id": 4,
                "temp": round(random.uniform(25.0, 26.0), 1),
                "hum": round(random.uniform(60.0, 90.0), 1),
                "rssi": random.randint(-90, -70),
                "bat": random.randint(6, 90),
                "type":"indoor",
                "floor":"10"
            },
            {
                "id": 5,
                "temp": round(random.uniform(23.0, 28.0), 1),
                "hum": round(random.uniform(60.0, 90.0), 1),
                "rssi": random.randint(-90, -70),
                "bat": random.randint(6, 90),
                "type":"indoor",
                "floor":"rooftop"
            }
        ],

        "hvac": {
            "thermostats1": {
                "setpoint": random.randint(68, 72),
                "humidity": random.randint(40, 60),
                "temperature": round(random.uniform(65.0, 75.0), 1),
                "op_mode": random.choice(["cooling", "heating", "idle"])
            },

            "thermostats2": {
                "setpoint": random.randint(68, 72),
                "humidity": random.randint(40, 60),
                "temperature": round(random.uniform(65.0, 75.0), 1),
                "op_mode": random.choice(["cooling", "heating", "idle"])
            },

            "heatpump": random.choice(["ON", "OFF"]),
            "gas_furnace": random.choice(["ON", "OFF"])
        },

        "network": {
            "active": "wifi",
            "status": {
                "ip": "192.168.96.69",
                "SSID": "SFSCWIFI",
                "signal": random.randint(-80, -50)
            }
        },

        "power": {
            "source": "battery",
            "bat_level": random.randint(60, 100)
        },

        "error_code": 0,

        "operation_mode": {
            "mode": "local_manual",
            "operation": {
                "heat_source": "HEATPUMP",
                "return_to_cloud_after_min": 240,
                "time_remaining_min": random.randint(0, 240),
                "initiated_by": "Admin"
            }
        }
    }

    return telemetry_data




# =========================
# Publish Telemetry
# =========================
try:

    while True:

        data = generate_telemetry_data()

        payload = json.dumps(
            data,
            separators=(",", ":")
        )

        result = client.publish(
            telemetry_topic,
            payload=payload,
            qos=1
        )

        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(".")
            # print("Sent:")
            # print("Topic:", telemetry_topic)
            # print("Payload:", payload)
        else:
            print("Publish failed, rc =", result.rc)

        time.sleep(30)

except KeyboardInterrupt:

    print("\nStopping MQTT client...")

finally:

    client.loop_stop()
    client.disconnect()