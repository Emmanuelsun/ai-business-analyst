import json
import pandas as pd
import streamlit as st
import plotly.express as px
from data_tools import (
    REQUIRED_COLUMNS,
    read_uploaded_file,
    find_missing_columns,
    guess_column,
    clean_data,
    build_summary,
)
from ai_analyst import get_insights, find_unverified_numbers
from report import build_report_html
from auth_tools import (
    current_user_email,
    sign_in,
    sign_up,
    sign_out,
    save_report,
    list_reports,
    delete_report,
)

st.set_page_config(page_title="Sales Insights", page_icon="📊", layout="wide")

TEAL = "#00C2A8"
GITHUB_URL = "https://github.com/Emmanuelsun/ai-business-analyst"

EXAMPLE_INSIGHTS = """**Overview**
Between January 5, 2026, and January 15, 2026, you recorded 11 sales totaling 950,500 Nigerian Naira. Please note this data covers only a few days and a small number of sales, so it is too small to be sure about long-term trends.

**Key Insights**
* Rice 50kg was your best product, making up 45.7% of your total sales with 434,000 Nigerian Naira.
* Printer Paper was your weakest product, bringing in 44,000 Nigerian Naira.
* Lagos was your best region with 395,000 Nigerian Naira in sales.

**Practical Recommendations**
* Keep enough Rice 50kg in stock since it is your top seller.
* Look closely at why Printer Paper brought in the lowest amount to decide if you should restock it.
* Focus some extra attention on customers in Lagos, as they brought in the highest regional sales.
"""

