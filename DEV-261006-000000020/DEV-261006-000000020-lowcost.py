
import os
import ssl
import json
import time
import random
import threading

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

# ==========================================
# LOAD ENV
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

PUBLISH_INTERVAL = 30

# Optional fallback values in .env
EFFICIENCY_RATIO = os.getenv("EFFICIENCY_RATIO")
TARIFF_RATIO = os.getenv("TARIFF_RATIO")

# ==========================================
# MQTT TOPICS
# ==========================================

telemetry_topic = f"device/{DEVICE_ID}/telemetry"
downlink_topic = f"device/{DEVICE_ID}/attribute/downlink"

# ==========================================
# GLOBAL OPERATION CONFIGURATION
# ==========================================

operation_mode = None
operation_lock = threading.Lock()

# ==========================================
# LOW COST DECISION
# ==========================================

def calculate_low_cost(operation):

    """
    A = eCOP / gEff
    B = Electricity Cost / Gas Cost

    A > B : HEAT_PUMP
    A < B : FURNACE_HEAT
    A = B : Keep current source
    """

    current_source = operation.get("source", "HEAT_PUMP")

    # Prefer ratios received from attributes
    efficiency_ratio = operation.get("efficiency_ratio")
    tariff_ratio = operation.get("tariff_ratio")

    # Calculate ratios if raw parameters are available
    if efficiency_ratio is None:

        ecop = operation.get("eCOP")
        geff = operation.get("gEff")

        if ecop is not None and geff is not None and float(geff) != 0:
            efficiency_ratio = float(ecop) / float(geff)

    if tariff_ratio is None:

        electricity_cost = operation.get("electricity_cost")
        gas_cost = operation.get("gas_cost")

        if electricity_cost is not None and gas_cost is not None and float(gas_cost) != 0:
            tariff_ratio = float(electricity_cost) / float(gas_cost)

    # Fallback to environment variables
    if efficiency_ratio is None and EFFICIENCY_RATIO:
        efficiency_ratio = float(EFFICIENCY_RATIO)

    if tariff_ratio is None and TARIFF_RATIO:
        tariff_ratio = float(TARIFF_RATIO)

    # Cannot calculate
    if efficiency_ratio is None or tariff_ratio is None:

        print("[LOW_COST] Missing efficiency_ratio or tariff_ratio")
        print("[LOW_COST] Keep current source:", current_source)

        return current_source

    A = float(efficiency_ratio)
    B = float(tariff_ratio)

    print("\n========== LOW COST CALCULATION ==========")
    print(f"Efficiency Ratio A : {A:.3f}")
    print(f"Tariff Ratio B     : {B:.3f}")

    if A > B:

        selected_source = "HEAT_PUMP"

    elif A < B:

        selected_source = "FURNACE_HEAT"

    else:

        selected_source = current_source

    print(f"Selected Source    : {selected_source}")
    print("==========================================\n")

    return selected_source


# ==========================================
# PROCESS OPERATION MODE
# ==========================================

def process_operation_mode(config):

    mode = config.get("mode", "LOCAL")
    operation = config.get("operation", {})

    operating_mode = operation.get(
        "operating_mode",
        "MANUAL"
    )

    current_source = operation.get(
        "source",
        "HEAT_PUMP"
    )

    print("\n========== OPERATION CONFIGURATION ==========")
    print("Mode          :", mode)
    print("Operating Mode:", operating_mode)
    print("Current Source:", current_source)

    # LOCAL is accepted as a compatibility alias for LOCAL_AUTO
    if mode == "LOCAL":
        mode = "LOCAL_AUTO"

    # CLOUD: use source selected by Cloud
    if mode == "CLOUD":

        print("[MODE] CLOUD CONTROL")
        selected_source = current_source

    # LOCAL MANUAL
    elif mode == "LOCAL_MANUAL":

        print("[MODE] LOCAL MANUAL")
        selected_source = current_source

    # LOCAL AUTO
    elif mode == "LOCAL_AUTO":

        print("[MODE] LOCAL AUTO")

        if operating_mode == "LOW_COST":

            selected_source = calculate_low_cost(operation)

        elif operating_mode == "LOW_EMISSION":

            print("[MODE] LOW_EMISSION logic not implemented")
            selected_source = current_source

        elif operating_mode == "MANUAL":

            selected_source = current_source

        else:

            print("[WARNING] Unknown operating mode")
            selected_source = current_source

    else:

        print("[WARNING] Unknown operation mode")
        selected_source = current_source

    operation["source"] = selected_source
    config["operation"] = operation

    print("Final Source:", selected_source)
    print("============================================\n")

    return config


