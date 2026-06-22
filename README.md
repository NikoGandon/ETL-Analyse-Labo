# ETL analyses de labo (Hub'Eau)

Pipeline Python pour nettoyer des analyses physico-chimiques au format long et produire une matrice prelevement x parametre.

Donnees : [Hub'Eau](https://hubeau.eaufrance.fr/), departement 37, 2023.

## Ce que fait le script

- curation des colonnes (71 -> 13 utiles)
- gestion des resultats sous seuil de quantification
- distinction "non teste" / "< LQ" / valeur quantifiee
- enrichissement via le referentiel stations
- pivot long -> large (2 matrices : calcul numerique + rapport textuel)
- rapport qualite avec regle d'agregation des duplicats

## Installation

```bash
pip install -r requirements.txt
```

## Donnees d'entree

Place les fichiers dans `raw/` :

```
raw/analyses_pc_37_2023.csv
raw/stations_pc_37.csv
```

Tu peux les recuperer via l'API Hub'Eau (analyses physico-chimiques + stations, dept 37).

## Lancement

```bash
python main.py
```

Sorties dans `output/` :

- `analyses_propres.csv` (format long nettoye)
- `matrice_physico_chimie.csv` (numerique, pour calculs)
- `matrice_physico_chimie_rapport.csv` (textuelle, pour lecture)
- `rapport_qualite.txt`
- `stats.json`

Visuel portfolio (HTML) :

```bash
python showcase.py
```

Genere `output/vitrine_avant_apres.html`.

## Resultats (2023, dept 37)

| | |
|---|---|
| Entree | 20 000 analyses, 71 colonnes |
| Sortie | 91 prelevements x 12 parametres |
| Sous seuil | 86,6 % (geres sans confusion avec "non teste") |
| Traitement | ~0,23 s |

## Structure

```
config.py       # chemins, parametres, regles d'agregation
consolidate.py  # nettoyage, enrichissement, pivot
main.py         # orchestration
showcase.py     # visuel HTML avant/apres
```
