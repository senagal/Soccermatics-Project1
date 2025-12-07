from mplsoccer import Sbopen
import pandas as pd

parser = Sbopen(dataframe=True)

competition_id = 55   # Euro 2024
season_id = 282

# Load matches
matches = parser.match(competition_id, season_id)

# Select Portugal matches
portugal_matches = matches[
    (matches['home_team_name'] == 'Portugal') |
    (matches['away_team_name'] == 'Portugal')
]

match_ids = portugal_matches['match_id'].tolist()

players_list = []

for match_id in match_ids:
    df, related, freeze, tactics = parser.event(match_id)

    # Filter only Portugal events
    portugal_events = df[df["team_name"] == "Portugal"]

    # Extract unique players + their positions
    unique_players = portugal_events[
        ["player_id", "player_name", "position_id", "position_name"]
    ].dropna().drop_duplicates()

    unique_players["match_id"] = match_id
    players_list.append(unique_players)

# Combine all matches
players_df = pd.concat(players_list, ignore_index=True)

# Remove duplicates (player has same position across matches)
players_df = players_df.drop_duplicates(subset=["player_id", "position_id"])
print(players_df[players_df["player_id"] == 5204][[
    "player_id", 
    "player_name", 
    "position_id", 
    "position_name",
    "match_id"
]])


