# AI Business Data Analyst

A web app that helps small business owners understand their sales. The owner uploads a sales file and gets a clean dashboard, interactive charts, plain-language insights written by an AI, and a downloadable report. Signed-in users can save reports and download them again later.

## What it does

- Reads sales data from **CSV or Excel** files
- Checks the file for the columns it needs, and lets the owner **match different column names** (for example "Qty" to "quantity")
- Cleans the data and tells the owner how many rows were left out
- Shows **total sales, number of orders, top product and top city**
- Draws **interactive charts**: sales by product, sales by city, and sales day by day
- Lets signed-in users generate a short **AI summary** of their numbers
- **Checks every number the AI writes** against the figures calculated in Python, and warns if one does not match
- Lets anyone **download a report**
- Lets signed-in users **save reports to a private history** and download or delete them later
- Works on **phones**: the layout stacks on small screens and all controls are on the main page

## Key design rules

**Python calculates every number. The AI only explains them.** The AI never sees the full sales file. It receives only a small summary of totals, and any number it writes that is not in that summary is flagged.

**Each user only sees their own saved reports.** Accounts and saved reports are stored in Supabase, and row level security rules let a signed-in user read, add and delete only their own rows.

## Built with

Python, Pandas, NumPy, Plotly, Matplotlib, Streamlit, Google Gemini API, Supabase (authentication and database), pytest, Git and GitHub.

## How to run it

1. Install Python 3.13 and create a virtual environment:

   ```
   py -3.13 -m venv venv
   venv\Scripts\Activate.ps1
   ```

2. Install the requirements:

   ```
   python -m pip install -r requirements.txt
   ```

3. Create a free [Google AI Studio](https://aistudio.google.com/apikey) key and a free [Supabase](https://supabase.com) project.

4. In Supabase, open the SQL editor and create the `reports` table with row level security. The SQL is in `supabase_setup.sql`.

5. Save your settings in a file called `.env` in the project folder. Never share this file or upload it to GitHub:

   ```
   GEMINI_API_KEY=your-gemini-key
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_KEY=your-supabase-publishable-key
   ```

6. Start the app:

   ```
   streamlit run app.py
   ```

Sample data is included in `data/sales_data.csv`.

## Project files

| File | Purpose |
|---|---|
| `app.py` | The Streamlit web app |
| `data_tools.py` | Reading, checking and cleaning data, and building the summary |
| `ai_analyst.py` | Asks the AI for insights and checks its numbers |
| `auth_tools.py` | Sign up, log in, and saving, listing and deleting reports |
| `report.py` | Builds the downloadable report |
| `test_calculations.py` | Automated tests for the calculations |
| `.streamlit/config.toml` | Colour theme |
| `supabase_setup.sql` | Database setup |
| `data/` | Sample sales files |

## Run the tests

```
python -m pytest -v
```

## Limitations

- The file must contain date, product, quantity, unit price and city information.
- Rows with missing or invalid values are left out.
- Short periods of data show a snapshot, not a long-term trend.
- The free Gemini tier has usage limits, and Google may use free-tier requests to improve its products. Use a paid key for real business data.
- Model names change over time. If the AI step fails with "model not found", update the model name in `ai_analyst.py`.
- For testing, email confirmation is switched off in Supabase. Before real users sign up, set up a proper email sender and switch confirmation back on.
- Saved reports contain business figures and are stored on Supabase's servers.

## What I learned

Built over several days while learning Python: data cleaning with Pandas, charts with Plotly, calling an AI API, protecting API keys with environment variables, user accounts and database security rules, responsive layout, testing, and version control with Git.