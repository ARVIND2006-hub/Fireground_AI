import pandas as pd

df = pd.read_csv("../dataset/sensor_data.csv")

print("Dataset loaded successfully!")
print()
print(df)

print()
print("Number of rows:", len(df))
print("Number of columns:", len(df.columns))