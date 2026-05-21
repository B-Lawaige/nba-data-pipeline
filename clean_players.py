import pandas as pd

df = pd.read_csv('nba_players_playoffs.csv')
print(f"Lignes brutes : {len(df)}")

# 1. COLONNES UTILES
colonnes = [
    'SEASON_ID', 'PLAYER_NAME', 'TEAM_NAME', 'GAME_ID',
    'GAME_DATE', 'MATCHUP', 'WL', 'MIN',
    'PTS', 'FGM', 'FGA', 'FG_PCT',
    'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PLUS_MINUS'
]
df = df[colonnes]

# 2. TYPES CORRECTS
df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
df['SEASON'] = df['SEASON_ID'].astype(str).str[-4:].astype(int)
df['WIN'] = (df['WL'] == 'W').astype(int)
df['HOME_AWAY'] = df['MATCHUP'].apply(lambda x: 'Home' if 'vs.' in x else 'Away')


# 3. RENOMMAGE
df = df.rename(columns={
    'PLAYER_NAME' : 'Player',
    'TEAM_NAME'   : 'Team',
    'GAME_DATE'   : 'Date',
    'PTS'         : 'Points',
    'FG_PCT'      : 'FG_Pct',
    'REB'         : 'Rebounds',
    'AST'         : 'Assists',
    'STL'         : 'Steals',
    'BLK'         : 'Blocks',
    'TOV'         : 'Turnovers',
    'PF'          : 'Fouls',
    'PLUS_MINUS'  : 'PlusMinus',
    'MIN'         : 'Minutes'
})

df['FG_Pct'] = df['FG_Pct'].fillna(0)
# Forcer le séparateur décimal français
df['FG_Pct'] = df['FG_Pct'].astype(str).str.replace('.', ',', regex=False)

# 4. FILTRE — garder uniquement les joueurs avec au moins 10 matchs playoffs
matchs_par_joueur = df.groupby('Player')['GAME_ID'].count()
stars = matchs_par_joueur[matchs_par_joueur >= 10].index
df = df[df['Player'].isin(stars)]

# 5. VERIFICATION
nulls = df.isnull().sum()
print("\nValeurs nulles :")
print(nulls[nulls > 0] if nulls.sum() > 0 else "Aucune valeur nulle !")
print(f"\nJoueurs retenus : {df['Player'].nunique()}")
print(f"Lignes finales : {len(df)}")

df.to_csv('nba_players_clean.csv', index=False)
print("Fichier sauvegarde : nba_players_clean.csv")