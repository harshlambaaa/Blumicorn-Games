
import os
import pandas as pd
import streamlit as st

# ---------- Config ----------
st.set_page_config(
    page_title="Blu Funnel Games Dashboard",
    layout="wide",
)

DATA_DIR = "data"
PLAYERS_CSV = os.path.join(DATA_DIR, "players.csv")
COMPANIES_CSV = os.path.join(DATA_DIR, "companies.csv")
PORTFOLIOS_CSV = os.path.join(DATA_DIR, "model_portfolios.csv")


# ---------- Helpers ----------
def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)


def load_csv(path: str, columns: list[str]) -> pd.DataFrame:
    ensure_data_dir()
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            # Ensure all expected columns exist
            for col in columns:
                if col not in df.columns:
                    df[col] = None
            return df[columns]
        except Exception:
            # Fall back to empty frame if corrupted
            return pd.DataFrame(columns=columns)
    else:
        df = pd.DataFrame(columns=columns)
        df.to_csv(path, index=False)
        return df


def save_csv(df: pd.DataFrame, path: str):
    ensure_data_dir()
    df.to_csv(path, index=False)


# ---------- Load data ----------
PLAYER_COLUMNS = ["player_id", "player_name", "coach", "batch", "status"]
COMPANY_COLUMNS = ["company_id", "company_name", "sector", "notes"]
PORTFOLIO_COLUMNS = ["player_id", "player_name", "company_id", "company_name", "allocation_pct", "notes"]

players_df = load_csv(PLAYERS_CSV, PLAYER_COLUMNS)
companies_df = load_csv(COMPANIES_CSV, COMPANY_COLUMNS)
portfolios_df = load_csv(PORTFOLIOS_CSV, PORTFOLIO_COLUMNS)


# ---------- UI: Sidebar ----------
st.sidebar.title("Blu Funnel Games")
st.sidebar.markdown("Use the tabs on the main page to navigate the dashboard and admin tools.")
st.sidebar.markdown("---")
st.sidebar.subheader("Quick stats")

col1, col2, col3 = st.sidebar.columns(3)
col1.metric("Players", len(players_df))
col2.metric("Companies", len(companies_df))
col3.metric("Holdings", len(portfolios_df))


# ---------- UI: Main Tabs ----------
tabs = st.tabs(
    [
        "Overview",
        "Players",
        "Companies",
        "Model Portfolios",
        "Admin",
    ]
)

# ---------- Overview Tab ----------
with tabs[0]:
    st.title("Blu Funnel Games Dashboard")
    st.markdown(
        """
        This dashboard lets you track players, companies, and their model portfolios.
        Use the **Admin** tab to add or edit data, which is saved as CSV files in the repository.
        """
    )

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Players snapshot")
        if len(players_df):
            st.dataframe(players_df, use_container_width=True)
        else:
            st.info("No players yet. Add some from the **Admin → Add Player** section.")

    with col_b:
        st.subheader("Companies snapshot")
        if len(companies_df):
            st.dataframe(companies_df, use_container_width=True)
        else:
            st.info("No companies yet. Add some from the **Admin → Add Company** section.")

    st.markdown("---")
    st.subheader("Model portfolio snapshot")
    if len(portfolios_df):
        st.dataframe(portfolios_df, use_container_width=True)
    else:
        st.info("No model portfolio entries yet. Use **Admin → Add to Model Portfolio**.")


# ---------- Players Tab ----------
with tabs[1]:
    st.header("Players")
    if len(players_df):
        st.dataframe(players_df, use_container_width=True)
    else:
        st.info("No players yet. Add them from the **Admin** tab.")


# ---------- Companies Tab ----------
with tabs[2]:
    st.header("Companies")
    if len(companies_df):
        st.dataframe(companies_df, use_container_width=True)
    else:
        st.info("No companies yet. Add them from the **Admin** tab.")


# ---------- Model Portfolios Tab ----------
with tabs[3]:
    st.header("Model Portfolios")

    if len(portfolios_df):
        # Simple filters
        filter_cols = st.columns(3)
        with filter_cols[0]:
            player_filter = st.selectbox(
                "Filter by player",
                options=["All"] + sorted(players_df["player_name"].dropna().unique().tolist())
            )
        with filter_cols[1]:
            company_filter = st.selectbox(
                "Filter by company",
                options=["All"] + sorted(companies_df["company_name"].dropna().unique().tolist())
            )
        with filter_cols[2]:
            min_alloc = st.number_input("Min allocation %", min_value=0.0, max_value=100.0, value=0.0, step=1.0)

        filtered = portfolios_df.copy()

        if player_filter != "All":
            filtered = filtered[filtered["player_name"] == player_filter]

        if company_filter != "All":
            filtered = filtered[filtered["company_name"] == company_filter]

        filtered = filtered[filtered["allocation_pct"].fillna(0) >= min_alloc]

        st.dataframe(filtered, use_container_width=True)
    else:
        st.info("No model portfolio entries yet. Use **Admin → Add to Model Portfolio**.")


