import os
from tensorflow.keras.models import load_model

MODEL_PATH = "../models/multitask_fireground_cnn_v2_vbx.keras"
EXPORT_PATH = "../models/savedmodel_vbx_v2"

print()
print("==============================================")
print(" VECTORBLOX COMPATIBLE V2 SAVEDMODEL EXPORT")
print("==============================================")
print()

print("Loading compatible V2 model...")
model = load_model(MODEL_PATH)

print("Model loaded successfully.")
print("Parameters:", model.count_params())
print()

print("Exporting SavedModel...")

model.export(EXPORT_PATH)

print()
print("SavedModel exported successfully:")
print(EXPORT_PATH)

print()
print("==============================================")
print("           EXPORT COMPLETE")
print("==============================================")