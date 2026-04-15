
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from wordcloud import WordCloud
from pywaffle import Waffle
import seaborn as sns
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
import re
import os
import pandas as pd
from IPython.display import display, Markdown

#Lectura y Separación de columnas 

# ------------------------------------------------------------
# LEER ARCHIVO (UNA SOLA COLUMNA)
# ------------------------------------------------------------
df = pd.read_csv("job_salary_prediction_dataset.csv")

# ------------------------------------------------------------
# TOMAR PRIMERA FILA COMO ENCABEZADO Y SEPARAR
# ------------------------------------------------------------
#encabezados = df_raw.iloc[0, 0].split(",")

# ------------------------------------------------------------
# TOMAR DATOS (desde fila 2 en adelante) y separar
# ------------------------------------------------------------
#datos = df_raw.iloc[1:, 0].str.split(",", expand=True)

# Asignar columnas correctas
#datos.columns = encabezados

# Reset index
#df = datos.reset_index(drop=True)

# ------------------------------------------------------------
# LIMPIAR NOMBRES
# ------------------------------------------------------------
#df.columns = df.columns.str.strip()

# ------------------------------------------------------------
# CONVERTIR NUMÉRICAS
# ------------------------------------------------------------
cols_num = [
    "experience_years",
    "skills_count",
    "certifications",
    "salary"
]

for col in cols_num:
     df[col] = pd.to_numeric(df[col], errors="coerce")
 
# ==========================================================
# 🚀 DASHBOARD FINAL 
# ==========================================================

from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd

