import paho.mqtt.client as mqtt
import json
import time

# =========================
# MQTT Configuration
# =========================
broker_address = "tconnect.innovation.com.vn"
port = 8883

client_id = "DEV-20260831-0002"

telemetry_topic = f"v1/devices/{client_id}/telemetry"
attribute_topic = f"v1/devices/{client_id}/attribute"

cert_file = "DEV-20260831-0002.crt"
key_file = "DEV-20260831-0002.key"


# =========================
# MQTT Callbacks
# =========================
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT Connected successfully")

        # Subscribe nếu server/device cần nhận message
        client.subscribe(telemetry_topic)

        print("Subscribed:", telemetry_topic)

    else:
        print("MQTT connection failed, rc =", rc)


def on_message(client, userdata, msg):
    print("Received:")
    print("  Topic:", msg.topic)
    print("  Payload:", msg.payload.decode())


def on_disconnect(client, userdata, rc):
    print("MQTT disconnected, rc =", rc)


# =========================
# Create MQTT Client
# =========================
client = mqtt.Client(client_id=client_id)

# mTLS
client.tls_set(
    certfile=cert_file,
    keyfile=key_file,
)

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
telemetry_data = {
    "lora_sensors": [
        {
            "id": 1,
            "temp": 25.6,
            "hum": 65.2,
            "rssi": -80,
            "bat": 90
        },
        {
            "id": 2,
            "temp": 24.9,
            "hum": 63.0,
            "rssi": -78,
            "bat": 88
        },
        {
            "id": 3,
            "temp": 25.1,
            "hum": 64.5,
            "rssi": -85,
            "bat": 92
        },
        {
            "id": 4,
            "temp": 26.0,
            "hum": 62.1,
            "rssi": -82,
            "bat": 75
        },
        {
            "id": 5,
            "temp": 25.4,
            "hum": 66.3,
            "rssi": -79,
            "bat": 81
        }
    ],

    "hvac": {
        "thermostats1": {
            "setpoint": 69,
            "humidity": 96,
            "temperature": 69,
            "op_mode": "cooling"
        },
        "thermostats2": {
            "setpoint": 69,
            "humidity": 96,
            "temperature": 69,
            "op_mode": "cooling"
        },
        "heatpump": "ON",
        "gas_furnace": "OFF"
    },

    "network": {
        "active": "wifi",
        "status": {
            "ip": "192.168.96.69",
            "SSID": "SFSCWIFI",
            "signal": -67
        }
    },

    "power": {
        "source": "battery",
        "bat_level": 96
    },

    "error_code": 0,

    "operation_mode": {
        "mode": "local_manual",
        "operation": {
            "heat_source": "HEATPUMP",
            "return_to_cloud_after_min": 240,
            "time_remaining_min": 180,
            "initiated_by": "Admin"
        }
    }
}


# =========================
# Publish Telemetry
# =========================
try:

    while True:

        payload = json.dumps(
            telemetry_data,
            separators=(",", ":")
        )

        result = client.publish(
            telemetry_topic,
            payload=payload,
            qos=1
        )

        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print("Sent:")
            print("Topic:", telemetry_topic)
            print("Payload:", payload)
        else:
            print("Publish failed, rc =", result.rc)

        time.sleep(30)

except KeyboardInterrupt:

    print("\nStopping MQTT client...")

finally:

    client.loop_stop()
    client.disconnect()