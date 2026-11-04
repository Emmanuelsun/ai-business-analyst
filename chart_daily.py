import os
import matplotlib.pyplot as plt
from data_tools import load_clean_data

df = load_clean_data()

daily_sales = df.groupby("date")["revenue"].sum()

plt.figure(figsize=(9, 5))
plt.plot(daily_sales.index, daily_sales.values, marker="o")
plt.title("Sales Day by Day")
plt.ylabel("Revenue (Naira)")
plt.xticks(rotation=45)
plt.tight_layout()

os.makedirs("charts", exist_ok=True)
plt.savefig("charts/daily_sales.png")
plt.show()