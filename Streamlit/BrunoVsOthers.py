from mplsoccer import Sbopen, Pitch
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Bruno vs Other midfielders in the EURO 2024", layout="wide")

# ---------------------------
# Load Data from CSV
# ---------------------------
@st.cache_data
def load_data():
    BASE_DIR = os.path.dirname(__file__)
    CSV_PATH = os.path.join(BASE_DIR, "euro2024_midfielders_summary.csv")
    return pd.read_csv(CSV_PATH)

full_stats = load_data()

# ---------------------------
# Constants
# ---------------------------
BRUNO_ID = 5204
PLAYER_ID = 5204
PLAYER_NAME = "Bruno Fernandes"

st.title("Bruno's passes in the matches he played in EURO 2024")

# ---------------------------
# StatsBomb parser
# ---------------------------
parser = Sbopen(dataframe=True)

# ---------------------------
# Match list
# ---------------------------
all_match_ids = [3942349, 3941020, 3930174, 3930166]

@st.cache_data
def get_match_names(match_ids):
    name_map = {}
    for idx, m_id in enumerate(match_ids):
        df, related, freeze, tactics = parser.event(m_id)
        teams = df["team_name"].dropna().unique().tolist()
        match_name = f"{teams[0]} vs {teams[1]}" if len(teams) == 2 else f"Match {m_id}"
        name_map[match_name] = m_id
    return name_map

match_name_map = get_match_names(all_match_ids)
match_names = list(match_name_map.keys())

# ---------------------------
# UI: match selector
# ---------------------------
selected_match_names = st.multiselect(
    "Select matches to display",
    options=match_names,
    default=match_names
)
selected_matches = [match_name_map[name] for name in selected_match_names]

# ---------------------------
# Load events
# ---------------------------
@st.cache_data
def load_events(match_ids):
    all_events = []
    match_team_names = {}
    for idx, m_id in enumerate(match_ids):
        df, related, freeze, tactics = parser.event(m_id)
        df["match_id"] = m_id
        all_events.append(df)
        teams = df["team_name"].dropna().unique().tolist()
        match_team_names[m_id] = f"{teams[0]} vs {teams[1]}" if len(teams) == 2 else f"Match {m_id}"
    return pd.concat(all_events, ignore_index=True), match_team_names

# ---------------------------
# Pitch map section
# ---------------------------
if selected_matches:
    events, match_team_names = load_events(selected_matches)

    # Player passes
    player_events = events[events["player_id"] == PLAYER_ID].copy()
    passes = player_events[player_events["type_name"] == "Pass"].copy()

    # Shot & goal assists
    shot_assists = passes[passes.get("pass_shot_assist", False) == True] if "pass_shot_assist" in passes.columns else passes.iloc[0:0]
    goal_assists = passes[passes.get("pass_goal_assist", False) == True] if "pass_goal_assist" in passes.columns else passes.iloc[0:0]

    # Create pitch
    pitch = Pitch(pitch_type="statsbomb", line_color="black")
    fig, ax = pitch.draw(figsize=(9, 6))

    colors = ["#032dff", "#03ff0b", "#ee03ff", "#ff7700", "#00ffff"]
    color_map = dict(zip(selected_matches, colors))

    for m_id in selected_matches:
        match_passes = passes[passes["match_id"] == m_id]
        pitch.arrows(
            match_passes["x"], match_passes["y"],
            match_passes["end_x"], match_passes["end_y"],
            ax=ax,
            width=1.2, headwidth=4, headlength=4,
            color=color_map[m_id],
            alpha=1.0,
            label=f"{match_team_names[m_id]} — Passes: {len(match_passes)}"
        )

    # Plot assists
    pitch.arrows(
        shot_assists["x"], shot_assists["y"],
        shot_assists["end_x"], shot_assists["end_y"],
        ax=ax, width=3, headwidth=7, headlength=7,
        color="red", alpha=1.0,
        label=f"Shot Assists: {len(shot_assists)}"
    )
    pitch.arrows(
        goal_assists["x"], goal_assists["y"],
        goal_assists["end_x"], goal_assists["end_y"],
        ax=ax, width=3.5, headwidth=8, headlength=8,
        color="yellow", alpha=1.0,
        label=f"Goal Assists: {len(goal_assists)}"
    )

    plt.title(f"{PLAYER_NAME}: Pass Map (Portugal's goal is on the left)", fontsize=16)
    plt.legend(loc="upper right", fontsize=8)
    st.pyplot(fig, use_container_width=True)

else:
    st.warning("Please select at least one match.")

# ---------------------------
# Metric selection for the bar chart (NOW BELOW pitch map)
# ---------------------------
metric = st.selectbox(
    "Choose metric to compare for bar chart",
    ["total_passes", "passes_per90", "total_shot_assists", "total_goal_assists", 
     "shot_assists_per90", "goal_assists_per90", "total_minutes_played", "matches_played"]
)

# ---------------------------
# Horizontal Bar Chart
# ---------------------------
st.subheader("Bruno Fernandes vs Other midfielders in the EURO 2024")
st.write("This comparison only includes players with above 150 total minutes played")

full_stats["highlight"] = full_stats["player_id"].apply(lambda x: "Bruno" if x == BRUNO_ID else "Peer")

hover_cols = [
    "matches_played", "total_minutes_played",
    "total_passes", "passes_per90",
    "total_shot_assists", "total_goal_assists",
    "shot_assists_per90", "goal_assists_per90"
]
hover_cols = [col for col in hover_cols if col in full_stats.columns]

fig_bar = px.bar(
    full_stats,
    x=metric,
    y='player_name',
    orientation='h',
    color="highlight",
    color_discrete_map={"Bruno": "red", "Peer": "blue"},
    hover_data=hover_cols
)

fig_bar.update_layout(
    yaxis={'categoryorder': 'total ascending'},
    xaxis_title=metric.replace('_', ' ').title(),
    yaxis_title="Players",
    showlegend=False,
    height=max(600, len(full_stats) * 20)
)

st.plotly_chart(fig_bar, use_container_width=True)

# ---------------------------
# Player Table
# ---------------------------
st.subheader("Full Player Comparison Table")
st.dataframe(full_stats.sort_values(metric, ascending=False).reset_index(drop=True))
