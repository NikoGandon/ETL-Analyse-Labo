"""Visuels avant/apres pour le portfolio (demo Hub'Eau).
Usage : python showcase.py (apres main.py)
"""

import json

import matplotlib.pyplot as plt
import pandas as pd

import config

N_LIGNES = 12
# Colonnes affichees
COLS_AFFICHEES = [
    "date_prelevement", "station", "cours_eau",
    "ph", "temperature_c", "conductivite_us_cm", "o2_dissous_mg_l",
    "nitrates_mg_l", "mes_mg_l",
]


def _matrice() -> pd.DataFrame:
    # matrice rapport (avec "< LQ" / "non teste")
    path = config.OUTPUT_DIR / "matrice_physico_chimie_rapport.csv"
    if not path.exists():
        raise FileNotFoundError("Lance main.py d'abord.")
    return pd.read_csv(path, dtype=str)


def _extrait(matrice: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in COLS_AFFICHEES if c in matrice.columns]
    ext = matrice[cols].head(N_LIGNES).copy()
    # vide = parametre pas demande
    ext = ext.fillna("non testé")
    ext = ext.rename(columns=config.LABELS_AFFICHAGE)
    return ext.astype(str)


def _table(ax, df, titre, header_color="#0ea5e9"):
    ax.axis("off")
    ax.set_title(titre, fontsize=13, fontweight="bold", loc="left", pad=10)
    t = ax.table(cellText=df.values, colLabels=df.columns, cellLoc="center", loc="upper left")
    t.auto_set_font_size(False)
    t.set_fontsize(8.5)
    t.scale(1, 1.5)
    t.auto_set_column_width(col=list(range(len(df.columns))))
    for (row, _c), cell in t.get_celld().items():
        cell.set_edgecolor("#d9dee3")
        if row == 0:
            cell.set_facecolor(header_color)
            cell.set_text_props(color="white", fontweight="bold")
        elif row % 2 == 0:
            cell.set_facecolor("#f1f7fb")


def _stats() -> dict:
    p = config.OUTPUT_DIR / "stats.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def vitrine_apres(ext):
    fig, ax = plt.subplots(figsize=(13, 4.5))
    _table(ax, ext, "Analyses 2023 - nettoyees et enrichies")
    fig.tight_layout()
    fig.savefig(config.OUTPUT_DIR / "vitrine_apres.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def vitrine_avant_apres(ext):
    brut = []
    with open(config.FICHIER_ANALYSES, encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= 3:
                break
            brut.append(line.rstrip("\n")[:120] + " …")
    texte_brut = "\n".join(brut)

    s = _stats()
    metrique = (
        f"{s.get('analyses_brutes', '?'):,} analyses brutes (71 col, "
        f"{s.get('pct_sous_seuil', '?')} % sous seuil) -> matrice "
        f"{s.get('matrice_lignes', '?')} x {s.get('matrice_parametres', '?')} "
        f"en {s.get('duree_traitement_s', '?')} s"
    ).replace(",", " ")

    fig = plt.figure(figsize=(13, 8))
    gs = fig.add_gridspec(2, 1, height_ratios=[1, 2.1], hspace=0.3)

    ax_a = fig.add_subplot(gs[0])
    ax_a.axis("off")
    ax_a.set_title("AVANT - CSV brut : 71 colonnes, codes, unites melees, 85 % < seuil",
                   fontsize=12.5, fontweight="bold", loc="left", color="#b91c1c")
    ax_a.text(0.0, 0.8, texte_brut, family="monospace", fontsize=7.5, va="top", ha="left",
              transform=ax_a.transAxes,
              bbox=dict(boxstyle="round,pad=0.6", facecolor="#fef2f2", edgecolor="#fca5a5"))

    ax_b = fig.add_subplot(gs[1])
    _table(ax_b, ext, "APRES - 1 ligne = 1 prelevement, 1 colonne = 1 parametre")

    fig.suptitle(metrique, fontsize=14, fontweight="bold", y=0.99)
    fig.savefig(config.OUTPUT_DIR / "vitrine_avant_apres.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def main():
    ext = _extrait(_matrice())
    vitrine_apres(ext)
    vitrine_avant_apres(ext)
    print("Visuels générés : output/vitrine_apres.png, output/vitrine_avant_apres.png")


if __name__ == "__main__":
    main()
