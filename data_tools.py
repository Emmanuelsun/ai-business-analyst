import pandas as pd


def load_clean_data(path="data/sales_data.csv"):
    df = pd.read_csv(path)
    df = df.dropna(subset=["quantity"])
    df["quantity"] = df["quantity"].astype(int)
    df["revenue"] = df["quantity"] * df["unit_price"]
    df["date"] = pd.to_datetime(df["date"])
    return df

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