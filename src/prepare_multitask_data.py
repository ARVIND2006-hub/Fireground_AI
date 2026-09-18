import pandas as pd
import numpy as np

from sklearn.preprocessing import LabelEncoder, StandardScaler


# ---------------------------------------
# 1. Load dataset
# ---------------------------------------

df = pd.read_csv("../dataset/multitask_training_data.csv")


# ---------------------------------------
# 2. Sensor features
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

activity_labels = []
environment_labels = []
physiological_labels = []


# Each window contains 10 time steps
window_size = 10


for start in range(0, len(df), window_size):

    window = df.iloc[start:start + window_size]

    if len(window) != window_size:
        continue

    # Sensor window
    X.append(
        window[features].values
    )

    # One label for each window
    activity_labels.append(
        window["activity"].iloc[0]
    )

    environment_labels.append(
        window["environment"].iloc[0]
    )

    physiological_labels.append(
        window["physiological"].iloc[0]
    )


X = np.array(X)


# ---------------------------------------
# 4. Encode activity labels
# ---------------------------------------

activity_encoder = LabelEncoder()

y_activity = activity_encoder.fit_transform(
    activity_labels
)


# ---------------------------------------
# 5. Encode environment labels
# ---------------------------------------

environment_encoder = LabelEncoder()

y_environment = environment_encoder.fit_transform(
    environment_labels
)


# ---------------------------------------
# 6. Encode physiological labels
# ---------------------------------------

physiological_encoder = LabelEncoder()

y_physiological = physiological_encoder.fit_transform(
    physiological_labels
)


# ---------------------------------------
# 7. Normalize sensor features
# ---------------------------------------

samples, timesteps, num_features = X.shape

X_2d = X.reshape(
    -1,
    num_features
)

scaler = StandardScaler()

X_scaled = scaler.fit_transform(
    X_2d
)

X_scaled = X_scaled.reshape(
    samples,
    timesteps,
    num_features
)


# ---------------------------------------
# 8. Display results
# ---------------------------------------

print("Multi-task sequences prepared!")
print()

print("X shape:", X_scaled.shape)

print("Activity target shape:", y_activity.shape)
print("Environment target shape:", y_environment.shape)
print("Physiological target shape:", y_physiological.shape)


print()
print("Activity mapping:")

for code, label in enumerate(activity_encoder.classes_):
    print(code, "=", label)


print()
print("Environment mapping:")

for code, label in enumerate(environment_encoder.classes_):
    print(code, "=", label)


print()
print("Physiological mapping:")

for code, label in enumerate(physiological_encoder.classes_):
    print(code, "=", label)