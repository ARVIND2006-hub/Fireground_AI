import pandas as pd
import numpy as np

# Load the training data
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

# Store sequences and labels
X = []
y = []

# Create one sequence from each scenario
for scenario in df["scenario"].unique():
    scenario_data = df[df["scenario"] == scenario]

    sequence = scenario_data[features].values

    X.append(sequence)
    y.append(scenario)

# Convert to NumPy arrays
X = np.array(X)

print("Sequences created successfully!")
print()
print("X shape:", X.shape)
print()
print("Number of sequences:", len(X))
print()
print("Sequence labels:")
print(y)