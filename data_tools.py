import pandas as pd

REQUIRED_COLUMNS = ["date", "product", "quantity", "unit_price", "customer_region"]


def read_uploaded_file(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    if name.endswith(".xlsx"):
        return pd.read_excel(uploaded_file)
    return None


def find_missing_columns(df):
    return [column for column in REQUIRED_COLUMNS if column not in df.columns]


def clean_data(df):
    df = df.copy()
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=REQUIRED_COLUMNS)
    df["quantity"] = df["quantity"].astype(int)
    df["revenue"] = df["quantity"] * df["unit_price"]
    return df


def load_clean_data(path="data/sales_data.csv"):
    return clean_data(pd.read_csv(path))


def build_summary(df):
    total_sales = int(df["revenue"].sum())
    by_product = df.groupby("product")["revenue"].sum().sort_values(ascending=False)
    by_region = df.groupby("customer_region")["revenue"].sum().sort_values(ascending=False)

    summary = {
        "number_of_sales": int(len(df)),
        "total_sales_naira": total_sales,
        "first_date": df["date"].min().strftime("%Y-%m-%d"),
        "last_date": df["date"].max().strftime("%Y-%m-%d"),
        "best_product": by_product.index[0],
        "best_product_share_percent": round(by_product.iloc[0] / total_sales * 100, 1),
        "weakest_product": by_product.index[-1],
        "sales_by_product": {name: int(value) for name, value in by_product.items()},
        "best_region": by_region.index[0],
        "sales_by_region": {name: int(value) for name, value in by_region.items()},
    }
    return summary

SYNONYMS = {
    "date": ["date", "order date", "sale date", "day"],
    "product": ["product", "item", "item name", "product name"],
    "quantity": ["quantity", "qty", "units", "units sold"],
    "unit_price": ["unit_price", "unit price", "price", "price per unit"],
    "customer_region": ["customer_region", "region", "city", "location", "area"],
}


def guess_column(needed, columns):
    for column in columns:
        if str(column).strip().lower() in SYNONYMS[needed]:
            return column
    return None