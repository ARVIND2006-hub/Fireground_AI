import numpy as np
import pickle
import tensorflow as tf


# ---------------------------------------
# 1. Load saved multi-task model
# ---------------------------------------

model = tf.keras.models.load_model(
    "../models/multitask_fireground_cnn.keras"
)


# ---------------------------------------
# 2. Load saved scaler
# ---------------------------------------

with open("../models/scaler.pkl", "rb") as file:
    scaler = pickle.load(file)


# ---------------------------------------
# 3. Create new 10-second sensor window
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
# 5. Predict
# ---------------------------------------

predictions = model.predict(
    window_scaled,
    verbose=0
)


# ---------------------------------------
# 6. Extract the three outputs
# ---------------------------------------

activity_probabilities = predictions[0][0]
environment_probabilities = predictions[1][0]
physiological_probabilities = predictions[2][0]


activity_code = int(np.argmax(activity_probabilities))
environment_code = int(np.argmax(environment_probabilities))
physiological_code = int(np.argmax(physiological_probabilities))


# ---------------------------------------
# 7. Class mappings
# ---------------------------------------

activity_labels = {
    0: "crawling",
    1: "standing",
    2: "walking"
}

environment_labels = {
    0: "normal",
    1: "risk"
}

physiological_labels = {
    0: "elevated",
    1: "high",
    2: "normal"
}


# ---------------------------------------
# 8. Display results
# ---------------------------------------

print("======================================")
print(" MULTI-TASK FIREGROUND AI")
print("======================================")

print()
print("Activity:")
print("Prediction:", activity_labels[activity_code])
print("Confidence:", round(float(activity_probabilities[activity_code]), 4))

print()
print("Environment:")
print("Prediction:", environment_labels[environment_code])
print("Confidence:", round(float(environment_probabilities[environment_code]), 4))

print()
print("Physiological/Activity State:")
print("Prediction:", physiological_labels[physiological_code])
print("Confidence:", round(float(
    physiological_probabilities[physiological_code]
), 4))