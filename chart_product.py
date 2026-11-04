import os
import matplotlib.pyplot as plt
from data_tools import load_clean_data

df = load_clean_data()

sales_by_product = df.groupby("product")["revenue"].sum().sort_values()

plt.figure(figsize=(9, 5))
plt.barh(sales_by_product.index, sales_by_product.values)
plt.title("Sales by Product")
plt.xlabel("Revenue (Naira)")
plt.tight_layout()

os.makedirs("charts", exist_ok=True)
plt.savefig("charts/sales_by_product.png")
plt.show()