import numpy as np
import pickle
import json
from datetime import datetime
import tensorflow as tf


# ---------------------------------------
# 1. Load saved CNN
# ---------------------------------------

model = tf.keras.models.load_model(
    "../models/multitask_fireground_cnn.keras"
)


# ---------------------------------------
# 2. Load saved scaler
# ---------------------------------------

with open(
    "../models/scaler.pkl",
    "rb"
) as file:

    scaler = pickle.load(file)


# ---------------------------------------
# 3. New 10-second sensor window
# ---------------------------------------
# 10 time steps × 9 sensor features
#
# Order:
# heart_rate
# acc_x
# acc_y
# acc_z
# gyro_x
# gyro_y
# gyro_z
# gas
# temperature

new_window = np.array([

    [82, 0.20, 0.30, 9.70, 0.02, 0.03, 0.02, 20, 30],
    [87, 0.30, 0.30, 9.60, 0.03, 0.03, 0.02, 25, 31],
    [92, 0.40, 0.40, 9.60, 0.04, 0.04, 0.03, 32, 33],
    [97, 0.50, 0.40, 9.50, 0.05, 0.05, 0.04, 45, 35],
    [102, 0.60, 0.40, 9.40, 0.06, 0.05, 0.04, 60, 37],
    [104, 0.60, 0.40, 9.40, 0.06, 0.06, 0.04, 63, 38],
    [106, 0.60, 0.40, 9.30, 0.07, 0.06, 0.05, 67, 39],
    [108, 0.70, 0.40, 9.30, 0.07, 0.06, 0.05, 70, 40],
    [110, 0.70, 0.50, 9.20, 0.08, 0.07, 0.06, 74, 41],
    [112, 0.70, 0.50, 9.20, 0.08, 0.07, 0.06, 78, 42]

])


# ---------------------------------------
# 4. Normalize the window
# ---------------------------------------

window_2d = new_window.reshape(-1, 9)

window_scaled = scaler.transform(window_2d)

window_scaled = window_scaled.reshape(1, 10, 9)


# ---------------------------------------
# 5. Run CNN
# ---------------------------------------

predictions = model.predict(
    window_scaled,
    verbose=0
)


# ---------------------------------------
# 6. Extract predictions
# ---------------------------------------

activity_prob = predictions[0][0]

environment_prob = predictions[1][0]

physiological_prob = predictions[2][0]


# ---------------------------------------
# 7. Class labels
# ---------------------------------------

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


# ---------------------------------------
# 8. Select predicted classes
# ---------------------------------------

activity_index = int(
    np.argmax(activity_prob)
)

environment_index = int(
    np.argmax(environment_prob)
)

physiological_index = int(
    np.argmax(physiological_prob)
)


activity = activity_labels[activity_index]

environment = environment_labels[environment_index]

physiological = physiological_labels[
    physiological_index
]


# ---------------------------------------
# 9. Calculate confidence
# ---------------------------------------

activity_confidence = float(
    activity_prob[activity_index]
)

environment_confidence = float(
    environment_prob[environment_index]
)

physiological_confidence = float(
    physiological_prob[physiological_index]
)


# ---------------------------------------
# 10. Prototype situational fusion
# ---------------------------------------

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


# ---------------------------------------
# 11. Determine event type
# ---------------------------------------

if situational_status == "HIGH":

    event_type = "deterioration"

elif situational_status == "ELEVATED":

    event_type = "environment_change"

else:

    event_type = "status_update"


# ---------------------------------------
# 12. Create automatic event
# ---------------------------------------

event = {

    "node_id": "FF01",

    "timestamp": datetime.now().isoformat(),

    "activity": activity,

    "activity_confidence": round(
        activity_confidence,
        4
    ),

    "environment": environment,

    "environment_confidence": round(
        environment_confidence,
        4
    ),

    "physiological_state": physiological,

    "physiological_confidence": round(
        physiological_confidence,
        4
    ),

    "risk_score": risk_score,

    "situational_status": situational_status,

    "event_type": event_type

}


# ---------------------------------------
# 13. Display event
# ---------------------------------------

print("======================================")
print(" AUTOMATIC FIREGROUND EVENT")
print("======================================")

print(
    json.dumps(
        event,
        indent=4
    )
)


# ---------------------------------------
# 14. Save event
# ---------------------------------------

with open(
    "../results/automatic_firefighter_event.json",
    "w"
) as file:

    json.dump(
        event,
        file,
        indent=4
    )


print()
print("Automatic event saved!")
print(
    "Saved to: ../results/automatic_firefighter_event.json"
)