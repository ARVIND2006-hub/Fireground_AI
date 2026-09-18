import numpy as np
from tensorflow.keras.models import load_model, Model
from tensorflow.keras.layers import Input, Conv2D, Softmax

OLD_MODEL_PATH = "../models/multitask_fireground_cnn_v2.keras"
NEW_MODEL_PATH = "../models/multitask_fireground_cnn_v2_vbx_no_reshape.keras"
X_TEST_PATH = "../dataset/v2_prepared/X_test.npy"

print()
print("================================================")
print("   VECTORBLOX V2 - NO RESHAPE MODEL")
print("================================================")
print()

# ------------------------------------------------
# Load original trained model
# ------------------------------------------------

old_model = load_model(OLD_MODEL_PATH)

print("Original model loaded.")
print("Original parameters:", old_model.count_params())
print()

# ------------------------------------------------
# New 4-D input
# [time, sensors, channel]
# ------------------------------------------------

inputs = Input(
    shape=(10, 9, 1),
    name="input_4d"
)

# ------------------------------------------------
# Original Conv1D #1 -> Conv2D
# ------------------------------------------------

x = Conv2D(
    filters=16,
    kernel_size=(3, 9),
    padding="valid",
    activation="relu",
    name="conv1"
)(inputs)

# ------------------------------------------------
# Original Conv1D #2 -> Conv2D
# ------------------------------------------------

x = Conv2D(
    filters=32,
    kernel_size=(3, 1),
    padding="valid",
    activation="relu",
    name="conv2"
)(x)

# ------------------------------------------------
# Replace GlobalAveragePooling1D
#
# Input to this layer:
#   6 x 1 x 32
#
# Output:
#   1 x 1 x 32
#
# Each output channel averages the six
# time samples of the same feature channel.
# ------------------------------------------------

x = Conv2D(
    filters=32,
    kernel_size=(6, 1),
    padding="valid",
    activation=None,
    use_bias=True,
    name="mean_conv"
)(x)

# ------------------------------------------------
# Shared Dense -> 1x1 Conv2D
# ------------------------------------------------

x = Conv2D(
    filters=32,
    kernel_size=(1, 1),
    padding="valid",
    activation="relu",
    name="dense_shared"
)(x)

# ------------------------------------------------
# Activity head
# ------------------------------------------------

activity_logits = Conv2D(
    filters=3,
    kernel_size=(1, 1),
    padding="valid",
    activation=None,
    name="activity_logits"
)(x)

activity = Softmax(
    axis=-1,
    name="activity"
)(activity_logits)

# ------------------------------------------------
# Environment head
# ------------------------------------------------

environment_logits = Conv2D(
    filters=2,
    kernel_size=(1, 1),
    padding="valid",
    activation=None,
    name="environment_logits"
)(x)

environment = Softmax(
    axis=-1,
    name="environment"
)(environment_logits)

# ------------------------------------------------
# Physiological head
# ------------------------------------------------

physiological_logits = Conv2D(
    filters=3,
    kernel_size=(1, 1),
    padding="valid",
    activation=None,
    name="physiological_logits"
)(x)

physiological = Softmax(
    axis=-1,
    name="physiological"
)(physiological_logits)

new_model = Model(
    inputs=inputs,
    outputs=[
        activity,
        environment,
        physiological
    ],
    name="fireground_v2_vbx_no_reshape"
)

# ------------------------------------------------
# Copy Conv1D #1 weights
#
# Old shape:
#   (3, 9, 16)
#
# New shape:
#   (3, 9, 1, 16)
# ------------------------------------------------

old_conv1 = old_model.get_layer("conv1")
new_conv1 = new_model.get_layer("conv1")

old_w, old_b = old_conv1.get_weights()

new_w = old_w[:, :, np.newaxis, :]

new_conv1.set_weights(
    [new_w, old_b]
)

# ------------------------------------------------
# Copy Conv1D #2 weights
#
# Old:
#   (3, 16, 32)
#
# New:
#   (3, 1, 16, 32)
# ------------------------------------------------

old_conv2 = old_model.get_layer("conv2")
new_conv2 = new_model.get_layer("conv2")

old_w, old_b = old_conv2.get_weights()

new_w = old_w[:, np.newaxis, :, :]

new_conv2.set_weights(
    [new_w, old_b]
)

# ------------------------------------------------
# Build exact average weights
# ------------------------------------------------

mean_weights = np.zeros(
    (6, 1, 32, 32),
    dtype=np.float32
)

for c in range(32):
    mean_weights[:, 0, c, c] = 1.0 / 6.0

mean_bias = np.zeros(
    32,
    dtype=np.float32
)

new_model.get_layer("mean_conv").set_weights(
    [mean_weights, mean_bias]
)

# ------------------------------------------------
# Copy shared Dense weights
# ------------------------------------------------

old_dense = old_model.get_layer("dense_shared")
new_dense = new_model.get_layer("dense_shared")

old_w, old_b = old_dense.get_weights()

new_w = old_w.reshape(
    1, 1, old_w.shape[0], old_w.shape[1]
)

new_dense.set_weights(
    [new_w, old_b]
)

# ------------------------------------------------
# Copy output Dense weights
# ------------------------------------------------

for old_name, new_name in [
    ("activity", "activity_logits"),
    ("environment", "environment_logits"),
    ("physiological", "physiological_logits")
]:

    old_layer = old_model.get_layer(old_name)
    new_layer = new_model.get_layer(new_name)

    old_w, old_b = old_layer.get_weights()

    new_w = old_w.reshape(
        1, 1, old_w.shape[0], old_w.shape[1]
    )

    new_layer.set_weights(
        [new_w, old_b]
    )

# ------------------------------------------------
# Test equivalence
# ------------------------------------------------

print("All learned weights copied.")
print("New parameters:", new_model.count_params())
print()

X_test = np.load(X_TEST_PATH)

# Original model expects [N,10,9]
old_pred = old_model.predict(
    X_test,
    verbose=0
)

# New model expects [N,10,9,1]
X_test_4d = X_test[..., np.newaxis]

new_pred = new_model.predict(
    X_test_4d,
    verbose=0
)

print("Testing prediction equivalence...")
print()

for i, name in enumerate([
    "Activity",
    "Environment",
    "Physiological"
]):

    old_output = old_pred[i]

    new_output = new_pred[i].squeeze(
        axis=(1, 2)
    )

    difference = np.max(
        np.abs(old_output - new_output)
    )

    old_classes = np.argmax(
        old_output,
        axis=-1
    )

    new_classes = np.argmax(
        new_output,
        axis=-1
    )

    agreement = np.mean(
        old_classes == new_classes
    )

    print(
        f"{name} max difference: "
        f"{difference:.10f}"
    )

    print(
        f"{name} class agreement: "
        f"{agreement:.4f}"
    )

# ------------------------------------------------
# Save
# ------------------------------------------------

new_model.save(
    NEW_MODEL_PATH
)

print()
print("Saved:")
print(NEW_MODEL_PATH)

print()
print("================================================")
print("              COMPLETE")
print("================================================")