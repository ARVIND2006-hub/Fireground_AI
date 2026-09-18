import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("../dataset/sensor_data.csv")

plt.plot(df["heart_rate"], marker="o")

plt.title("Heart Rate")
plt.xlabel("Sample")
plt.ylabel("Heart Rate")

plt.show()
