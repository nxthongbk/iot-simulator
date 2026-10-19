import paho.mqtt.client as mqtt
import json
import time
import random
import math

from datetime import datetime, time as dt_time


# ============================================================
# MQTT CONFIG
# ============================================================

MQTT_HOST = "pdm.tmainnovation.com"
MQTT_PORT = 1883

MQTT_USERNAME = "admin"
MQTT_PASSWORD = "admin"

DEVICE_ID = "Turbin"

MQTT_TOPIC = f"incoming/data/{DEVICE_ID}/values"


# ============================================================
# MACHINE WORKING SCHEDULE
# ============================================================

WORK_START_1 = dt_time(8, 0)
WORK_END_1 = dt_time(12, 0)

WORK_START_2 = dt_time(13, 0)
WORK_END_2 = dt_time(17, 0)


# ============================================================
# SIMULATION CONFIG
# ============================================================

SEND_INTERVAL = 5

ABNORMAL_PROBABILITY = 0.05

ABNORMAL_MIN_DURATION = 3
ABNORMAL_MAX_DURATION = 10


# ============================================================
# PRODUCTION CONFIG
# ============================================================

IDEAL_PRODUCTION_RATE = 28.0

NORMAL_PRODUCTION_MIN = 14.0
NORMAL_PRODUCTION_MAX = 18.0

NORMAL_REJECT_RATE = 0.01

EXPECTED_KWH_PER_PIECE = 0.30

ENERGY_PER_PIECE_WARNING = 1.20

HIGH_REJECT_RATE_THRESHOLD = 0.05

MIN_PRODUCTION_FOR_ANALYSIS = 5

PRODUCTION_TARGET_QTY = 1500


# ============================================================
# INITIAL SENSOR STATE
# ============================================================

temperature = 32.0

battery = 3.72
soc = 87.5


# ============================================================
# INITIAL ENERGY
# ============================================================

current_kwh = 12543.68
current_kvah = 13021.42
current_kvarh = 3512.76


# ============================================================
# PRODUCTION STATE
# ============================================================

production_total_qty = 0.0
production_good_qty = 0.0
production_reject_qty = 0.0


# ============================================================
# ABNORMAL STATE
# ============================================================

abnormal_active = False
abnormal_type = None
abnormal_remaining = 0


# ============================================================
# MACHINE STATUS
# ============================================================

def is_machine_working():

    now = datetime.now().time()

    if WORK_START_1 <= now < WORK_END_1:
        return True

    if WORK_START_2 <= now < WORK_END_2:
        return True

    return False


# ============================================================
# SAFE DIVISION
# ============================================================

def safe_div(a, b):

    if b == 0:
        return 0.0

    return a / b


# ============================================================
# START ABNORMAL
# ============================================================

def start_abnormal():

    global abnormal_active
    global abnormal_type
    global abnormal_remaining

    abnormal_types = [

        "HIGH_VIBRATION",
        "HIGH_TEMPERATURE",
        "HIGH_ACCELERATION",
        "FFT_SPIKE",

        "OVER_CURRENT",
        "HIGH_POWER",
        "LOW_POWER_FACTOR",
        "VOLTAGE_ABNORMAL",

        "LOW_PRODUCTION",
        "HIGH_ENERGY",
        "NO_PRODUCTION",
        "HIGH_REJECT"
    ]

    abnormal_type = random.choice(
        abnormal_types
    )

    abnormal_remaining = random.randint(
        ABNORMAL_MIN_DURATION,
        ABNORMAL_MAX_DURATION
    )

    abnormal_active = True

    print()
    print("=" * 100)
    print("!!! SIMULATED ABNORMAL EVENT START !!!")
    print(f"Type     : {abnormal_type}")
    print(f"Duration : {abnormal_remaining} samples")
    print("=" * 100)
    print()


# ============================================================
# UPDATE ABNORMAL
# ============================================================

def update_abnormal_state(machine_running):

    global abnormal_active
    global abnormal_remaining

    if not machine_running:

        abnormal_active = False
        abnormal_remaining = 0

        return

    if not abnormal_active:

        if random.random() < ABNORMAL_PROBABILITY:

            start_abnormal()

    else:

        abnormal_remaining -= 1

        if abnormal_remaining <= 0:

            print()
            print("=" * 100)
            print("!!! SIMULATED ABNORMAL EVENT END !!!")
            print(f"Type : {abnormal_type}")
            print("=" * 100)
            print()

            abnormal_active = False


# ============================================================
# FFT GENERATOR
# ============================================================

