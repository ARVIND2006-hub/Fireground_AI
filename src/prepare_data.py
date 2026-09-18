import pandas as pd
from sklearn.preprocessing import LabelEncoder

# Load dataset
df = pd.read_csv("../dataset/sensor_data.csv")

# Convert activity text into numbers
encoder = LabelEncoder()
df["activity_code"] = encoder.fit_transform(df["activity"])

print("Activity mapping:")
for label, code in zip(encoder.classes_, encoder.transform(encoder.classes_)):
    print(label, "=", code)

print()
print("Prepared dataset:")
print(df)

print()
print("Input features:")
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

print(X)

print()
print("Target:")
y = df["activity_code"]

print(y)