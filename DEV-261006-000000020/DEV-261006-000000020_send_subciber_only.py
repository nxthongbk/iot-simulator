import os
import ssl
import json
import time
import random

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

# ==========================================
# Load .env
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

DEVICE_ID = os.getenv("DEVICE_ID")
CERT_ID = os.getenv("CERT_ID")

BROKER = os.getenv("MQTT_BROKER", "sfscm.net")
PORT = int(os.getenv("MQTT_PORT", "8883"))

CERTS_DIR = os.getenv("CERTS_DIR", BASE_DIR)

if not os.path.isabs(CERTS_DIR):
    CERTS_DIR = os.path.join(BASE_DIR, CERTS_DIR)

CERTFILE = os.path.join(CERTS_DIR, f"{CERT_ID}.crt")
KEYFILE = os.path.join(CERTS_DIR, f"{CERT_ID}.key")
CA_CERTFILE = os.path.join(CERTS_DIR, "sfscm.pem")

# ==========================================
# MQTT Topics
# ==========================================

telemetry_topic = f"device/{DEVICE_ID}/telemetry"
downlink_topic = f"device/{DEVICE_ID}/attribute/downlink"

PUBLISH_INTERVAL = 30

# ==========================================
# Generate Telemetry Data
# ==========================================

def generate_telemetry():

    telemetry_data = {
        "lora_sensors": [
            {
                "id": 1,
                "temp": round(random.uniform(2.0, 4.0), 1),
                "hum": round(random.uniform(60.0, 90.0), 1),
                "rssi": random.randint(-90, -70),
                "bat": random.randint(6, 90),
                "type": "outdoor",
                "floor": "0"
            },
            {
                "id": 2,
                "temp": round(random.uniform(23.0, 24.0), 1),
                "hum": round(random.uniform(60.0, 90.0), 1),
                "rssi": random.randint(-90, -70),
                "bat": random.randint(6, 90),
                "type": "indoor",
                "floor": "1"
            },
            {
                "id": 3,
                "temp": round(random.uniform(24.0, 25.0), 1),
                "hum": round(random.uniform(60.0, 90.0), 1),
                "rssi": random.randint(-90, -70),
                "bat": random.randint(6, 90),
                "type": "indoor",
                "floor": "5"
            },
            {
                "id": 4,
                "temp": round(random.uniform(25.0, 26.0), 1),
                "hum": round(random.uniform(60.0, 90.0), 1),
                "rssi": random.randint(-90, -70),
                "bat": random.randint(6, 90),
                "type": "indoor",
                "floor": "10"
            },
            {
                "id": 5,
                "temp": round(random.uniform(23.0, 28.0), 1),
                "hum": round(random.uniform(60.0, 90.0), 1),
                "rssi": random.randint(-90, -70),
                "bat": random.randint(6, 90),
                "type": "indoor",
                "floor": "rooftop"
            }
        ]
    }

    return telemetry_data


# ==========================================
# MQTT Callbacks
# ==========================================

def on_connect(client, userdata, flags, rc):

    if rc == 0:

        print("[MQTT] Connected successfully")

        # Subscribe Downlink
        client.subscribe(downlink_topic, qos=1)

        print(f"[MQTT] Subscribe: {downlink_topic}")

    else:

        print(f"[MQTT] Connection failed: {rc}")


def on_subscribe(client, userdata, mid, granted_qos):

    print(f"[MQTT] Subscribe ACK: {granted_qos}")


def on_message(client, userdata, msg):

    print("\n========== DOWNLINK RECEIVED ==========")

    print("Topic:", msg.topic)

    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        print("Payload:", json.dumps(payload, indent=4, ensure_ascii=False))

    except Exception:
        print("Payload:", msg.payload.decode("utf-8", errors="replace"))

    print("=======================================\n")


def on_publish(client, userdata, mid):

    print(f"[MQTT] Publish ACK: mid={mid}")


def on_disconnect(client, userdata, rc):

    print(f"[MQTT] Disconnected: {rc}")


# ==========================================
# MQTT Client
# ==========================================

client = mqtt.Client(client_id=DEVICE_ID)

client.tls_set(
    ca_certs=CA_CERTFILE,
    certfile=CERTFILE,
    keyfile=KEYFILE,
    cert_reqs=ssl.CERT_NONE
)

client.tls_insecure_set(True)

client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_publish = on_publish
client.on_disconnect = on_disconnect


# ==========================================
# Connect MQTT
# ==========================================

print("====================================")
print("DEVICE_ID:", DEVICE_ID)
print("CERT_ID:", CERT_ID)
print("BROKER:", BROKER)
print("PORT:", PORT)
print("TELEMETRY:", telemetry_topic)
print("DOWNLINK:", downlink_topic)
print("====================================")

print("[MQTT] Connecting...")

client.connect(BROKER, PORT, 60)

# Start MQTT background loop
client.loop_start()


# ==========================================
# Publish Telemetry Every 30 Seconds
# ==========================================

try:

    while True:

        if client.is_connected():

            telemetry_data = generate_telemetry()

            payload = json.dumps(telemetry_data)

            result = client.publish(
                telemetry_topic,
                payload=payload,
                qos=1
            )

            if result.rc == mqtt.MQTT_ERR_SUCCESS:

                print(
                    f"\n[TELEMETRY] Published successfully "
                    f"| topic={telemetry_topic}"
                )

                print(
                    json.dumps(
                        telemetry_data,
                        indent=4,
                        ensure_ascii=False
                    )
                )

            else:

                print(
                    f"[TELEMETRY] Publish failed: rc={result.rc}"
                )

        else:

            print("[MQTT] Not connected. Waiting for reconnect...")

        time.sleep(PUBLISH_INTERVAL)


except KeyboardInterrupt:

    print("\n[MQTT] Stopping...")

finally:

    client.disconnect()
    client.loop_stop()

    print("[MQTT] Disconnected")