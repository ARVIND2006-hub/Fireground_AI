import pandas as pd
import numpy as np
import tensorflow as tf

from sklearn.preprocessing import LabelEncoder, StandardScaler


# -----------------------------------
# 1. Load the training dataset
# -----------------------------------

df = pd.read_csv("../dataset/training_data.csv")


# -----------------------------------
# 2. Select sensor features
# -----------------------------------

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


# -----------------------------------
# 3. Create sequences
# -----------------------------------

X = []
labels = []

for scenario in df["scenario"].unique():

    scenario_data = df[df["scenario"] == scenario]

    sequence = scenario_data[features].values

    X.append(sequence)
    labels.append(scenario)


X = np.array(X)


# -----------------------------------
# 4. Encode labels
# -----------------------------------

encoder = LabelEncoder()

y = encoder.fit_transform(labels)


# -----------------------------------
# 5. Normalize sensor values
# -----------------------------------

samples, timesteps, num_features = X.shape

X_2d = X.reshape(-1, num_features)

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X_2d)

X_scaled = X_scaled.reshape(
    samples,
    timesteps,
    num_features
)


# -----------------------------------
# 6. Create 1D-CNN
# -----------------------------------

model = tf.keras.Sequential([

    tf.keras.layers.Input(
        shape=(timesteps, num_features)
    ),

    tf.keras.layers.Conv1D(
        filters=16,
        kernel_size=3,
        activation="relu"
    ),

    tf.keras.layers.Conv1D(
        filters=32,
        kernel_size=3,
        activation="relu"
    ),

    tf.keras.layers.GlobalAveragePooling1D(),

    tf.keras.layers.Dense(
        16,
        activation="relu"
    ),

    tf.keras.layers.Dense(
        len(encoder.classes_),
        activation="softmax"
    )
])


# -----------------------------------
# 7. Compile model
# -----------------------------------

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)


# -----------------------------------
# 8. Show model structure
# -----------------------------------

model.summary()