import pandas as pd


def load_clean_data(path="data/sales_data.csv"):
    df = pd.read_csv(path)
    df = df.dropna(subset=["quantity"])
    df["quantity"] = df["quantity"].astype(int)
    df["revenue"] = df["quantity"] * df["unit_price"]
    df["date"] = pd.to_datetime(df["date"])
    return df