import pandas as pd

# Load time-series data
df = pd.read_csv("../dataset/fireground_timeseries.csv")

# Features used by the AI
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

# Create one 10-second window
window = df[features].values

print("10-second window created!")
print()
print("Shape:", window.shape)
print()
print(window)