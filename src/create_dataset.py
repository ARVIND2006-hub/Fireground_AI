import pandas as pd

data = {
    "heart_rate": [78, 82, 85, 90, 96],
    "acc_x": [0.1, 0.2, 0.3, 0.4, 0.5],
    "acc_y": [0.2, 0.3, 0.2, 0.4, 0.3],
    "acc_z": [9.8, 9.7, 9.8, 9.6, 9.5],
    "gyro_x": [0.01, 0.02, 0.03, 0.04, 0.05],
    "gyro_y": [0.02, 0.03, 0.02, 0.04, 0.03],
    "gyro_z": [0.01, 0.01, 0.02, 0.03, 0.04],
    "gas": [20, 25, 30, 40, 55],
    "temperature": [30, 31, 32, 34, 36],
    "activity": ["standing", "walking", "walking", "crawling", "crawling"]
}

df = pd.DataFrame(data)

df.to_csv("../dataset/sensor_data.csv", index=False)

print("Dataset created successfully!")
print(df)
