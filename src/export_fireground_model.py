import os
import numpy as np
from tensorflow.keras.models import load_model


MODEL_PATH = "../models/multitask_fireground_cnn.keras"
OUTPUT_DIR = "../models/exported"


print()
print("==============================================")
print("     FIREGROUND AI MODEL EXPORT")
print("==============================================")
print()

# --------------------------------------------------
# Create output folder
# --------------------------------------------------

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --------------------------------------------------
# Load model
# --------------------------------------------------

print("Loading model...")

model = load_model(MODEL_PATH)

print("Model loaded.")
print()

# --------------------------------------------------
# Save model without optimizer
# --------------------------------------------------

optimized_model_path = (
    OUTPUT_DIR +
    "/fireground_inference.keras"
)

model.save(
    optimized_model_path,
    include_optimizer=False
)

print("Inference model saved:")
print(optimized_model_path)
print()

# --------------------------------------------------
# Export model weights
# --------------------------------------------------

weights_path = (
    OUTPUT_DIR +
    "/fireground_weights.npz"
)

weights = {}

for layer in model.layers:

    layer_weights = layer.get_weights()

    if len(layer_weights) == 0:
        continue

    for index, weight in enumerate(layer_weights):

        key = f"{layer.name}_weight_{index}"

        weights[key] = weight

        print(
            f"{key}: shape={weight.shape}"
        )

np.savez(
    weights_path,
    **weights
)

print()
print("Weights exported:")
print(weights_path)

# --------------------------------------------------
# Print model information
# --------------------------------------------------

print()
print("==============================================")
print("MODEL INFORMATION")
print("==============================================")

print("Input shape:", model.input_shape)

print("Outputs:")

for output in model.outputs:
    print(output.shape)

print()

print(
    "Trainable parameters:",
    model.count_params()
)

print()
print("Export completed successfully.")
print("==============================================")