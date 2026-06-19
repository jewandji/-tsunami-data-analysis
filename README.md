# Analyse des Tsunamis Historiques

> Projet final — Data Analysis (MACSIN4A2225) | Hugo ALATRISTA-SALAS | ESILV

## Équipe

| Nom | Rôle |
|-----|------|
| Mileina Malou | Responsable |
| Jean-Eudes Wandji | Membre |
| Yobe Gnadame | Membre |

---

## Dataset

**Tsunami Historical Data — NOAA / Kaggle**

- 2 259 événements tsunamigènes recensés
- Période couverte : 330 av. J-C → 2020
- Source : [NOAA Natural Hazards](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/tsunamis) / [Kaggle](https://www.kaggle.com)

### Dimensions multidimensionnelles

| Dimension | Colonnes clés |
|-----------|--------------|
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
Méthode : `groupby('COUNTRY').size().sort_values().head(10)`

### Indicateur 2 — Frequent Pattern Mining
Règles d'association entre la cause, la région et le niveau de dégâts via l'algorithme **Apriori**.  
Paramètres : `min_support=0.05`, `min_confidence=0.40`, tri par lift.  
Exemple : *Earthquake + Pacific → Damage Extreme* (lift 2.3)

### Indicateur 3 — Analyse temporelle
Évolution du nombre de tsunamis confirmés par décennie depuis 1800, avec prévision par **régression polynomiale** (degré 2) sur 3 décennies.

### Indicateur 4 — Analyse spatiale
Clustering géographique des zones à risque avec **DBSCAN** (`eps=5.0°`, `min_samples=5`).  
Résultats : 4 clusters principaux identifiés (Japon/Russie, Indonésie/Philippines, Chili/Pérou, côte Pacifique USA) + carte interactive Folium.

---

## Installation

```bash
# 1. Cloner le repo
git clone https://github.com/jewandji/tsunami-data-analysis-l.git
cd tsunami-data-analysis-l

# 2. Installer les dépendances
pip install pandas numpy matplotlib seaborn folium scikit-learn mlxtend dash plotly

# 3. Lancer le notebook
jupyter notebook tsunami_notebook.ipynb

# 4. Lancer le dashboard (dans un terminal séparé)
python dashboard.py
# puis ouvrir http://127.0.0.1:8050
```

---

## Dashboard

Le dashboard Python Dash affiche les 4 indicateurs de manière interactive :

- **Ind. 1** — Bar chart horizontal : Top 10 pays
- **Ind. 2** — Tableau Apriori : Top 10 règles (support / confiance / lift)
- **Ind. 3** — Bar chart : évolution par décennie + prévision
- **Ind. 4** — Carte scatter_geo : clusters DBSCAN colorés par zone

Un export statique est disponible dans `malou_dashboard.html`.

---

## Usage des LLM

Certaines parties du code ont été développées avec l'assistance de **Claude (Anthropic)**.  
Les prompts sont documentés dans les cellules markdown du notebook.
