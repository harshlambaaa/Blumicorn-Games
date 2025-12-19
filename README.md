
# Blu Funnel Games Dashboard

A simple Streamlit-based dashboard for Blu Funnel Games that:

- Uses **tabs** instead of separate pages for navigation.
- Has an **Admin** section where you can:
  - Add players.
  - Add companies.
  - Add companies to players' model portfolios.
- Persists all admin data to CSV files in the `data/` folder so it can be committed to your GitHub repository.

## Project Structure

```text
blu_funnel_games_dashboard/
├─ app.py
├─ requirements.txt
├─ data/
│  ├─ players.csv
│  ├─ companies.csv
│  └─ model_portfolios.csv
```

The CSV files are auto-created on first run if they don't exist.

## Running Locally

1. Create and activate a virtual environment (optional but recommended).
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   streamlit run app.py
   ```

4. Open the URL that Streamlit prints in your terminal.
