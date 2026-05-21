import pandas as pd
from google.cloud import storage
from google.cloud import bigquery
from io import StringIO
import os

# ─────────────────────────────────────────
# LECTURE DEPUIS GCS
# ─────────────────────────────────────────
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'gcp-credentials.json'
storage_client = storage.Client()

BUCKET_NAME = 'nba-raw-data-20260511'
FILE_NAME = 'nba_playoffs_raw.csv'

bucket = storage_client.bucket(BUCKET_NAME)
blob = bucket.blob(FILE_NAME)
csv_data = blob.download_as_string().decode('utf-8')

# Convertir en dataframe
df = pd.read_csv(StringIO(csv_data))
print(f"✅ Données chargées depuis GCS : gs://{BUCKET_NAME}/{FILE_NAME}")
print(f"Lignes brutes : {len(df)}")

# ─────────────────────────────────────────
# 1. COLONNES UTILES SEULEMENT
# ─────────────────────────────────────────
colonnes = [
    'SEASON_ID', 'TEAM_NAME', 'GAME_ID', 'GAME_DATE', 'MATCHUP',
    'WL', 'PTS', 'FGM', 'FGA', 'FG_PCT',
    'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT',
    'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PLUS_MINUS'
]
df = df[colonnes]

# ─────────────────────────────────────────
# 2. TYPES CORRECTS
# ─────────────────────────────────────────
df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
df['SEASON'] = df['SEASON_ID'].astype(str).str[-4:].astype(int)  # ex: 2023

# ─────────────────────────────────────────
# 3. COLONNES CALCULÉES
# ─────────────────────────────────────────

# Victoire : 1 ou 0
df['WIN'] = (df['WL'] == 'W').astype(int)

# Home ou Away (MATCHUP contient "vs." si domicile, "@" si extérieur)
df['HOME_AWAY'] = df['MATCHUP'].apply(lambda x: 'Home' if 'vs.' in x else 'Away')

# Nom de l'adversaire (extrait du MATCHUP)
df['OPPONENT'] = df['MATCHUP'].apply(lambda x: x.split(' ')[-1])

# ─────────────────────────────────────────
# 4. RENOMMAGE PROPRE
# ─────────────────────────────────────────
df = df.rename(columns={
    'TEAM_NAME'  : 'Team',
    'GAME_DATE'  : 'Date',
    'PTS'        : 'Points',
    'FG_PCT'     : 'FG_Pct',
    'FG3_PCT'    : 'FG3_Pct',
    'FT_PCT'     : 'FT_Pct',
    'REB'        : 'Rebounds',
    'AST'        : 'Assists',
    'STL'        : 'Steals',
    'BLK'        : 'Blocks',
    'TOV'        : 'Turnovers',
    'PF'         : 'Fouls',
    'PLUS_MINUS' : 'PlusMinus',
    'OREB'       : 'Off_Rebounds',
    'DREB'       : 'Def_Rebounds',
})

# ─────────────────────────────────────────
# 5. VÉRIFICATION VALEURS NULLES
# ─────────────────────────────────────────
nulls = df.isnull().sum()
print("\nValeurs nulles par colonne :")
print(nulls[nulls > 0] if nulls.sum() > 0 else "Aucune valeur nulle !")

# ─────────────────────────────────────────
# 6. UPLOAD VERS BIGQUERY
# ─────────────────────────────────────────
bq_client = bigquery.Client()

PROJECT_ID = 'nba-data-pipeline-496010'
DATASET_ID = 'nba_data'
TABLE_ID = 'nba_playoffs_clean'

# Créer la table ID complète
table_id = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

# Convertir les colonnes de pourcentage en float avant d'envoyer à BigQuery
for col in ['FG_Pct', 'FG3_Pct', 'FT_Pct']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Configurer le job d'upload
job_config = bigquery.LoadJobConfig(
    write_disposition="WRITE_TRUNCATE",  # Remplacer la table si elle existe
    autodetect=True
)

job = bq_client.load_table_from_dataframe(df, table_id, job_config=job_config)
job.result()  # Attendre la fin du job

print(f"\n✅ Données uploadées dans BigQuery : {table_id}")
print(f"Lignes finales : {len(df)}")
print(f"\nAperçu :")
print(df[['Team', 'Date', 'SEASON', 'Points', 'FG_Pct', 'Rebounds', 'WIN', 'HOME_AWAY']].head(5))