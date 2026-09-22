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

DEVICE_ID = "RoboDrill-CI-11-VibrationSensor"

MQTT_TOPIC = f"incoming/data/{DEVICE_ID}/values"

# ============================================================
# MACHINE WORKING SCHEDULE
# ============================================================

WORK_START_1 = dt_time(8, 0)
WORK_END_1 = dt_time(12, 0)

WORK_START_2 = dt_time(13, 0)
WORK_END_2 = dt_time(17, 0)

# Gửi dữ liệu mỗi 5 giây
SEND_INTERVAL = 5

# ============================================================
# SENSOR STATE
# ============================================================

temperature = 32.0
battery = 3.72
soc = 87.5

# ============================================================
# MACHINE STATUS
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
# GENERATE VIBRATION DATA
# ============================================================

def generate_data():

    global temperature
    global battery
    global soc

    machine_running = is_machine_working()

    # ========================================================
    # MACHINE RUNNING
    # ========================================================

    if machine_running:

        # ----------------------------------------------------
        # Temperature
        # ----------------------------------------------------

        temperature += random.uniform(0.00, 0.08)

        # Giới hạn nhiệt độ
        temperature = min(temperature, 45.0)

        # ----------------------------------------------------
        # VIBRATION VELOCITY
        # ----------------------------------------------------

        velocity_x = random.uniform(1.2, 2.8)
        velocity_y = random.uniform(1.0, 2.5)
        velocity_z = random.uniform(1.3, 2.7)

        velocity_peak_x = velocity_x * random.uniform(1.7, 2.2)
        velocity_peak_y = velocity_y * random.uniform(1.7, 2.2)
        velocity_peak_z = velocity_z * random.uniform(1.7, 2.2)

        # ----------------------------------------------------
        # ACCELERATION
        # ----------------------------------------------------

        acceleration_x = random.uniform(0.25, 0.55)
        acceleration_y = random.uniform(0.20, 0.50)
        acceleration_z = random.uniform(0.30, 0.60)

        acceleration_peak_x = acceleration_x * random.uniform(2.2, 3.0)
        acceleration_peak_y = acceleration_y * random.uniform(2.2, 3.0)
        acceleration_peak_z = acceleration_z * random.uniform(2.2, 3.0)

        # ----------------------------------------------------
        # FFT
        # ----------------------------------------------------

        FFT_x = random.uniform(70.0, 150.0)
        FFT_y = random.uniform(60.0, 130.0)
        FFT_z = random.uniform(80.0, 170.0)

        # ----------------------------------------------------
        # BATTERY
        # ----------------------------------------------------

        battery -= random.uniform(0.00001, 0.00005)

        battery = max(battery, 3.20)

        # ----------------------------------------------------
        # SOC
        # ----------------------------------------------------

        soc -= random.uniform(0.0001, 0.001)

        soc = max(soc, 10.0)

    # ========================================================
    # MACHINE STOPPED
    # ========================================================

    else:

        # ----------------------------------------------------
        # Temperature giảm dần
        # ----------------------------------------------------

        temperature -= random.uniform(0.01, 0.05)

        temperature = max(temperature, 28.0)

        # ----------------------------------------------------
        # LOW VIBRATION
        # ----------------------------------------------------

        velocity_x = random.uniform(0.05, 0.20)
        velocity_y = random.uniform(0.04, 0.18)
        velocity_z = random.uniform(0.05, 0.22)

        velocity_peak_x = velocity_x * random.uniform(1.5, 2.0)
        velocity_peak_y = velocity_y * random.uniform(1.5, 2.0)
        velocity_peak_z = velocity_z * random.uniform(1.5, 2.0)

        # ----------------------------------------------------
        # ACCELERATION
        # ----------------------------------------------------

        acceleration_x = random.uniform(0.01, 0.05)
        acceleration_y = random.uniform(0.01, 0.04)
        acceleration_z = random.uniform(0.01, 0.05)

        acceleration_peak_x = acceleration_x * random.uniform(1.5, 2.5)
        acceleration_peak_y = acceleration_y * random.uniform(1.5, 2.5)
        acceleration_peak_z = acceleration_z * random.uniform(1.5, 2.5)

        # ----------------------------------------------------
        # FFT
        # ----------------------------------------------------

        FFT_x = random.uniform(5.0, 20.0)
        FFT_y = random.uniform(5.0, 20.0)
        FFT_z = random.uniform(5.0, 25.0)

        # ----------------------------------------------------
        # BATTERY
        # ----------------------------------------------------

        battery -= random.uniform(0.000001, 0.00001)

        battery = max(battery, 3.20)

        # ----------------------------------------------------
        # SOC
        # ----------------------------------------------------

        soc -= random.uniform(0.00001, 0.0001)

        soc = max(soc, 10.0)

    # ========================================================
    # RETURN JSON
    # ========================================================

    return {
        "temperature": round(temperature, 2),
        "humidity": round(random.uniform(50.0, 60.0), 2),

        "battery": round(battery, 3),
        "soc": round(soc, 2),

        "velocity_x": round(velocity_x, 3),
        "velocity_y": round(velocity_y, 3),
        "velocity_z": round(velocity_z, 3),

        "velocity_peak_x": round(velocity_peak_x, 3),
        "velocity_peak_y": round(velocity_peak_y, 3),
        "velocity_peak_z": round(velocity_peak_z, 3),

        "acceleration_x": round(acceleration_x, 3),
        "acceleration_y": round(acceleration_y, 3),
        "acceleration_z": round(acceleration_z, 3),

        "acceleration_peak_x": round(acceleration_peak_x, 3),
        "acceleration_peak_y": round(acceleration_peak_y, 3),
        "acceleration_peak_z": round(acceleration_peak_z, 3),

        "FFT_x": round(FFT_x, 2),
        "FFT_y": round(FFT_y, 2),
        "FFT_z": round(FFT_z, 2)
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

client = mqtt.Client(
    client_id=DEVICE_ID
)

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
                f"Temp={data['temperature']} C | "
                f"Velocity=({data['velocity_x']}, "
                f"{data['velocity_y']}, "
                f"{data['velocity_z']}) | "
                f"Acceleration=({data['acceleration_x']}, "
                f"{data['acceleration_y']}, "
                f"{data['acceleration_z']}) | "
                f"FFT=({data['FFT_x']}, "
                f"{data['FFT_y']}, "
                f"{data['FFT_z']})"
            )

        else:

            print("Publish failed")

        time.sleep(SEND_INTERVAL)


except KeyboardInterrupt:

    print("Stopping...")

    client.loop_stop()
    client.disconnect()