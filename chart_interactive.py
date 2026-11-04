import os
import plotly.express as px
from data_tools import load_clean_data

df = load_clean_data()

sales_by_product = df.groupby("product")["revenue"].sum().reset_index()
sales_by_product = sales_by_product.sort_values("revenue", ascending=False)

fig = px.bar(
    sales_by_product,
    x="product",
    y="revenue",
    title="Sales by Product (move your mouse over a bar)",
    labels={"product": "Product", "revenue": "Revenue (Naira)"},
)

os.makedirs("charts", exist_ok=True)
fig.write_html("charts/sales_by_product.html")
fig.show()