import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler

# Load data
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

# Encode labels
encoder = LabelEncoder()
y = encoder.fit_transform(labels)

# -----------------------------
# Normalize sensor values
# -----------------------------

# Shape:
# X = (4 sequences, 5 time steps, 9 features)

# Reshape temporarily so StandardScaler
# can process all feature columns
samples, timesteps, num_features = X.shape

X_2d = X.reshape(-1, num_features)

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X_2d)

# Convert back to sequence format
X_scaled = X_scaled.reshape(samples, timesteps, num_features)

print("Normalization completed!")
print()
print("Original shape:", X.shape)
print("Normalized shape:", X_scaled.shape)

print()
print("First normalized sequence:")
print(X_scaled[0])

print()
print("Labels:", y)