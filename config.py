"""Config pipeline Hub'Eau - analyses physico-chimiques, dept 37, 2023."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "raw"
OUTPUT_DIR = BASE_DIR / "output"

FICHIER_ANALYSES = RAW_DIR / "analyses_pc_37_2023.csv"
FICHIER_STATIONS = RAW_DIR / "stations_pc_37.csv"

SEP = ";"
ENCODINGS = ("utf-8", "latin-1")

# Valeurs manquantes
MISSING_TOKENS = {"", ".", "N/A", "NA", "nan", "NaN"}

# Colonnes a garder (71 -> essentiel)
COLS_ANALYSES = [
    "code_station", "libelle_station", "date_prelevement", "heure_prelevement",
    "libelle_parametre", "resultat", "symbole_unite",
    "code_remarque", "mnemo_remarque", "limite_quantification", "limite_detection",
    "libelle_qualification", "nom_laboratoire",
]
COLS_STATIONS = [
    "code_station", "libelle_commune", "code_commune", "nom_cours_eau", "libelle_region",
]

NUMERIC_COLS = {"resultat", "limite_quantification", "limite_detection"}

# Parametres retenus : libelle Hub'Eau -> colonne snake_case (SQL/BI safe)
PARAMS_PHYSICO = {
    "Potentiel en Hydrogène (pH)": "ph",
    "Température de l'Eau": "temperature_c",
    "Conductivité à 25°C": "conductivite_us_cm",
    "Oxygène dissous": "o2_dissous_mg_l",
    "Taux de saturation en oxygène": "saturation_o2_pct",
    "Nitrates": "nitrates_mg_l",
    "Nitrites": "nitrites_mg_l",
    "Phosphore total": "phosphore_total_mg_l",
    "Matières en suspension": "mes_mg_l",
    "Turbidité Formazine Néphélométrique": "turbidite_nfu",
    "Carbone Organique": "carbone_organique_mg_l",
    "Demande Biochimique en oxygène en 5 jours (D.B.O.5)": "dbo5_mg_l",
}

# Renommage des colonnes d'index
RENAME_INDEX = {
    "libelle_station": "station",
    "libelle_commune": "commune",
    "nom_cours_eau": "cours_eau",
}

# Libelles avec unites, pour l'affichage uniquement (pas dans les CSV)
LABELS_AFFICHAGE = {
    "date_prelevement": "Date",
    "station": "Station",
    "commune": "Commune",
    "cours_eau": "Cours d'eau",
    "ph": "pH",
    "temperature_c": "Température (°C)",
    "conductivite_us_cm": "Conductivité (µS/cm)",
    "o2_dissous_mg_l": "O2 dissous (mg/L)",
    "saturation_o2_pct": "Saturation O2 (%)",
    "nitrates_mg_l": "Nitrates (mg/L)",
    "nitrites_mg_l": "Nitrites (mg/L)",
    "phosphore_total_mg_l": "Phosphore total (mg/L)",
    "mes_mg_l": "MES (mg/L)",
    "turbidite_nfu": "Turbidité (NFU)",
    "carbone_organique_mg_l": "Carbone org. (mg/L)",
    "dbo5_mg_l": "DBO5 (mg/L)",
}

# Agregation des duplicats (meme station/date/parametre)
REGLE_AGREGATION = "moyenne"  # "moyenne" | "recent"
