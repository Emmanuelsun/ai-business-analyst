from data_tools import load_clean_data, build_summary
from ai_analyst import get_insights, find_unverified_numbers

df = load_clean_data()
summary = build_summary(df)

insights = get_insights(summary)
print(insights)

problems = find_unverified_numbers(insights, summary)

print("\n--- Number check ---")
if problems:
    print("Warning: these numbers are not in our facts:", problems)
else:
    print("All numbers in the advice match our facts.")