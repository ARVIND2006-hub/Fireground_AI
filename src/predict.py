import numpy as np
import pickle
import tensorflow as tf


# ---------------------------------------
# 1. Load saved model
# ---------------------------------------

model = tf.keras.models.load_model(
    "../models/fireground_cnn.keras"
)


# ---------------------------------------
# 2. Load saved scaler
# ---------------------------------------

with open("../models/scaler.pkl", "rb") as file:
    scaler = pickle.load(file)


# ---------------------------------------
# 3. Load class labels
# ---------------------------------------

class_labels = {}

with open("../models/class_labels.txt", "r") as file:

    for line in file:
        code, label = line.strip().split("=")
        class_labels[int(code)] = label


# ---------------------------------------
# 4. Create a new example window
# ---------------------------------------
# 10 time steps × 9 sensor features

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
# 5. Normalize the new window
# ---------------------------------------

num_features = new_window.shape[1]

window_2d = new_window.reshape(-1, num_features)

window_scaled = scaler.transform(window_2d)

window_scaled = window_scaled.reshape(1, 10, 9)


# ---------------------------------------
# 6. Make prediction
# ---------------------------------------

probabilities = model.predict(
    window_scaled,
    verbose=0
)

predicted_code = int(np.argmax(probabilities[0]))

predicted_label = class_labels[predicted_code]

confidence = float(probabilities[0][predicted_code])


# ---------------------------------------
# 7. Display result
# ---------------------------------------

print("===================================")
print(" FIREGROUND AI PREDICTION")
print("===================================")

print("Predicted class :", predicted_label)
print("Confidence      :", round(confidence, 4))

print()
print("All class probabilities:")

for code, probability in enumerate(probabilities[0]):

    print(
        class_labels[code],
        ":",
        round(float(probability), 4)
    )