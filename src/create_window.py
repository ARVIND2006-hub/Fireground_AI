import pandas as pd
import numpy as np

# Load the sensor dataset
df = pd.read_csv("../dataset/sensor_data.csv")

# Select the sensor features
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

window = df[features].values

print("Time window created!")
print()
print("Window shape:", window.shape)
print()
print(window)
