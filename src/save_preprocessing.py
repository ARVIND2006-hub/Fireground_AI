import pandas as pd
import numpy as np
import pickle

from sklearn.preprocessing import LabelEncoder, StandardScaler


# ---------------------------------------
# 1. Load the same training dataset
# ---------------------------------------

df = pd.read_csv("../dataset/cnn_training_data.csv")


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
labels = []

for scenario in df["scenario"].unique():

    scenario_data = df[df["scenario"] == scenario]

    for start in range(0, len(scenario_data), 10):

        window = scenario_data.iloc[start:start + 10]

        if len(window) == 10:
            X.append(window[features].values)
            labels.append(scenario)


X = np.array(X)


# ---------------------------------------
# 4. Fit label encoder
# ---------------------------------------

encoder = LabelEncoder()
y = encoder.fit_transform(labels)


# ---------------------------------------
# 5. Fit scaler
# ---------------------------------------

samples, timesteps, num_features = X.shape

X_2d = X.reshape(-1, num_features)

scaler = StandardScaler()
scaler.fit(X_2d)


# ---------------------------------------
# 6. Save scaler
# ---------------------------------------

with open("../models/scaler.pkl", "wb") as file:
    pickle.dump(scaler, file)


# ---------------------------------------
# 7. Save class labels
# ---------------------------------------

with open("../models/class_labels.txt", "w") as file:

    for code, label in enumerate(encoder.classes_):
        file.write(f"{code}={label}\n")


print("Preprocessing information saved!")
print()
print("Saved files:")
print("scaler.pkl")
print("class_labels.txt")