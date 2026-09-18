import time
import numpy as np
import pandas as pd
import joblib
from tensorflow.keras.models import load_model


# ============================================================
# PATHS
# ============================================================

MODEL_PATH = "../models/multitask_fireground_cnn_v2.keras"
SCALER_PATH = "../models/scaler_v2.pkl"
DATA_PATH = "../dataset/live_sensor_stream.csv"


# ============================================================
# SETTINGS
# ============================================================

WINDOW_SIZE = 10

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
# LABELS
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
# RISK SCORE
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


def get_status(score):

    if score >= 4:
        return "HIGH"

    elif score >= 2:
        return "ELEVATED"

    return "NORMAL"


# ============================================================
# LOAD MODEL
# ============================================================

print()
print("================================================")
print("        FIREGROUND AI V2 LIVE TEST")
print("================================================")
print()

print("Loading V2 CNN...")

model = load_model(MODEL_PATH)

scaler = joblib.load(SCALER_PATH)

print("V2 CNN loaded successfully.")
print()


# ============================================================
# LOAD STREAM
# ============================================================

df = pd.read_csv(DATA_PATH)

print("Live stream loaded.")
print("Total samples:", len(df))
print()


# ============================================================
# BUFFER
# ============================================================

buffer = []

window_number = 0

status_counts = {
    "NORMAL": 0,
    "ELEVATED": 0,
    "HIGH": 0
}


# ============================================================
# PROCESS STREAM
# ============================================================

for index, row in df.iterrows():

    sample = row[
        FEATURES
    ].values.astype(np.float32)

    buffer.append(sample)

    print(
        f"Received sample "
        f"{index + 1:02d}/{len(df)} "
        f"| {row['timestamp']}"
    )

    if len(buffer) < WINDOW_SIZE:

        time.sleep(0.05)

        continue

    # --------------------------------------------------------
    # CREATE WINDOW
    # --------------------------------------------------------

    window = np.array(buffer)

    # --------------------------------------------------------
    # SCALE
    # --------------------------------------------------------

    scaled_window = scaler.transform(
        window
    )

    # --------------------------------------------------------
    # CNN INPUT
    # --------------------------------------------------------

    cnn_input = scaled_window.reshape(
        1,
        WINDOW_SIZE,
        len(FEATURES)
    )

    # --------------------------------------------------------
    # PREDICTION
    # --------------------------------------------------------

    predictions = model.predict(
        cnn_input,
        verbose=0
    )

    activity_probs = predictions[0].squeeze()

    environment_probs = predictions[1].squeeze()

    physiological_probs = predictions[2].squeeze()

    # --------------------------------------------------------
    # CLASS INDICES
    # --------------------------------------------------------

    activity_index = np.argmax(
        activity_probs
    )

    environment_index = np.argmax(
        environment_probs
    )

    physiological_index = np.argmax(
        physiological_probs
    )

    # --------------------------------------------------------
    # LABELS
    # --------------------------------------------------------

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
        activity_probs[activity_index]
    )

    environment_confidence = float(
        environment_probs[environment_index]
    )

    physiological_confidence = float(
        physiological_probs[
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

    status = get_status(
        risk_score
    )

    status_counts[status] += 1

    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

    window_number += 1

    print()
    print("----------------------------------------")
    print(
        f"V2 AI UPDATE - WINDOW "
        f"{window_number}"
    )
    print("----------------------------------------")

    print(
        f"Activity       : {activity} "
        f"({activity_confidence:.3f})"
    )

    print(
        f"Environment    : {environment} "
        f"({environment_confidence:.3f})"
    )

    print(
        f"Physiological  : {physiological} "
        f"({physiological_confidence:.3f})"
    )

    print(
        "Risk Score     :",
        risk_score
    )

    print(
        "Status         :",
        status
    )

    # --------------------------------------------------------
    # SLIDE WINDOW
    # --------------------------------------------------------

    buffer.pop(0)

    time.sleep(0.05)


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("================================================")
print("             V2 LIVE TEST COMPLETE")
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
    status_counts["NORMAL"]
)

print(
    "ELEVATED windows:",
    status_counts["ELEVATED"]
)

print(
    "HIGH windows:",
    status_counts["HIGH"]
)

print()
print("================================================")