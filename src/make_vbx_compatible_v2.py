import os
import numpy as np
from tensorflow.keras.models import load_model, Model
from tensorflow.keras.layers import (
    Input,
    Conv1D,
    Reshape,
    AveragePooling2D,
    Flatten,
    Dense
)

OLD_MODEL_PATH = "../models/multitask_fireground_cnn_v2.keras"
NEW_MODEL_PATH = "../models/multitask_fireground_cnn_v2_vbx.keras"
X_TEST_PATH = "../dataset/v2_prepared/X_test.npy"

print()
print("================================================")
print("   CREATE VECTORBLOX-COMPATIBLE V2 MODEL")
print("================================================")
print()

print("Loading original V2 model...")
old_model = load_model(OLD_MODEL_PATH)
print("Original model loaded.")
print("Parameters:", old_model.count_params())
print()

# ------------------------------------------------
# Build equivalent model without GlobalAveragePooling1D
# ------------------------------------------------

inputs = Input(
    shape=(10, 9),
    name="input_layer"
)

x = Conv1D(
    filters=16,
    kernel_size=3,
    activation="relu",
    name="conv1"
)(inputs)

x = Conv1D(
    filters=32,
    kernel_size=3,
    activation="relu",
    name="conv2"
)(x)

# Convert [batch, 6, 32] -> [batch, 6, 32, 1]
x = Reshape(
    (6, 32, 1),
    name="reshape_for_pool"
)(x)

# Average across the 6 time positions
x = AveragePooling2D(
    pool_size=(6, 1),
    strides=(6, 1),
    padding="valid",
    name="avg_pool"
)(x)

x = Flatten(
    name="flatten"
)(x)

x = Dense(
    32,
    activation="relu",
    name="dense_shared"
)(x)

activity = Dense(
    3,
    activation="softmax",
    name="activity"
)(x)

environment = Dense(
    2,
    activation="softmax",
    name="environment"
)(x)

physiological = Dense(
    3,
    activation="softmax",
    name="physiological"
)(x)

new_model = Model(
    inputs=inputs,
    outputs=[
        activity,
        environment,
        physiological
    ],
    name="fireground_v2_vbx"
)

# ------------------------------------------------
# Copy learned weights from original model
# ------------------------------------------------

for layer_name in [
    "conv1",
    "conv2",
    "dense_shared",
    "activity",
    "environment",
    "physiological"
]:
    old_layer = old_model.get_layer(layer_name)
    new_layer = new_model.get_layer(layer_name)

    new_layer.set_weights(
        old_layer.get_weights()
    )

print("Original learned weights copied.")
print()

print("New model parameters:", new_model.count_params())

# ------------------------------------------------
# Compare original and new model
# ------------------------------------------------

print()
print("Testing equivalence...")

X_test = np.load(X_TEST_PATH)

old_predictions = old_model.predict(
    X_test,
    verbose=0
)

new_predictions = new_model.predict(
    X_test,
    verbose=0
)

for index, name in enumerate([
    "Activity",
    "Environment",
    "Physiological"
]):
    difference = np.max(
        np.abs(
            old_predictions[index]
            - new_predictions[index]
        )
    )

    print(
        f"{name} maximum prediction difference: "
        f"{difference:.10f}"
    )

# Compare predicted classes
for index, name in enumerate([
    "Activity",
    "Environment",
    "Physiological"
]):
    old_classes = np.argmax(
        old_predictions[index],
        axis=1
    )

    new_classes = np.argmax(
        new_predictions[index],
        axis=1
    )

    agreement = np.mean(
        old_classes == new_classes
    )

    print(
        f"{name} class agreement: "
        f"{agreement:.4f}"
    )

# ------------------------------------------------
# Save model
# ------------------------------------------------

new_model.save(NEW_MODEL_PATH)

print()
print("Saved:")
print(NEW_MODEL_PATH)

print()
print("================================================")
print("             MODEL CREATION COMPLETE")
print("================================================")