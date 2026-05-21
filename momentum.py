import pandas as pd
from google.cloud import bigquery
import os

# ─────────────────────────────────────────
# LECTURE DEPUIS BIGQUERY
# ─────────────────────────────────────────
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'gcp-credentials.json'
bq_client = bigquery.Client()

PROJECT_ID = 'nba-data-pipeline-496010'
DATASET_ID = 'nba_data'
SOURCE_TABLE = 'nba_playoffs_clean'

query = f"""
SELECT SEASON_ID, Team as TEAM_NAME, GAME_ID, Date as GAME_DATE, MATCHUP, 
       CASE WHEN WIN = 1 THEN 'W' ELSE 'L' END as WL
FROM `{PROJECT_ID}.{DATASET_ID}.{SOURCE_TABLE}`
"""

df = bq_client.query(query).to_dataframe()
print(f"✅ Données chargées depuis BigQuery : {PROJECT_ID}.{DATASET_ID}.{SOURCE_TABLE}")
print(f"Lignes : {len(df)}")

# Garder uniquement les colonnes utiles
df = df[['SEASON_ID', 'TEAM_NAME', 'GAME_ID', 'GAME_DATE', 'MATCHUP', 'WL']]
df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
df['WIN'] = (df['WL'] == 'W').astype(int)
df['SEASON'] = df['SEASON_ID'].astype(str).str[-4:].astype(int)

# Identifier la série (les deux équipes qui s'affrontent)
df['HOME'] = df['MATCHUP'].apply(lambda x: x.split(' vs. ')[0] if 'vs.' in x else x.split(' @ ')[1])
df['AWAY'] = df['MATCHUP'].apply(lambda x: x.split(' @ ')[0] if '@' in x else x.split(' vs. ')[1])
df['SERIE_ID'] = df['SEASON'].astype(str) + '_' + df[['HOME', 'AWAY']].apply(lambda x: '_'.join(sorted([x['HOME'], x['AWAY']])), axis=1)

# Trier par série et date
df = df.sort_values(['SERIE_ID', 'GAME_DATE'])

# Calculer le numéro du match dans la série
df['GAME_NUMBER'] = df.groupby(['SERIE_ID', 'TEAM_NAME']).cumcount() + 1

# Calculer les victoires cumulées dans la série
df['WINS_IN_SERIE'] = df.groupby(['SERIE_ID', 'TEAM_NAME'])['WIN'].cumsum()

# Victoires AVANT ce match (momentum)
df['WINS_BEFORE'] = df['WINS_IN_SERIE'] - df['WIN']

# ─────────────────────────────────────────
# UPLOAD VERS BIGQUERY
# ─────────────────────────────────────────
MOMENTUM_TABLE = 'nba_momentum'
table_id = f"{PROJECT_ID}.{DATASET_ID}.{MOMENTUM_TABLE}"

job_config = bigquery.LoadJobConfig(
    write_disposition="WRITE_TRUNCATE",  # Remplacer la table si elle existe
    autodetect=True
)

job = bq_client.load_table_from_dataframe(df, table_id, job_config=job_config)
job.result()  # Attendre la fin du job

print(f"\n✅ Données uploadées dans BigQuery : {table_id}")
print(f"Lignes finales : {len(df)}")
print(f"\nAperçu :")
print(df[['TEAM_NAME', 'GAME_DATE', 'SERIE_ID', 'GAME_NUMBER', 'WINS_BEFORE', 'WIN']].head(10))