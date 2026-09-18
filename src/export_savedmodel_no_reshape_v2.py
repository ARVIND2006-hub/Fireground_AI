import os
from tensorflow.keras.models import load_model

MODEL_PATH = "../models/multitask_fireground_cnn_v2_vbx_no_reshape.keras"
EXPORT_PATH = "../models/savedmodel_vbx_no_reshape_v2"

print()
print("================================================")
print(" FIREGROUND AI V2 - SAVEDMODEL EXPORT")
print("================================================")
print()

print("Loading no-reshape model...")

model = load_model(MODEL_PATH)

print("Model loaded successfully.")
print("Parameters:", model.count_params())
print()

print("Exporting SavedModel...")

model.export(EXPORT_PATH)

print()
print("SavedModel created:")
print(EXPORT_PATH)

print()
print("================================================")
print("             EXPORT COMPLETE")
print("================================================")