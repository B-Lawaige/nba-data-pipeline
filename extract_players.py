from nba_api.stats.endpoints import leaguegamelog
import pandas as pd
import time

saisons = [
    '2013-14', '2014-15', '2015-16', '2016-17', '2017-18',
    '2018-19', '2019-20', '2020-21', '2021-22', '2022-23'
]

all_data = []

for saison in saisons:
    print(f"Récupération saison {saison}...")
    
    gamelog = leaguegamelog.LeagueGameLog(
        season=saison,
        season_type_all_star='Playoffs',
        player_or_team_abbreviation='P'  # P = joueurs
    )
    
    df = gamelog.get_data_frames()[0]
    all_data.append(df)
    time.sleep(1)

df_players = pd.concat(all_data, ignore_index=True)

print(f"\n✅ Total lignes : {len(df_players)}")
print(df_players.columns.tolist())

df_players.to_csv('nba_players_playoffs.csv', index=False)
print("✅ Fichier sauvegardé : nba_players_playoffs.csv")