# ==========================================
# RECEIVE ATTRIBUTE
# ==========================================

def on_message(client, userdata, msg):

    global operation_mode

    print("\n========== ATTRIBUTE RECEIVED ==========")
    print("Topic:", msg.topic)

    try:

        payload = json.loads(msg.payload.decode("utf-8"))

        print(json.dumps(
            payload,
            indent=4,
            ensure_ascii=False
        ))

        # Support both direct and wrapped attribute formats
        config = payload.get("operation_mode", payload)

        if not isinstance(config, dict):
            raise ValueError("Invalid operation_mode format")

        if "operation" not in config:
            raise ValueError("Missing operation configuration")

        # Process new configuration
        updated_config = process_operation_mode(config)

        with operation_lock:
            operation_mode = updated_config

        print("[ATTRIBUTE] Configuration updated successfully")

    except Exception as e:

        print("[ATTRIBUTE] Processing error:", str(e))

    print("========================================\n")


# ==========================================
# GENERATE SENSOR TELEMETRY
# ==========================================

def generate_telemetry():

    return {
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


# ==========================================
# MQTT CALLBACKS
# ==========================================

def on_connect(client, userdata, flags, rc):

    if rc == 0:

        print("[MQTT] Connected successfully")

        client.subscribe(downlink_topic, qos=1)

        print("[MQTT] Subscribe:", downlink_topic)

    else:

        print("[MQTT] Connection failed:", rc)


def on_subscribe(client, userdata, mid, granted_qos):

    print("[MQTT] Subscribe ACK:", granted_qos)


def on_publish(client, userdata, mid):

    print(f"[MQTT] Publish ACK: mid={mid}")


def on_disconnect(client, userdata, rc):

    print("[MQTT] Disconnected:", rc)


# ==========================================
# MQTT CLIENT
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
# CONNECT
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
client.loop_start()


# ==========================================
# PUBLISH TELEMETRY EVERY 30 SECONDS
# ==========================================

try:

    while True:

        if client.is_connected():

            telemetry_data = generate_telemetry()

            # Get latest operation configuration
            with operation_lock:
                current_operation_mode = (
                    json.loads(json.dumps(operation_mode))
                    if operation_mode is not None
                    else None
                )

            # Add operation_mode to telemetry
            if current_operation_mode is not None:

                telemetry_data["operation_mode"] = current_operation_mode

            payload = json.dumps(
                telemetry_data,
                ensure_ascii=False
            )

            result = client.publish(
                telemetry_topic,
                payload=payload,
                qos=1
            )

            if result.rc == mqtt.MQTT_ERR_SUCCESS:

                print("\n[TELEMETRY] Published successfully")
                print("Topic:", telemetry_topic)

                print(json.dumps(
                    telemetry_data,
                    indent=4,
                    ensure_ascii=False
                ))

            else:

                print("[TELEMETRY] Publish failed:", result.rc)

        else:

            print("[MQTT] Not connected. Waiting for reconnect...")

        time.sleep(PUBLISH_INTERVAL)


except KeyboardInterrupt:

    print("\n[MQTT] Stopping...")

finally:

    client.disconnect()
    client.loop_stop()

    print("[MQTT] Disconnected")
