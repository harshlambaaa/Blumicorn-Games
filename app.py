import os
import pandas as pd
import streamlit as st

# ---------- Config ----------
st.set_page_config(
    page_title="Investment Portfolio Tracker",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = "data"
PLAYERS_CSV = os.path.join(DATA_DIR, "players.csv")
COMPANIES_CSV = os.path.join(DATA_DIR, "companies.csv")
PORTFOLIOS_CSV = os.path.join(DATA_DIR, "model_portfolios.csv")

# ---------- Constants ----------
DESIGNATIONS = [
    "Analyst/Sr. Analyst",
    "Associate",
    "AVP/VP",
    "Director",
    "Partner"
]

TEAMS = [
    "Core - DomesTech Pod",
    "Core - DeepTech Pod",
    "Core - FinTech Pod",
    "Core - SaaS/AI Pod",
    "Network Investments",
    "Growth Investments"
]

PIPELINE_STAGES = ["Showcase", "IC", "Wired"]

FOUNDER_ARCHETYPES = ["First-time", "Seasoned"]

SECTORS = ["DomesTech", "DeepTech", "FinTech", "SaaS/AI"]

COMPANY_STAGES = ["Formation", "Traction"]


# ---------- Helpers ----------
def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)


def load_csv(path: str, columns: list[str]) -> pd.DataFrame:
    ensure_data_dir()
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            for col in columns:
                if col not in df.columns:
                    df[col] = None
            return df[columns]
        except Exception:
            return pd.DataFrame(columns=columns)
    else:
        df = pd.DataFrame(columns=columns)
        df.to_csv(path, index=False)
        return df


def save_csv(df: pd.DataFrame, path: str):
    ensure_data_dir()
    df.to_csv(path, index=False)


def get_partners(players_df: pd.DataFrame) -> list[str]:
    """Get list of all partners"""
    partners = players_df[players_df["designation"] == "Partner"]["player_name"].dropna().tolist()
    return sorted(partners)


def get_all_players_names(players_df: pd.DataFrame) -> list[str]:
    """Get list of all player names"""
    return sorted(players_df["player_name"].dropna().tolist())


# ---------- Load data ----------
PLAYER_COLUMNS = ["player_id", "player_name", "designation", "team"]
COMPANY_COLUMNS = [
    "company_id", "company_name", "pipeline_stage", "founder_archetype",
    "sector", "company_stage", "lead", "co_lead", "deal_team"
]
PORTFOLIO_COLUMNS = [
    "player_id", "player_name", "designation", "companies"
]

players_df = load_csv(PLAYERS_CSV, PLAYER_COLUMNS)
companies_df = load_csv(COMPANIES_CSV, COMPANY_COLUMNS)
portfolios_df = load_csv(PORTFOLIOS_CSV, PORTFOLIO_COLUMNS)


# ---------- UI: Sidebar ----------
st.sidebar.title("📊 Investment Portfolio Tracker")
st.sidebar.markdown("---")
st.sidebar.subheader("Quick Statistics")

col1, col2 = st.sidebar.columns(2)
col1.metric("Team Members", len(players_df))
col2.metric("Companies", len(companies_df))

st.sidebar.markdown("---")
st.sidebar.caption("Use the tabs to navigate between different views and administration functions.")


# ---------- UI: Main Tabs ----------
tabs = st.tabs([
    "📈 Overview",
    "👥 Team Members",
    "🏢 Companies",
    "💼 Model Portfolios",
    "⚙️ Admin"
])


