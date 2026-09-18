import pandas as pd
import time

# Load the practice time-series data
df = pd.read_csv(
    "../dataset/fireground_timeseries.csv"
)

print("======================================")
print(" SIMULATED LIVE SENSOR STREAM")
print("======================================")

print()

# Send one sensor row at a time
for index, row in df.iterrows():

    print(
        f"Time: {row['timestamp']} | "
        f"HR: {row['heart_rate']} | "
        f"Gas: {row['gas']} | "
        f"Temp: {row['temperature']} | "
        f"Activity: {row['activity']}"
    )

    # Wait 0.5 second to simulate live arrival
    time.sleep(0.5)

print()
print("Sensor stream completed.")