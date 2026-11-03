import pandas as pd

df = pd.read_csv("data/sales_data.csv")

print("Sale with a missing quantity:")
print(df[df["quantity"].isna()])

print("\nRows before cleaning:", len(df))

df = df.dropna(subset=["quantity"])

print("Rows after cleaning:", len(df))
df["quantity"] = df["quantity"].astype(int)

df["revenue"] = df["quantity"] * df["unit_price"]

print("\nCleaned table with revenue:")
print(df)

total_sales = df["revenue"].sum()

print(f"\nTotal sales: {total_sales:,}")

sales_by_product = df.groupby("product")["revenue"].sum().sort_values(ascending=False)

print("\nSales by product:")
print(sales_by_product)

sales_by_region = df.groupby("customer_region")["revenue"].sum().sort_values(ascending=False)

print("\nSales by region:")
print(sales_by_region)