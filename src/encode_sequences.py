import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

# Load training data
df = pd.read_csv("../dataset/training_data.csv")

# Sensor features
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

# Create sequences
X = []
labels = []

for scenario in df["scenario"].unique():
    scenario_data = df[df["scenario"] == scenario]

    sequence = scenario_data[features].values

    X.append(sequence)
    labels.append(scenario)

X = np.array(X)

# Convert scenario names to numbers
encoder = LabelEncoder()
y = encoder.fit_transform(labels)

print("Encoded sequences successfully!")
print()
print("X shape:", X.shape)
print()
print("y shape:", y.shape)
print()
print("Scenario mapping:")

for code, label in enumerate(encoder.classes_):
    print(code, "=", label)

print()
print("Encoded labels:")
print(y)