import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

# Load dataset
df = pd.read_csv("../dataset/sensor_data.csv")

# Convert activity labels into numbers
encoder = LabelEncoder()
y = encoder.fit_transform(df["activity"])

# Input features
X = df[
    [
        "heart_rate",
        "acc_x",
        "acc_y",
        "acc_z",
        "gyro_x",
        "gyro_y",
        "gyro_z",
        "gas",
        "temperature",
    ]
]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.4,
    random_state=42
)

# Create AI model
model = DecisionTreeClassifier(random_state=42)

# Train model
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Check accuracy
accuracy = accuracy_score(y_test, y_pred)

print("Actual values:   ", y_test)
print("Predicted values: ", y_pred)
print("Accuracy:", accuracy)

print()
print("Activity labels:")
for code, label in enumerate(encoder.classes_):
    print(code, "=", label)