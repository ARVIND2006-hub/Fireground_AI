import pandas as pd
import numpy as np
import tensorflow as tf

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import confusion_matrix, classification_report


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
# 4. Encode labels
# ---------------------------------------

encoder = LabelEncoder()
y = encoder.fit_transform(labels)


# ---------------------------------------
# 5. Normalize
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

model.fit(
    X_train,
    y_train,
    epochs=20,
    batch_size=32,
    validation_split=0.2,
    verbose=0
)


# ---------------------------------------
# 10. Predict
# ---------------------------------------

probabilities = model.predict(
    X_test,
    verbose=0
)

y_pred = np.argmax(probabilities, axis=1)


# ---------------------------------------
# 11. Confusion matrix
# ---------------------------------------

cm = confusion_matrix(y_test, y_pred)

print()
print("CONFUSION MATRIX")
print("----------------")
print(cm)


# ---------------------------------------
# 12. Classification report
# ---------------------------------------

print()
print("CLASSIFICATION REPORT")
print("---------------------")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=encoder.classes_
    )
)


# ---------------------------------------
# 13. Show some predictions
# ---------------------------------------

print("SAMPLE PREDICTIONS")
print("------------------")

for i in range(min(10, len(y_test))):

    actual = encoder.inverse_transform([y_test[i]])[0]
    predicted = encoder.inverse_transform([y_pred[i]])[0]

    confidence = probabilities[i][y_pred[i]]

    print(
        f"Actual: {actual:20s} "
        f"Predicted: {predicted:20s} "
        f"Confidence: {confidence:.3f}"
    )