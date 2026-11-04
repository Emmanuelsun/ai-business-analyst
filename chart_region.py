import os
import matplotlib.pyplot as plt
from data_tools import load_clean_data

df = load_clean_data()

sales_by_region = df.groupby("customer_region")["revenue"].sum().sort_values(ascending=False)

plt.figure(figsize=(8, 5))
plt.bar(sales_by_region.index, sales_by_region.values)
plt.title("Sales by City")
plt.ylabel("Revenue (Naira)")
plt.tight_layout()

os.makedirs("charts", exist_ok=True)
plt.savefig("charts/sales_by_region.png")
plt.show()