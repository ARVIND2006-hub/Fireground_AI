import pandas as pd
import numpy as np
import tensorflow as tf

from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split


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
# 3. Create 10-step windows
# ---------------------------------------

X = []

activity_labels = []
environment_labels = []
physiological_labels = []

window_size = 10

for start in range(0, len(df), window_size):

    window = df.iloc[start:start + window_size]

    if len(window) != window_size:
        continue

    X.append(window[features].values)

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
# 4. Encode labels
# ---------------------------------------

activity_encoder = LabelEncoder()
environment_encoder = LabelEncoder()
physiological_encoder = LabelEncoder()

y_activity = activity_encoder.fit_transform(
    activity_labels
)

y_environment = environment_encoder.fit_transform(
    environment_labels
)

y_physiological = physiological_encoder.fit_transform(
    physiological_labels
)


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

indices = np.arange(samples)

train_idx, test_idx = train_test_split(
    indices,
    test_size=0.20,
    random_state=42,
    stratify=y_activity
)

X_train = X_scaled[train_idx]
X_test = X_scaled[test_idx]

activity_train = y_activity[train_idx]
activity_test = y_activity[test_idx]

environment_train = y_environment[train_idx]
environment_test = y_environment[test_idx]

physiological_train = y_physiological[train_idx]
physiological_test = y_physiological[test_idx]


print("Training windows:", len(X_train))
print("Testing windows :", len(X_test))


# ---------------------------------------
# 7. Shared CNN
# ---------------------------------------

inputs = tf.keras.Input(
    shape=(timesteps, num_features)
)

x = tf.keras.layers.Conv1D(
    filters=16,
    kernel_size=3,
    activation="relu"
)(inputs)

x = tf.keras.layers.Conv1D(
    filters=32,
    kernel_size=3,
    activation="relu"
)(x)

x = tf.keras.layers.GlobalAveragePooling1D()(x)

x = tf.keras.layers.Dense(
    32,
    activation="relu"
)(x)


# ---------------------------------------
# 8. Three output heads
# ---------------------------------------

activity_output = tf.keras.layers.Dense(
    len(activity_encoder.classes_),
    activation="softmax",
    name="activity"
)(x)

environment_output = tf.keras.layers.Dense(
    len(environment_encoder.classes_),
    activation="softmax",
    name="environment"
)(x)

physiological_output = tf.keras.layers.Dense(
    len(physiological_encoder.classes_),
    activation="softmax",
    name="physiological"
)(x)


# ---------------------------------------
# 9. Create multi-output model
# ---------------------------------------

model = tf.keras.Model(
    inputs=inputs,
    outputs=[
        activity_output,
        environment_output,
        physiological_output
    ]
)


# ---------------------------------------
# 10. Compile
# ---------------------------------------

model.compile(
    optimizer="adam",

    loss={
        "activity": "sparse_categorical_crossentropy",
        "environment": "sparse_categorical_crossentropy",
        "physiological": "sparse_categorical_crossentropy"
    },

    metrics={
        "activity": ["accuracy"],
        "environment": ["accuracy"],
        "physiological": ["accuracy"]
    }
)


# ---------------------------------------
# 11. Show model
# ---------------------------------------

model.summary()


# ---------------------------------------
# 12. Train model
# ---------------------------------------

history = model.fit(
    X_train,

    {
        "activity": activity_train,
        "environment": environment_train,
        "physiological": physiological_train
    },

    validation_split=0.20,
    epochs=20,
    batch_size=32,
    verbose=1
)


# ---------------------------------------
# 13. Evaluate
# ---------------------------------------

results = model.evaluate(
    X_test,

    {
        "activity": activity_test,
        "environment": environment_test,
        "physiological": physiological_test
    },

    verbose=1
)

print()
print("Multi-task CNN evaluation completed!")
print("Evaluation results:")
print(results)

# ---------------------------------------
# 14. Save multi-task CNN
# ---------------------------------------

model.save("../models/multitask_fireground_cnn.keras")

print()
print("Multi-task CNN saved successfully!")
print("Saved to: ../models/multitask_fireground_cnn.keras")