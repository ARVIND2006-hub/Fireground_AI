import pandas as pd

# Load the time-series data
df = pd.read_csv("../dataset/fireground_timeseries.csv")

# Calculate changes during the 10-second window
heart_rate_change = df["heart_rate"].iloc[-1] - df["heart_rate"].iloc[0]
gas_change = df["gas"].iloc[-1] - df["gas"].iloc[0]
temperature_change = df["temperature"].iloc[-1] - df["temperature"].iloc[0]

print("Sensor trends")
print("----------------------")

print("Heart rate change :", heart_rate_change)
print("Gas change        :", gas_change)
print("Temperature change:", temperature_change)