import pandas as pd
import numpy as np

from sklearn.preprocessing import LabelEncoder, StandardScaler


# ---------------------------------------
# 1. Load dataset
# ---------------------------------------

df = pd.read_csv("../dataset/cnn_training_data.csv")


# ---------------------------------------
# 2. Select sensor features
# ---------------------------------------

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


# ---------------------------------------
# 3. Create sequences
# ---------------------------------------

X = []
labels = []

for scenario in df["scenario"].unique():

    scenario_data = df[df["scenario"] == scenario]

    # Every 10 rows = one time window
    for start in range(0, len(scenario_data), 10):

        window = scenario_data.iloc[start:start + 10]

        if len(window) == 10:

            X.append(window[features].values)
            labels.append(scenario)


X = np.array(X)


# ---------------------------------------
# 4. Encode labels
# ---------------------------------------

encoder = LabelEncoder()
y = encoder.fit_transform(labels)


# ---------------------------------------
# 5. Normalize features
# ---------------------------------------

samples, timesteps, num_features = X.shape

X_2d = X.reshape(-1, num_features)

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X_2d)

X_scaled = X_scaled.reshape(
    samples,
    timesteps,
    num_features
)


# ---------------------------------------
# 6. Display results
# ---------------------------------------

print("CNN dataset prepared successfully!")
print()

print("X shape:", X_scaled.shape)
print("y shape:", y.shape)

print()
print("Number of windows:", len(X_scaled))
print("Time steps per window:", timesteps)
print("Features per time step:", num_features)

print()
print("Class mapping:")

for code, label in enumerate(encoder.classes_):
    print(code, "=", label)