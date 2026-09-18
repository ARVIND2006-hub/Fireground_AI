import json
import numpy as np
import joblib
from tensorflow.keras.models import load_model


# ============================================================
# PATHS
# ============================================================

MODEL_PATH = "../models/exported/fireground_inference.keras"

WEIGHTS_PATH = "../models/quantized/fireground_weights_int8.npz"

INFO_PATH = "../models/quantized/quantization_info.json"

SCALER_PATH = "../models/scaler.pkl"

DATA_PATH = "../dataset/live_sensor_stream.csv"


# ============================================================
# LOAD ORIGINAL MODEL
# ============================================================

print()
print("================================================")
print("      FIREGROUND AI INT8 VERIFICATION")
print("================================================")
print()

print("Loading original FP32 model...")

model = load_model(MODEL_PATH)

print("FP32 model loaded.")
print()


# ============================================================
# LOAD QUANTIZED WEIGHTS
# ============================================================

print("Loading INT8 weights...")

int8_data = np.load(WEIGHTS_PATH)

with open(INFO_PATH, "r") as file:
    quant_info = json.load(file)

print("INT8 weights loaded.")
print()


# ============================================================
# DEQUANTIZATION TEST
# ============================================================

print("Checking INT8 → FP32 reconstruction...")
print()

max_error = 0.0

for name in int8_data.files:

    int8_weights = int8_data[name]

    scale = quant_info[name]["scale"]

    reconstructed = (
        int8_weights.astype(np.float32) * scale
    )

    original_min = quant_info[name]["min"]

    original_max = quant_info[name]["max"]

    reconstructed_min = float(
        np.min(reconstructed)
    )

    reconstructed_max = float(
        np.max(reconstructed)
    )

    error = max(
        abs(original_min - reconstructed_min),
        abs(original_max - reconstructed_max)
    )

    max_error = max(max_error, error)

    print(
        f"{name}: "
        f"reconstructed range "
        f"[{reconstructed_min:.6f}, "
        f"{reconstructed_max:.6f}] "
        f"| max error={error:.8f}"
    )


# ============================================================
# LOAD SENSOR DATA
# ============================================================

print()
print("Loading test sensor window...")

df = np.genfromtxt(
    DATA_PATH,
    delimiter=",",
    names=True
)


# ============================================================
# SENSOR FEATURES
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
# CREATE 10-SAMPLE WINDOW
# ============================================================

window = np.column_stack(
    [
        df[feature][:10]
        for feature in features
    ]
).astype(np.float32)


print("Window shape:", window.shape)


# ============================================================
# APPLY SAME SCALER
# ============================================================

scaler = joblib.load(SCALER_PATH)

scaled_window = scaler.transform(window)

cnn_input = scaled_window.reshape(
    1,
    10,
    9
)


# ============================================================
# FP32 PREDICTION
# ============================================================

print()
print("Running FP32 inference...")

fp32_predictions = model.predict(
    cnn_input,
    verbose=0
)


# ============================================================
# DISPLAY FP32 RESULTS
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


activity_index = np.argmax(
    fp32_predictions[0][0]
)

environment_index = np.argmax(
    fp32_predictions[1][0]
)

physiological_index = np.argmax(
    fp32_predictions[2][0]
)


print()
print("================================================")
print("FP32 PREDICTION")
print("================================================")

print(
    "Activity:",
    activity_labels[activity_index]
)

print(
    "Activity confidence:",
    float(
        fp32_predictions[0][0][activity_index]
    )
)

print(
    "Environment:",
    environment_labels[environment_index]
)

print(
    "Environment confidence:",
    float(
        fp32_predictions[1][0][environment_index]
    )
)

print(
    "Physiological:",
    physiological_labels[physiological_index]
)

print(
    "Physiological confidence:",
    float(
        fp32_predictions[2][0][physiological_index]
    )
)


# ============================================================
# QUANTIZATION ERROR SUMMARY
# ============================================================

print()
print("================================================")
print("QUANTIZATION SUMMARY")
print("================================================")

print(
    "Maximum weight reconstruction error:",
    max_error
)

print()
print("INT8 weight verification completed.")
print("================================================")