def generate_fft_data(
    machine_running,
    velocity_x,
    velocity_y,
    velocity_z
):

    # --------------------------------------------------------
    # MACHINE STOPPED
    # --------------------------------------------------------

    if not machine_running:

        return {

            "fft_amplitude_x": random.uniform(
                0.05,
                0.30
            ),

            "fft_amplitude_y": random.uniform(
                0.05,
                0.30
            ),

            "fft_amplitude_z": random.uniform(
                0.05,
                0.40
            ),

            "fft_frequency_x": random.uniform(
                5.0,
                20.0
            ),

            "fft_frequency_y": random.uniform(
                5.0,
                20.0
            ),

            "fft_frequency_z": random.uniform(
                5.0,
                25.0
            ),

            "fft_rms_x": random.uniform(
                0.03,
                0.15
            ),

            "fft_rms_y": random.uniform(
                0.03,
                0.15
            ),

            "fft_rms_z": random.uniform(
                0.03,
                0.20
            ),

            "fft_peak_x": random.uniform(
                0.08,
                0.40
            ),

            "fft_peak_y": random.uniform(
                0.08,
                0.40
            ),

            "fft_peak_z": random.uniform(
                0.10,
                0.50
            ),

            "fft_1x_x": random.uniform(
                0.02,
                0.10
            ),

            "fft_2x_x": random.uniform(
                0.01,
                0.06
            ),

            "fft_3x_x": random.uniform(
                0.005,
                0.04
            ),

            "fft_1x_y": random.uniform(
                0.02,
                0.10
            ),

            "fft_2x_y": random.uniform(
                0.01,
                0.06
            ),

            "fft_3x_y": random.uniform(
                0.005,
                0.04
            ),

            "fft_1x_z": random.uniform(
                0.02,
                0.12
            ),

            "fft_2x_z": random.uniform(
                0.01,
                0.07
            ),

            "fft_3x_z": random.uniform(
                0.005,
                0.05
            )
        }


    # --------------------------------------------------------
    # MACHINE RUNNING
    # --------------------------------------------------------

    base_frequency = random.uniform(
        49.0,
        51.0
    )

    amplitude_x = (
        velocity_x *
        random.uniform(
            0.9,
            1.3
        )
    )

    amplitude_y = (
        velocity_y *
        random.uniform(
            0.9,
            1.3
        )
    )

    amplitude_z = (
        velocity_z *
        random.uniform(
            0.9,
            1.3
        )
    )

    frequency_x = (
        base_frequency +
        random.uniform(
            -1.0,
            1.0
        )
    )

    frequency_y = (
        base_frequency +
        random.uniform(
            -1.0,
            1.0
        )
    )

    frequency_z = (
        base_frequency *
        random.choice(
            [
                1.0,
                1.0,
                2.0
            ]
        ) +
        random.uniform(
            -1.0,
            1.0
        )
    )

    rms_x = amplitude_x / math.sqrt(2)
    rms_y = amplitude_y / math.sqrt(2)
    rms_z = amplitude_z / math.sqrt(2)

    peak_x = (
        amplitude_x *
        random.uniform(
            1.6,
            2.1
        )
    )

    peak_y = (
        amplitude_y *
        random.uniform(
            1.6,
            2.1
        )
    )

    peak_z = (
        amplitude_z *
        random.uniform(
            1.6,
            2.1
        )
    )

    # --------------------------------------------------------
    # HARMONICS
    # --------------------------------------------------------

    fft_1x_x = (
        amplitude_x *
        random.uniform(
            0.70,
            1.00
        )
    )

    fft_2x_x = (
        amplitude_x *
        random.uniform(
            0.15,
            0.40
        )
    )

    fft_3x_x = (
        amplitude_x *
        random.uniform(
            0.05,
            0.20
        )
    )


    fft_1x_y = (
        amplitude_y *
        random.uniform(
            0.70,
            1.00
        )
    )

    fft_2x_y = (
        amplitude_y *
        random.uniform(
            0.15,
            0.40
        )
    )

    fft_3x_y = (
        amplitude_y *
        random.uniform(
            0.05,
            0.20
        )
    )


    fft_1x_z = (
        amplitude_z *
        random.uniform(
            0.70,
            1.00
        )
    )

    fft_2x_z = (
        amplitude_z *
        random.uniform(
            0.15,
            0.40
        )
    )

    fft_3x_z = (
        amplitude_z *
        random.uniform(
            0.05,
            0.20
        )
    )


    # --------------------------------------------------------
    # FFT SPIKE
    # --------------------------------------------------------

    if (
        abnormal_active
        and abnormal_type == "FFT_SPIKE"
    ):

        multiplier = random.uniform(
            3.0,
            6.0
        )

        amplitude_x *= multiplier
        amplitude_y *= multiplier
        amplitude_z *= multiplier

        rms_x = amplitude_x / math.sqrt(2)
        rms_y = amplitude_y / math.sqrt(2)
        rms_z = amplitude_z / math.sqrt(2)

        peak_x = amplitude_x * 2.0
        peak_y = amplitude_y * 2.0
        peak_z = amplitude_z * 2.0

        fft_1x_x *= multiplier
        fft_2x_x *= multiplier
        fft_3x_x *= multiplier

        fft_1x_y *= multiplier
        fft_2x_y *= multiplier
        fft_3x_y *= multiplier

        fft_1x_z *= multiplier
        fft_2x_z *= multiplier
        fft_3x_z *= multiplier


    return {

        "fft_amplitude_x": amplitude_x,
        "fft_amplitude_y": amplitude_y,
        "fft_amplitude_z": amplitude_z,

        "fft_frequency_x": frequency_x,
        "fft_frequency_y": frequency_y,
        "fft_frequency_z": frequency_z,

        "fft_rms_x": rms_x,
        "fft_rms_y": rms_y,
        "fft_rms_z": rms_z,

        "fft_peak_x": peak_x,
        "fft_peak_y": peak_y,
        "fft_peak_z": peak_z,

        "fft_1x_x": fft_1x_x,
        "fft_2x_x": fft_2x_x,
        "fft_3x_x": fft_3x_x,

        "fft_1x_y": fft_1x_y,
        "fft_2x_y": fft_2x_y,
        "fft_3x_y": fft_3x_y,

        "fft_1x_z": fft_1x_z,
        "fft_2x_z": fft_2x_z,
        "fft_3x_z": fft_3x_z
    }


