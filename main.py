"""Pipeline Hub'Eau : nettoyage, enrichissement et pivot.
Usage : python main.py
"""

import json
import time

import config
import consolidate


def export(df, nom: str) -> None:
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = config.OUTPUT_DIR / f"{nom}.csv"
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"  -> {path}")


def build_report(analyses, matrice, stats) -> str:
    L = []
    L.append("=" * 66)
    L.append("  RAPPORT QUALITÉ — Analyses physico-chimiques 2023 (Hub'Eau, Indre-et-Loire)")
    L.append("=" * 66)
    L.append("")
    L.append("ENTRÉE (données brutes)")
    L.append("-" * 66)
    L.append(f"  analyses brutes      : {stats['analyses_brutes']:>6} lignes x {stats['colonnes_brutes']} colonnes")
    L.append(f"  stations (référentiel): {stats['stations']:>6} stations")
    L.append("")
    L.append("OPÉRATIONS")
    L.append("-" * 66)
    L.append(f"  - curation : 71 colonnes -> {len(config.COLS_ANALYSES)} colonnes utiles")
    L.append(f"  - résultats < seuil de quantif./détection : {stats['pct_sous_seuil']} % (signalés, non confondus avec des mesures)")
    L.append(f"  - analyses « non faites » neutralisées    : {stats['analyses_non_faites']}")
    L.append(f"  - dates+heures converties en datetime")
    L.append(f"  - enrichissement : commune / cours d'eau / région ajoutés par jointure")
    L.append("")
    L.append("SORTIE")
    L.append("-" * 66)
    L.append(f"  table longue nettoyée : {stats['analyses_brutes']} lignes, {stats['colonnes_propres']} colonnes")
    L.append(f"  matrice physico-chimie : {stats['matrice_lignes']} prélèvements x {stats['matrice_parametres']} paramètres")
    L.append(f"  stations couvertes     : {stats['stations_couvertes']}")
    L.append(f"  cours d'eau couverts   : {stats['cours_eau']}")
    L.append("")
    L.append("MÉTHODOLOGIE (traçabilité)")
    L.append("-" * 66)
    L.append("  - 2 matrices distinctes pour ne pas confondre les cas :")
    L.append("      * matrice_physico_chimie.csv         (STRICTE, numérique) : pour les calculs")
    L.append("        -> cellule vide = paramètre non mesuré OU sous seuil")
    L.append("      * matrice_physico_chimie_rapport.csv (RAPPORT, textuelle) : pour la lecture")
    L.append("        -> valeur / « < LQ » (sous seuil) / « non testé » (analyse absente)")
    L.append("  - En-têtes des CSV de données en snake_case ASCII (SQL/BI/Python-safe).")
    L.append(f"  - Règle d'agrégation des duplicats (même station/date/paramètre) : {config.REGLE_AGREGATION.upper()}.")
    L.append(f"    Nombre de cas de duplicats agrégés : {stats['duplicats_agreges']}.")
    L.append("")
    L.append("=" * 66)
    L.append("  20 000 analyses brutes  ->  matrices exploitables, traçables et fiables")
    L.append("=" * 66)
    rapport = "\n".join(L)
    (config.OUTPUT_DIR / "rapport_qualite.txt").write_text(rapport, encoding="utf-8")
    return rapport


def main() -> None:
    print("\n[1/4] Chargement des données réelles Hub'Eau...")
    analyses_raw = consolidate.load_raw(config.FICHIER_ANALYSES, config.COLS_ANALYSES)
    stations_raw = consolidate.load_raw(config.FICHIER_STATIONS, config.COLS_STATIONS)

    t0 = time.perf_counter()

    print("[2/4] Nettoyage (seuils de détection, types, dates)...")
    analyses = consolidate.clean_analyses(analyses_raw)
    stations = consolidate.clean_stations(stations_raw)

    print("[3/4] Enrichissement + pivot long->large...")
    analyses = consolidate.enrich(analyses, stations)
    matrice = consolidate.pivot_strict(analyses)
    matrice_rapport = consolidate.pivot_rapport(analyses)
    duplicats = consolidate.compter_duplicats(analyses)

    duree = time.perf_counter() - t0

    print("[4/4] Rapport + export...")
    stats = {
        "analyses_brutes": len(analyses_raw),
        "colonnes_brutes": 71,
        "colonnes_propres": analyses.shape[1],
        "stations": len(stations),
        "pct_sous_seuil": round(100 * analyses["sous_seuil"].mean(), 1),
        "analyses_non_faites": int(analyses["analyse_non_faite"].sum()),
        "matrice_lignes": len(matrice),
        "matrice_parametres": sum(c in matrice.columns for c in config.PARAMS_PHYSICO.values()),
        "stations_couvertes": int(matrice["station"].nunique()),
        "cours_eau": int(matrice["cours_eau"].nunique()),
        "duplicats_agreges": duplicats,
        "regle_agregation": config.REGLE_AGREGATION,
        "duree_traitement_s": round(duree, 2),
    }

    export(analyses, "analyses_propres")
    export(matrice, "matrice_physico_chimie")
    export(matrice_rapport, "matrice_physico_chimie_rapport")
    (config.OUTPUT_DIR / "stats.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("\n" + build_report(analyses, matrice, stats))
    print(f"\n  Traitement (nettoyage + enrichissement + pivot) : {duree:.2f} s\n")


if __name__ == "__main__":
    main()
