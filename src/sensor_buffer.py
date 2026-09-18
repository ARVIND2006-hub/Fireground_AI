import pandas as pd
import numpy as np
import time


# ---------------------------------------
# Load simulated sensor stream
# ---------------------------------------

df = pd.read_csv(
    "../dataset/fireground_timeseries.csv"
)


# ---------------------------------------
# Sensor features
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
# Buffer
# ---------------------------------------

buffer = []

window_size = 10


print("======================================")
print(" REAL-TIME SENSOR BUFFER")
print("======================================")
print()


# ---------------------------------------
# Receive sensor samples
# ---------------------------------------

for _, row in df.iterrows():

    sensor_values = row[features].values

    buffer.append(sensor_values)

    print(
        "Received:",
        row["timestamp"],
        "| Buffer:",
        len(buffer),
        "/",
        window_size
    )

    # -----------------------------------
    # Window is ready
    # -----------------------------------

    if len(buffer) == window_size:

        window = np.array(buffer)

        print()
        print("--------------------------------------")
        print("10-SAMPLE WINDOW READY")
        print("--------------------------------------")

        print(
            "Window shape:",
            window.shape
        )

        print()

        print(window)

        print()

        break

    time.sleep(0.5)


print("--------------------------------------")
print("Buffer demonstration completed.")