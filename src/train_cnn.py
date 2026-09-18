import pandas as pd
import numpy as np
import tensorflow as tf

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler


# ---------------------------------------
# 1. Load dataset
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
# 3. Create windows
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
# 4. Encode labels
# ---------------------------------------

encoder = LabelEncoder()
y = encoder.fit_transform(labels)


# ---------------------------------------
# 5. Normalize sensor data
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
# 6. Train/test split
# ---------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


print("Training windows:", len(X_train))
print("Testing windows :", len(X_test))


# ---------------------------------------
# 7. Create CNN
# ---------------------------------------

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


# ---------------------------------------
# 8. Compile
# ---------------------------------------

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)


# ---------------------------------------
# 9. Train
# ---------------------------------------

history = model.fit(
    X_train,
    y_train,
    epochs=20,
    batch_size=32,
    validation_split=0.2,
    verbose=1
)


# ---------------------------------------
# 10. Evaluate
# ---------------------------------------

loss, accuracy = model.evaluate(
    X_test,
    y_test,
    verbose=0
)

print()
print("CNN training completed!")
print("Test accuracy:", accuracy)


# ---------------------------------------
# 11. Class mapping
# ---------------------------------------

print()
print("Class mapping:")

for code, label in enumerate(encoder.classes_):
    print(code, "=", label)


# ---------------------------------------
# 12. Save the trained CNN
# ---------------------------------------

model.save("../models/fireground_cnn.keras")

print()
print("Model saved successfully!")
print("Saved to: ../models/fireground_cnn.keras")