import os
import json
import numpy as np


INPUT_PATH = "../models/exported/fireground_weights.npz"

OUTPUT_DIR = "../models/quantized"

OUTPUT_WEIGHTS = (
    OUTPUT_DIR +
    "/fireground_weights_int8.npz"
)

OUTPUT_INFO = (
    OUTPUT_DIR +
    "/quantization_info.json"
)


# ============================================================
# CREATE OUTPUT FOLDER
# ============================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)


print()
print("==============================================")
print("      FIREGROUND AI INT8 QUANTIZATION")
print("==============================================")
print()

print("Loading floating-point weights...")
print(INPUT_PATH)
print()


# ============================================================
# LOAD WEIGHTS
# ============================================================

data = np.load(INPUT_PATH)


quantized = {}

quantization_info = {}


# ============================================================
# QUANTIZE EACH WEIGHT ARRAY
# ============================================================

for name in data.files:

    weights = data[name].astype(np.float32)

    max_abs = np.max(np.abs(weights))

    # Avoid divide-by-zero
    if max_abs == 0:

        scale = 1.0

    else:

        scale = max_abs / 127.0

    quantized_weights = np.round(
        weights / scale
    ).astype(np.int8)

    quantized[name] = quantized_weights

    quantization_info[name] = {

        "original_shape":
            list(weights.shape),

        "original_dtype":
            str(weights.dtype),

        "quantized_dtype":
            str(quantized_weights.dtype),

        "min":
            float(np.min(weights)),

        "max":
            float(np.max(weights)),

        "scale":
            float(scale),

        "quantized_min":
            int(np.min(quantized_weights)),

        "quantized_max":
            int(np.max(quantized_weights))
    }

    print(
        f"{name}: "
        f"{weights.shape} "
        f"-> INT8 "
        f"scale={scale:.8f}"
    )


# ============================================================
# SAVE INT8 WEIGHTS
# ============================================================

np.savez(
    OUTPUT_WEIGHTS,
    **quantized
)


# ============================================================
# SAVE QUANTIZATION INFORMATION
# ============================================================

with open(
    OUTPUT_INFO,
    "w"
) as file:

    json.dump(
        quantization_info,
        file,
        indent=4
    )


# ============================================================
# SUMMARY
# ============================================================

print()
print("==============================================")
print("QUANTIZATION COMPLETE")
print("==============================================")

print()
print("INT8 weights saved to:")
print(OUTPUT_WEIGHTS)

print()
print("Quantization information saved to:")
print(OUTPUT_INFO)

print()
print("Total weight arrays:", len(data.files))

print()
print("==============================================")