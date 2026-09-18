import pandas as pd

# Create 10 seconds of example sensor data
data = {
    "timestamp": [
        "14:00:00",
        "14:00:01",
        "14:00:02",
        "14:00:03",
        "14:00:04",
        "14:00:05",
        "14:00:06",
        "14:00:07",
        "14:00:08",
        "14:00:09"
    ],

    "heart_rate": [78, 80, 82, 85, 88, 90, 93, 96, 99, 102],

    "acc_x": [0.1, 0.2, 0.2, 0.3, 0.3, 0.4, 0.4, 0.5, 0.5, 0.6],
    "acc_y": [0.2, 0.2, 0.3, 0.2, 0.3, 0.3, 0.4, 0.3, 0.4, 0.4],
    "acc_z": [9.8, 9.7, 9.8, 9.7, 9.6, 9.6, 9.5, 9.5, 9.4, 9.4],

    "gyro_x": [0.01, 0.01, 0.02, 0.02, 0.03, 0.03, 0.04, 0.04, 0.05, 0.05],
    "gyro_y": [0.02, 0.02, 0.03, 0.02, 0.03, 0.04, 0.04, 0.05, 0.05, 0.06],
    "gyro_z": [0.01, 0.02, 0.02, 0.03, 0.03, 0.04, 0.04, 0.05, 0.06, 0.06],

    "gas": [20, 21, 23, 25, 28, 32, 37, 43, 50, 58],

    "temperature": [30, 30, 31, 31, 32, 33, 33, 34, 35, 36],

    "activity": [
        "standing",
        "standing",
        "walking",
        "walking",
        "walking",
        "walking",
        "crawling",
        "crawling",
        "crawling",
        "crawling"
    ]
}

df = pd.DataFrame(data)

df.to_csv("../dataset/fireground_timeseries.csv", index=False)

print("Time-series dataset created successfully!")
print()
print(df)