# ---------- Overview Tab ----------
with tabs[0]:
    st.title("Investment Portfolio Dashboard")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Team Members", len(players_df))
    with col2:
        st.metric("Total Companies", len(companies_df))
    with col3:
        partners_count = len(players_df[players_df["designation"] == "Partner"])
        st.metric("Partners", partners_count)
    with col4:
        portfolio_count = len(portfolios_df)
        st.metric("Portfolio Entries", portfolio_count)

    st.markdown("---")

    # Team breakdown
    if len(players_df):
        st.subheader("Team Composition")
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("**By Designation**")
            designation_counts = players_df["designation"].value_counts()
            st.dataframe(
                designation_counts.reset_index().rename(columns={"index": "Designation", "designation": "Count"}),
                use_container_width=True,
                hide_index=True
            )

        with col_b:
            st.markdown("**By Team**")
            team_counts = players_df["team"].value_counts()
            st.dataframe(
                team_counts.reset_index().rename(columns={"index": "Team", "team": "Count"}),
                use_container_width=True,
                hide_index=True
            )

    st.markdown("---")

    # Companies breakdown
    if len(companies_df):
        st.subheader("Portfolio Overview")
        col_c, col_d = st.columns(2)

        with col_c:
            st.markdown("**By Pipeline Stage**")
            stage_counts = companies_df["pipeline_stage"].value_counts()
            st.dataframe(
                stage_counts.reset_index().rename(columns={"index": "Stage", "pipeline_stage": "Count"}),
                use_container_width=True,
                hide_index=True
            )

        with col_d:
            st.markdown("**By Sector**")
            sector_counts = companies_df["sector"].value_counts()
            st.dataframe(
                sector_counts.reset_index().rename(columns={"index": "Sector", "sector": "Count"}),
                use_container_width=True,
                hide_index=True
            )


# ---------- Team Members Tab ----------
with tabs[1]:
    st.header("Team Members")

    if len(players_df):
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            designation_filter = st.selectbox(
                "Filter by Designation",
                options=["All"] + DESIGNATIONS
            )
        with col2:
            team_filter = st.selectbox(
                "Filter by Team",
                options=["All"] + TEAMS
            )

        filtered_players = players_df.copy()
        if designation_filter != "All":
            filtered_players = filtered_players[filtered_players["designation"] == designation_filter]
        if team_filter != "All":
            filtered_players = filtered_players[filtered_players["team"] == team_filter]

        st.dataframe(
            filtered_players,
            use_container_width=True,
            hide_index=True,
            column_config={
                "player_id": st.column_config.NumberColumn("ID", width="small"),
                "player_name": st.column_config.TextColumn("Name", width="medium"),
                "designation": st.column_config.TextColumn("Designation", width="medium"),
                "team": st.column_config.TextColumn("Team", width="large"),
            }
        )
    else:
        st.info("No team members yet. Add them from the **Admin** tab.")


# ---------- Companies Tab ----------
with tabs[2]:
    st.header("Companies")

    if len(companies_df):
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            pipeline_filter = st.selectbox(
                "Filter by Pipeline Stage",
                options=["All"] + PIPELINE_STAGES
            )
        with col2:
            sector_filter = st.selectbox(
                "Filter by Sector",
                options=["All"] + SECTORS
            )
        with col3:
            stage_filter = st.selectbox(
                "Filter by Company Stage",
                options=["All"] + COMPANY_STAGES
            )

        filtered_companies = companies_df.copy()
        if pipeline_filter != "All":
            filtered_companies = filtered_companies[filtered_companies["pipeline_stage"] == pipeline_filter]
        if sector_filter != "All":
            filtered_companies = filtered_companies[filtered_companies["sector"] == sector_filter]
        if stage_filter != "All":
            filtered_companies = filtered_companies[filtered_companies["company_stage"] == stage_filter]

        st.dataframe(
            filtered_companies,
            use_container_width=True,
            hide_index=True,
            column_config={
                "company_id": st.column_config.NumberColumn("ID", width="small"),
                "company_name": st.column_config.TextColumn("Company Name", width="medium"),
                "pipeline_stage": st.column_config.TextColumn("Pipeline Stage", width="small"),
                "founder_archetype": st.column_config.TextColumn("Founder Type", width="small"),
                "sector": st.column_config.TextColumn("Sector", width="small"),
                "company_stage": st.column_config.TextColumn("Stage", width="small"),
                "lead": st.column_config.TextColumn("Lead", width="medium"),
                "co_lead": st.column_config.TextColumn("Co-Lead", width="medium"),
                "deal_team": st.column_config.TextColumn("Deal Team", width="large"),
            }
        )
    else:
        st.info("No companies yet. Add them from the **Admin** tab.")


