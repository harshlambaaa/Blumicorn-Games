import os
import pandas as pd
import streamlit as st
import subprocess
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ---------- Config ----------
st.set_page_config(
    page_title="Dashboard | Blu Funnel Games",
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

CHEQUE_OPTIONS = ["Core", "Traction"]


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


def save_to_github() -> tuple[bool, str]:
    """Commit and push data changes to GitHub"""
    try:
        # Add data files
        subprocess.run(["git", "add", "data/*.csv"], check=True, capture_output=True, text=True)

        # Check if there are changes to commit
        status = subprocess.run(["git", "status", "--porcelain", "data/"], capture_output=True, text=True)
        if not status.stdout.strip():
            return False, "No changes to save"

        # Commit with timestamp
        commit_msg = f"Update portfolio data - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True, capture_output=True, text=True)

        # Push to remote
        subprocess.run(["git", "push"], check=True, capture_output=True, text=True, timeout=30)

        return True, "Data saved to GitHub successfully!"
    except subprocess.TimeoutExpired:
        return False, "Push timed out. Please check your connection."
    except subprocess.CalledProcessError as e:
        return False, f"Git error: {e.stderr if e.stderr else 'Unknown error'}"
    except Exception as e:
        return False, f"Error: {str(e)}"


# ---------- Load data ----------
PLAYER_COLUMNS = ["player_id", "player_name", "designation", "team"]
COMPANY_COLUMNS = [
    "company_id", "company_name", "pipeline_stage", "founder_archetype",
    "sector", "company_stage", "cheque", "lead", "co_lead", "deal_team"
]
PORTFOLIO_COLUMNS = [
    "player_id", "player_name", "designation", "companies"
]

players_df = load_csv(PLAYERS_CSV, PLAYER_COLUMNS)
companies_df = load_csv(COMPANIES_CSV, COMPANY_COLUMNS)
portfolios_df = load_csv(PORTFOLIOS_CSV, PORTFOLIO_COLUMNS)


# ---------- UI: Sidebar ----------
st.sidebar.title("📊 Blu Funnel Games")
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
    "💡 Insights",
    "⚙️ Admin"
])


# ---------- Overview Tab ----------
with tabs[0]:
    st.title("Overview")

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
                "cheque": st.column_config.TextColumn("Cheque", width="small"),
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