st.markdown(
    """
    <style>
    .block-container { padding-top: 5rem; padding-bottom: 3rem; max-width: 1200px; }
    .hero {
        background: linear-gradient(135deg, #00C2A8 0%, #1B6EF3 100%);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 24px;
    }
    .hero-title { font-size: 2rem; font-weight: 700; color: #FFFFFF; line-height: 1.2; }
    .hero-sub { margin-top: 6px; color: #E6FFFB; }
    div[data-testid="stMetric"] {
        background: #141C2F;
        border: 1px solid #22304D;
        border-left: 4px solid #00C2A8;
        border-radius: 12px;
        padding: 14px 16px;
    }
    div[data-testid="stMetricValue"] { font-size: 1.6rem; }
    div[data-testid="stMetricValue"] > div {
        white-space: normal;
        overflow: visible;
        text-overflow: clip;
    }
    footer { visibility: hidden; }

    @media (max-width: 640px) {
        .block-container { padding-left: 1rem; padding-right: 1rem; padding-top: 4.5rem; }
        .hero { padding: 16px 18px; border-radius: 12px; }
        .hero-title { font-size: 1.4rem; }
        div[data-testid="stMetric"] { padding: 10px 12px; }
        div.stButton > button, div.stDownloadButton > button {
            width: 100%;
            min-height: 44px;
        }
    }
    </style>
    <div class="hero">
        <div class="hero-title">Sales Insights Dashboard</div>
        <div class="hero-sub">A clear view of how your business is performing.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption("Portfolio demo: please use sample or test data only, and a throwaway email if you sign up.")


def style_chart(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#E8EEF8",
        margin=dict(l=10, r=10, t=50, b=10),
    )
    fig.update_xaxes(showgrid=False, automargin=True)
    fig.update_yaxes(gridcolor="#22304D", automargin=True)
    return fig


top_left, top_right = st.columns(2)

with top_left:
    with st.container(border=True):
        st.subheader("Your data")
        uploaded = st.file_uploader(
            "Upload a sales file",
            type=["csv", "xlsx"],
            key=f"uploader_{st.session_state.get('uploader_version', 0)}",
        )
        st.caption("Your file needs these columns: date, product, quantity, unit_price, customer_region.")
        st.caption("Test data only, please. This is a demo.")

with top_right:
    with st.container(border=True):
        st.subheader("Account")
        user_email = current_user_email()
        if user_email:
            st.write(f"Signed in as **{user_email}**")
            if st.button("Log out"):
                sign_out()
                st.rerun()
        else:
            st.caption("Log in to save reports, see your history and generate AI insights.")
            login_tab, signup_tab = st.tabs(["Log in", "Sign up"])
            with login_tab:
                login_email = st.text_input("Email", key="login_email")
                login_password = st.text_input("Password", type="password", key="login_password")
                if st.button("Log in", key="login_button"):
                    ok, message = sign_in(login_email.strip(), login_password)
                    if ok:
                        st.rerun()
                    else:
                        st.error(message)
            with signup_tab:
                signup_email = st.text_input("Email", key="signup_email")
                signup_password = st.text_input(
                    "Password (at least 6 characters)", type="password", key="signup_password"
                )
                if st.button("Create account", key="signup_button"):
                    ok, message = sign_up(signup_email.strip(), signup_password)
                    if ok and current_user_email():
                        st.rerun()
                    elif ok:
                        st.success(message)
                    else:
                        st.error(message)
                st.caption("This is a portfolio demo. Please use a throwaway email and a password you do not use anywhere else.")
            st.caption("Saved reports are linked to your account and are not shown to other users.")

if uploaded is None:
    raw = pd.read_csv("data/sales_data.csv")
    st.info("You are viewing sample data. Upload your own file in the box above to analyse your business.")
else:
    try:
        raw = read_uploaded_file(uploaded)
    except Exception:
        st.error("We could not read this file. Please upload a valid CSV or Excel (.xlsx) file.")
        st.stop()

raw.columns = [str(c).strip() for c in raw.columns]

missing = find_missing_columns(raw)
if missing:
    st.warning("Your column names are different from ours. Please check that each one below is matched correctly.")

    options = ["Choose a column"] + [c for c in raw.columns if c not in REQUIRED_COLUMNS]
    choices = {}
    for needed in missing:
        guess = guess_column(needed, raw.columns)
        index = options.index(guess) if guess in options else 0
        choices[needed] = st.selectbox(
            f"Which column is '{needed}'?", options, index=index, key=f"map_{needed}"
        )

    picked = list(choices.values())
    if "Choose a column" in picked:
        st.info("Please choose a column for each item above to continue.")
        st.stop()
    if len(set(picked)) < len(picked):
        st.error("The same column was chosen twice. Please choose a different column for each item.")
        st.stop()

    raw = raw.rename(columns={choice: needed for needed, choice in choices.items()})

df = clean_data(raw)

if df.empty:
    st.error("No usable rows were found in this file.")
    st.stop()

removed = len(raw) - len(df)
if removed > 0:
    st.warning(f"{removed} row(s) were left out because they had missing or invalid values.")

summary = build_summary(df)

data_key = json.dumps(summary, sort_keys=True)
if st.session_state.get("data_key") != data_key:
    st.session_state["data_key"] = data_key
    st.session_state.pop("insights", None)
    st.session_state.pop("problems", None)

card1, card2, card3, card4 = st.columns(4)
card1.metric("Total sales", f"₦{summary['total_sales_naira']:,}")
card2.metric("Orders", summary["number_of_sales"])
card3.metric("Top product", summary["best_product"])
card4.metric("Top city", summary["best_region"])

by_product = df.groupby("product")["revenue"].sum().reset_index()
by_product = by_product.sort_values("revenue", ascending=False)

by_region = df.groupby("customer_region")["revenue"].sum().reset_index()
by_region = by_region.sort_values("revenue", ascending=False)

by_day = df.groupby("date")["revenue"].sum().reset_index()

tab_overview, tab_trends, tab_ai, tab_data, tab_history = st.tabs(
    ["Overview", "Trends", "AI Insights", "Data", "History"]
)

with tab_overview:
    left, right = st.columns(2)
    with left:
        fig_product = px.bar(
            by_product, x="product", y="revenue", title="Sales by product",
            labels={"product": "Product", "revenue": "Revenue (₦)"},
            color_discrete_sequence=[TEAL], text_auto=".3s",
        )
        st.plotly_chart(style_chart(fig_product), theme=None)
    with right:
        fig_region = px.bar(
            by_region, x="customer_region", y="revenue", title="Sales by city",
            labels={"customer_region": "City", "revenue": "Revenue (₦)"},
            color_discrete_sequence=[TEAL], text_auto=".3s",
        )
        st.plotly_chart(style_chart(fig_region), theme=None)

with tab_trends:
    fig_day = px.line(
        by_day, x="date", y="revenue", markers=True, title="Sales day by day",
        labels={"date": "Date", "revenue": "Revenue (₦)"},
        color_discrete_sequence=[TEAL],
    )
    st.plotly_chart(style_chart(fig_day), theme=None)
    st.caption("Short periods show a snapshot, not a long-term trend.")

with tab_ai:
    st.subheader("AI insights")
    if not current_user_email():
        if uploaded is None:
            st.info("Log in to generate fresh AI insights. Here is an example that was generated earlier from the sample data.")
            st.markdown(EXAMPLE_INSIGHTS)
            st.caption("Example only. Every figure in it was checked against the sample data. Log in to generate your own.")
        else:
            st.info("Log in from the Account box at the top to generate AI insights for your file.")
    else:
        st.write("Press the button to get a short written summary of your numbers.")
        st.caption("Only a summary of totals is sent to the AI, never your full file.")

        if st.button("Generate insights"):
            with st.spinner("Reading your numbers..."):
                text = get_insights(summary)
                st.session_state["insights"] = text
                st.session_state["problems"] = find_unverified_numbers(text, summary)

        if "insights" in st.session_state:
            text = st.session_state["insights"]
            if text.startswith(("The AI could not", "No API key")):
                st.error(text)
            else:
                st.markdown(text)
                if st.session_state["problems"]:
                    st.warning(
                        "Some figures could not be matched to your data: "
                        + ", ".join(st.session_state["problems"])
                    )
                else:
                    st.success("Every figure in this summary was checked against your data.")
                st.caption("Insights are written by AI from your data. Please review them before making business decisions.")

with tab_data:
    table = df.copy()
    table["date"] = table["date"].dt.date
    st.dataframe(table, hide_index=True)

with tab_history:
    st.subheader("Your saved reports")
    if not current_user_email():
        st.info("Log in from the Account box at the top to see and keep your past reports.")
    else:
        saved = list_reports()
        if not saved:
            st.write("You have no saved reports yet. Use 'Save report to my history' at the bottom of the page.")
        for item in saved:
            when = item["created_at"][:16].replace("T", " ")
            col_a, col_b, col_c = st.columns([5, 2, 1])
            col_a.write(f"**{item['title']}**  \n{when} UTC")
            col_b.download_button(
                "Download",
                data=item["html"],
                file_name=f"report_{item['id']}.html",
                mime="text/html",
                key=f"dl_{item['id']}",
            )
            if col_c.button("Delete", key=f"del_{item['id']}"):
                delete_report(item["id"])
                st.rerun()

report_insights = st.session_state.get("insights")
if report_insights and report_insights.startswith(("The AI could not", "No API key")):
    report_insights = None

report_html = build_report_html(summary, report_insights, st.session_state.get("problems"))

with st.container(border=True):
    st.subheader("Your report")
    st.caption("Download a summary you can keep, print or share. If you generated AI insights, they are included.")

    flash = st.session_state.pop("flash", None)
    if flash:
        st.success(flash)

    btn_a, btn_b = st.columns(2)
    with btn_a:
        st.download_button(
            "Download report",
            data=report_html,
            file_name="sales_report.html",
            mime="text/html",
        )
    with btn_b:
        if current_user_email():
            if st.button("Save report to my history"):
                title = f"Sales report {summary['first_date']} to {summary['last_date']}"
                ok, message = save_report(title, report_html)
                if ok:
                    st.session_state["flash"] = message
                    st.rerun()
                else:
                    st.error(message)
        else:
            st.caption("Log in to save reports to your history.")

st.divider()
st.caption(
    f"Portfolio project built with Python, Pandas, Plotly, Streamlit, Gemini and Supabase. "
    f"[Source code on GitHub]({GITHUB_URL})"
)