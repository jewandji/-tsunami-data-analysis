# Analyse des Tsunamis Historiques

> Projet final – Data Analysis (MACSIN4A2225) | ESILV

## Équipe

| Nom | Rôle |
|-----|------|
| Mileina Malou | Responsable |
| Jean-Eudes Wandji | Membre |
| Yobe Gnadame | Membre |

---

## Projet
Analyse interactive des données historiques de tsunamis à l'aide d'un dashboard Dash.

## Dataset

**Tsunami Historical Data – NOAA / Kaggle**

- 2 259 événements tsunamigènes recensés
- Période couverte : 330 av. J-C → 2020
- Source : [NOAA Natural Hazards](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/tsunamis) / [Kaggle](https://www.kaggle.com)

### Dimensions multidimensionnelles

| Dimension | Colonnes clés |
|-----------|---------------|
| Temporelle | `YEAR`, `MONTH`, `DAY`, `HOUR`, `MINUTE` |
| Spatiale | `LATITUDE`, `LONGITUDE`, `COUNTRY`, `REGION` |
| Analytique | `CAUSE`, `EQ_MAGNITUDE`, `DEATHS_TOTAL`, `DAMAGE_TOTAL` |

---

## Structure du projet

```
tsunami-data-analysis/
├── data/
│   └── tsunami_dataset.csv          # Dataset NOAA
├── malou_notebook.ipynb           # Notebook principal (KDD complet)
├── dashboard.py                     # Script du dashboard Python Dash
├── malou_dashboard.html  # Export HTML du dashboard
├── malou_slides.pdf        # Slides de présentation
├── README.md
└── .gitignore
```

---

## Indicateurs construits

### Indicateur 1 — Groupement
Top 10 des pays les plus touchés par des tsunamis confirmés.

### Indicateur 2 — Frequent Pattern Mining
Règles d'association entre la cause, la région et le niveau de dégâts via l'algorithme **Apriori**.

### Indicateur 3 — Analyse temporelle
Évolution du nombre de tsunamis confirmés par décennie depuis 1800.

### Indicateur 4 — Analyse spatiale
Clustering géographique des zones à risque avec **DBSCAN**.

---

## Installation

```powershell
python -m pip install dash plotly pandas scikit-learn mlxtend
```

> Optionnel : le script propose aussi une installation automatique des dépendances via `python dashboard.py --install-deps`.

---

## Utilisation

```powershell
python dashboard.py
```

Puis ouvrir le navigateur à l’adresse : `http://127.0.0.1:8050`.

Le script génère également un fichier `malou_dashboard.html` dans le répertoire du projet.

---

## Notes
- Le dataset doit rester présent dans `data/tsunami_dataset.csv`.
- Le dashboard utilise `Dash`, `Plotly`, `pandas`, `scikit-learn` et `mlxtend`.

---

## Usage des LLM

Certaines parties du code ont été développées avec l'assistance de Claude (Anthropic).  
Les prompts sont documentés dans les cellules markdown du notebook.

