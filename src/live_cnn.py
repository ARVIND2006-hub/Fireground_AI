import time
import pickle
import numpy as np
import pandas as pd
import tensorflow as tf


# ============================================================
# 1. LOAD MODEL
# ============================================================

print("Loading CNN model...")

model = tf.keras.models.load_model(
    "../models/multitask_fireground_cnn.keras"
)


# ============================================================
# 2. LOAD SCALER
# ============================================================

with open(
    "../models/scaler.pkl",
    "rb"
) as file:

    scaler = pickle.load(file)


# ============================================================
# 3. LOAD SENSOR STREAM
# ============================================================

df = pd.read_csv(
    "../dataset/fireground_timeseries.csv"
)


# ============================================================
# 4. SENSOR FEATURES
# ============================================================

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


# ============================================================
# 5. BUFFER
# ============================================================

buffer = []

window_size = 10


# ============================================================
# 6. LABELS
# ============================================================

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


# ============================================================
# 7. START LIVE STREAM
# ============================================================

print()
print("======================================")
print(" LIVE SENSOR + CNN SYSTEM")
print("======================================")
print()


for _, row in df.iterrows():

    # --------------------------------------------------------
    # Receive one sensor sample
    # --------------------------------------------------------

    sensor_values = row[features].values.astype(float)

    buffer.append(sensor_values)


    print(
        f"Received {row['timestamp']} | "
        f"Buffer: {len(buffer)}/{window_size}"
    )


    # --------------------------------------------------------
    # Wait until we have 10 samples
    # --------------------------------------------------------

    if len(buffer) < window_size:

        time.sleep(0.5)

        continue


    # ========================================================
    # 8. CREATE 10 × 9 WINDOW
    # ========================================================

    window = np.array(buffer)


    # ========================================================
    # 9. NORMALIZE
    # ========================================================

    window_2d = window.reshape(
        -1,
        9
    )

    window_scaled = scaler.transform(
        window_2d
    )


    # CNN expects:
    # batch × time × features

    window_scaled = window_scaled.reshape(
        1,
        10,
        9
    )


    # ========================================================
    # 10. RUN CNN
    # ========================================================

    predictions = model.predict(
        window_scaled,
        verbose=0
    )


    # ========================================================
    # 11. EXTRACT OUTPUTS
    # ========================================================

    activity_probabilities = predictions[0][0]

    environment_probabilities = predictions[1][0]

    physiological_probabilities = predictions[2][0]


    # ========================================================
    # 12. FIND PREDICTIONS
    # ========================================================

    activity_index = int(
        np.argmax(activity_probabilities)
    )

    environment_index = int(
        np.argmax(environment_probabilities)
    )

    physiological_index = int(
        np.argmax(physiological_probabilities)
    )


    activity = activity_labels[
        activity_index
    ]

    environment = environment_labels[
        environment_index
    ]

    physiological = physiological_labels[
        physiological_index
    ]


    # ========================================================
    # 13. CONFIDENCE
    # ========================================================

    activity_confidence = float(
        activity_probabilities[
            activity_index
        ]
    )

    environment_confidence = float(
        environment_probabilities[
            environment_index
        ]
    )

    physiological_confidence = float(
        physiological_probabilities[
            physiological_index
        ]
    )


    # ========================================================
    # 14. DISPLAY CNN RESULT
    # ========================================================

    print()
    print("--------------------------------------")
    print(" CNN PREDICTION")
    print("--------------------------------------")

    print(
        "Activity:",
        activity,
        "| Confidence:",
        round(activity_confidence, 3)
    )

    print(
        "Environment:",
        environment,
        "| Confidence:",
        round(environment_confidence, 3)
    )

    print(
        "Physiological state:",
        physiological,
        "| Confidence:",
        round(physiological_confidence, 3)
    )


    # ========================================================
    # 15. LOCAL FUSION
    # ========================================================

    risk_score = 0


    if environment == "risk":

        risk_score += 2


    if activity == "crawling":

        risk_score += 1


    if physiological == "high":

        risk_score += 2


    if risk_score >= 4:

        situational_status = "HIGH"

    elif risk_score >= 2:

        situational_status = "ELEVATED"

    else:

        situational_status = "NORMAL"


    # ========================================================
    # 16. DISPLAY FUSION RESULT
    # ========================================================

    print()
    print("--------------------------------------")
    print(" LOCAL SITUATIONAL INTELLIGENCE")
    print("--------------------------------------")

    print(
        "Risk score:",
        risk_score
    )

    print(
        "Situational status:",
        situational_status
    )


    # ========================================================
    # 17. END DEMO
    # ========================================================

    break


print()
print("======================================")
print(" Live CNN demonstration completed.")
print("======================================")