from mplsoccer import Sbopen
import pandas as pd

# Initialize parser
parser = Sbopen(dataframe=True)

# Competition and season IDs
competition_id = 55   # Euro 2024
season_id = 282       # Euro 2024 season

# Load all matches for this competition and season
matches = parser.match(competition_id, season_id)

# Select only relevant columns: match_id, home and away teams
matches_info = matches[['match_id', 'home_team_name', 'away_team_name']]

# Display
print(matches_info)

# Optionally, convert to a nicer table
matches_info.reset_index(drop=True, inplace=True)
matches_info
