from nba_api.stats.endpoints import leaguegamefinder
import pandas as pd

# On récupère quelques matchs playoffs pour tester
gamefinder = leaguegamefinder.LeagueGameFinder(
    season_nullable='2022-23',
    season_type_nullable='Playoffs'
)

df = gamefinder.get_data_frames()[0]

print(f"Nombre de lignes : {len(df)}")
print(df.columns.tolist())
print(df.head(3))