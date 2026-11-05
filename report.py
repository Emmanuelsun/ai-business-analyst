import html
import re
from datetime import date

STYLE = """
body { font-family: Arial, sans-serif; margin: 40px; color: #222; max-width: 800px; }
h1 { margin-bottom: 4px; }
h2 { margin-top: 32px; border-bottom: 1px solid #ddd; padding-bottom: 4px; }
table { border-collapse: collapse; width: 100%; margin-top: 8px; }
th, td { text-align: left; padding: 8px; border-bottom: 1px solid #eee; }
th { background: #f5f5f5; }
.muted { color: #666; font-size: 13px; }
.warn { color: #9a6700; }
"""


def make_table(rows, headers):
    head = "".join(f"<th>{html.escape(h)}</th>" for h in headers)
    body = ""
    for row in rows:
        cells = "".join(f"<td>{html.escape(str(cell))}</td>" for cell in row)
        body += f"<tr>{cells}</tr>"
    return f"<table><tr>{head}</tr>{body}</table>"


def ai_text_to_html(text):
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?m)^\s*\* ", "• ", text)
    return text.replace("\n", "<br>")


def build_report_html(summary, insights=None, problems=None):
    product_rows = [(name, f"₦{value:,}") for name, value in summary["sales_by_product"].items()]
    region_rows = [(name, f"₦{value:,}") for name, value in summary["sales_by_region"].items()]

    ai_section = ""
    if insights:
        if problems:
            check = "Some figures could not be matched to the data: " + ", ".join(problems)
            check_html = f'<p class="warn">{html.escape(check)}</p>'
        else:
            check_html = '<p class="muted">Every figure in this summary was checked against the data.</p>'
        ai_section = (
            "<h2>AI insights</h2>"
            + f"<p>{ai_text_to_html(insights)}</p>"
            + check_html
            + '<p class="muted">Insights are written by AI from the data. Please review them before making business decisions.</p>'
        )

    today = date.today().strftime("%d %B %Y")

    return f"""<html>
<head>
<meta charset="utf-8">
<title>Sales Report</title>
<style>{STYLE}</style>
</head>
<body>
<h1>Sales Report</h1>
<p class="muted">Prepared on {today} &middot; Period covered: {summary['first_date']} to {summary['last_date']}</p>

<h2>Key figures</h2>
{make_table([
    ("Total sales", f"₦{summary['total_sales_naira']:,}"),
    ("Number of orders", summary["number_of_sales"]),
    ("Top product", f"{summary['best_product']} ({summary['best_product_share_percent']}% of sales)"),
    ("Weakest product", summary["weakest_product"]),
    ("Top city", summary["best_region"]),
], ["Measure", "Value"])}

<h2>Sales by product</h2>
{make_table(product_rows, ["Product", "Revenue"])}

<h2>Sales by city</h2>
{make_table(region_rows, ["City", "Revenue"])}

{ai_section}
</body>
</html>
"""