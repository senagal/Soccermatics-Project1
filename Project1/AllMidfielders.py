import pandas as pd
from mplsoccer import Sbopen

parser = Sbopen()
competition_id = 55
season_id = 282

TARGET_POSITIONS = [9, 11, 19]

# Load all matches
matches = parser.match(competition_id=competition_id, season_id=season_id)
match_ids = matches['match_id'].tolist()

all_players = []

for match_id in match_ids:
    df, related, freeze, tactics = parser.event(match_id)
    
    # Home/away teams
    match_row = matches[matches['match_id'] == match_id].iloc[0]
    home_team = match_row['home_team_name']
    away_team = match_row['away_team_name']
    
    half = len(tactics) // 2  # approximate home/away split
    
    for idx, row in tactics.iterrows():
        team_name = home_team if idx < half else away_team
        
        if row['position_id'] in TARGET_POSITIONS:
            all_players.append({
                'match_id': match_id,
                'team_name': team_name,
                'player_id': row['player_id'],
                'player_name': row['player_name'],
                'position_id': row['position_id'],
                'position_name': row['position_name']
            })

# Convert to DataFrame
df_players = pd.DataFrame(all_players)

# Count the number of matches each player played in each target position
position_counts = df_players.groupby(
    ['player_id', 'player_name', 'position_id', 'position_name']
).size().reset_index(name='appearances')

# Sort by number of appearances
position_counts = position_counts.sort_values(by='appearances', ascending=False)

# Save to CSV
position_counts.to_csv("target_positions_appearances.csv", index=False)

print("Saved target positions appearances to 'target_positions_appearances.csv'")
