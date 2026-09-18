import numpy as np
import pickle
import tensorflow as tf


# ---------------------------------------
# 1. Load saved multi-task CNN
# ---------------------------------------

model = tf.keras.models.load_model(
    "../models/multitask_fireground_cnn.keras"
)


# ---------------------------------------
# 2. Load scaler
# ---------------------------------------

with open("../models/scaler.pkl", "rb") as file:
    scaler = pickle.load(file)


# ---------------------------------------
# 3. New 10-second sensor window
# ---------------------------------------

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
# 4. Normalize
# ---------------------------------------

window_2d = new_window.reshape(-1, 9)

window_scaled = scaler.transform(window_2d)

window_scaled = window_scaled.reshape(1, 10, 9)


# ---------------------------------------
# 5. CNN predictions
# ---------------------------------------

predictions = model.predict(
    window_scaled,
    verbose=0
)


activity_prob = predictions[0][0]
environment_prob = predictions[1][0]
physiological_prob = predictions[2][0]


# ---------------------------------------
# 6. Convert predictions to labels
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


activity_index = int(np.argmax(activity_prob))
environment_index = int(np.argmax(environment_prob))
physiological_index = int(np.argmax(physiological_prob))


activity = activity_labels[activity_index]
environment = environment_labels[environment_index]
physiological = physiological_labels[physiological_index]


# ---------------------------------------
# 7. Simple prototype fusion
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
# 8. Generate event
# ---------------------------------------

print("======================================")
print(" LOCAL SITUATIONAL INTELLIGENCE")
print("======================================")

print()
print("Activity:", activity)
print("Environment:", environment)
print("Physiological state:", physiological)

print()
print("Prototype risk score:", risk_score)
print("Situational status:", situational_status)

print()
print("EVENT")

print("--------------------------------------")

if situational_status == "HIGH":

    print("Deterioration pattern detected.")
    print("Generate local fireground alert.")

elif situational_status == "ELEVATED":

    print("Elevated conditions detected.")
    print("Continue monitoring.")

else:

    print("No elevated pattern detected.")

print("--------------------------------------")