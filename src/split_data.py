import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Load dataset
df = pd.read_csv("../dataset/sensor_data.csv")

# Convert activity labels to numbers
encoder = LabelEncoder()
y = encoder.fit_transform(df["activity"])

# Select input features
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

# Split the data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.4,
    random_state=42
)

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))

print()
print("X_train:")
print(X_train)

print()
print("X_test:")
print(X_test)

print()
print("y_train:")
print(y_train)

print()
print("y_test:")
print(y_test)