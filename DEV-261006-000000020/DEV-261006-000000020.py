
import os
import ssl
import json
import time
import random
import threading

import paho.mqtt.client as mqtt
from dotenv import load_dotenv


# ==================================================
# LOAD ENVIRONMENT
# ==================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

DEVICE_ID = os.getenv("DEVICE_ID")
CERT_ID = os.getenv("CERT_ID")

if not DEVICE_ID or not CERT_ID:
    raise ValueError("DEVICE_ID and CERT_ID must be configured in .env")

BROKER = os.getenv("MQTT_BROKER", "sfscm.net")
PORT = int(os.getenv("MQTT_PORT", "8883"))

CERTS_DIR = os.getenv("CERTS_DIR", BASE_DIR)

if not os.path.isabs(CERTS_DIR):
    CERTS_DIR = os.path.join(BASE_DIR, CERTS_DIR)

CERTFILE = os.path.join(CERTS_DIR, f"{CERT_ID}.crt")
KEYFILE = os.path.join(CERTS_DIR, f"{CERT_ID}.key")
CA_CERTFILE = os.path.join(CERTS_DIR, "sfscm.pem")


# ==================================================
# MQTT TOPICS
# ==================================================

telemetry_topic = f"device/{DEVICE_ID}/telemetry"
downlink_topic = f"device/{DEVICE_ID}/attribute/downlink"
request_topic = f"device/{DEVICE_ID}/attribute/uplink"


# ==================================================
# INTERVALS
# ==================================================

PUBLISH_INTERVAL = 30
REQUEST_INTERVAL = 60

REQUEST_TYPES = [
    "energy_rate",
    "season",
    "hvac"
]




# ==================================================
# LOW-COST CONFIGURATION
# ==================================================

# Default gas price from the reference document.
# Unit: cent/kWh
#
# Replace this with the actual Server value
# when received through energy_rate.

DEFAULT_GAS_COST = 3.52

# OAT source:
# LoRa Sensor ID = 1 (outdoor)

OAT_SENSOR_ID = 1

# All prices must use the same currency and energy unit.

low_cost_data = {
    "electricity_cost": None,
    "gas_cost": DEFAULT_GAS_COST,
    "tou_period": None,
    "season": None,
    "hvac_curves": {},
    "last_heating_source": None
}

# Sensor data
sensor_data = {}

# Thread safety
data_lock = threading.RLock()


# ==================================================
# UTILITY
# ==================================================

def get_number(data, keys):

    if not isinstance(data, dict):
        return None

    for key in keys:

        value = data.get(key)

        if value is not None:

            try:
                return float(value)
            except (ValueError, TypeError):
                continue

    return None


def safe_float(value):

    try:
        return float(value)
    except (ValueError, TypeError):
        return None


# ==================================================
# GENERATE TELEMETRY DATA
# ==================================================

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
        ],

        "hvac": {
            "thermostats1": {
                "setpoint": 26,
                "hum": 96,
                "temp": 22,
                "op_mode": "heating"
            },
            "thermostats2": {
                "setpoint": 28,
                "hum": 96,
                "temp": 23,
                "op_mode": "heating"
            },
            "mau": {
                "hum": 60,
                "temp": 29
            },
            "is_connected": True
        }
        ,
        "onboard_sensor": {
              "temp": round(random.uniform(23.0, 28.0), 1),
              "hum": round(random.uniform(50.0, 70.0), 1),
           }
    }

    # Store generated outdoor sensor value
    with data_lock:

        for sensor in telemetry_data["lora_sensors"]:
            sensor_data[sensor["id"]] = sensor.copy()

    return telemetry_data


# ==================================================
# LINEAR INTERPOLATION
# ==================================================

def interpolate_curve(curve, oat, value_key):

    if not curve or oat is None:
        return None

    points = []

    for item in curve:

        point_oat = safe_float(item.get("oat"))
        point_value = safe_float(item.get(value_key))

        if point_oat is None or point_value is None:
            continue

        points.append((point_oat, point_value))

    if not points:
        return None

    points.sort(key=lambda x: x[0])

    # Exact match
    for point_oat, point_value in points:

        if abs(oat - point_oat) < 0.000001:
            return point_value

    # Boundary handling:
    # Use nearest endpoint outside the performance curve range.
    if oat <= points[0][0]:
        return points[0][1]

    if oat >= points[-1][0]:
        return points[-1][1]

    # Linear interpolation
    for i in range(len(points) - 1):

        x1, y1 = points[i]
        x2, y2 = points[i + 1]

        if x1 <= oat <= x2:

            if x2 == x1:
                return y1

            result = y1 + (
                (oat - x1) * (y2 - y1) / (x2 - x1)
            )

            return result

    return None


