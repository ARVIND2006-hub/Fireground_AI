import time
import numpy as np
import pandas as pd
import joblib
from tensorflow.keras.models import load_model


# ==========================================
# FILE PATHS
# ==========================================

MODEL_PATH = "../models/multitask_fireground_cnn.keras"
SCALER_PATH = "../models/scaler.pkl"
DATA_PATH = "../dataset/live_sensor_stream.csv"


# ==========================================
# LOAD MODEL
# ==========================================

print("Loading CNN model...")

model = load_model(MODEL_PATH)

scaler = joblib.load(SCALER_PATH)

print("Model loaded successfully.")
print()


# ==========================================
# LOAD LIVE SENSOR STREAM
# ==========================================

df = pd.read_csv(DATA_PATH)

print("Live sensor stream loaded.")
print("Total samples:", len(df))
print()


# ==========================================
# SENSOR FEATURES
# ==========================================

features = [
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


# ==========================================
# SLIDING WINDOW
# ==========================================

WINDOW_SIZE = 10

buffer = []

window_number = 0


# ==========================================
# CLASS LABELS
# ==========================================

activity_labels = [
    "crawling",
    "standing",
    "walking"
]

environment_labels = [
    "normal",
    "risk"
]

physiological_labels = [
    "elevated",
    "high",
    "normal"
]


# ==========================================
# RISK SCORE
# ==========================================

def calculate_risk_score(activity, environment, physiological):

    score = 0

    if environment == "risk":
        score += 2

    if activity == "crawling":
        score += 1

    if physiological == "high":
        score += 2

    return score


# ==========================================
# STATUS
# ==========================================

def get_status(score):

    if score >= 4:
        return "HIGH"

    elif score >= 2:
        return "ELEVATED"

    else:
        return "NORMAL"


# ==========================================
# START STREAM
# ==========================================

print("Starting sliding-window CNN...")
print("Window size:", WINDOW_SIZE)
print()

for index, row in df.iterrows():

    # --------------------------------------
    # RECEIVE ONE SENSOR SAMPLE
    # --------------------------------------

    sample = row[features].values.astype(float)

    buffer.append(sample)

    print(
        f"Received sample {index + 1:02d}/"
        f"{len(df)} | Time: {row['timestamp']}"
    )

    # --------------------------------------
    # WAIT FOR 10 SAMPLES
    # --------------------------------------

    if len(buffer) < WINDOW_SIZE:

        time.sleep(0.05)

        continue

    # --------------------------------------
    # CREATE WINDOW
    # --------------------------------------

    window = np.array(buffer)

    print()
    print("----------------------------------------")
    print(f"AI UPDATE - WINDOW {window_number + 1}")
    print("----------------------------------------")

    print("Window shape:", window.shape)

    # --------------------------------------
    # SCALE WINDOW
    # --------------------------------------

    scaled_window = scaler.transform(window)

    # --------------------------------------
    # CNN INPUT
    # --------------------------------------

    cnn_input = scaled_window.reshape(
        1,
        WINDOW_SIZE,
        len(features)
    )

    # --------------------------------------
    # CNN PREDICTION
    # --------------------------------------

    predictions = model.predict(
        cnn_input,
        verbose=0
    )

    # --------------------------------------
    # REMOVE BATCH DIMENSION
    # --------------------------------------

    activity_prediction = predictions[0].squeeze()

    environment_prediction = predictions[1].squeeze()

    physiological_prediction = predictions[2].squeeze()

    # --------------------------------------
    # FIND PREDICTED CLASS
    # --------------------------------------

    activity_index = np.argmax(
        activity_prediction
    )

    environment_index = np.argmax(
        environment_prediction
    )

    physiological_index = np.argmax(
        physiological_prediction
    )

    # --------------------------------------
    # CONVERT INDEX TO LABEL
    # --------------------------------------

    activity = activity_labels[
        activity_index
    ]

    environment = environment_labels[
        environment_index
    ]

    physiological = physiological_labels[
        physiological_index
    ]

    # --------------------------------------
    # CONFIDENCE
    # --------------------------------------

    activity_confidence = activity_prediction[
        activity_index
    ]

    environment_confidence = environment_prediction[
        environment_index
    ]

    physiological_confidence = physiological_prediction[
        physiological_index
    ]

    # --------------------------------------
    # RISK SCORE
    # --------------------------------------

    risk_score = calculate_risk_score(
        activity,
        environment,
        physiological
    )

    status = get_status(risk_score)

    # --------------------------------------
    # DISPLAY RESULTS
    # --------------------------------------

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

    print()

    print("Risk Score     :", risk_score)

    print("Status         :", status)

    # --------------------------------------
    # SLIDE WINDOW
    # --------------------------------------

    buffer.pop(0)

    window_number += 1

    time.sleep(0.05)


# ==========================================
# END
# ==========================================

print()
print("----------------------------------------")
print("STREAM COMPLETE")
print("----------------------------------------")

print(
    "Total AI windows processed:",
    window_number
)

print()
print("Sliding-window CNN demonstration complete.")