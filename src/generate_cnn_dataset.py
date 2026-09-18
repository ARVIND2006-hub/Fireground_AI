import numpy as np
import pandas as pd

# Reproducible random data
np.random.seed(42)

# Number of windows per class
windows_per_class = 200

# Number of time steps in each window
timesteps = 10

# Sensor feature names
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

rows = []

# -------------------------------------------------
# Generate one window for a given scenario
# -------------------------------------------------

def generate_window(scenario):

    # Base values
    heart_rate = 75
    gas = 20
    temperature = 30

    for t in range(timesteps):

        # -----------------------------------------
        # NORMAL
        # -----------------------------------------
        if scenario == "normal":

            hr = np.random.normal(75, 2)
            gx = np.random.normal(0.01, 0.005)
            gy = np.random.normal(0.02, 0.005)
            gz = np.random.normal(0.01, 0.005)

            ax = np.random.normal(0.10, 0.03)
            ay = np.random.normal(0.20, 0.03)
            az = np.random.normal(9.80, 0.05)

            gas_value = np.random.normal(20, 2)
            temp = np.random.normal(30, 0.5)

        # -----------------------------------------
        # WALKING
        # -----------------------------------------
        elif scenario == "walking":

            hr = 80 + t * 1.0 + np.random.normal(0, 2)

            ax = 0.20 + t * 0.04 + np.random.normal(0, 0.03)
            ay = 0.20 + np.random.normal(0, 0.05)
            az = 9.70 + np.random.normal(0, 0.07)

            gx = 0.02 + t * 0.004 + np.random.normal(0, 0.005)
            gy = 0.02 + t * 0.003 + np.random.normal(0, 0.005)
            gz = 0.01 + t * 0.003 + np.random.normal(0, 0.005)

            gas_value = 20 + t * 0.5 + np.random.normal(0, 2)
            temp = 30 + t * 0.1 + np.random.normal(0, 0.5)

        # -----------------------------------------
        # ENVIRONMENT RISK
        # -----------------------------------------
        elif scenario == "environment_risk":

            hr = 78 + t * 0.8 + np.random.normal(0, 2)

            ax = np.random.normal(0.10, 0.03)
            ay = np.random.normal(0.20, 0.03)
            az = np.random.normal(9.80, 0.05)

            gx = np.random.normal(0.01, 0.005)
            gy = np.random.normal(0.02, 0.005)
            gz = np.random.normal(0.01, 0.005)

            gas_value = 20 + t * 4 + np.random.normal(0, 2)
            temp = 30 + t * 0.6 + np.random.normal(0, 0.5)

        # -----------------------------------------
        # COMBINED RISK
        # -----------------------------------------
        elif scenario == "combined_risk":

            hr = 82 + t * 2.0 + np.random.normal(0, 2)

            ax = 0.20 + t * 0.04 + np.random.normal(0, 0.04)
            ay = 0.30 + np.random.normal(0, 0.05)
            az = 9.70 - t * 0.03 + np.random.normal(0, 0.06)

            gx = 0.02 + t * 0.004 + np.random.normal(0, 0.006)
            gy = 0.03 + t * 0.004 + np.random.normal(0, 0.006)
            gz = 0.02 + t * 0.004 + np.random.normal(0, 0.006)

            gas_value = 20 + t * 4.5 + np.random.normal(0, 2)
            temp = 30 + t * 0.7 + np.random.normal(0, 0.5)

        else:
            raise ValueError("Unknown scenario")

        rows.append({
            "scenario": scenario,
            "time_step": t,
            "heart_rate": hr,
            "acc_x": ax,
            "acc_y": ay,
            "acc_z": az,
            "gyro_x": gx,
            "gyro_y": gy,
            "gyro_z": gz,
            "gas": gas_value,
            "temperature": temp
        })


# -------------------------------------------------
# Generate all four classes
# -------------------------------------------------

scenarios = [
    "normal",
    "walking",
    "environment_risk",
    "combined_risk"
]

for scenario in scenarios:

    for _ in range(windows_per_class):
        generate_window(scenario)


# Convert to DataFrame
df = pd.DataFrame(rows)

# Save dataset
df.to_csv("../dataset/cnn_training_data.csv", index=False)

print("CNN practice dataset created successfully!")
print()
print("Total rows:", len(df))
print("Total columns:", len(df.columns))
print()
print("Rows per scenario:")
print(df["scenario"].value_counts())