# ==================================================
# UPDATE HVAC PERFORMANCE CURVES
# ==================================================

def update_hvac_curves(data):

    if not isinstance(data, dict):
        return

    hvac_list = data.get("hvac", [])

    if not isinstance(hvac_list, list):
        print("[HVAC] Invalid HVAC performance data")
        return

    new_curves = {}

    for equipment in hvac_list:

        equipment_type = str(
            equipment.get("type", "")
        ).upper()

        performance_curve = equipment.get(
            "performance_curve", []
        )

        if equipment_type not in ["ELECTRIC", "GAS"]:
            continue

        if not isinstance(performance_curve, list):
            continue

        new_curves[equipment_type] = {
            "maximum_heating_capacity": safe_float(
                equipment.get("maximum_heating_capacity")
            ),
            "performance_curve": performance_curve
        }

    if new_curves:

        with data_lock:
            low_cost_data["hvac_curves"].update(new_curves)

        print(
            "[HVAC] Performance curves updated:",
            list(new_curves.keys())
        )

    else:

        print("[HVAC] No valid performance curves received")


# ==================================================
# UPDATE ENERGY RATE
# ==================================================

def update_energy_rate(data):

    # Expected Server response:
    # data.energy_rate.electricity_price
    # data.energy_rate.gas_price

    energy_rate = data.get("energy_rate", {})
    print("<><><><><><><><><><><><><><><M><><><><><--------------------------------------------")
    print(energy_rate)

    if not isinstance(energy_rate, dict):
        print("[ENERGY] Invalid energy_rate payload")
        return

    electricity_price = safe_float(
        energy_rate.get("electricity_price")
    )

    gas_price = safe_float(
        energy_rate.get("gas_price")
    )

    electricity_mode = energy_rate.get("electricity_mode")
    gas_mode = energy_rate.get("gas_mode")
    interval = energy_rate.get("interval")

    with data_lock:

        if electricity_price is not None and electricity_price > 0:
            low_cost_data["electricity_cost"] = electricity_price

        if gas_price is not None and gas_price > 0:
            low_cost_data["gas_cost"] = gas_price

        if electricity_mode is not None:
            low_cost_data["electricity_mode"] = electricity_mode

        if gas_mode is not None:
            low_cost_data["gas_mode"] = gas_mode

        if interval is not None:
            low_cost_data["energy_interval"] = interval

    print("\n========== ENERGY RATE UPDATED ==========")

    print(f"Electricity Mode : {electricity_mode}")
    print(f"Electricity Price: {electricity_price}")
    print(f"Gas Mode         : {gas_mode}")
    print(f"Gas Price        : {gas_price}")
    print(f"Interval         : {interval}")

    print("=========================================\n")



# ==================================================
# UPDATE SEASON
# ==================================================

def update_season(data):

    season = data.get("season")

    if season is not None:

        with data_lock:
            low_cost_data["season"] = season

        print("[SEASON] Updated:", season)


# ==================================================
# GET CURRENT OAT
# ==================================================

def get_current_oat():

    with data_lock:

        sensor = sensor_data.get(OAT_SENSOR_ID)

        if sensor is None:
            return None

        return safe_float(sensor.get("temp"))


# ==================================================
# LOW-COST CALCULATION
# ==================================================

