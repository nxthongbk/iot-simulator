import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime, time as dt_time

# ============================================================
# MQTT CONFIG
# ============================================================

MQTT_HOST = "pdm.tmainnovation.com"
MQTT_PORT = 1883

MQTT_USERNAME = "admin"
MQTT_PASSWORD = "admin"

DEVICE_ID = "RoboDrill-CI-11-ElectricMeter"

MQTT_TOPIC = f"incoming/data/{DEVICE_ID}/values"

# ============================================================
# MACHINE WORKING SCHEDULE
# ============================================================

WORK_START_1 = dt_time(8, 0)
WORK_END_1   = dt_time(12, 0)

WORK_START_2 = dt_time(13, 0)
WORK_END_2   = dt_time(17, 0)

# Interval gửi dữ liệu
SEND_INTERVAL = 5

# ============================================================
# INITIAL ENERGY
# ============================================================

current_kwh = 12543.68
current_kvah = 13021.42
current_kvarh = 3512.76

# ============================================================
# MACHINE STATE
# ============================================================

def is_machine_working():

    now = datetime.now().time()

    # Ca sáng
    if WORK_START_1 <= now < WORK_END_1:
        return True

    # Ca chiều
    if WORK_START_2 <= now < WORK_END_2:
        return True

    return False


# ============================================================
# GENERATE ELECTRIC DATA
# ============================================================

def generate_data():

    global current_kwh
    global current_kvah
    global current_kvarh

    machine_running = is_machine_working()

    # --------------------------------------------------------
    # VOLTAGE
    # --------------------------------------------------------

    V1N = random.uniform(219.0, 222.0)
    V2N = random.uniform(219.0, 222.0)
    V3N = random.uniform(219.0, 222.0)

    VLN = (V1N + V2N + V3N) / 3

    V12 = random.uniform(379.0, 383.0)
    V23 = random.uniform(379.0, 383.0)
    V31 = random.uniform(379.0, 383.0)

    VLL = (V12 + V23 + V31) / 3

    # --------------------------------------------------------
    # MACHINE RUNNING
    # --------------------------------------------------------

    if machine_running:

        # Current
        I1 = random.uniform(10.0, 14.0)
        I2 = random.uniform(10.0, 14.0)
        I3 = random.uniform(10.0, 14.0)

        AI = (I1 + I2 + I3) / 3

        # Power
        kW1 = random.uniform(2.2, 3.2)
        kW2 = random.uniform(2.2, 3.2)
        kW3 = random.uniform(2.2, 3.2)

        kW = kW1 + kW2 + kW3

        # Power factor
        PF1 = random.uniform(0.92, 0.98)
        PF2 = random.uniform(0.92, 0.98)
        PF3 = random.uniform(0.92, 0.98)

        PF = (PF1 + PF2 + PF3) / 3

        # Apparent power
        kVA1 = kW1 / PF1
        kVA2 = kW2 / PF2
        kVA3 = kW3 / PF3

        kVA = kVA1 + kVA2 + kVA3

        # Reactive power
        kVAr1 = (kVA1 ** 2 - kW1 ** 2) ** 0.5
        kVAr2 = (kVA2 ** 2 - kW2 ** 2) ** 0.5
        kVAr3 = (kVA3 ** 2 - kW3 ** 2) ** 0.5

        kVAr = kVAr1 + kVAr2 + kVAr3

        # Frequency
        F = random.uniform(49.95, 50.05)

        # ----------------------------------------------------
        # ENERGY
        # ----------------------------------------------------

        # 5 seconds -> hours
        elapsed_hours = SEND_INTERVAL / 3600

        current_kwh += kW * elapsed_hours
        current_kvah += kVA * elapsed_hours
        current_kvarh += kVAr * elapsed_hours

    # --------------------------------------------------------
    # MACHINE STOPPED
    # --------------------------------------------------------

    else:

        # Máy vẫn có nguồn nhưng không tải
        I1 = random.uniform(0.05, 0.20)
        I2 = random.uniform(0.05, 0.20)
        I3 = random.uniform(0.05, 0.20)

        AI = (I1 + I2 + I3) / 3

        kW1 = random.uniform(0.01, 0.04)
        kW2 = random.uniform(0.01, 0.04)
        kW3 = random.uniform(0.01, 0.04)

        kW = kW1 + kW2 + kW3

        PF1 = random.uniform(0.70, 0.90)
        PF2 = random.uniform(0.70, 0.90)
        PF3 = random.uniform(0.70, 0.90)

        PF = (PF1 + PF2 + PF3) / 3

        kVA1 = kW1 / PF1
        kVA2 = kW2 / PF2
        kVA3 = kW3 / PF3

        kVA = kVA1 + kVA2 + kVA3

        kVAr1 = (kVA1 ** 2 - kW1 ** 2) ** 0.5
        kVAr2 = (kVA2 ** 2 - kW2 ** 2) ** 0.5
        kVAr3 = (kVA3 ** 2 - kW3 ** 2) ** 0.5

        kVAr = kVAr1 + kVAr2 + kVAr3

        F = random.uniform(49.98, 50.02)

        # Energy vẫn tăng rất nhỏ
        elapsed_hours = SEND_INTERVAL / 3600

        current_kwh += kW * elapsed_hours
        current_kvah += kVA * elapsed_hours
        current_kvarh += kVAr * elapsed_hours

    # ========================================================
    # RETURN JSON
    # ========================================================

    return {
        "V1N": round(V1N, 2),
        "V2N": round(V2N, 2),
        "V3N": round(V3N, 2),
        "VLN": round(VLN, 2),

        "V12": round(V12, 2),
        "V23": round(V23, 2),
        "V31": round(V31, 2),
        "VLL": round(VLL, 2),

        "I1": round(I1, 2),
        "I2": round(I2, 2),
        "I3": round(I3, 2),
        "AI": round(AI, 2),

        "kW1": round(kW1, 3),
        "kW2": round(kW2, 3),
        "kW3": round(kW3, 3),

        "kVA1": round(kVA1, 3),
        "kVA2": round(kVA2, 3),
        "kVA3": round(kVA3, 3),

        "kVAr1": round(kVAr1, 3),
        "kVAr2": round(kVAr2, 3),
        "kVAr3": round(kVAr3, 3),

        "kW": round(kW, 3),
        "kVA": round(kVA, 3),
        "kVAr": round(kVAr, 3),

        "PF1": round(PF1, 3),
        "PF2": round(PF2, 3),
        "PF3": round(PF3, 3),
        "PF": round(PF, 3),

        "F": round(F, 2),

        "kWh": round(current_kwh, 3),
        "kVAh": round(current_kvah, 3),
        "kVArh": round(current_kvarh, 3)
    }


