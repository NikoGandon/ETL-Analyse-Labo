"""Nettoyage, enrichissement et pivot des analyses Hub'Eau."""

from pathlib import Path

import numpy as np
import pandas as pd

import config


def load_raw(path: Path, usecols: list[str]) -> pd.DataFrame:
    """Lit un CSV en str avec auto-detection de l'encodage."""
    last_error = None
    for enc in config.ENCODINGS:
        try:
            return pd.read_csv(
                path, sep=config.SEP, dtype=str, encoding=enc,
                usecols=usecols, keep_default_na=False,
            )
        except (UnicodeDecodeError, UnicodeError) as exc:
            last_error = exc
    raise UnicodeError(f"Encodage impossible pour {path} : {last_error}")


def _strip(df: pd.DataFrame) -> pd.DataFrame:
    """Strip les cellules texte."""
    return df.apply(lambda s: s.str.strip() if s.dtype == object else s)


def _to_float(series: pd.Series) -> pd.Series:
    """Virgule decimale -> float."""
    return pd.to_numeric(series.str.replace(",", ".", regex=False), errors="coerce")


def _fmt_num(v) -> str:
    """0.0200 -> '0.02', NaN -> ''."""
    return f"{v:g}" if pd.notna(v) else ""


def clean_analyses(df: pd.DataFrame) -> pd.DataFrame:
    """NaN, seuils de detection, types, dates."""
    df = _strip(df)
    df = df.replace(list(config.MISSING_TOKENS), np.nan)

    # Flag sous-seuil : on cible "Resultat < ..." specifiquement,
    # parce que "Resultat > quantif et < saturation" est une mesure valide
    mnemo = df["mnemo_remarque"].fillna("").str.strip()
    df["analyse_non_faite"] = mnemo.str.contains("non faite", case=False)
    df["sous_seuil"] = mnemo.str.match(r"R.sultat\s*<")

    for col in config.NUMERIC_COLS:
        df[col] = _to_float(df[col])

    # analyse non faite -> pas de resultat
    df.loc[df["analyse_non_faite"], "resultat"] = np.nan

    # resultat exploitable = valeur quantifiee (pour la matrice de calcul)
    df["resultat_exploitable"] = df["resultat"].where(~df["sous_seuil"])

    # valeur d'affichage : garde la distinction "non teste" / "< LQ" / valeur
    seuil = df["limite_quantification"].fillna(df["resultat"])
    affichee = df["resultat"].map(_fmt_num)
    affichee = affichee.where(~df["sous_seuil"], "< " + seuil.map(_fmt_num))
    affichee = affichee.mask(df["analyse_non_faite"], "non testé")
    df["valeur_affichee"] = affichee

    # date/heure en datetime
    base = df["date_prelevement"].fillna("") + " " + df["heure_prelevement"].fillna("00:00:00")
    df["date_heure_prelevement"] = pd.to_datetime(base.str.strip(), errors="coerce")
    return df


def clean_stations(df: pd.DataFrame) -> pd.DataFrame:
    """Strip + NaN + dedup sur code_station."""
    df = _strip(df)
    df = df.replace(list(config.MISSING_TOKENS), np.nan)
    return df.drop_duplicates(subset=["code_station"], keep="first")


def enrich(analyses: pd.DataFrame, stations: pd.DataFrame) -> pd.DataFrame:
    """Jointure avec les stations (commune, cours d'eau, region)."""
    return analyses.merge(stations, on="code_station", how="left", validate="m:1")


# Pivot long -> large
INDEX_PIVOT = ["date_prelevement", "libelle_station", "libelle_commune", "nom_cours_eau"]
CLE_DUPLICAT = ["date_prelevement", "code_station", "parametre"]


def _subset_physico(df: pd.DataFrame) -> pd.DataFrame:
    """Filtre sur les parametres de PARAMS_PHYSICO."""
    sous = df[df["libelle_parametre"].isin(config.PARAMS_PHYSICO)].copy()
    sous["parametre"] = sous["libelle_parametre"].map(config.PARAMS_PHYSICO)
    return sous


def compter_duplicats(df: pd.DataFrame) -> int:
    """Nombre de (station, date, parametre) avec plusieurs mesures."""
    sous = _subset_physico(df)
    tailles = sous.groupby(CLE_DUPLICAT).size()
    return int((tailles > 1).sum())


def _ordonner(matrice: pd.DataFrame) -> pd.DataFrame:
    matrice.columns.name = None
    matrice = matrice.rename(columns=config.RENAME_INDEX)
    base = ["date_prelevement", "station", "commune", "cours_eau"]
    cols = base + [c for c in config.PARAMS_PHYSICO.values() if c in matrice.columns]
    return matrice[cols].sort_values(["date_prelevement", "station"])


def pivot_strict(df: pd.DataFrame) -> pd.DataFrame:
    """Matrice numerique (pour calculs). NaN = pas mesure ou sous seuil."""
    sous = _subset_physico(df)
    aggfunc = "mean" if config.REGLE_AGREGATION == "moyenne" else "last"
    matrice = pd.pivot_table(
        sous, index=INDEX_PIVOT, columns="parametre",
        values="resultat_exploitable", aggfunc=aggfunc,
    ).reset_index()
    return _ordonner(matrice)


def pivot_rapport(df: pd.DataFrame) -> pd.DataFrame:
    """Matrice textuelle (pour lecture). Garde "< LQ" / "non teste" / valeur."""
    sous = _subset_physico(df)
    matrice = sous.pivot_table(
        index=INDEX_PIVOT, columns="parametre",
        values="valeur_affichee", aggfunc="first",
    ).reset_index()
    return _ordonner(matrice)
