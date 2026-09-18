import pandas as pd

# Create synthetic practice data
data = {
    "scenario": [
        "normal", "normal", "normal", "normal", "normal",
        "walking", "walking", "walking", "walking", "walking",
        "environment_risk", "environment_risk", "environment_risk",
        "environment_risk", "environment_risk",
        "combined_risk", "combined_risk", "combined_risk",
        "combined_risk", "combined_risk"
    ],

    "heart_rate": [
        75, 76, 77, 78, 79,
        80, 82, 84, 86, 88,
        80, 82, 84, 86, 88,
        82, 87, 92, 97, 102
    ],

    "acc_x": [
        0.1, 0.1, 0.1, 0.1, 0.1,
        0.2, 0.3, 0.4, 0.5, 0.6,
        0.1, 0.1, 0.1, 0.1, 0.1,
        0.2, 0.3, 0.4, 0.5, 0.6
    ],

    "acc_y": [
        0.2, 0.2, 0.2, 0.2, 0.2,
        0.2, 0.3, 0.2, 0.3, 0.4,
        0.2, 0.2, 0.2, 0.2, 0.2,
        0.3, 0.3, 0.4, 0.4, 0.4
    ],

    "acc_z": [
        9.8, 9.8, 9.8, 9.8, 9.8,
        9.7, 9.7, 9.6, 9.6, 9.5,
        9.8, 9.8, 9.8, 9.8, 9.8,
        9.7, 9.6, 9.6, 9.5, 9.4
    ],

    "gyro_x": [
        0.01, 0.01, 0.01, 0.01, 0.01,
        0.02, 0.03, 0.04, 0.05, 0.06,
        0.01, 0.01, 0.01, 0.01, 0.01,
        0.02, 0.03, 0.04, 0.05, 0.06
    ],

    "gyro_y": [
        0.02, 0.02, 0.02, 0.02, 0.02,
        0.02, 0.03, 0.03, 0.04, 0.04,
        0.02, 0.02, 0.02, 0.02, 0.02,
        0.03, 0.03, 0.04, 0.05, 0.05
    ],

    "gyro_z": [
        0.01, 0.01, 0.01, 0.01, 0.01,
        0.01, 0.02, 0.02, 0.03, 0.03,
        0.01, 0.01, 0.01, 0.01, 0.01,
        0.02, 0.02, 0.03, 0.04, 0.04
    ],

    "gas": [
        20, 20, 21, 21, 22,
        20, 21, 22, 23, 24,
        20, 25, 30, 40, 55,
        20, 25, 32, 45, 60
    ],

    "temperature": [
        30, 30, 30, 30, 30,
        30, 30, 31, 31, 31,
        30, 31, 32, 34, 36,
        30, 31, 33, 35, 37
    ],

    "activity": [
        "standing", "standing", "standing", "standing", "standing",
        "walking", "walking", "walking", "walking", "walking",
        "standing", "standing", "standing", "standing", "standing",
        "walking", "walking", "crawling", "crawling", "crawling"
    ]
}

df = pd.DataFrame(data)

# Save dataset
df.to_csv("../dataset/training_data.csv", index=False)

print("Training dataset created successfully!")
print()
print(df)

print()
print("Number of samples:", len(df))
print("Number of columns:", len(df.columns))