def calculate_low_cost():

    with data_lock:

        electricity_cost = low_cost_data["electricity_cost"]
        gas_cost = low_cost_data["gas_cost"]

        curves = {
            key: value.copy()
            for key, value in low_cost_data["hvac_curves"].items()
        }

        last_source = low_cost_data["last_heating_source"]
        tou_period = low_cost_data["tou_period"]
        season = low_cost_data["season"]

    oat = get_current_oat()

    print("\n")
    print("=" * 55)
    print("          LOW-COST HEATING CALCULATION")
    print("=" * 55)

    print(f"OAT                 : {oat} °C")
    print(f"Electricity Cost    : {electricity_cost} cent/kWh")
    print(f"Gas Cost            : {gas_cost} cent/kWh")
    print(f"TOU Period          : {tou_period}")
    print(f"Season              : {season}")

    electric = curves.get("ELECTRIC")
    gas = curves.get("GAS")

    if oat is None:
        print("[LOW-COST] Waiting for outdoor temperature")
        return None

    if electricity_cost is None or gas_cost is None:
        print("[LOW-COST] Waiting for energy prices")
        return None

    if electricity_cost <= 0 or gas_cost <= 0:
        print("[LOW-COST] Invalid energy prices")
        return None

    if electric is None or gas is None:
        print("[LOW-COST] Waiting for HVAC performance curves")
        return None

    # --------------------------------------
    # Get COP from ELECTRIC performance curve
    # --------------------------------------

    electric_curve = electric.get("performance_curve", [])

    ecop = interpolate_curve(
        electric_curve,
        oat,
        "cop"
    )

    # --------------------------------------
    # Get Gas Efficiency from GAS curve
    # --------------------------------------

    gas_curve = gas.get("performance_curve", [])

    gas_eff_percent = interpolate_curve(
        gas_curve,
        oat,
        "efficiency"
    )

    if ecop is None or gas_eff_percent is None:

        print("[LOW-COST] Cannot calculate equipment efficiency")
        return None

    # Convert percentage to decimal
    gas_eff = gas_eff_percent / 100.0

    if ecop <= 0 or gas_eff <= 0:
        print("[LOW-COST] Invalid equipment efficiency")
        return None

    # --------------------------------------
    # Calculate ratios
    # --------------------------------------

    A = ecop / gas_eff
    B = electricity_cost / gas_cost

    print("-" * 55)
    print(f"Electric COP (eCOP)  : {ecop:.3f}")
    print(f"Gas Efficiency       : {gas_eff_percent:.2f}%")
    print(f"Gas Efficiency (gEff): {gas_eff:.3f}")

    print("-" * 55)

    print(f"Efficiency Ratio (A) : {A:.3f}")
    print(f"Tariff Ratio (B)     : {B:.3f}")

    print("-" * 55)

    
    # --------------------------------------
    # Select Heating Source
    # --------------------------------------

    if A > B:

        heating_source = "HP_HEAT"
        reason = "Electric heating has lower operating cost"

    elif A < B:

        heating_source = "FURNACE_HEAT"
        reason = "Gas heating has lower operating cost"

    else:

        heating_source = last_source
        reason = "Equal cost - keep previous source"

    print("\n------------------------------------------")
    print(f"RECOMMENDED HEATING SOURCE: {heating_source}")
    print(f"Reason: {reason}")
    print("------------------------------------------")

    # --------------------------------------
    # Automatic Edge Switching
    # --------------------------------------

    if heating_source is not None:

        # if heating_source != last_source:

        #     print("[LOW-COST] Heating source change detected")

        success = publish_heating_source_config(
            heating_source
        )

        if success:

            with data_lock:
                low_cost_data["last_heating_source"] = heating_source

        # else:

        #     print(
        #         f"[LOW-COST] Source unchanged: {heating_source}. "
        #         "No CONFIG command required."
        #     )

    return {
        "mode": "LOW_COST",
        "oat": oat,
        "ecop": round(ecop, 3),
        "gas_efficiency": round(gas_eff_percent, 2),
        "gas_eff": round(gas_eff, 3),
        "efficiency_ratio": round(A, 3),
        "tariff_ratio": round(B, 3),
        "electricity_cost": electricity_cost,
        "gas_cost": gas_cost,
        "tou_period": tou_period,
        "heating_source": heating_source,
        "reason": reason
    }


# ==================================================
# PROCESS DOWNLINK
# ==================================================

def process_downlink(payload):

    if not isinstance(payload, dict):
        return

    data = payload.get("data", {})

    if not isinstance(data, dict):
        return

    # ======================================
    # ENERGY RATE RESPONSE
    # ======================================

    if isinstance(data.get("energy_rate"), dict):

        print("[DOWNLINK] Energy rate received")

        update_energy_rate(data)

        calculate_low_cost()

    # ======================================
    # HVAC PERFORMANCE CURVE RESPONSE
    # ======================================

    if isinstance(data.get("hvac"), list):

        print("[DOWNLINK] HVAC performance curves received")

        update_hvac_curves(data)

        calculate_low_cost()

    # ======================================
    # SEASON RESPONSE
    # ======================================

    if isinstance(data.get("season"), dict):

        print("[DOWNLINK] Season received")

        update_season(data["season"])

    elif data.get("type") == "season":

        print("[DOWNLINK] Season received")

        update_season(data)

    # ======================================
    # ALTERNATIVE RESPONSE FORMAT
    # ======================================

    elif data.get("type") == "hvac":

        print("[DOWNLINK] HVAC received")

        update_hvac_curves(data)

        calculate_low_cost()


# ==================================================
# GENERATE REQUEST
# ==================================================

def generate_request(request_type):

    return {
        "type": "REQUEST",
        "timestamp": int(time.time()),
        "data": {
            "type": request_type
        }
    }


# ==================================================
# PUBLISH REQUESTS
# ==================================================

def publish_requests():

    if not client.is_connected():
        return

    print("\n========== SENDING REQUESTS ==========")

    for request_type in REQUEST_TYPES:

        request_data = generate_request(request_type)

        result = client.publish(
            request_topic,
            payload=json.dumps(request_data),
            qos=1
        )

        if result.rc == mqtt.MQTT_ERR_SUCCESS:

            print(f"[REQUEST] Sent: {request_type}")

        else:

            print(
                f"[REQUEST] Failed: {request_type}, "
                f"rc={result.rc}"
            )

    print("=======================================\n")
