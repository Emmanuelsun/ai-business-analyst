import os
import re
import html
import webbrowser
import plotly.express as px
from data_tools import load_clean_data, build_summary
from ai_analyst import get_insights, find_unverified_numbers


def advice_to_html(text):
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?m)^\* ", "• ", text)
    return text.replace("\n", "<br>")


df = load_clean_data()
summary = build_summary(df)

total_sales = df["revenue"].sum()

by_product = df.groupby("product")["revenue"].sum().reset_index()
by_product = by_product.sort_values("revenue", ascending=False)

by_region = df.groupby("customer_region")["revenue"].sum().reset_index()
by_region = by_region.sort_values("revenue", ascending=False)

by_day = df.groupby("date")["revenue"].sum().reset_index()

best_product = by_product.iloc[0]["product"]
best_region = by_region.iloc[0]["customer_region"]

fig_product = px.bar(by_product, x="product", y="revenue", title="Sales by Product")
fig_region = px.bar(by_region, x="customer_region", y="revenue", title="Sales by City")
fig_day = px.line(by_day, x="date", y="revenue", markers=True, title="Sales Day by Day")

insights = get_insights(summary)
problems = find_unverified_numbers(insights, summary)

if problems:
    check_note = "Warning: these numbers could not be matched to our facts: " + ", ".join(problems)
else:
    check_note = "Number check passed: every number in this advice matches the facts calculated by Python."

page = f"""
<html>
<head>
<meta charset="utf-8">
<title>Shop Sales Dashboard</title>
</head>
<body style="font-family: Arial; margin: 30px;">
<h1>Shop Sales Dashboard</h1>
<p><b>Total sales:</b> {total_sales:,} Naira</p>
<p><b>Best product:</b> {best_product}</p>
<p><b>Best city:</b> {best_region}</p>

<div style="background: #eef3ff; border-radius: 8px; padding: 16px; margin: 20px 0; max-width: 800px;">
<h2>Advice from your AI helper</h2>
<p>{advice_to_html(insights)}</p>
<p style="color: #555; font-size: 13px;">{check_note}</p>
<p style="color: #555; font-size: 13px;">All numbers are calculated by Python. The AI only explains them in words.</p>
</div>

{fig_product.to_html(full_html=False, include_plotlyjs=True)}
{fig_region.to_html(full_html=False, include_plotlyjs=False)}
{fig_day.to_html(full_html=False, include_plotlyjs=False)}
</body>
</html>
"""

os.makedirs("charts", exist_ok=True)
with open("charts/dashboard.html", "w", encoding="utf-8") as file:
    file.write(page)

webbrowser.open("file:///" + os.path.abspath("charts/dashboard.html"))