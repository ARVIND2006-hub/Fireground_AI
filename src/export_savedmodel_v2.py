import os
from tensorflow.keras.models import load_model

MODEL_PATH = "../models/multitask_fireground_cnn_v2.keras"
EXPORT_PATH = "../models/savedmodel_v2"

print()
print("==============================================")
print("   FIREGROUND AI V2 SAVEDMODEL EXPORT")
print("==============================================")
print()

print("Loading V2 model...")
model = load_model(MODEL_PATH)

print("Model loaded successfully.")
print("Parameters:", model.count_params())
print()

if os.path.exists(EXPORT_PATH):
    print("SavedModel directory already exists.")
else:
    print("Exporting to SavedModel...")
    model.export(EXPORT_PATH)
    print("Export completed.")

print()
print("SavedModel path:")
print(EXPORT_PATH)

print()
print("==============================================")
print("           EXPORT COMPLETE")
print("==============================================")