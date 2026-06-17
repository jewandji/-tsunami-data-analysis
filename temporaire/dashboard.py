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
# Output   : fig (plotly Figure) - distribution des causes

def build_indicator2_figure(df):
    """
    Indicateur 2 (pattern mining) : distribution des causes
    des tsunamis. Sert de support visuel aux regles d'association
    calculees dans le notebook (cause x region x degats).
    """
    cause_counts = df['CAUSE'].value_counts().reset_index()
    cause_counts.columns = ['CAUSE', 'COUNT']
    fig = px.pie(
        cause_counts, values='COUNT', names='CAUSE',
        title='Indicateur 2 - Distribution des causes des tsunamis',
        hole=0.3
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
# Output   : fig (plotly Figure) - carte mondiale des tsunamis

def build_indicator4_figure(df):
    """
    Indicateur 4 (spatial) : carte mondiale des tsunamis,
    coloree par cause. Sert de support visuel au clustering
    DBSCAN realise dans le notebook.
    """
    df_map = df[df['LATITUDE'].notna() & df['LONGITUDE'].notna()].copy()
    fig = px.scatter_geo(
        df_map, lat='LATITUDE', lon='LONGITUDE',
        color='CAUSE', hover_name='COUNTRY',
        hover_data={'YEAR': True, 'EQ_MAGNITUDE': True},
        title='Indicateur 4 - Carte mondiale des tsunamis par cause',
        projection='natural earth'
    )
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
                'Equipe : Mileina Malou (responsable), Yobe Gnadame, Jean-Eudes Wandji',
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

    with open('familyNameLeader_dashboard.html', 'w') as f:
        f.write(html_content)

    return app


# Bloc principal

if __name__ == "__main__":
    FILE_PATH = "/content/tsunami_dataset.csv"  # Modifier si necessaire
    df = load_data(FILE_PATH)
    app = build_dashboard(df)
    print("Dashboard lance sur http://127.0.0.1:8050")
    app.run(debug=False, port=8050)
