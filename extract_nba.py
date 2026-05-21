from nba_api.stats.endpoints import leaguegamefinder
import pandas as pd
import time
from google.cloud import storage
from io import StringIO
import os

# 10 saisons de playoffs
saisons = [
    '2013-14', '2014-15', '2015-16', '2016-17', '2017-18',
    '2018-19', '2019-20', '2020-21', '2021-22', '2022-23'
]

all_data = []

for saison in saisons:
    print(f"Récupération saison {saison}...")
    
    gamefinder = leaguegamefinder.LeagueGameFinder(
        season_nullable=saison,
        season_type_nullable='Playoffs'
    )
    
    df = gamefinder.get_data_frames()[0]
    all_data.append(df)
    
    #évite de se faire bloquer par l'API
    time.sleep(1)  

# On combine tout
df_final = pd.concat(all_data, ignore_index=True)

print(f"\nTotal lignes : {len(df_final)}")
print(f"Saisons : {df_final['SEASON_ID'].nunique()}")

# ─────────────────────────────────────────
# UPLOAD VERS GCS
# ─────────────────────────────────────────

# Authentification avec la clé JSON
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'gcp-credentials.json'
client = storage.Client()

# Paramètres GCS
BUCKET_NAME = 'nba-raw-data-20260511'
FILE_NAME = 'nba_playoffs_raw.csv'

# Convertir le dataframe en CSV (en mémoire)
csv_buffer = StringIO()
df_final.to_csv(csv_buffer, index=False)
csv_data = csv_buffer.getvalue()

# Uploader vers GCS
bucket = client.bucket(BUCKET_NAME)
blob = bucket.blob(FILE_NAME)
blob.upload_from_string(csv_data, content_type='text/csv')

print(f"Fichier uploadé dans GCS : gs://{BUCKET_NAME}/{FILE_NAME}")