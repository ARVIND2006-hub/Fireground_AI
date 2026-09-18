import time
import json
import numpy as np
import pandas as pd
import joblib
from datetime import datetime
from tensorflow.keras.models import load_model


# ============================================================
# FILE PATHS
# ============================================================

MODEL_PATH = "../models/multitask_fireground_cnn.keras"
SCALER_PATH = "../models/scaler.pkl"
DATA_PATH = "../dataset/live_sensor_stream.csv"
OUTPUT_PATH = "../results/live_fireground_result.json"


# ============================================================
# SETTINGS
# ============================================================

WINDOW_SIZE = 10

SAMPLE_DELAY = 0.05


# ============================================================
# SENSOR FEATURES
# ============================================================

FEATURES = [
    "heart_rate",
    "acc_x",
    "acc_y",
    "acc_z",
    "gyro_x",
    "gyro_y",
    "gyro_z",
    "gas",
    "temperature"
]


# ============================================================
# CNN LABELS
# ============================================================

ACTIVITY_LABELS = [
    "crawling",
    "standing",
    "walking"
]

ENVIRONMENT_LABELS = [
    "normal",
    "risk"
]

PHYSIOLOGICAL_LABELS = [
    "elevated",
    "high",
    "normal"
]


# ============================================================
# RISK CALCULATION
# ============================================================

def calculate_risk_score(
    activity,
    environment,
    physiological
):

    score = 0

    if environment == "risk":
        score += 2

    if activity == "crawling":
        score += 1

    if physiological == "high":
        score += 2

    return score


# ============================================================
# LOCAL STATUS
# ============================================================

def get_local_status(score):

    if score >= 4:
        return "HIGH"

    elif score >= 2:
        return "ELEVATED"

    else:
        return "NORMAL"


# ============================================================
# EVENT TYPE
# ============================================================

def get_event_type(
    activity,
    environment,
    physiological
):

    if (
        activity == "crawling"
        and environment == "risk"
        and physiological == "high"
    ):
        return "deterioration"

    elif environment == "risk":
        return "environmental_risk"

    elif physiological == "high":
        return "physiological_alert"

    else:
        return "normal"


# ============================================================
# ZONE ANALYSIS
# ============================================================

def get_zone_status(
    firefighter_status,
    environment
):

    if firefighter_status == "HIGH":
        return "HIGH"

    if environment == "risk":
        return "ELEVATED"

    if firefighter_status == "ELEVATED":
        return "ELEVATED"

    return "NORMAL"


# ============================================================
# LOAD MODEL
# ============================================================

print()
print("================================================")
print("       FIREGROUND AI LIVE SYSTEM")
print("================================================")
print()

print("Loading CNN model...")

model = load_model(MODEL_PATH)

scaler = joblib.load(SCALER_PATH)

print("CNN model loaded successfully.")
print()


# ============================================================
# LOAD SENSOR STREAM
# ============================================================

df = pd.read_csv(DATA_PATH)

print("Live sensor stream loaded.")
print("Total sensor samples:", len(df))
print()


# ============================================================
# BUFFER
# ============================================================

buffer = []

window_number = 0

results = []


# ============================================================
# SIMULATED FIREFIGHTER
# ============================================================

firefighter_id = "FF01"

firefighter_x = 10

firefighter_y = 20


# ============================================================
# START LIVE PROCESSING
# ============================================================

print("Starting live Fireground AI...")
print()