# ---------- Insights Tab ----------
with tabs[4]:
    st.header("💡 Deal Fantasy League Insights")

    # Prepare vote data from portfolios
    if len(portfolios_df) == 0 or len(companies_df) == 0:
        st.info("📊 Add companies and model portfolios to see insights.")
    else:
        # Create vote matrix: which players voted for which companies
        vote_data = []
        for _, portfolio in portfolios_df.iterrows():
            player_id = portfolio['player_id']
            player_name = portfolio['player_name']
            designation = portfolio['designation']
            companies_str = portfolio['companies']

            if pd.notna(companies_str) and companies_str:
                voted_companies = [c.strip() for c in companies_str.split(',')]
                for company in voted_companies:
                    vote_data.append({
                        'player_id': player_id,
                        'player_name': player_name,
                        'designation': designation,
                        'company_name': company
                    })

        votes_df = pd.DataFrame(vote_data)

        # Merge with company data to get pipeline stages, leads, etc.
        if len(votes_df) > 0:
            votes_df = votes_df.merge(
                companies_df[['company_name', 'pipeline_stage', 'sector', 'cheque', 'lead', 'co_lead']],
                on='company_name',
                how='left'
            )

        # Merge players with designation/team info
        if len(votes_df) > 0:
            votes_df = votes_df.merge(
                players_df[['player_name', 'team']],
                on='player_name',
                how='left'
            )

        # ====================
        # SECTION 1: Overview Metrics
        # ====================
        st.subheader("📊 Overview Metrics")

        total_votes = len(votes_df) if len(votes_df) > 0 else 0
        total_companies = len(companies_df)
        total_players = len(players_df)

        # Calculate companies with votes
        if len(votes_df) > 0:
            companies_with_votes = votes_df['company_name'].nunique()
            companies_with_zero_votes = total_companies - companies_with_votes
            avg_votes_per_company = votes_df.groupby('company_name').size().mean() if len(votes_df) > 0 else 0
        else:
            companies_with_votes = 0
            companies_with_zero_votes = total_companies
            avg_votes_per_company = 0

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Votes Cast", total_votes)
        col2.metric("Companies in Pipeline", total_companies)
        col3.metric("Players Participating", total_players)
        col4.metric("Avg Votes per Company", f"{avg_votes_per_company:.1f}")
        col5.metric("Companies with Zero Votes", companies_with_zero_votes, delta=None if companies_with_zero_votes == 0 else f"-{companies_with_zero_votes}", delta_color="inverse")

        st.markdown("---")

        if len(votes_df) == 0:
            st.info("No votes cast yet. Assign companies to team members in Model Portfolios to see insights.")
        else:
            # ====================
            # SECTION 2: Vote Distribution Analysis
            # ====================
            st.subheader("📈 Vote Distribution Analysis")
            st.caption("Understanding which companies are getting the most attention from the team")

            # Calculate votes per company
            company_votes = votes_df.groupby('company_name').size().reset_index(name='votes')
            company_votes = company_votes.sort_values('votes', ascending=False)

            # Add companies with zero votes
            all_companies = companies_df[['company_name']].copy()
            all_companies = all_companies.merge(company_votes, on='company_name', how='left')
            all_companies['votes'] = all_companies['votes'].fillna(0).astype(int)
            all_companies = all_companies.sort_values('votes', ascending=False)

            col_a, col_b = st.columns(2)

            with col_a:
                # Donut chart
                fig_donut = go.Figure(data=[go.Pie(
                    labels=all_companies['company_name'],
                    values=all_companies['votes'],
                    hole=0.4,
                    marker=dict(colors=px.colors.sequential.Blues_r),
                    textinfo='label+percent',
                    hovertemplate='<b>%{label}</b><br>Votes: %{value}<br>Percentage: %{percent}<extra></extra>'
                )])
                fig_donut.update_layout(
                    title=f"Vote Distribution Across Companies<br><sub>Total Votes: {total_votes}</sub>",
                    showlegend=False,
                    height=400
                )
                st.plotly_chart(fig_donut, use_container_width=True)

            with col_b:
                # Horizontal bar chart
                fig_bar = px.bar(
                    all_companies,
                    y='company_name',
                    x='votes',
                    orientation='h',
                    title='Companies Ranked by Votes',
                    color='votes',
                    color_continuous_scale='Blues',
                    labels={'votes': 'Number of Votes', 'company_name': 'Company'}
                )
                fig_bar.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig_bar, use_container_width=True)

            st.markdown("---")

            # ====================
            # SECTION 3: Pipeline Stage Analysis
            # ====================
            st.subheader("🎯 Pipeline Stage Analysis")
            st.caption("How votes are distributed across different pipeline stages")

            # Merge companies with votes
            stage_analysis = companies_df.merge(
                all_companies[['company_name', 'votes']],
                on='company_name',
                how='left'
            )
            stage_analysis['votes'] = stage_analysis['votes'].fillna(0)

            col_c, col_d = st.columns(2)

            with col_c:
                # Count companies per stage
                stage_counts = stage_analysis.groupby('pipeline_stage').size().reset_index(name='count')
                stage_order = ['Showcase', 'IC', 'Wired']
                stage_counts['pipeline_stage'] = pd.Categorical(stage_counts['pipeline_stage'], categories=stage_order, ordered=True)
                stage_counts = stage_counts.sort_values('pipeline_stage')

                fig_stage_count = px.area(
                    stage_counts,
                    x='pipeline_stage',
                    y='count',
                    title='Number of Companies at Each Stage',
                    labels={'pipeline_stage': 'Pipeline Stage', 'count': 'Number of Companies'},
                    markers=True,
                    color_discrete_sequence=['#1f77b4']
                )
                fig_stage_count.update_layout(height=350)
                st.plotly_chart(fig_stage_count, use_container_width=True)

            with col_d:
                # Average votes by stage
                stage_votes_avg = stage_analysis.groupby('pipeline_stage')['votes'].mean().reset_index()
                stage_votes_avg['pipeline_stage'] = pd.Categorical(stage_votes_avg['pipeline_stage'], categories=stage_order, ordered=True)
                stage_votes_avg = stage_votes_avg.sort_values('pipeline_stage')

                fig_stage_votes = px.bar(
                    stage_votes_avg,
                    x='pipeline_stage',
                    y='votes',
                    title='Average Votes by Pipeline Stage',
                    labels={'pipeline_stage': 'Pipeline Stage', 'votes': 'Avg Votes'},
                    color='votes',
                    color_continuous_scale='Blues'
                )
                fig_stage_votes.update_layout(height=350, showlegend=False)
                st.plotly_chart(fig_stage_votes, use_container_width=True)

            # Box plot for vote distribution by stage
            fig_box = px.box(
                stage_analysis,
                x='pipeline_stage',
                y='votes',
                title='Vote Distribution Statistics by Pipeline Stage',
                labels={'pipeline_stage': 'Pipeline Stage', 'votes': 'Votes'},
                color='pipeline_stage',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_box.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig_box, use_container_width=True)

            st.markdown("---")

            # ====================
            # SECTION 4: Lead & Co-Lead Performance
            # ====================
            st.subheader("👔 Lead & Co-Lead Performance")
            st.caption("How deals led by different partners are performing in votes")

            # Parse leads and co-leads (they're comma-separated)
            lead_votes = []
            for _, row in stage_analysis.iterrows():
                if pd.notna(row['lead']) and row['lead']:
                    leads = [l.strip() for l in row['lead'].split(',')]
                    for lead in leads:
                        lead_votes.append({
                            'lead': lead,
                            'pipeline_stage': row['pipeline_stage'],
                            'votes': row['votes'],
                            'company': row['company_name']
                        })

            if lead_votes:
                lead_votes_df = pd.DataFrame(lead_votes)

                col_e, col_f = st.columns(2)

                with col_e:
                    # Stagewise vote distribution for leads
                    lead_stage_votes = lead_votes_df.groupby(['lead', 'pipeline_stage'])['votes'].mean().reset_index()
                    lead_stage_votes['pipeline_stage'] = pd.Categorical(lead_stage_votes['pipeline_stage'], categories=stage_order, ordered=True)

                    fig_lead_stage = px.bar(
                        lead_stage_votes,
                        x='votes',
                        y='lead',
                        color='pipeline_stage',
                        orientation='h',
                        title='Average Votes by Lead (Stagewise)',
                        labels={'votes': 'Avg Votes', 'lead': 'Lead'},
                        color_discrete_sequence=px.colors.qualitative.Set2,
                        barmode='group'
                    )
                    fig_lead_stage.update_layout(height=400)
                    st.plotly_chart(fig_lead_stage, use_container_width=True)

                with col_f:
                    # Overall average votes by lead
                    lead_overall = lead_votes_df.groupby('lead')['votes'].mean().reset_index()
                    lead_overall = lead_overall.sort_values('votes', ascending=True)

                    fig_lead_overall = px.bar(
                        lead_overall,
                        x='votes',
                        y='lead',
                        orientation='h',
                        title='Average Votes by Lead (Overall)',
                        labels={'votes': 'Avg Votes', 'lead': 'Lead'},
                        color='votes',
                        color_continuous_scale='Blues'
                    )
                    fig_lead_overall.update_layout(height=400, showlegend=False)
                    st.plotly_chart(fig_lead_overall, use_container_width=True)

            # Co-Lead analysis
            co_lead_votes = []
            for _, row in stage_analysis.iterrows():
                if pd.notna(row['co_lead']) and row['co_lead']:
                    co_leads = [c.strip() for c in row['co_lead'].split(',')]
                    for co_lead in co_leads:
                        co_lead_votes.append({
                            'co_lead': co_lead,
                            'pipeline_stage': row['pipeline_stage'],
                            'votes': row['votes'],
                            'company': row['company_name']
                        })

            if co_lead_votes:
                co_lead_votes_df = pd.DataFrame(co_lead_votes)

                col_g, col_h = st.columns(2)

                with col_g:
                    # Stagewise vote distribution for co-leads
                    co_lead_stage_votes = co_lead_votes_df.groupby(['co_lead', 'pipeline_stage'])['votes'].mean().reset_index()
                    co_lead_stage_votes['pipeline_stage'] = pd.Categorical(co_lead_stage_votes['pipeline_stage'], categories=stage_order, ordered=True)

                    fig_co_lead_stage = px.bar(
                        co_lead_stage_votes,
                        x='votes',
                        y='co_lead',
                        color='pipeline_stage',
                        orientation='h',
                        title='Average Votes by Co-Lead (Stagewise)',
                        labels={'votes': 'Avg Votes', 'co_lead': 'Co-Lead'},
                        color_discrete_sequence=px.colors.qualitative.Pastel,
                        barmode='group'
                    )
                    fig_co_lead_stage.update_layout(height=400)
                    st.plotly_chart(fig_co_lead_stage, use_container_width=True)

                with col_h:
                    # Overall average votes by co-lead
                    co_lead_overall = co_lead_votes_df.groupby('co_lead')['votes'].mean().reset_index()
                    co_lead_overall = co_lead_overall.sort_values('votes', ascending=True)

                    fig_co_lead_overall = px.bar(
                        co_lead_overall,
                        x='votes',
                        y='co_lead',
                        orientation='h',
                        title='Average Votes by Co-Lead (Overall)',
                        labels={'votes': 'Avg Votes', 'co_lead': 'Co-Lead'},
                        color='votes',
                        color_continuous_scale='Teal'
                    )
                    fig_co_lead_overall.update_layout(height=400, showlegend=False)
                    st.plotly_chart(fig_co_lead_overall, use_container_width=True)

            st.markdown("---")

            # ====================
            # SECTION 5: Player Analytics
            # ====================
            st.subheader("🎮 Player Analytics")
            st.caption("Understanding voting patterns and engagement across team members")

            # Create voting matrix for heatmap
            vote_matrix = votes_df.pivot_table(
                index='player_name',
                columns='company_name',
                aggfunc='size',
                fill_value=0
            )

            # Heatmap
            fig_heatmap = px.imshow(
                vote_matrix,
                labels=dict(x="Company", y="Player", color="Voted"),
                title="Voting Patterns Heatmap (Player × Company)",
                color_continuous_scale='Blues',
                aspect='auto'
            )
            fig_heatmap.update_layout(height=max(400, len(vote_matrix) * 30))
            st.plotly_chart(fig_heatmap, use_container_width=True)

            col_i, col_j = st.columns(2)

            with col_i:
                # Player activity by designation
                player_activity = votes_df.groupby(['player_name', 'designation']).size().reset_index(name='votes')
                player_activity = player_activity.sort_values('votes', ascending=True)

                fig_player_activity = px.bar(
                    player_activity,
                    x='votes',
                    y='player_name',
                    color='designation',
                    orientation='h',
                    title='Number of Companies Voted by Each Player',
                    labels={'votes': 'Number of Votes', 'player_name': 'Player'},
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_player_activity.update_layout(height=max(400, len(player_activity) * 25))
                st.plotly_chart(fig_player_activity, use_container_width=True)

            with col_j:
                # Designation-wise participation
                designation_votes = votes_df.groupby('designation').size().reset_index(name='votes')

                fig_designation = go.Figure(data=[go.Pie(
                    labels=designation_votes['designation'],
                    values=designation_votes['votes'],
                    hole=0.4,
                    marker=dict(colors=px.colors.qualitative.Pastel),
                    textinfo='label+percent'
                )])
                fig_designation.update_layout(
                    title='Vote Distribution by Designation',
                    height=400
                )
                st.plotly_chart(fig_designation, use_container_width=True)

            # Team/Pod analysis
            if 'team' in votes_df.columns:
                team_votes = votes_df.groupby('team').size().reset_index(name='votes')
                team_votes = team_votes.sort_values('votes', ascending=False)

                fig_team = px.bar(
                    team_votes,
                    x='team',
                    y='votes',
                    title='Voting Activity by Team/Pod',
                    labels={'team': 'Team/Pod', 'votes': 'Number of Votes'},
                    color='votes',
                    color_continuous_scale='Teal'
                )
                fig_team.update_layout(height=350, showlegend=False)
                fig_team.update_xaxes(tickangle=-45)
                st.plotly_chart(fig_team, use_container_width=True)

            st.markdown("---")

            # ====================
            # SECTION 6: Advanced Insights
            # ====================
            st.subheader("🔍 Advanced Insights")
            st.caption("Deep dive into consensus, alignment, and cheque type analysis")

            # Consensus score
            total_players_count = len(players_df)
            company_vote_percentage = all_companies.copy()
            company_vote_percentage['vote_percentage'] = (company_vote_percentage['votes'] / total_players_count * 100).round(1)
            company_vote_percentage = company_vote_percentage.sort_values('vote_percentage', ascending=False)

            high_consensus = company_vote_percentage[company_vote_percentage['vote_percentage'] >= 50]
            low_consensus = company_vote_percentage[company_vote_percentage['vote_percentage'] < 20]

            col_k, col_l = st.columns(2)

            with col_k:
                if len(high_consensus) > 0:
                    st.success(f"💡 **High Consensus Deals ({len(high_consensus)} companies)**")
                    st.caption("More than 50% of the team voted for these companies")
                    for _, row in high_consensus.iterrows():
                        st.write(f"• **{row['company_name']}** - {row['vote_percentage']}% ({int(row['votes'])} votes)")
                else:
                    st.info("No high consensus deals yet (>50% team voting)")

            with col_l:
                if len(low_consensus) > 0:
                    st.warning(f"⚠️ **Underrated Companies ({len(low_consensus)} companies)**")
                    st.caption("Less than 20% of the team voted for these companies")
                    for _, row in low_consensus.head(5).iterrows():
                        st.write(f"• **{row['company_name']}** - {row['vote_percentage']}% ({int(row['votes'])} votes)")
                else:
                    st.success("All companies have reasonable attention (>20% voting)")

            # Cheque type analysis
            if 'cheque' in companies_df.columns:
                cheque_analysis = stage_analysis.groupby('cheque')['votes'].agg(['sum', 'mean', 'count']).reset_index()
                cheque_analysis.columns = ['Cheque Type', 'Total Votes', 'Avg Votes', 'Count']

                col_m, col_n = st.columns(2)

                with col_m:
                    fig_cheque_total = px.bar(
                        cheque_analysis,
                        x='Cheque Type',
                        y='Total Votes',
                        title='Total Votes by Cheque Type',
                        color='Total Votes',
                        color_continuous_scale='Blues'
                    )
                    fig_cheque_total.update_layout(height=350, showlegend=False)
                    st.plotly_chart(fig_cheque_total, use_container_width=True)

                with col_n:
                    fig_cheque_avg = px.bar(
                        cheque_analysis,
                        x='Cheque Type',
                        y='Avg Votes',
                        title='Average Votes by Cheque Type',
                        color='Avg Votes',
                        color_continuous_scale='Teal'
                    )
                    fig_cheque_avg.update_layout(height=350, showlegend=False)
                    st.plotly_chart(fig_cheque_avg, use_container_width=True)

            # Lead-Player Alignment (same pod voting)
            if 'team' in votes_df.columns and lead_votes:
                st.markdown("#### Lead-Player Alignment Analysis")
                st.caption("Do players vote more for deals led by partners from their own pod?")

                # Merge player teams with lead teams
                lead_teams = players_df[['player_name', 'team']].rename(columns={'player_name': 'lead', 'team': 'lead_team'})
                lead_votes_with_teams = pd.DataFrame(lead_votes).merge(lead_teams, on='lead', how='left')

                # Merge with voter teams
                votes_with_lead = votes_df.merge(
                    companies_df[['company_name', 'lead']],
                    on='company_name',
                    how='left'
                )

                # Check if same pod
                alignment_data = []
                for _, vote in votes_with_lead.iterrows():
                    if pd.notna(vote['lead']) and vote['lead']:
                        leads = [l.strip() for l in vote['lead'].split(',')]
                        for lead in leads:
                            lead_team_data = players_df[players_df['player_name'] == lead]
                            if len(lead_team_data) > 0:
                                lead_team = lead_team_data.iloc[0]['team']
                                voter_team = vote['team']
                                same_pod = (lead_team == voter_team)
                                alignment_data.append({
                                    'same_pod': 'Same Pod' if same_pod else 'Cross-Pod',
                                    'count': 1
                                })

                if alignment_data:
                    alignment_df = pd.DataFrame(alignment_data)
                    alignment_summary = alignment_df.groupby('same_pod').size().reset_index(name='votes')

                    fig_alignment = px.pie(
                        alignment_summary,
                        names='same_pod',
                        values='votes',
                        title='Same-Pod vs Cross-Pod Voting',
                        color_discrete_sequence=px.colors.qualitative.Set2
                    )
                    fig_alignment.update_layout(height=350)
                    st.plotly_chart(fig_alignment, use_container_width=True)

                    same_pod_pct = alignment_summary[alignment_summary['same_pod'] == 'Same Pod']['votes'].sum() / alignment_summary['votes'].sum() * 100
                    if same_pod_pct > 60:
                        st.info(f"💡 **Insight:** {same_pod_pct:.1f}% of votes are for deals led by partners from the same pod, showing strong team alignment.")
                    elif same_pod_pct < 40:
                        st.success(f"💡 **Insight:** {100-same_pod_pct:.1f}% of votes are cross-pod, showing great cross-functional collaboration!")


# ---------- Admin Tab ----------
with tabs[5]:
    # Header with save button
    header_col1, header_col2 = st.columns([3, 1])
    with header_col1:
        st.header("Administration")
    with header_col2:
        st.write("")  # Spacer for alignment
        if st.button("💾 Save to GitHub", use_container_width=True, type="primary"):
            with st.spinner("Saving to GitHub..."):
                success, message = save_to_github()
                if success:
                    st.success(message)
                else:
                    if "No changes" in message:
                        st.info(message)
                    else:
                        st.error(message)

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

            col4, col5 = st.columns(2)
            with col4:
                sector = st.selectbox("Sector *", options=SECTORS)
            with col5:
                cheque = st.selectbox("Cheque *", options=CHEQUE_OPTIONS)

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
                        "cheque": cheque,
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

                            # Filter current companies to only include those that still exist
                            valid_current_companies = [c for c in current_companies_list if c in company_options]

                            selected_companies = st.multiselect(
                                "Companies",
                                options=company_options,
                                default=valid_current_companies,
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
