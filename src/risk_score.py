import pandas as pd

# Load time-series data
df = pd.read_csv("../dataset/fireground_timeseries.csv")

# Calculate trends
heart_rate_change = df["heart_rate"].iloc[-1] - df["heart_rate"].iloc[0]
gas_change = df["gas"].iloc[-1] - df["gas"].iloc[0]
temperature_change = df["temperature"].iloc[-1] - df["temperature"].iloc[0]

# Start risk score
risk_score = 0

# Example learning rules
if gas_change >= 20:
    risk_score += 2

if temperature_change >= 5:
    risk_score += 2

if heart_rate_change >= 20:
    risk_score += 1

if df["activity"].iloc[-1] == "crawling":
    risk_score += 1

# Convert score to a simple risk level
if risk_score <= 1:
    risk_level = "LOW"
elif risk_score <= 3:
    risk_level = "MEDIUM"
elif risk_score <= 5:
    risk_level = "HIGH"
else:
    risk_level = "CRITICAL"

print("Fireground Situational Risk")
print("----------------------------")
print("Heart rate change :", heart_rate_change)
print("Gas change        :", gas_change)
print("Temperature change:", temperature_change)
print("Current activity  :", df["activity"].iloc[-1])
print("Risk score        :", risk_score)
print("Risk level        :", risk_level)