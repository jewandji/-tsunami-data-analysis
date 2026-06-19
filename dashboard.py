# Dashboard interactif - Analyse des Tsunamis Historiques
# Data Analysis (MACSIN4A2225) - Projet Final
#
# Membres de l'équipe :
#   - Mileina Malou
#   - Jean-Eudes Wandji
#   - Yobe GNADAME
#
# Dataset : Tsunami Historical Data (NOAA / Kaggle)
#
# Pour lancer ce dashboard :
#   pip install dash plotly pandas
#   python dashboard.py
#   puis ouvrir http://127.0.0.1:8050 dans le navigateur

import pandas as pd
import sys
import subprocess

# Liste des dependances requises
REQUIREMENTS = ["dash", "plotly", "pandas"]

def install_requirements():
    """Tentative d'installation automatique des dependances via pip."""
    cmd = [sys.executable, "-m", "pip", "install"] + REQUIREMENTS
    subprocess.check_call(cmd)


if "--install-deps" in sys.argv:
    try:
        print("Installation des dependances...")
        install_requirements()
        print("Installation terminee. Relancer le script normalement.")
    except Exception as e:
        print("Echec de l'installation automatique:", e)
    sys.exit(0)


try:
    import dash
    from dash import dcc, html
except ModuleNotFoundError as e:
    print("Missing dependency:", e)
    print("Installez les dependances requises puis relancez:")
    print("    pip install -r requirements.txt")
    print("Ou relancer avec l'option d'installation automatique:")
    print("    python dashboard.py --install-deps")
    sys.exit(1)
import plotly.express as px



# Fonction : load_data
# Input    : file_path (str) - chemin vers le fichier CSV
# Output   : df (DataFrame) - donnees brutes chargees

def load_data(file_path):
    """Charge le dataset tsunami dans un DataFrame pandas."""
    return pd.read_csv(file_path)


# Fonction : build_indicator1_figure
# Input    : df (DataFrame) - donnees nettoyees
# Output   : fig (plotly Figure) - top 10 pays (groupement)

