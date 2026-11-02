import pandas as pd

df = pd.read_csv("data/sales_data.csv")

print(df.head())
print("\nHow many rows and columns:")
print(df.shape)

print("\nMissing values in each column:")
print(df.isna().sum())