# ============================================================
# GENERATE DATA
# ============================================================

def generate_data():

    global temperature
    global battery
    global soc

    global current_kwh
    global current_kvah
    global current_kvarh

    global production_total_qty
    global production_good_qty
    global production_reject_qty


    # ========================================================
    # MACHINE STATUS
    # ========================================================

    machine_running = is_machine_working()


    # ========================================================
    # ABNORMAL STATE
    # ========================================================

    update_abnormal_state(
        machine_running
    )


    # ========================================================
    # VIBRATION
    # ========================================================

    if machine_running:

        temperature += random.uniform(
            0.00,
            0.08
        )

        temperature = min(
            temperature,
            45.0
        )


        velocity_x = random.uniform(
            1.2,
            2.8
        )

        velocity_y = random.uniform(
            1.0,
            2.5
        )

        velocity_z = random.uniform(
            1.3,
            2.7
        )


        acceleration_x = random.uniform(
            0.25,
            0.55
        )

        acceleration_y = random.uniform(
            0.20,
            0.50
        )

        acceleration_z = random.uniform(
            0.30,
            0.60
        )


        if (
            abnormal_active
            and abnormal_type == "HIGH_VIBRATION"
        ):

            velocity_x *= random.uniform(
                2.0,
                3.0
            )

            velocity_y *= random.uniform(
                2.0,
                3.0
            )

            velocity_z *= random.uniform(
                2.0,
                3.0
            )


        if (
            abnormal_active
            and abnormal_type == "HIGH_ACCELERATION"
        ):

            acceleration_x *= random.uniform(
                2.0,
                3.0
            )

            acceleration_y *= random.uniform(
                2.0,
                3.0
            )

            acceleration_z *= random.uniform(
                2.0,
                3.0
            )


        velocity_peak_x = (
            velocity_x *
            random.uniform(
                1.7,
                2.2
            )
        )

        velocity_peak_y = (
            velocity_y *
            random.uniform(
                1.7,
                2.2
            )
        )

        velocity_peak_z = (
            velocity_z *
            random.uniform(
                1.7,
                2.2
            )
        )


        acceleration_peak_x = (
            acceleration_x *
            random.uniform(
                2.2,
                3.0
            )
        )

        acceleration_peak_y = (
            acceleration_y *
            random.uniform(
                2.2,
                3.0
            )
        )

        acceleration_peak_z = (
            acceleration_z *
            random.uniform(
                2.2,
                3.0
            )
        )


        if (
            abnormal_active
            and abnormal_type == "HIGH_TEMPERATURE"
        ):

            temperature += random.uniform(
                5.0,
                12.0
            )


    else:

        temperature -= random.uniform(
            0.01,
            0.05
        )

        temperature = max(
            temperature,
            28.0
        )


        velocity_x = random.uniform(
            0.05,
            0.20
        )

        velocity_y = random.uniform(
            0.04,
            0.18
        )

        velocity_z = random.uniform(
            0.05,
            0.22
        )


        acceleration_x = random.uniform(
            0.01,
            0.05
        )

        acceleration_y = random.uniform(
            0.01,
            0.04
        )

        acceleration_z = random.uniform(
            0.01,
            0.05
        )


        velocity_peak_x = (
            velocity_x *
            random.uniform(
                1.5,
                2.0
            )
        )

        velocity_peak_y = (
            velocity_y *
            random.uniform(
                1.5,
                2.0
            )
        )

        velocity_peak_z = (
            velocity_z *
            random.uniform(
                1.5,
                2.0
            )
        )


        acceleration_peak_x = (
            acceleration_x *
            random.uniform(
                1.5,
                2.5
            )
        )

        acceleration_peak_y = (
            acceleration_y *
            random.uniform(
                1.5,
                2.5
            )
        )

        acceleration_peak_z = (
            acceleration_z *
            random.uniform(
                1.5,
                2.5
            )
        )


    # ========================================================
    # BATTERY
    # ========================================================

    battery -= random.uniform(
        0.00001,
        0.00005
    )

    battery = max(
        battery,
        3.20
    )


    soc -= random.uniform(
        0.0001,
        0.001
    )

    soc = max(
        soc,
        10.0
    )


    # ========================================================
    # FFT
    # ========================================================

    fft = generate_fft_data(

        machine_running,

        velocity_x,
        velocity_y,
        velocity_z
    )


    # ========================================================
    # VOLTAGE
    # ========================================================

    V1N = random.uniform(
        219.0,
        222.0
    )

    V2N = random.uniform(
        219.0,
        222.0
    )

    V3N = random.uniform(
        219.0,
        222.0
    )

    VLN = (
        V1N +
        V2N +
        V3N
    ) / 3


    V12 = random.uniform(
        379.0,
        383.0
    )

    V23 = random.uniform(
        379.0,
        383.0
    )

    V31 = random.uniform(
        379.0,
        383.0
    )

    VLL = (
        V12 +
        V23 +
        V31
    ) / 3


    # ========================================================
    # ELECTRIC
    # ========================================================

    if machine_running:

        I1 = random.uniform(
            10.0,
            14.0
        )

        I2 = random.uniform(
            10.0,
            14.0
        )

        I3 = random.uniform(
            10.0,
            14.0
        )

        AI = (
            I1 +
            I2 +
            I3
        ) / 3


        kW1 = random.uniform(
            2.2,
            3.2
        )

        kW2 = random.uniform(
            2.2,
            3.2
        )

        kW3 = random.uniform(
            2.2,
            3.2
        )


        # HIGH POWER
        if (
            abnormal_active
            and abnormal_type == "HIGH_POWER"
        ):

            kW1 *= random.uniform(
                1.5,
                2.0
            )

            kW2 *= random.uniform(
                1.5,
                2.0
            )

            kW3 *= random.uniform(
                1.5,
                2.0
            )


        kW = (
            kW1 +
            kW2 +
            kW3
        )


        PF1 = random.uniform(
            0.92,
            0.98
        )

        PF2 = random.uniform(
            0.92,
            0.98
        )

        PF3 = random.uniform(
            0.92,
            0.98
        )


        if (
            abnormal_active
            and abnormal_type == "LOW_POWER_FACTOR"
        ):

            PF1 = random.uniform(
                0.55,
                0.70
            )

            PF2 = random.uniform(
                0.55,
                0.70
            )

            PF3 = random.uniform(
                0.55,
                0.70
            )


        PF = (
            PF1 +
            PF2 +
            PF3
        ) / 3


        kVA1 = kW1 / PF1
        kVA2 = kW2 / PF2
        kVA3 = kW3 / PF3

        kVA = (
            kVA1 +
            kVA2 +
            kVA3
        )


        kVAr1 = math.sqrt(
            max(
                0,
                kVA1 ** 2 -
                kW1 ** 2
            )
        )

        kVAr2 = math.sqrt(
            max(
                0,
                kVA2 ** 2 -
                kW2 ** 2
            )
        )

        kVAr3 = math.sqrt(
            max(
                0,
                kVA3 ** 2 -
                kW3 ** 2
            )
        )

        kVAr = (
            kVAr1 +
            kVAr2 +
            kVAr3
        )


        F = random.uniform(
            49.95,
            50.05
        )


    else:

        I1 = random.uniform(
            0.05,
            0.20
        )

        I2 = random.uniform(
            0.05,
            0.20
        )

        I3 = random.uniform(
            0.05,
            0.20
        )

        AI = (
            I1 +
            I2 +
            I3
        ) / 3


        kW1 = random.uniform(
            0.01,
            0.04
        )

        kW2 = random.uniform(
            0.01,
            0.04
        )

        kW3 = random.uniform(
            0.01,
            0.04
        )


        # ----------------------------------------------------
        # Simulate abnormal standby power
        # ----------------------------------------------------

        if (
            abnormal_active
            and abnormal_type == "HIGH_ENERGY"
        ):

            kW1 = random.uniform(
                0.8,
                1.5
            )

            kW2 = random.uniform(
                0.8,
                1.5
            )

            kW3 = random.uniform(
                0.8,
                1.5
            )


        kW = (
            kW1 +
            kW2 +
            kW3
        )


        PF1 = random.uniform(
            0.70,
            0.90
        )

        PF2 = random.uniform(
            0.70,
            0.90
        )

        PF3 = random.uniform(
            0.70,
            0.90
        )

        PF = (
            PF1 +
            PF2 +
            PF3
        ) / 3


        kVA1 = kW1 / PF1
        kVA2 = kW2 / PF2
        kVA3 = kW3 / PF3

        kVA = (
            kVA1 +
            kVA2 +
            kVA3
        )


        kVAr1 = math.sqrt(
            max(
                0,
                kVA1 ** 2 -
                kW1 ** 2
            )
        )

        kVAr2 = math.sqrt(
            max(
                0,
                kVA2 ** 2 -
                kW2 ** 2
            )
        )

        kVAr3 = math.sqrt(
            max(
                0,
                kVA3 ** 2 -
                kW3 ** 2
            )
        )

        kVAr = (
            kVAr1 +
            kVAr2 +
            kVAr3
        )


        F = random.uniform(
            49.98,
            50.02
        )


    # ========================================================
    # PRODUCTION
    # ========================================================

    production_rate = 0.0

    produced_this_interval = 0.0

    good_this_interval = 0.0

    reject_this_interval = 0.0


    if machine_running:

        production_rate = random.uniform(
            NORMAL_PRODUCTION_MIN,
            NORMAL_PRODUCTION_MAX
        )


        # ----------------------------------------------------
        # LOW PRODUCTION
        # ----------------------------------------------------

        if (
            abnormal_active
            and abnormal_type == "LOW_PRODUCTION"
        ):

            production_rate *= random.uniform(
                0.30,
                0.60
            )


        # ----------------------------------------------------
        # NO PRODUCTION
        # ----------------------------------------------------

        if (
            abnormal_active
            and abnormal_type == "NO_PRODUCTION"
        ):

            production_rate = 0.0


        # ----------------------------------------------------
        # Production in current interval
        # ----------------------------------------------------

        produced_this_interval = (
            production_rate *
            SEND_INTERVAL /
            60.0
        )


        # ----------------------------------------------------
        # Reject
        # ----------------------------------------------------

        reject_rate = (
            NORMAL_REJECT_RATE
        )


        if (
            abnormal_active
            and abnormal_type == "HIGH_REJECT"
        ):

            reject_rate = random.uniform(
                0.08,
                0.20
            )


        reject_this_interval = (
            produced_this_interval *
            reject_rate
        )


        good_this_interval = (
            produced_this_interval -
            reject_this_interval
        )


        # ----------------------------------------------------
        # Update production
        # ----------------------------------------------------

        production_total_qty += (
            produced_this_interval
        )

        production_good_qty += (
            good_this_interval
        )

        production_reject_qty += (
            reject_this_interval
        )


    # ========================================================
    # PRODUCTION KPI
    # ========================================================

    reject_rate_total = safe_div(
        production_reject_qty,
        production_total_qty
    )


    production_progress = (
        safe_div(
            production_total_qty,
            PRODUCTION_TARGET_QTY
        )
        * 100.0
    )


    # ========================================================
    # ENERGY
    # ========================================================

    elapsed_hours = (
        SEND_INTERVAL /
        3600.0
    )


    energy_consumed_this_interval = (
        kW *
        elapsed_hours
    )


    current_kwh += (
        energy_consumed_this_interval
    )

    current_kvah += (
        kVA *
        elapsed_hours
    )

    current_kvarh += (
        kVAr *
        elapsed_hours
    )


    # ========================================================
    # ENERGY PER PIECE
    # ========================================================

    interval_energy_per_piece = safe_div(
        energy_consumed_this_interval,
        good_this_interval
    )


    # For current production session
    #
    # We use energy consumed since simulator start.
    #

    cumulative_energy_per_piece = safe_div(
        current_kwh,
        production_good_qty
    )


    # Better efficiency comparison:
    #
    # Expected energy / actual energy per piece

    if (
        production_good_qty >=
        MIN_PRODUCTION_FOR_ANALYSIS
    ):

        energy_efficiency_percent = (
            EXPECTED_KWH_PER_PIECE /
            cumulative_energy_per_piece
        ) * 100.0

    else:

        energy_efficiency_percent = 0.0


    energy_efficiency_percent = max(
        0.0,
        min(
            energy_efficiency_percent,
            200.0
        )
    )


    # ========================================================
    # OEE
    # ========================================================

    availability = (
        100.0
        if machine_running
        else 0.0
    )


    performance = safe_div(
        production_rate,
        IDEAL_PRODUCTION_RATE
    ) * 100.0


    performance = max(
        0.0,
        min(
            performance,
            100.0
        )
    )


    quality = (
        100.0 -
        reject_rate_total * 100.0
    )


    quality = max(
        0.0,
        min(
            quality,
            100.0
        )
    )


    oee = (
        availability *
        performance *
        quality
    ) / 10000.0


    # ========================================================
    # EXCEPTION DETECTION
    # ========================================================

    exceptions = []

    exception_score = 0


    # --------------------------------------------------------
    # 1. RUNNING BUT NO PRODUCTION
    # --------------------------------------------------------

    if (
        machine_running
        and production_rate <= 0
        and kW > 1.0
    ):

        exceptions.append(
            "MACHINE_RUNNING_NO_PRODUCTION"
        )

        exception_score += 40


    # --------------------------------------------------------
    # 2. HIGH ENERGY + LOW PRODUCTION
    # --------------------------------------------------------

    if (
        machine_running
        and good_this_interval > 0
        and interval_energy_per_piece >
            EXPECTED_KWH_PER_PIECE *
            ENERGY_PER_PIECE_WARNING
    ):

        exceptions.append(
            "HIGH_ENERGY_LOW_PRODUCTION"
        )

        exception_score += 30


    # --------------------------------------------------------
    # 3. HIGH ENERGY PER PIECE
    # --------------------------------------------------------

    if (
        production_good_qty >=
        MIN_PRODUCTION_FOR_ANALYSIS
        and
        cumulative_energy_per_piece >
        EXPECTED_KWH_PER_PIECE *
        ENERGY_PER_PIECE_WARNING
    ):

        exceptions.append(
            "HIGH_ENERGY_PER_PIECE"
        )

        exception_score += 25


    # --------------------------------------------------------
    # 4. STOPPED BUT HIGH POWER
    # --------------------------------------------------------

    if (
        not machine_running
        and kW > 1.0
    ):

        exceptions.append(
            "MACHINE_STOPPED_HIGH_ENERGY"
        )

        exception_score += 35


    # --------------------------------------------------------
    # 5. HIGH REJECT
    # --------------------------------------------------------

    if (
        production_total_qty >=
        MIN_PRODUCTION_FOR_ANALYSIS
        and
        reject_rate_total >
        HIGH_REJECT_RATE_THRESHOLD
    ):

        exceptions.append(
            "HIGH_REJECT_RATE"
        )

        exception_score += 25


    # --------------------------------------------------------
    # 6. LOW PRODUCTION RATE
    # --------------------------------------------------------

    if (
        machine_running
        and
        production_rate > 0
        and
        production_rate <
        IDEAL_PRODUCTION_RATE * 0.70
    ):

        exceptions.append(
            "LOW_PRODUCTION_RATE"
        )

        exception_score += 20


    # --------------------------------------------------------
    # 7. FFT
    # --------------------------------------------------------

    if (
        fft["fft_amplitude_x"] > 5.0
        or
        fft["fft_amplitude_y"] > 5.0
        or
        fft["fft_amplitude_z"] > 5.0
    ):

        exceptions.append(
            "HIGH_FFT"
        )

        exception_score += 20


    # --------------------------------------------------------
    # 8. TEMPERATURE
    # --------------------------------------------------------

    if temperature > 70.0:

        exceptions.append(
            "HIGH_TEMPERATURE"
        )

        exception_score += 20


    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    exception_score = min(
        exception_score,
        100
    )


    if exceptions:

        exception = True

        exception_type = exceptions[0]

    else:

        exception = False

        exception_type = "NORMAL"


    # ========================================================
    # PAYLOAD
    # ========================================================

    return {

        # ====================================================
        # MACHINE
        # ====================================================

        "machine_status":
            "RUNNING"
            if machine_running
            else "STOPPED",

        "abnormal":
            abnormal_active,

        "abnormal_type":
            abnormal_type
            if abnormal_active
            else "NORMAL",


        # ====================================================
        # TEMPERATURE / BATTERY
        # ====================================================

        "temperature": round(
            temperature,
            2
        ),

        "humidity": round(
            random.uniform(
                50.0,
                60.0
            ),
            2
        ),

        "battery": round(
            battery,
            3
        ),

        "soc": round(
            soc,
            2
        ),


        # ====================================================
        # VIBRATION
        # ====================================================

        "velocity_x": round(
            velocity_x,
            3
        ),

        "velocity_y": round(
            velocity_y,
            3
        ),

        "velocity_z": round(
            velocity_z,
            3
        ),

        "velocity_peak_x": round(
            velocity_peak_x,
            3
        ),

        "velocity_peak_y": round(
            velocity_peak_y,
            3
        ),

        "velocity_peak_z": round(
            velocity_peak_z,
            3
        ),


        "acceleration_x": round(
            acceleration_x,
            3
        ),

        "acceleration_y": round(
            acceleration_y,
            3
        ),

        "acceleration_z": round(
            acceleration_z,
            3
        ),

        "acceleration_peak_x": round(
            acceleration_peak_x,
            3
        ),

        "acceleration_peak_y": round(
            acceleration_peak_y,
            3
        ),

        "acceleration_peak_z": round(
            acceleration_peak_z,
            3
        ),


        # ====================================================
        # FFT
        # ====================================================

        "fft_amplitude_x": round(
            fft["fft_amplitude_x"],
            3
        ),

        "fft_amplitude_y": round(
            fft["fft_amplitude_y"],
            3
        ),

        "fft_amplitude_z": round(
            fft["fft_amplitude_z"],
            3
        ),


        "fft_frequency_x": round(
            fft["fft_frequency_x"],
            2
        ),

        "fft_frequency_y": round(
            fft["fft_frequency_y"],
            2
        ),

        "fft_frequency_z": round(
            fft["fft_frequency_z"],
            2
        ),


        "fft_rms_x": round(
            fft["fft_rms_x"],
            3
        ),

        "fft_rms_y": round(
            fft["fft_rms_y"],
            3
        ),

        "fft_rms_z": round(
            fft["fft_rms_z"],
            3
        ),


        "fft_peak_x": round(
            fft["fft_peak_x"],
            3
        ),

        "fft_peak_y": round(
            fft["fft_peak_y"],
            3
        ),

        "fft_peak_z": round(
            fft["fft_peak_z"],
            3
        ),


        "fft_1x_x": round(
            fft["fft_1x_x"],
            3
        ),

        "fft_2x_x": round(
            fft["fft_2x_x"],
            3
        ),

        "fft_3x_x": round(
            fft["fft_3x_x"],
            3
        ),


        "fft_1x_y": round(
            fft["fft_1x_y"],
            3
        ),

        "fft_2x_y": round(
            fft["fft_2x_y"],
            3
        ),

        "fft_3x_y": round(
            fft["fft_3x_y"],
            3
        ),


        "fft_1x_z": round(
            fft["fft_1x_z"],
            3
        ),

        "fft_2x_z": round(
            fft["fft_2x_z"],
            3
        ),

        "fft_3x_z": round(
            fft["fft_3x_z"],
            3
        ),


        # ====================================================
        # PRODUCTION
        # ====================================================

        "production_total_qty": round(
            production_total_qty,
            2
        ),

        "production_good_qty": round(
            production_good_qty,
            2
        ),

        "production_reject_qty": round(
            production_reject_qty,
            2
        ),

        "production_rate": round(
            production_rate,
            2
        ),

        "production_target_qty":
            PRODUCTION_TARGET_QTY,

        "production_progress": round(
            production_progress,
            2
        ),

        "reject_rate": round(
            reject_rate_total * 100.0,
            2
        ),


        # ====================================================
        # CURRENT PRODUCTION
        # ====================================================

        "produced_this_interval": round(
            produced_this_interval,
            3
        ),

        "good_this_interval": round(
            good_this_interval,
            3
        ),

        "reject_this_interval": round(
            reject_this_interval,
            3
        ),


        # ====================================================
        # ENERGY
        # ====================================================

        "kW": round(
            kW,
            3
        ),

        "kWh": round(
            current_kwh,
            3
        ),

        "energy_consumed_interval": round(
            energy_consumed_this_interval,
            5
        ),

        "energy_per_piece": round(
            interval_energy_per_piece,
            4
        ),

        "cumulative_energy_per_piece": round(
            cumulative_energy_per_piece,
            4
        ),

        "expected_energy_per_piece": round(
            EXPECTED_KWH_PER_PIECE,
            3
        ),

        "energy_efficiency_percent": round(
            energy_efficiency_percent,
            2
        ),


        # ====================================================
        # OEE
        # ====================================================

        "availability": round(
            availability,
            2
        ),

        "performance": round(
            performance,
            2
        ),

        "quality": round(
            quality,
            2
        ),

        "oee": round(
            oee,
            2
        ),


        # ====================================================
        # EXCEPTION
        # ====================================================

        "exception":
            exception,

        "exception_type":
            exception_type,

        "exception_score":
            exception_score,

        "exceptions":
            exceptions,


        # ====================================================
        # ELECTRIC
        # ====================================================

        "V1N": round(
            V1N,
            2
        ),

        "V2N": round(
            V2N,
            2
        ),

        "V3N": round(
            V3N,
            2
        ),

        "VLN": round(
            VLN,
            2
        ),


        "V12": round(
            V12,
            2
        ),

        "V23": round(
            V23,
            2
        ),

        "V31": round(
            V31,
            2
        ),

        "VLL": round(
            VLL,
            2
        ),


        "I1": round(
            I1,
            2
        ),

        "I2": round(
            I2,
            2
        ),

        "I3": round(
            I3,
            2
        ),

        "AI": round(
            AI,
            2
        ),


        "kW1": round(
            kW1,
            3
        ),

        "kW2": round(
            kW2,
            3
        ),

        "kW3": round(
            kW3,
            3
        ),


        "kVA1": round(
            kVA1,
            3
        ),

        "kVA2": round(
            kVA2,
            3
        ),

        "kVA3": round(
            kVA3,
            3
        ),


        "kVAr1": round(
            kVAr1,
            3
        ),

        "kVAr2": round(
            kVAr2,
            3
        ),

        "kVAr3": round(
            kVAr3,
            3
        ),


        "kVA": round(
            kVA,
            3
        ),

        "kVAr": round(
            kVAr,
            3
        ),


        "PF1": round(
            PF1,
            3
        ),

        "PF2": round(
            PF2,
            3
        ),

        "PF3": round(
            PF3,
            3
        ),

        "PF": round(
            PF,
            3
        ),

        "F": round(
            F,
            2
        ),


        "kVAh": round(
            current_kvah,
            3
        ),

        "kVArh": round(
            current_kvarh,
            3
        )
    }


