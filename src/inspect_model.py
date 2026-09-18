from tensorflow.keras.models import load_model


MODEL_PATH = "../models/multitask_fireground_cnn.keras"


print()
print("==============================================")
print("       FIREGROUND AI MODEL INSPECTION")
print("==============================================")
print()

model = load_model(MODEL_PATH)

print("MODEL INPUT")
print("----------------------------------------------")
print("Input shape:", model.input_shape)

print()
print("MODEL OUTPUTS")
print("----------------------------------------------")

for output in model.outputs:
    print(output.shape)

print()
print("MODEL LAYERS")
print("----------------------------------------------")

for i, layer in enumerate(model.layers):
    print(
        i,
        "|",
        layer.name,
        "|",
        layer.__class__.__name__,
        "|",
        layer.output.shape
    )

print()
print("MODEL PARAMETERS")
print("----------------------------------------------")
print("Total parameters:", model.count_params())

print()
print("MODEL SUMMARY")
print("----------------------------------------------")

model.summary()

print()
print("==============================================")
print("Inspection completed.")
print("==============================================")