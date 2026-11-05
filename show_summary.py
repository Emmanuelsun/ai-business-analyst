import json
from data_tools import load_clean_data, build_summary

df = load_clean_data()
summary = build_summary(df)

print(json.dumps(summary, indent=2))