# ---------- Model Portfolios Tab ----------
with tabs[3]:
    st.header("Model Portfolios")

    if len(portfolios_df):
        # Filter by designation
        designation_filter = st.selectbox(
            "Filter by Designation",
            options=["All"] + DESIGNATIONS,
            key="portfolio_designation_filter"
        )

        filtered_portfolios = portfolios_df.copy()
        if designation_filter != "All":
            filtered_portfolios = filtered_portfolios[filtered_portfolios["designation"] == designation_filter]

        if len(filtered_portfolios):
            st.dataframe(
                filtered_portfolios,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "player_id": st.column_config.NumberColumn("ID", width="small"),
                    "player_name": st.column_config.TextColumn("Name", width="medium"),
                    "designation": st.column_config.TextColumn("Designation", width="medium"),
                    "companies": st.column_config.TextColumn("Companies", width="large"),
                }
            )
        else:
            st.info(f"No portfolio entries for {designation_filter}.")
    else:
        st.info("No model portfolio entries yet. Use **Admin → Manage Model Portfolios**.")


# ---------- Admin Tab ----------
with tabs[4]:
    st.header("Administration")

    admin_subtabs = st.tabs([
        "➕ Add Team Member",
        "➕ Add Company",
        "💼 Manage Model Portfolios"
    ])

    # --- Add Team Member ---
    with admin_subtabs[0]:
        st.subheader("Add Team Member")

        with st.form("add_player_form", clear_on_submit=True):
            player_name = st.text_input("Name *", placeholder="Enter full name")

            col1, col2 = st.columns(2)
            with col1:
                designation = st.selectbox("Designation *", options=DESIGNATIONS)
            with col2:
                team = st.selectbox("Team *", options=TEAMS)

            submitted = st.form_submit_button("➕ Add Team Member", use_container_width=True)

            if submitted:
                if not player_name.strip():
                    st.error("❌ Name is required.")
                else:
                    players_df = load_csv(PLAYERS_CSV, PLAYER_COLUMNS)
                    new_id = int(players_df["player_id"].max() + 1) if len(players_df) else 1

                    new_row = {
                        "player_id": new_id,
                        "player_name": player_name.strip(),
                        "designation": designation,
                        "team": team,
                    }

                    players_df = pd.concat([players_df, pd.DataFrame([new_row])], ignore_index=True)
                    save_csv(players_df, PLAYERS_CSV)
                    st.success(f"✅ Team member '{player_name}' added successfully!")
                    st.rerun()

    # --- Add Company ---
    with admin_subtabs[1]:
        st.subheader("Add Company")

        # Reload to get latest partners list
        current_players_df = load_csv(PLAYERS_CSV, PLAYER_COLUMNS)
        partners = get_partners(current_players_df)
        all_players = get_all_players_names(current_players_df)

        if not partners:
            st.warning("⚠️ No partners found. Please add at least one team member with 'Partner' designation first.")

        with st.form("add_company_form", clear_on_submit=True):
            company_name = st.text_input("Company Name *", placeholder="Enter company name")

            col1, col2, col3 = st.columns(3)
            with col1:
                pipeline_stage = st.selectbox("Pipeline Stage *", options=PIPELINE_STAGES)
            with col2:
                founder_archetype = st.selectbox("Founder Archetype *", options=FOUNDER_ARCHETYPES)
            with col3:
                company_stage = st.selectbox("Company Stage *", options=COMPANY_STAGES)

            sector = st.selectbox("Sector *", options=SECTORS)

            st.markdown("**Deal Team Configuration**")
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                lead = st.multiselect("Lead *", options=partners, help="Select partner(s) leading this deal")
            with col_b:
                co_lead = st.multiselect("Co-Lead", options=all_players, help="Select co-lead(s)")
            with col_c:
                deal_team = st.multiselect("Deal Team", options=all_players, help="Select deal team members")

            submitted = st.form_submit_button("➕ Add Company", use_container_width=True)

            if submitted:
                if not company_name.strip():
                    st.error("❌ Company name is required.")
                elif not lead:
                    st.error("❌ At least one lead is required.")
                else:
                    companies_df = load_csv(COMPANIES_CSV, COMPANY_COLUMNS)
                    new_id = int(companies_df["company_id"].max() + 1) if len(companies_df) else 1

                    new_row = {
                        "company_id": new_id,
                        "company_name": company_name.strip(),
                        "pipeline_stage": pipeline_stage,
                        "founder_archetype": founder_archetype,
                        "sector": sector,
                        "company_stage": company_stage,
                        "lead": ", ".join(lead),
                        "co_lead": ", ".join(co_lead) if co_lead else "",
                        "deal_team": ", ".join(deal_team) if deal_team else "",
                    }

                    companies_df = pd.concat([companies_df, pd.DataFrame([new_row])], ignore_index=True)
                    save_csv(companies_df, COMPANIES_CSV)
                    st.success(f"✅ Company '{company_name}' added successfully!")
                    st.rerun()

    # --- Manage Model Portfolios ---
    with admin_subtabs[2]:
        st.subheader("Manage Model Portfolios")

        current_players_df = load_csv(PLAYERS_CSV, PLAYER_COLUMNS)
        current_companies_df = load_csv(COMPANIES_CSV, COMPANY_COLUMNS)

        if not len(current_players_df) or not len(current_companies_df):
            st.warning("⚠️ You need at least one team member and one company to manage portfolios.")
        else:
            # Group players by designation for clean display
            st.markdown("**Assign companies to team members**")

            for designation in DESIGNATIONS:
                players_in_designation = current_players_df[
                    current_players_df["designation"] == designation
                ]

                if len(players_in_designation):
                    st.markdown(f"### {designation}")

                    for _, player in players_in_designation.iterrows():
                        with st.form(f"portfolio_form_{player['player_id']}", clear_on_submit=False):
                            st.markdown(f"**{player['player_name']}** — _{player['team']}_")

                            # Get current companies for this player
                            current_portfolio = portfolios_df[
                                portfolios_df["player_id"] == player["player_id"]
                            ]

                            current_companies_str = ""
                            if len(current_portfolio):
                                current_companies_str = current_portfolio.iloc[0]["companies"]

                            current_companies_list = []
                            if current_companies_str:
                                current_companies_list = [c.strip() for c in current_companies_str.split(",")]

                            # Multiselect for companies
                            company_options = sorted(current_companies_df["company_name"].dropna().tolist())
                            selected_companies = st.multiselect(
                                "Companies",
                                options=company_options,
                                default=current_companies_list,
                                key=f"companies_{player['player_id']}",
                                label_visibility="collapsed"
                            )

                            col_save, col_clear = st.columns([1, 1])
                            with col_save:
                                save_btn = st.form_submit_button("💾 Save", use_container_width=True)
                            with col_clear:
                                clear_btn = st.form_submit_button("🗑️ Clear", use_container_width=True)

                            if save_btn:
                                # Reload latest data
                                portfolios_df = load_csv(PORTFOLIOS_CSV, PORTFOLIO_COLUMNS)

                                # Remove existing entry for this player
                                portfolios_df = portfolios_df[portfolios_df["player_id"] != player["player_id"]]

                                # Add new entry if companies selected
                                if selected_companies:
                                    new_row = {
                                        "player_id": player["player_id"],
                                        "player_name": player["player_name"],
                                        "designation": player["designation"],
                                        "companies": ", ".join(selected_companies),
                                    }
                                    portfolios_df = pd.concat([portfolios_df, pd.DataFrame([new_row])], ignore_index=True)

                                save_csv(portfolios_df, PORTFOLIOS_CSV)
                                st.success(f"✅ Portfolio updated for {player['player_name']}")
                                st.rerun()

                            if clear_btn:
                                portfolios_df = load_csv(PORTFOLIOS_CSV, PORTFOLIO_COLUMNS)
                                portfolios_df = portfolios_df[portfolios_df["player_id"] != player["player_id"]]
                                save_csv(portfolios_df, PORTFOLIOS_CSV)
                                st.success(f"✅ Portfolio cleared for {player['player_name']}")
                                st.rerun()

                        st.markdown("---")