# ============================================================
# MQTT CALLBACK
# ============================================================

def on_connect(
    client,
    userdata,
    flags,
    rc
):

    if rc == 0:

        print()
        print("=" * 100)
        print("MQTT CONNECTED")
        print(f"Host   : {MQTT_HOST}:{MQTT_PORT}")
        print(f"Device : {DEVICE_ID}")
        print(f"Topic  : {MQTT_TOPIC}")
        print("=" * 100)

    else:

        print(
            f"MQTT connection failed, rc={rc}"
        )


# ============================================================
# PUBLISH CALLBACK
# ============================================================

def on_publish(
    client,
    userdata,
    mid
):

    print(
        f"MQTT Publish OK - message_id={mid}"
    )


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

print(
    "Connecting to MQTT..."
)

client.connect(
    MQTT_HOST,
    MQTT_PORT,
    keepalive=60
)

client.loop_start()


# ============================================================
# MAIN LOOP
# ============================================================

try:

    while True:

        now = datetime.now()

        # ----------------------------------------------------
        # Generate data
        # ----------------------------------------------------

        data = generate_data()


        # ----------------------------------------------------
        # JSON PAYLOAD
        # ----------------------------------------------------

        payload = json.dumps(
            data,
            indent=2,
            ensure_ascii=False
        )


        # ====================================================
        # PRINT FULL PAYLOAD
        # ====================================================

        print()
        print()
        print("=" * 100)
        print(
            f"TIME: {now.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        print(
            f"TOPIC: {MQTT_TOPIC}"
        )
        print("-" * 100)

        print(payload)

        print("=" * 100)


        # ====================================================
        # PRINT SUMMARY
        # ====================================================

        print()
        print("--------------- SUMMARY ----------------")

        print(
            f"Machine Status       : "
            f"{data['machine_status']}"
        )

        print(
            f"Production           : "
            f"{data['production_total_qty']:.2f} pcs"
        )

        print(
            f"Good Production      : "
            f"{data['production_good_qty']:.2f} pcs"
        )

        print(
            f"Reject               : "
            f"{data['production_reject_qty']:.2f} pcs"
        )

        print(
            f"Production Rate      : "
            f"{data['production_rate']:.2f} pcs/min"
        )

        print(
            f"Power                : "
            f"{data['kW']:.3f} kW"
        )

        print(
            f"Energy               : "
            f"{data['kWh']:.3f} kWh"
        )

        print(
            f"Energy / Good Piece  : "
            f"{data['cumulative_energy_per_piece']:.4f} kWh/pcs"
        )

        print(
            f"Energy Efficiency    : "
            f"{data['energy_efficiency_percent']:.2f}%"
        )

        print(
            f"FFT Frequency        : "
            f"X={data['fft_frequency_x']:.2f} Hz, "
            f"Y={data['fft_frequency_y']:.2f} Hz, "
            f"Z={data['fft_frequency_z']:.2f} Hz"
        )

        print(
            f"FFT Amplitude        : "
            f"X={data['fft_amplitude_x']:.3f}, "
            f"Y={data['fft_amplitude_y']:.3f}, "
            f"Z={data['fft_amplitude_z']:.3f}"
        )

        print(
            f"OEE                 : "
            f"{data['oee']:.2f}%"
        )

        print(
            f"Exception            : "
            f"{data['exception']}"
        )

        print(
            f"Exception Type       : "
            f"{data['exception_type']}"
        )

        print(
            f"Exception Score      : "
            f"{data['exception_score']}"
        )

        if data["exceptions"]:

            print(
                "Exceptions           : "
                + ", ".join(
                    data["exceptions"]
                )
            )

        print("----------------------------------------")


        # ====================================================
        # MQTT PUBLISH
        # ====================================================

        result = client.publish(
            MQTT_TOPIC,
            payload,
            qos=1
        )


        if result.rc != mqtt.MQTT_ERR_SUCCESS:

            print(
                f"MQTT Publish FAILED: rc={result.rc}"
            )


        # ====================================================
        # WAIT
        # ====================================================

        time.sleep(
            SEND_INTERVAL
        )


# ============================================================
# STOP
# ============================================================

except KeyboardInterrupt:

    print()
    print("Stopping simulator...")

    client.loop_stop()

    client.disconnect()

    print("MQTT disconnected.")