# ============================================================
# MQTT CALLBACK
# ============================================================

def on_connect(client, userdata, flags, rc):

    if rc == 0:
        print("MQTT Connected OK")
        print(f"Device : {DEVICE_ID}")
        print(f"Topic  : {MQTT_TOPIC}")

    else:
        print(f"MQTT Connect failed, rc={rc}")


def on_publish(client, userdata, mid):

    print(f"Data sent OK, message id = {mid}")


# ============================================================
# MQTT CLIENT
# ============================================================

client = mqtt.Client(client_id=DEVICE_ID)

client.username_pw_set(
    MQTT_USERNAME,
    MQTT_PASSWORD
)

client.on_connect = on_connect
client.on_publish = on_publish


# ============================================================
# CONNECT
# ============================================================

print("Connecting to MQTT...")

client.connect(
    MQTT_HOST,
    MQTT_PORT,
    keepalive=60
)

client.loop_start()


# ============================================================
# SEND DATA
# ============================================================

try:

    while True:

        now = datetime.now()

        machine_running = is_machine_working()

        data = generate_data()

        payload = json.dumps(data)

        result = client.publish(
            MQTT_TOPIC,
            payload,
            qos=1
        )

        # ----------------------------------------------------
        # LOG
        # ----------------------------------------------------

        status = "RUNNING" if machine_running else "STOPPED"

        if result.rc == mqtt.MQTT_ERR_SUCCESS:

            print(
                f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] "
                f"[{status}] "
                f"kW={data['kW']} | "
                f"kWh={data['kWh']} | "
                f"I={data['AI']} A"
            )

        else:

            print("Publish failed")

        time.sleep(SEND_INTERVAL)


except KeyboardInterrupt:

    print("Stopping...")

    client.loop_stop()
    client.disconnect()