# ==================================================
# PUBLISH HEATING SOURCE CONFIG
# ==================================================

def publish_heating_source_config(heating_source):

    if not client.is_connected():
        print("[EDGE] MQTT not connected. Cannot switch source.")
        return False

    source_mapping = {
        "HP_HEAT": "HP_HEAT",
        "COOLING": "COOLING",
        "FURNACE_HEAT": "FURNACE_HEAT"
    }

    edge_source = source_mapping.get(heating_source)

    if edge_source is None:
        print(f"[EDGE] Unsupported heating source: {heating_source}")
        return False

    config_payload = {
        "type": "CONFIG",
        "timestamp": int(time.time()),
        "data": {
            "operation_mode": {
                "mode": "LOCAL",
                "operation": {
                    "operating_mode": "LOW_COST",
                    "duration": 240,
                    "source": edge_source,
                    "running_time": 180,
                    "initiated_by": "SFSC"
                }
            }
        }
    }

    result = client.publish(
        request_topic,
        payload=json.dumps(config_payload),
        qos=1
    )

    if result.rc == mqtt.MQTT_ERR_SUCCESS:

        print("\n========== EDGE CONFIG SENT ==========")
        print(f"Operating Mode : LOW_COST")
        print(f"Heating Source : {edge_source}")
        print(f"Duration       : 240")
        print(f"Running Time   : 180")
        print(f"Initiated By   : SFSC")
        print("Payload:")
        print(json.dumps(config_payload, indent=4))
        print("======================================\n")

        return True

    print(f"[EDGE] Config publish failed: {result.rc}")
    return False


# ==================================================
# MQTT CALLBACKS
# ==================================================

def on_connect(client, userdata, flags, rc):

    if rc == 0:

        print("[MQTT] Connected successfully")

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

        payload = json.loads(
            msg.payload.decode("utf-8")
        )

        print(
            "Payload:",
            json.dumps(
                payload,
                indent=4,
                ensure_ascii=False
            )
        )

        process_downlink(payload)

    except Exception as e:

        print("[DOWNLINK] Processing error:", str(e))

        print(
            "Payload:",
            msg.payload.decode("utf-8", errors="replace")
        )

    print("=======================================\n")


def on_publish(client, userdata, mid):

    print(f"[MQTT] Publish ACK: mid={mid}")


def on_disconnect(client, userdata, rc):

    print(f"[MQTT] Disconnected: {rc}")


# ==================================================
# MQTT CLIENT
# ==================================================

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

client.reconnect_delay_set(
    min_delay=1,
    max_delay=30
)


# ==================================================
# CONNECT MQTT
# ==================================================

print("=" * 55)
print("DEVICE_ID :", DEVICE_ID)
print("BROKER    :", BROKER)
print("PORT      :", PORT)
print("TELEMETRY :", telemetry_topic)
print("REQUEST   :", request_topic)
print("DOWNLINK  :", downlink_topic)
print("=" * 55)

print("[MQTT] Connecting...")

client.connect(BROKER, PORT, 60)

client.loop_start()


# ==================================================
# MAIN LOOP
# ==================================================

last_telemetry_time = 0
last_request_time = 0

try:

    while True:

        current_time = time.time()

        if client.is_connected():

            # ----------------------------------
            # TELEMETRY EVERY 30 SECONDS
            # ----------------------------------

            if current_time - last_telemetry_time >= PUBLISH_INTERVAL:

                telemetry_data = generate_telemetry()

                # Calculate Low-Cost result
                low_cost_result = calculate_low_cost()

                if low_cost_result is not None:

                    telemetry_data["low_cost"] = low_cost_result

                result = client.publish(
                    telemetry_topic,
                    payload=json.dumps(telemetry_data),
                    qos=1
                )

                if result.rc == mqtt.MQTT_ERR_SUCCESS:

                    print(
                        "[TELEMETRY] Published successfully"
                    )

                else:

                    print(
                        f"[TELEMETRY] Publish failed: {result.rc}"
                    )

                last_telemetry_time = current_time

            # ----------------------------------
            # REQUEST EVERY 60 SECONDS
            # ----------------------------------

            if current_time - last_request_time >= REQUEST_INTERVAL:

                publish_requests()

                last_request_time = current_time

        else:

            print("[MQTT] Not connected. Waiting for reconnect...")

        time.sleep(1)


except KeyboardInterrupt:

    print("\n[MQTT] Stopping...")


finally:

    client.disconnect()
    client.loop_stop()

    print("[MQTT] Disconnected")
