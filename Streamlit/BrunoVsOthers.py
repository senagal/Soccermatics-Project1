import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Bruno vs Other midfielders in the EURO 2024", layout="wide")

# ---------------------------
# Load Data from CSV
# ---------------------------
@st.cache_data
def load_data():
    # Read the precomputed CSV with players > 150 minutes
    df = pd.read_csv("euro2024_midfielders_summary.csv")
    return df

full_stats = load_data()

# ---------------------------
# Player Selection
# ---------------------------
BRUNO_ID = 5204

# Split Bruno from peers
bruno_row = full_stats[full_stats['player_id'] == BRUNO_ID]
peers_df = full_stats[full_stats['player_id'] != BRUNO_ID]

# ---------------------------
# Metric Selection
# ---------------------------
metric = st.selectbox(
    "Choose metric to compare",
    ["total_passes", "total_shot_assists", "total_goal_assists", 
     "shot_assists_per90", "goal_assists_per90", "total_minutes_played", "matches_played"]
)

st.title("Bruno Fernandes vs Other midfielders in the EURO 2024")
st.write("This comparison only includes players with above 150 total minutes played")
# ---------------------------
# Horizontal Bar Chart (Plotly)
# ---------------------------
st.subheader("Horizontal Bar Chart")
hover_cols = ["matches_played", "total_minutes_played", "total_passes", "total_shot_assists", "total_goal_assists", "shot_assists_per90", "goal_assists_per90"]

fig_bar = px.bar(
    full_stats,
    x=metric,
    y='player_name',
    orientation='h',
    color=full_stats['player_id'] == BRUNO_ID,
    color_discrete_map={True: 'red', False: 'blue'},
    hover_data=hover_cols
)

fig_bar.update_layout(
    yaxis={'categoryorder':'total ascending'},
    xaxis_title=metric.replace('_',' ').title(),
    yaxis_title="Players",
    showlegend=False,
    height=max(600, len(full_stats)*20)
)

st.plotly_chart(fig_bar, use_container_width=True)

# ---------------------------
# Player Table
# ---------------------------
st.subheader("Full Player Comparison Table")
st.dataframe(full_stats.sort_values(metric, ascending=False).reset_index(drop=True))