def build_indicator1_figure(df):
    """
    Indicateur 1 (groupement) : Top 10 des pays les plus touches
    par des tsunamis confirmes ('Definite Tsunami').
    """
    definite = df[df['EVENT_VALIDITY'] == 'Definite Tsunami']
    top_countries = (
        definite.groupby('COUNTRY').size()
        .reset_index(name='NB_TSUNAMIS')
        .sort_values('NB_TSUNAMIS', ascending=False)
        .head(10)
    )
    fig = px.bar(
        top_countries, x='NB_TSUNAMIS', y='COUNTRY',
        orientation='h', color='NB_TSUNAMIS',
        color_continuous_scale='Reds',
        title='Indicateur 1 - Top 10 pays (tsunamis confirmes)',
        labels={'NB_TSUNAMIS': 'Nombre de tsunamis', 'COUNTRY': 'Pays'}
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    return fig



# Fonction : build_indicator2_figure
# Input    : df (DataFrame) - donnees nettoyees
# Output   : fig (plotly Figure) - top 10 regles d'association (Apriori)

def build_indicator2_figure(df):
    """
    Indicateur 2 (pattern mining) : applique l'algorithme Apriori sur
    les variables CAUSE x REGION x DAMAGE_TOTAL_DESCRIPTION et affiche
    les 10 meilleures regles d'association triees par lift dans un tableau.
    """
    from mlxtend.frequent_patterns import apriori, association_rules
    from mlxtend.preprocessing import TransactionEncoder
    import plotly.graph_objects as go

    # Preparation des transactions
    cols_needed = ['CAUSE', 'REGION', 'DAMAGE_TOTAL_DESCRIPTION']
    df_clean = df[cols_needed].dropna().copy()

    def simplify_cause(cause):
        if 'Earthquake' in str(cause): return 'Cause_Earthquake'
        elif 'Volcano' in str(cause): return 'Cause_Volcano'
        elif 'Landslide' in str(cause): return 'Cause_Landslide'
        else: return 'Cause_Other'

    def simplify_region(region):
        if 'Japan' in str(region): return 'Region_Japan'
        elif 'Pacific' in str(region): return 'Region_Pacific'
        elif 'Mediterranean' in str(region): return 'Region_Mediterranean'
        elif 'Atlantic' in str(region): return 'Region_Atlantic'
        elif 'Indian Ocean' in str(region): return 'Region_IndianOcean'
        elif 'America' in str(region) or 'Caribbean' in str(region): return 'Region_Americas'
        else: return 'Region_Other'

    def format_damage(d):
        return 'Damage_' + str(d).replace(' ', '_').replace('(', '').replace(')', '').replace('~', '').replace('$', '').replace('>', '').strip()

    df_clean['CAUSE_S']  = df_clean['CAUSE'].apply(simplify_cause)
    df_clean['REGION_S'] = df_clean['REGION'].apply(simplify_region)
    df_clean['DAMAGE_S'] = df_clean['DAMAGE_TOTAL_DESCRIPTION'].apply(format_damage)

    transactions = df_clean[['CAUSE_S', 'REGION_S', 'DAMAGE_S']].values.tolist()
    te = TransactionEncoder()
    encoded_df = pd.DataFrame(te.fit_transform(transactions), columns=te.columns_)

    # Apriori + regles d'association
    frequent_items = apriori(encoded_df, min_support=0.05, use_colnames=True)
    rules = association_rules(frequent_items, metric='confidence', min_threshold=0.4)
    rules = rules.sort_values('lift', ascending=False).head(10)

    # Formatage pour affichage
    antecedents = rules['antecedents'].apply(lambda x: ', '.join(list(x)))
    consequents = rules['consequents'].apply(lambda x: ', '.join(list(x)))

    fig = go.Figure(data=[go.Table(
        columnwidth=[250, 200, 80, 80, 70],
        header=dict(
            values=['<b>Si... (antecedent)</b>', '<b>Alors... (consequent)</b>',
                    '<b>Support</b>', '<b>Confiance</b>', '<b>Lift</b>'],
            fill_color='#2c3e50',
            font=dict(color='white', size=12),
            align='left',
            height=32
        ),
        cells=dict(
            values=[
                antecedents.tolist(),
                consequents.tolist(),
                rules['support'].round(3).tolist(),
                rules['confidence'].round(3).tolist(),
                rules['lift'].round(2).tolist()
            ],
            fill_color=[['#f9f9f9' if i % 2 == 0 else 'white' for i in range(len(rules))]],
            align='left',
            font=dict(size=11),
            height=28
        )
    )])
    fig.update_layout(
        title='Indicateur 2 - Top 10 regles d\'association (Apriori, triees par lift)',
        margin=dict(l=10, r=10, t=40, b=10)
    )
    return fig



# Fonction : build_indicator3_figure
# Input    : df (DataFrame) - donnees nettoyees
#            start_year (int) - annee de debut de l'analyse
# Output   : fig (plotly Figure) - evolution par decennie

def build_indicator3_figure(df, start_year=1800):
    """
    Indicateur 3 (temporel) : evolution du nombre de tsunamis
    confirmes par decennie depuis start_year.
    """
    df_temp = df[(df['YEAR'] >= start_year) &
                  (df['EVENT_VALIDITY'] == 'Definite Tsunami')].copy()
    df_temp['DECADE'] = (df_temp['YEAR'] // 10) * 10
    decade_counts = df_temp.groupby('DECADE').size().reset_index(name='NB_TSUNAMIS')

    fig = px.bar(
        decade_counts, x='DECADE', y='NB_TSUNAMIS',
        title=f'Indicateur 3 - Evolution par decennie (depuis {start_year})',
        labels={'DECADE': 'Decennie', 'NB_TSUNAMIS': 'Nombre de tsunamis'},
        color='NB_TSUNAMIS', color_continuous_scale='Blues'
    )
    return fig


# Fonction : build_indicator4_figure
# Input    : df (DataFrame) - donnees nettoyees
# Output   : fig (plotly Figure) - carte mondiale avec clusters DBSCAN

def build_indicator4_figure(df):
    """
    Indicateur 4 (spatial) : reproduit le clustering DBSCAN du notebook
    et affiche les clusters sur une carte mondiale Plotly scatter_geo.
    Chaque couleur correspond a un cluster DBSCAN (zone a risque).
    Les points noirs sont les evenements isoles (bruit DBSCAN).
    """
    from sklearn.cluster import DBSCAN

    # Filtrer les tsunamis confirmes avec coordonnees valides
    df_spatial = df[
        (df['EVENT_VALIDITY'] == 'Definite Tsunami') &
        df['LATITUDE'].notna() & df['LONGITUDE'].notna()
    ].copy()

    # Application de DBSCAN (memes parametres que le notebook)
    coords = df_spatial[['LATITUDE', 'LONGITUDE']].values
    db = DBSCAN(eps=5.0, min_samples=5, metric='euclidean').fit(coords)
    df_spatial['CLUSTER'] = db.labels_

    n_clusters = len(set(db.labels_)) - (1 if -1 in db.labels_ else 0)

    # Colonne d'affichage : "Bruit" pour les points isoles, "Cluster N" sinon
    df_spatial['CLUSTER_LABEL'] = df_spatial['CLUSTER'].apply(
        lambda x: 'Bruit (isole)' if x == -1 else f'Cluster {x}'
    )

    fig = px.scatter_geo(
        df_spatial,
        lat='LATITUDE',
        lon='LONGITUDE',
        color='CLUSTER_LABEL',
        hover_name='COUNTRY',
        hover_data={'YEAR': True, 'CAUSE': True, 'CLUSTER_LABEL': False},
        title=f'Indicateur 4 - Clustering spatial DBSCAN ({n_clusters} zones a risque identifiees)',
        projection='natural earth',
        opacity=0.7
    )
    fig.update_traces(marker=dict(size=4))
    fig.update_layout(legend_title_text='Cluster DBSCAN')
    return fig



# Fonction : build_dashboard
# Input    : df (DataFrame) - donnees nettoyees
# Output   : app (dash.Dash) - application Dash prete a lancer

def build_dashboard(df):
    """Construit l'application Dash avec les 4 indicateurs."""

    fig1 = build_indicator1_figure(df)
    fig2 = build_indicator2_figure(df)
    fig3 = build_indicator3_figure(df)
    fig4 = build_indicator4_figure(df)

    app = dash.Dash(__name__)

    app.layout = html.Div([

        # En-tete : titre, dataset, membres de l'equipe
        html.Div([
            html.H1(
                'Dashboard - Analyse des Tsunamis Historiques',
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '5px'}
            ),
            html.P(
                'Dataset : Tsunami Historical Data (NOAA / Kaggle)',
                style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': '14px', 'margin': '2px'}
            ),
            html.P(
                'Equipe : Mileina Malou (responsable), Jean-Eudes Wandji, Yobe Gnadame',
                style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': '14px', 'margin': '2px'}
            ),
        ], style={'backgroundColor': '#ecf0f1', 'padding': '20px', 'marginBottom': '20px'}),

        # Ligne 1 : Indicateurs 1 et 2
        html.Div([
            html.Div(dcc.Graph(figure=fig1),
                     style={'width': '55%', 'display': 'inline-block', 'padding': '10px'}),
            html.Div(dcc.Graph(figure=fig2),
                     style={'width': '43%', 'display': 'inline-block', 'padding': '10px'}),
        ]),

        # Ligne 2 : Indicateurs 3 et 4
        html.Div([
            html.Div(dcc.Graph(figure=fig3),
                     style={'width': '45%', 'display': 'inline-block', 'padding': '10px'}),
            html.Div(dcc.Graph(figure=fig4),
                     style={'width': '53%', 'display': 'inline-block', 'padding': '10px'}),
        ]),

    ], style={'fontFamily': 'Arial, sans-serif', 'maxWidth': '1400px', 'margin': '0 auto'})

    from plotly.offline import plot
    import plotly.graph_objects as go

    html_content = "<h1>Dashboard Tsunami - Preuve de fonctionnement</h1>"
    for fig in [fig1, fig2, fig3, fig4]:
        html_content += plot(fig, output_type='div', include_plotlyjs='cdn')

    with open('malou_dashboard.html', 'w') as f:
        f.write(html_content)

    return app


# Bloc principal

if __name__ == "__main__":
    FILE_PATH = "data/tsunami_dataset.csv"  # chemin relatif au repo
    df = load_data(FILE_PATH)
    app = build_dashboard(df)
    print("Dashboard lance sur http://127.0.0.1:8050")
    app.run(debug=False, port=8050)