# ==========================================================
# ASEGURAR NUMÉRICAS
# ==========================================================
for c in ["experience_years","skills_count","certifications","salary"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

FONT = "Montserrat, sans-serif"

# ==========================================================
# APP
# ==========================================================
app = Dash(__name__)

# ==========================================================
# LAYOUT
# ==========================================================
app.layout = html.Div([

# ----------------------------------------------------------
# HEADER
# ----------------------------------------------------------
html.H1(
    "🚀 Mi Futuro Tech",
    style={
        "textAlign":"center",
        "fontFamily":FONT,
        "fontWeight":"800",
        "fontSize":"44px",
        "color":"white",
        "textShadow":"2px 2px 8px rgba(0,0,0,.35)",
        "marginBottom":"5px"
    }
),

html.P(
    "Descubre carreras, empleabilidad e ingresos para decidir mejor tu futuro",
    style={
        "textAlign":"center",
        "fontFamily":FONT,
        "fontWeight":"600",
        "fontSize":"18px",
        "color":"white",
        "textShadow":"1px 1px 5px rgba(0,0,0,.35)",
        "marginBottom":"25px"
    }
),

# ----------------------------------------------------------
# FILTROS
# ----------------------------------------------------------
html.Div([

dcc.Dropdown(
    id="f1",
    options=[{"label":i,"value":i} for i in sorted(df["job_title"].dropna().unique())],
    multi=True,
    placeholder="🎓 Carrera",
    style={"fontFamily":FONT}
),

dcc.Dropdown(
    id="f2",
    options=[{"label":i,"value":i} for i in sorted(df["location"].dropna().unique())],
    multi=True,
    placeholder="🌍 País",
    style={"fontFamily":FONT}
),

dcc.Dropdown(
    id="f3",
    options=[{"label":i,"value":i} for i in sorted(df["education_level"].dropna().unique())],
    multi=True,
    placeholder="📚 Educación",
    style={"fontFamily":FONT}
),

dcc.Dropdown(
    id="f4",
    options=[{"label":i,"value":i} for i in sorted(df["remote_work"].dropna().unique())],
    multi=True,
    placeholder="💻 Modalidad",
    style={"fontFamily":FONT}
),

], style={
    "display":"grid",
    "gridTemplateColumns":"repeat(4,1fr)",
    "gap":"12px",
    "marginBottom":"20px"
}),

# ----------------------------------------------------------
# KPI
# ----------------------------------------------------------
html.Div(id="cards", style={
    "display":"grid",
    "gridTemplateColumns":"repeat(4,1fr)",
    "gap":"14px",
    "marginBottom":"20px"
}),

# ----------------------------------------------------------
# MAPA GRANDE PRINCIPAL
# ----------------------------------------------------------
dcc.Graph(id="g_map", style={"height":"620px"}),

# ----------------------------------------------------------
# FILA 1
# ----------------------------------------------------------
html.Div([
    dcc.Graph(id="g1"),
    dcc.Graph(id="g2"),
    dcc.Graph(id="g3"),
], style={
    "display":"grid",
    "gridTemplateColumns":"1fr 1fr 1fr",
    "gap":"12px",
    "marginTop":"10px"
}),

# ----------------------------------------------------------
# FILA 2
# ----------------------------------------------------------
html.Div([
    dcc.Graph(id="g4"),
    dcc.Graph(id="g5"),
    dcc.Graph(id="g6"),
], style={
    "display":"grid",
    "gridTemplateColumns":"1fr 1fr 1fr",
    "gap":"12px",
    "marginTop":"10px"
}),

# ----------------------------------------------------------
# FILA 3
# ----------------------------------------------------------
html.Div([
    dcc.Graph(id="g7"),
], style={"marginTop":"10px"})

],
style={
    "backgroundImage":"url('https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=1800&q=80')",
    "backgroundSize":"cover",
    "backgroundPosition":"center",
    "backgroundRepeat":"no-repeat",
    "minHeight":"100vh",
    "padding":"20px",
    "fontFamily":FONT
}
)

# ==========================================================
# CALLBACK
# ==========================================================
@app.callback(
Output("cards","children"),
Output("g_map","figure"),
Output("g1","figure"),
Output("g2","figure"),
Output("g3","figure"),
Output("g4","figure"),
Output("g5","figure"),
Output("g6","figure"),
Output("g7","figure"),

Input("f1","value"),
Input("f2","value"),
Input("f3","value"),
Input("f4","value"),
)
def actualizar(a,b,c,d):

    dff = df.copy()

    if a: dff = dff[dff["job_title"].isin(a)]
    if b: dff = dff[dff["location"].isin(b)]
    if c: dff = dff[dff["education_level"].isin(c)]
    if d: dff = dff[dff["remote_work"].isin(d)]

    if dff.empty:
        dff = df.copy()

# ----------------------------------------------------------
# KPI
# ----------------------------------------------------------
    salario_promedio = dff["salary"].mean()

    top_job = (
        dff.groupby("job_title")["salary"]
        .mean()
        .sort_values(ascending=False)
        .index[0]
    )

    top_country = (
        dff.groupby("location")["salary"]
        .mean()
        .sort_values(ascending=False)
        .index[0]
    )

    pct_remote = (
        dff["remote_work"]
        .astype(str)
        .str.lower()
        .isin(["yes"])
        .mean() * 100
    )

    def tarjeta(titulo, valor, color):
        return html.Div([
            html.H4(titulo, style={"marginBottom":"8px","color":"white"}),
            html.H2(valor, style={"margin":"0","color":"white"})
        ], style={
            "background":color,
            "padding":"20px",
            "borderRadius":"18px",
            "textAlign":"center",
            "fontFamily":FONT,
            "boxShadow":"0 4px 10px rgba(0,0,0,.25)"
        })

    cards = [
        tarjeta("💰 Salario Promedio", f"${salario_promedio:,.0f}", "#1abc9c"),
        tarjeta("🚀 Mejor Carrera", top_job, "#3498db"),
        tarjeta("🌍 Mejor País", top_country, "#9b59b6"),
        tarjeta("🏠 % Remoto", f"{pct_remote:.1f}%", "#e67e22"),
    ]

# ----------------------------------------------------------
# MAPA
# ----------------------------------------------------------
    country_salary = (
        dff.groupby("location")["salary"]
        .mean()
        .reset_index()
    )

    g_map = px.scatter_geo(
        country_salary,
        locations="location",
        locationmode="country names",
        size="salary",
        color="salary",
        hover_name="location",
        projection="natural earth",
        title="🌍 Salario promedio por país",
        size_max=40,
        color_continuous_scale="Viridis"
    )

# ----------------------------------------------------------
# TOP CARRERAS
# ----------------------------------------------------------
    top_jobs = (
        dff.groupby("job_title")["salary"]
        .mean()
        .reset_index()
        .sort_values("salary", ascending=False)
        .head(10)
    )

    g1 = px.bar(
        top_jobs,
        x="salary",
        y="job_title",
        orientation="h",
        color="salary",
        text="salary",
        title="💼 Top carreras mejor pagadas"
    )

# ----------------------------------------------------------
# EXPERIENCIA
# ----------------------------------------------------------
    df_exp = (
        dff.groupby("experience_years")["salary"]
        .mean()
        .reset_index()
    )

    g2 = px.line(
        df_exp,
        x="experience_years",
        y="salary",
        markers=True,
        title="📈 Experiencia e impacto en el Salario"
    )

# ----------------------------------------------------------
# EDUCACIÓN
# ----------------------------------------------------------
    orden_educacion = [
        "High School","Diploma","Bachelor","Master","PhD"
    ]

    g3 = px.box(
        dff,
        x="education_level",
        y="salary",
        color="education_level",
        category_orders={"education_level": orden_educacion},
        title="🎓 Impacto del nivel educativo"
    )

# ----------------------------------------------------------
# MODALIDAD PIE
# ----------------------------------------------------------
    df_pie = dff["remote_work"].value_counts().reset_index()
    df_pie.columns = ["modalidad","cantidad"]

    g4 = px.pie(
        df_pie,
        names="modalidad",
        values="cantidad",
        hole=0.45,
        title="🏠 Modalidades de trabajo"
    )

# ----------------------------------------------------------
# INDUSTRIA TREEMAP
# ----------------------------------------------------------
    df_industry = (
        dff.groupby("industry")["salary"]
        .mean()
        .reset_index()
    )

    g5 = px.treemap(
        df_industry,
        path=["industry"],
        values="salary",
        color="salary",
        color_continuous_scale="Viridis",
        title="🏭 Salario por industria"
    )

# ----------------------------------------------------------
# HABILIDADES
# ----------------------------------------------------------
    df_skills = (
        dff.groupby("skills_count")
        .agg(
            salario_promedio=("salary","mean"),
            cantidad_personas=("salary","count")
        )
        .reset_index()
    )

    g6 = px.scatter(
        df_skills,
        x="skills_count",
        y="salario_promedio",
        size="cantidad_personas",
        title="🧠 Habilidades e impacto en el Salario"
    )

# ----------------------------------------------------------
# EXTRA BOX MODALIDAD
# ----------------------------------------------------------
    g7 = px.box(
        dff,
        x="remote_work",
        y="salary",
        color="remote_work",
        title="💻 Salario según modalidad"
    )

# ----------------------------------------------------------
# ESTILO GENERAL
# ----------------------------------------------------------
    figs = [g_map,g1,g2,g3,g4,g5,g6,g7]

    for fig in figs:
        fig.update_layout(
            font_family=FONT,
            paper_bgcolor="rgba(255,255,255,.55)",
            plot_bgcolor="rgba(255,255,255,.18)",
            title_x=0.5,
            margin=dict(l=20,r=20,t=55,b=20)
        )

    g_map.update_layout(height=620)

    return cards,g_map,g1,g2,g3,g4,g5,g6,g7

# ==========================================================
# RUN
# ==========================================================
app.run(debug=True, port=8050)