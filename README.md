# NBA Data Pipeline 🏀

Analyse du momentum dans les séries éliminatoires NBA (2013-2023).

## Architecture

```
nba-api → Extract → GCS → Transform → BigQuery → Power BI Dashboard
         (10 ans)        (Clean)     (Analysis)
```

### Étapes du Pipeline

1. **Extract** (`extract_nba.py` + `extract_players.py`)
   - Récupère 10 saisons de playoffs via l'API NBA Stats
   - Données: matchs, équipes, joueurs
   - Upload vers Google Cloud Storage

2. **Clean** (`clean_nba.py` + `clean_players.py`)
   - Sélection colonnes pertinentes
   - Conversion types de données
   - Calcul colonnes dérivées (victoires, home/away)
   - Filtrage (ex: joueurs avec ≥10 matchs playoffs)

3. **Transform** (`momentum.py`)
   - Calcul du momentum par série
   - Victoires cumulées (`WINS_BEFORE`)
   - Identifiant unique de série (`SERIE_ID`)
   - Upload final vers BigQuery

4. **Dashboard** (`NBA_analysis.pbix`)
   - Visualisation Power BI
   - Analyse des winning streaks
   - Performance par saison/équipe

## Installation

```bash
# Clone le repo
git clone <your-repo-url>
cd nba-data-pipeline

# Crée un environnement Python (optionnel)
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Installe les dépendances
pip install -r requirements.txt
```

## Configuration GCP

1. Crée un fichier `gcp-credentials.json` avec tes identifiants GCP
   - ⚠️ **Ne le push JAMAIS sur GitHub** (déjà dans `.gitignore`)

2. Assure-toi d'avoir:
   - Bucket GCS: `nba-raw-data-20260511`
   - Dataset BigQuery: `nba_data`
   - Permissions: Storage, BigQuery

## Exécution

```bash
# Récupérer les données brutes
python extract_nba.py
python extract_players.py

# Nettoyer les données
python clean_nba.py
python clean_players.py

# Analyser le momentum
python momentum.py

# Tester
python test_nba.py
```

## Dépendances

- `pandas` - Manipulation données
- `nba_api` - API NBA Stats
- `google-cloud-storage` - Accès GCS
- `google-cloud-bigquery` - Accès BigQuery

## Structure Fichiers

```
├── extract_nba.py           # Extraction matchs playoffs
├── extract_players.py       # Extraction joueurs playoffs
├── clean_nba.py             # Nettoyage matchs
├── clean_players.py         # Nettoyage joueurs
├── momentum.py              # Analyse momentum + upload BQ
├── test_nba.py              # Tests
├── NBA_analysis.pbix        # Dashboard Power BI
└── README.md               # Ce fichier
```

## À Faire

- [ ] Automatiser exécution (Cloud Scheduler)
- [ ] Ajouter data validation
- [ ] Tests unitaires
- [ ] Pipeline CI/CD
- [ ] Documenter API NBA utilisée

## Licence

MIT

## Auteur

Created on May 21, 2026