for index, row in df.iterrows():

    # --------------------------------------------------------
    # RECEIVE SENSOR SAMPLE
    # --------------------------------------------------------

    sample = row[FEATURES].values.astype(float)

    buffer.append(sample)

    print(
        f"Received sample "
        f"{index + 1:02d}/{len(df)} | "
        f"Time: {row['timestamp']}"
    )

    # --------------------------------------------------------
    # WAIT FOR COMPLETE WINDOW
    # --------------------------------------------------------

    if len(buffer) < WINDOW_SIZE:

        time.sleep(SAMPLE_DELAY)

        continue

    # --------------------------------------------------------
    # CREATE CNN WINDOW
    # --------------------------------------------------------

    window = np.array(buffer)

    # --------------------------------------------------------
    # SCALE DATA
    # --------------------------------------------------------

    scaled_window = scaler.transform(window)

    # --------------------------------------------------------
    # CNN INPUT
    # --------------------------------------------------------

    cnn_input = scaled_window.reshape(
        1,
        WINDOW_SIZE,
        len(FEATURES)
    )

    # --------------------------------------------------------
    # CNN PREDICTION
    # --------------------------------------------------------

    predictions = model.predict(
        cnn_input,
        verbose=0
    )

    activity_prediction = predictions[0].squeeze()

    environment_prediction = predictions[1].squeeze()

    physiological_prediction = predictions[2].squeeze()

    # --------------------------------------------------------
    # PREDICT CLASSES
    # --------------------------------------------------------

    activity_index = np.argmax(
        activity_prediction
    )

    environment_index = np.argmax(
        environment_prediction
    )

    physiological_index = np.argmax(
        physiological_prediction
    )

    activity = ACTIVITY_LABELS[
        activity_index
    ]

    environment = ENVIRONMENT_LABELS[
        environment_index
    ]

    physiological = PHYSIOLOGICAL_LABELS[
        physiological_index
    ]

    # --------------------------------------------------------
    # CONFIDENCE
    # --------------------------------------------------------

    activity_confidence = float(
        activity_prediction[activity_index]
    )

    environment_confidence = float(
        environment_prediction[environment_index]
    )

    physiological_confidence = float(
        physiological_prediction[
            physiological_index
        ]
    )

    # --------------------------------------------------------
    # RISK
    # --------------------------------------------------------

    risk_score = calculate_risk_score(
        activity,
        environment,
        physiological
    )

    local_status = get_local_status(
        risk_score
    )

    event_type = get_event_type(
        activity,
        environment,
        physiological
    )

    # --------------------------------------------------------
    # ZONE
    # --------------------------------------------------------

    zone = "A"

    zone_status = get_zone_status(
        local_status,
        environment
    )

    # --------------------------------------------------------
    # ALERT
    # --------------------------------------------------------

    if local_status == "HIGH":

        alert_priority = "HIGH"

    elif local_status == "ELEVATED":

        alert_priority = "MEDIUM"

    else:

        alert_priority = "LOW"

    # --------------------------------------------------------
    # COMMAND CENTER OUTPUT
    # --------------------------------------------------------

    print()
    print("================================================")
    print(
        f"       AI UPDATE - WINDOW "
        f"{window_number + 1}"
    )
    print("================================================")

    print()
    print("FIREFIGHTER")
    print("-----------------------------------------------")

    print("Node ID:", firefighter_id)

    print(
        "Position:",
        firefighter_x,
        ",",
        firefighter_y
    )

    print("Zone:", zone)

    print()

    print("AI PREDICTION")
    print("-----------------------------------------------")

    print(
        f"Activity: {activity} "
        f"({activity_confidence:.3f})"
    )

    print(
        f"Environment: {environment} "
        f"({environment_confidence:.3f})"
    )

    print(
        f"Physiological state: {physiological} "
        f"({physiological_confidence:.3f})"
    )

    print()

    print("RISK ANALYSIS")
    print("-----------------------------------------------")

    print("Risk score:", risk_score)

    print("Local status:", local_status)

    print("Event type:", event_type)

    print()

    print("ZONE STATUS")
    print("-----------------------------------------------")

    print("Zone A:", zone_status)

    print()

    print("COMMAND CENTER")
    print("-----------------------------------------------")

    print("Alert priority:", alert_priority)

    if local_status == "HIGH":

        print()
        print("!!! HIGH RISK ALERT !!!")
        print(
            "Firefighter",
            firefighter_id,
            "requires attention."
        )

    # --------------------------------------------------------
    # SAVE RESULT IN MEMORY
    # --------------------------------------------------------

    result = {

        "window": window_number + 1,

        "timestamp": row["timestamp"],

        "firefighter": {

            "node_id": firefighter_id,

            "x": firefighter_x,

            "y": firefighter_y,

            "zone": zone
        },

        "ai_prediction": {

            "activity": activity,

            "activity_confidence":
                activity_confidence,

            "environment": environment,

            "environment_confidence":
                environment_confidence,

            "physiological_state":
                physiological,

            "physiological_confidence":
                physiological_confidence
        },

        "risk": {

            "risk_score": risk_score,

            "local_status": local_status,

            "event_type": event_type
        },

        "zone": {

            "zone_id": zone,

            "zone_status": zone_status
        },

        "command_center": {

            "alert_priority":
                alert_priority
        }
    }

    results.append(result)

    # --------------------------------------------------------
    # SLIDE WINDOW
    # --------------------------------------------------------

    buffer.pop(0)

    window_number += 1

    time.sleep(SAMPLE_DELAY)


# ============================================================
# OVERALL ANALYSIS
# ============================================================

high_windows = sum(
    1
    for result in results
    if result["risk"]["local_status"] == "HIGH"
)

elevated_windows = sum(
    1
    for result in results
    if result["risk"]["local_status"] == "ELEVATED"
)

normal_windows = sum(
    1
    for result in results
    if result["risk"]["local_status"] == "NORMAL"
)


# ============================================================
# OVERALL STATUS
# ============================================================

if high_windows > 0:

    overall_status = "HIGH"

elif elevated_windows > 0:

    overall_status = "ELEVATED"

else:

    overall_status = "NORMAL"


# ============================================================
# FINAL RESULT
# ============================================================

final_result = {

    "system": "Fireground AI",

    "generated_at":
        datetime.now().isoformat(),

    "sensor_samples":
        len(df),

    "window_size":
        WINDOW_SIZE,

    "ai_windows_processed":
        window_number,

    "window_statistics": {

        "normal":
            normal_windows,

        "elevated":
            elevated_windows,

        "high":
            high_windows
    },

    "overall_status":
        overall_status,

    "firefighter":
        firefighter_id,

    "results":
        results
}


# ============================================================
# SAVE JSON
# ============================================================

with open(
    OUTPUT_PATH,
    "w"
) as file:

    json.dump(
        final_result,
        file,
        indent=4
    )


# ============================================================
# FINAL DISPLAY
# ============================================================

print()
print()
print("================================================")
print("       FIREGROUND AI SYSTEM COMPLETE")
print("================================================")

print()

print(
    "Sensor samples:",
    len(df)
)

print(
    "AI windows processed:",
    window_number
)

print()

print(
    "NORMAL windows:",
    normal_windows
)

print(
    "ELEVATED windows:",
    elevated_windows
)

print(
    "HIGH windows:",
    high_windows
)

print()

print(
    "OVERALL FIREGROUND STATUS:",
    overall_status
)

print()

print(
    "Result saved to:"
)

print(OUTPUT_PATH)

print()
print("================================================")