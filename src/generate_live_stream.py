import numpy as np
import pandas as pd

np.random.seed(42)

rows = []

for t in range(60):

    # First 20 seconds: normal
    if t < 20:

        heart_rate = 75 + np.random.normal(0, 2)
        gas = 20 + np.random.normal(0, 2)
        temperature = 30 + np.random.normal(0, 0.4)

        acc_x = 0.10 + np.random.normal(0, 0.03)
        acc_y = 0.20 + np.random.normal(0, 0.03)
        acc_z = 9.80 + np.random.normal(0, 0.05)

        gyro_x = 0.01 + np.random.normal(0, 0.005)
        gyro_y = 0.02 + np.random.normal(0, 0.005)
        gyro_z = 0.01 + np.random.normal(0, 0.005)

    # 20–40 seconds: walking
    elif t < 40:

        step = t - 20

        heart_rate = 80 + step * 0.5 + np.random.normal(0, 2)
        gas = 20 + np.random.normal(0, 2)
        temperature = 30 + step * 0.05 + np.random.normal(0, 0.4)

        acc_x = 0.20 + step * 0.015 + np.random.normal(0, 0.03)
        acc_y = 0.20 + np.random.normal(0, 0.05)
        acc_z = 9.70 + np.random.normal(0, 0.07)

        gyro_x = 0.02 + step * 0.002 + np.random.normal(0, 0.005)
        gyro_y = 0.02 + step * 0.002 + np.random.normal(0, 0.005)
        gyro_z = 0.01 + step * 0.002 + np.random.normal(0, 0.005)

    # 40–60 seconds: deteriorating conditions
    else:

        step = t - 40

        heart_rate = 90 + step * 1.0 + np.random.normal(0, 2)

        gas = 35 + step * 2.0 + np.random.normal(0, 2)

        temperature = 33 + step * 0.3 + np.random.normal(0, 0.4)

        acc_x = 0.40 + step * 0.01 + np.random.normal(0, 0.04)
        acc_y = 0.30 + np.random.normal(0, 0.05)
        acc_z = 9.60 - step * 0.01 + np.random.normal(0, 0.06)

        gyro_x = 0.04 + step * 0.002 + np.random.normal(0, 0.006)
        gyro_y = 0.04 + step * 0.002 + np.random.normal(0, 0.006)
        gyro_z = 0.03 + step * 0.002 + np.random.normal(0, 0.006)

    rows.append({
        "timestamp": f"14:{t // 60:02d}:{t % 60:02d}",
        "heart_rate": heart_rate,
        "acc_x": acc_x,
        "acc_y": acc_y,
        "acc_z": acc_z,
        "gyro_x": gyro_x,
        "gyro_y": gyro_y,
        "gyro_z": gyro_z,
        "gas": gas,
        "temperature": temperature
    })


df = pd.DataFrame(rows)

df.to_csv(
    "../dataset/live_sensor_stream.csv",
    index=False
)

print("60-second live sensor stream created!")
print()
print("Total samples:", len(df))
print()
print(df.head())
print()
print(df.tail())