# ---------- Admin Tab ----------
with tabs[4]:
    st.header("Admin")

    st.markdown(
        """
        Use these tools to maintain the master data.  
        Changes are saved to CSV files inside the `data/` folder so they can be committed to Git.
        """
    )

    admin_subtabs = st.tabs(
        [
            "Add Player",
            "Add Company",
            "Add to Model Portfolio",
        ]
    )

    # --- Add Player ---
    with admin_subtabs[0]:
        st.subheader("Add Player")

        with st.form("add_player_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                player_name = st.text_input("Player name *")
                coach = st.text_input("Coach / Owner")
            with col2:
                batch = st.text_input("Batch / Cohort (e.g. 'Jan', 'Feb')")
                status = st.text_input("Status (e.g. 'Core', 'Tracking')")

            submitted = st.form_submit_button("Save player")
            if submitted:
                if not player_name.strip():
                    st.error("Player name is required.")
                else:
                    # Reload latest
                    players_df = load_csv(PLAYERS_CSV, PLAYER_COLUMNS)
                    new_id = (players_df["player_id"].max() + 1) if len(players_df) else 1
                    new_row = {
                        "player_id": new_id,
                        "player_name": player_name.strip(),
                        "coach": coach.strip() if coach else "",
                        "batch": batch.strip() if batch else "",
                        "status": status.strip() if status else "",
                    }
                    players_df = pd.concat([players_df, pd.DataFrame([new_row])], ignore_index=True)
                    save_csv(players_df, PLAYERS_CSV)
                    st.success(f"Player '{player_name}' added with ID {new_id}.")
                    st.experimental_rerun()

    # --- Add Company ---
    with admin_subtabs[1]:
        st.subheader("Add Company")

        with st.form("add_company_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                company_name = st.text_input("Company name *")
                sector = st.text_input("Sector / Category")
            with col2:
                notes = st.text_area("Notes", height=80)

            submitted = st.form_submit_button("Save company")
            if submitted:
                if not company_name.strip():
                    st.error("Company name is required.")
                else:
                    companies_df = load_csv(COMPANIES_CSV, COMPANY_COLUMNS)
                    new_id = (companies_df["company_id"].max() + 1) if len(companies_df) else 1
                    new_row = {
                        "company_id": new_id,
                        "company_name": company_name.strip(),
                        "sector": sector.strip() if sector else "",
                        "notes": notes.strip() if notes else "",
                    }
                    companies_df = pd.concat([companies_df, pd.DataFrame([new_row])], ignore_index=True)
                    save_csv(companies_df, COMPANIES_CSV)
                    st.success(f"Company '{company_name}' added with ID {new_id}.")
                    st.experimental_rerun()

    # --- Add to Model Portfolio ---
    with admin_subtabs[2]:
        st.subheader("Add company to a player's model portfolio")

        if not len(players_df) or not len(companies_df):
            st.warning("You need at least one player and one company before adding to a model portfolio.")
        else:
            with st.form("add_portfolio_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    player_name_sel = st.selectbox(
                        "Player *",
                        options=sorted(players_df["player_name"].dropna().unique().tolist()),
                    )
                    company_name_sel = st.selectbox(
                        "Company *",
                        options=sorted(companies_df["company_name"].dropna().unique().tolist()),
                    )
                with col2:
                    allocation_pct = st.number_input(
                        "Allocation %",
                        min_value=0.0,
                        max_value=100.0,
                        value=5.0,
                        step=0.5,
                    )
                    notes = st.text_area("Notes", height=80)

                submitted = st.form_submit_button("Save to portfolio")
                if submitted:
                    # Reload latest
                    players_df = load_csv(PLAYERS_CSV, PLAYER_COLUMNS)
                    companies_df = load_csv(COMPANIES_CSV, COMPANY_COLUMNS)
                    portfolios_df = load_csv(PORTFOLIOS_CSV, PORTFOLIO_COLUMNS)

                    player_row = players_df[players_df["player_name"] == player_name_sel].iloc[0]
                    company_row = companies_df[companies_df["company_name"] == company_name_sel].iloc[0]

                    new_row = {
                        "player_id": player_row["player_id"],
                        "player_name": player_row["player_name"],
                        "company_id": company_row["company_id"],
                        "company_name": company_row["company_name"],
                        "allocation_pct": allocation_pct,
                        "notes": notes.strip() if notes else "",
                    }

                    portfolios_df = pd.concat([portfolios_df, pd.DataFrame([new_row])], ignore_index=True)
                    save_csv(portfolios_df, PORTFOLIOS_CSV)

                    st.success(
                        f"Added {company_name_sel} to {player_name_sel}'s model portfolio "
                        f"with allocation {allocation_pct}%."
                    )
                    st.experimental_rerun()
