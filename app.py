import os
import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output

# ==========================================================
# DATA
# ==========================================================
df = pd.read_csv("job_salary_prediction_dataset.csv")

# Orden educación
orden_educacion = [
    "High School",
    "Associate",
    "Bachelor",
    "Master",
    "PhD"
]
df["education_level"] = pd.Categorical(
    df["education_level"],
    categories=orden_educacion,
    ordered=True
)

# Modalidad remoto/presencial
df["remote_work"] = df["remote_work"].map({
    "Yes": "Remoto",
    "No": "Presencial",
    "Hybrid": "Hibrido"
})
df["remote_work"] = df["remote_work"].fillna("Desconocido")

# Asegurar numéricas
for c in ["experience_years", "skills_count", "certifications", "salary"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

FONT = "Montserrat, sans-serif"

# ==========================================================
# APP
# ==========================================================
app = Dash(__name__)

# ==========================================================
# LAYOUT
# ==========================================================
app.layout = html.Div([

    # HEADER
    html.Div([
        html.Img(
            src="/assets/futurista.png",
            style={
                "width": "60px",
                "marginRight": "12px",
                "filter": "drop-shadow(0 0 10px #00eaff)"
            }
        ),
        html.H1(
            "Mi Futuro Tech",
            style={
                "fontFamily": FONT,
                "fontWeight": "800",
                "fontSize": "44px",
                "color": "white",
                "textShadow": "2px 2px 8px rgba(0,0,0,.35)",
                "margin": "0"
            }
        )
    ], style={
        "display": "flex",
        "justifyContent": "center",
        "alignItems": "center",
        "marginBottom": "5px"
    }),

    html.P(
        "Descubre carreras, empleabilidad e ingresos anuales para decidir mejor tu futuro",
        style={
            "textAlign": "center",
            "fontFamily": FONT,
            "fontWeight": "600",
            "fontSize": "18px",
            "color": "white",
            "textShadow": "1px 1px 5px rgba(0,0,0,.35)",
            "marginBottom": "10px"
        }
    ),

    html.P(
        "Nota: todos los salarios mostrados corresponden a montos anuales.",
        style={
            "textAlign": "center",
            "fontFamily": FONT,
            "fontSize": "14px",
            "color": "#e0e0e0",
            "marginBottom": "25px"
        }
    ),

    # FILTROS
    html.Div([
        dcc.Dropdown(
            id="f1",
            options=[{"label": i, "value": i} for i in sorted(df["job_title"].dropna().unique())],
            multi=True,
            placeholder="🎓 Carrera",
            style={"fontFamily": FONT}
        ),

        dcc.Dropdown(
            id="f2",
            options=[{"label": i, "value": i} for i in sorted(df["location"].dropna().unique())],
            multi=True,
            placeholder="🌍 País",
            style={"fontFamily": FONT}
        ),

        dcc.Dropdown(
            id="f3",
            options=[{"label": i, "value": i} for i in orden_educacion],
            multi=True,
            placeholder="📚 Educación",
            style={"fontFamily": FONT}
        ),

        dcc.Dropdown(
            id="f4",
            options=[{"label": i, "value": i} for i in sorted(df["remote_work"].dropna().unique())],
            multi=True,
            placeholder="💻 Modalidad",
            style={"fontFamily": FONT}
        ),
    ], style={
        "display": "grid",
        "gridTemplateColumns": "repeat(4,1fr)",
        "gap": "12px",
        "marginBottom": "10px"
    }),

    # KPI
    html.Div(id="cards", style={
        "display": "grid",
        "gridTemplateColumns": "repeat(4,1fr)",
        "gap": "14px",
        "marginBottom": "20px"
    }),
        # SWITCH MAPA
    html.Div([
        dcc.RadioItems(
            id="map_mode",
            options=[
                {"label": "🌐 Puntos", "value": "scatter"},
                {"label": "🗺️ Coroplético", "value": "choropleth"}
            ],
            value="scatter",
            inline=True,
            style={
                "color": "white",
                "fontFamily": FONT,
                "marginBottom": "15px"
            }
        )
    ]),

    # MAPA
    dcc.Graph(id="g_map", style={"height": "620px"}),

    # FILA 1
    html.Div([
        dcc.Graph(id="g1"),
        dcc.Graph(id="g2"),
        dcc.Graph(id="g3"),
    ], style={
        "display": "grid",
        "gridTemplateColumns": "1fr 1fr 1fr",
        "gap": "12px",
        "marginTop": "10px"
    }),

    # FILA 2
    html.Div([
        dcc.Graph(id="g4"),
        dcc.Graph(id="g5"),
        dcc.Graph(id="g6"),
    ], style={
        "display": "grid",
        "gridTemplateColumns": "1fr 1fr 1fr",
        "gap": "12px",
        "marginTop": "10px"
    }),

    # FILA 3
    html.Div([
        dcc.Graph(id="g7"),
    ], style={"marginTop": "10px"})

], style={
    "backgroundImage": "url('https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=1800&q=80')",
    "backgroundSize": "cover",
    "backgroundPosition": "center",
    "backgroundRepeat": "no-repeat",
    "minHeight": "100vh",
    "padding": "20px",
    "fontFamily": FONT
})

# ==========================================================
# CALLBACK FINAL
# ==========================================================
@app.callback(
    [
        Output("cards", "children"),
        Output("g_map", "figure"),
        Output("g1", "figure"),
        Output("g2", "figure"),
        Output("g3", "figure"),
        Output("g4", "figure"),
        Output("g5", "figure"),
        Output("g6", "figure"),
        Output("g7", "figure"),
    ],
    [
        Input("f1", "value"),
        Input("f2", "value"),
        Input("f3", "value"),
        Input("f4", "value"),
        Input("map_mode", "value")
    ]
)
def actualizar(f1, f2, f3, f4, map_mode):

    # -----------------------------
    # FILTRADO
    # -----------------------------
    dff = df.copy()

    if f1:
        dff = dff[dff["job_title"].isin(f1)]
    if f2:
        dff = dff[dff["location"].isin(f2)]
    if f3:
        dff = dff[dff["education_level"].isin(f3)]
    if f4:
        dff = dff[dff["remote_work"].isin(f4)]

    if dff.empty:
        dff = df.copy()

    # -----------------------------
    # NOMBRES VARIABLES
    # -----------------------------
    nombres_leyendas = {
        "job_title": "Carrera",
        "location": "País",
        "education_level": "Nivel Educativo",
        "remote_work": "Modalidad",
        "salary": "Salario Anual",
        "experience_years": "Años de Experiencia",
        "skills_count": "Cantidad de Habilidades",
        "industry": "Industria"
    }

    # -----------------------------
    # LEYENDA DINÁMICA
    # -----------------------------
    filtros = []

    if f1:
        filtros.append(f"🎓 {nombres_leyendas['job_title']}: {', '.join(f1)}")
    if f2:
        filtros.append(f"🌍 {nombres_leyendas['location']}: {', '.join(f2)}")
    if f3:
        filtros.append(f"📚 {nombres_leyendas['education_level']}: {', '.join(f3)}")
    if f4:
        filtros.append(f"💻 {nombres_leyendas['remote_work']}: {', '.join(f4)}")

    leyenda = " | ".join(filtros) if filtros else "Sin filtros aplicados"

    # -----------------------------
    # KPI
    # -----------------------------
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
        .eq("remoto")
        .mean() * 100
    )

    # Función tarjeta
    def tarjeta(titulo, valor, color):
        return html.Div([
            html.H4(titulo, style={"marginBottom": "8px", "color": "white"}),
            html.H2(valor, style={"margin": "0", "color": "white"})
        ], style={
            "background": color,
            "padding": "20px",
            "borderRadius": "18px",
            "textAlign": "center",
            "fontFamily": FONT,
            "boxShadow": "0 4px 10px rgba(0,0,0,.25)"
        })

    # Tarjetas PNG futuristas
    cards = [
        tarjeta(
            html.Span([
                html.Img(src="/assets/carrera.png", style={"width": "32px", "marginRight": "8px"}),
                "Mejor Carrera"
            ]),
            top_job,
            "#9b59b6"
        ),
        tarjeta(
            html.Span([
                html.Img(src="/assets/mundo.png", style={"width": "32px", "marginRight": "8px"}),
                "Mejor País"
            ]),
            top_country,
            "#00ff9d"
        ),
        tarjeta(
            html.Span([
                html.Img(src="/assets/salario.png", style={"width": "32px", "marginRight": "8px"}),
                "Salario Promedio Anual"
            ]),
            f"${salario_promedio:,.0f}",
            "#00eaff"
        ),
        tarjeta(
            html.Span([
                html.Img(src="/assets/remoto.png", style={"width": "32px", "marginRight": "8px"}),
                "% Remoto"
            ]),
            f"{pct_remote:.1f}%",
            "#ff00e6"
        ),
    ]

    # -----------------------------
    # MAPA (con switch)
    # -----------------------------
    country_salary = (
        dff.groupby("location")["salary"]
        .mean()
        .reset_index()
    )

    if map_mode == "scatter":
        g_map = px.scatter_geo(
            country_salary,
            locations="location",
            locationmode="country names",
            size="salary",
            color="salary",
            hover_name="location",
            projection="natural earth",
            title=f"🛰️ Salario promedio anual por país<br><sup>{leyenda}</sup>",
            size_max=40,
            color_continuous_scale="Viridis"
        )
    else:
        g_map = px.choropleth(
            country_salary,
            locations="location",
            locationmode="country names",
            color="salary",
            hover_name="location",
            projection="natural earth",
            title=f"🗺️ Salario promedio anual por país (Coroplético)<br><sup>{leyenda}</sup>",
            color_continuous_scale="Viridis"
        )

    # -----------------------------
    # GRÁFICO 1 – Top carreras
    # -----------------------------
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
        title=f"🤖 Top carreras mejor pagadas<br><sup>{leyenda}</sup>"
    )

    g1.update_layout(
        xaxis_title="Salario Anual",
        yaxis_title="Carrera"
    )

    # -----------------------------
    # GRÁFICO 2 – Experiencia
    # -----------------------------
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
        title=f"📈 Experiencia e impacto en el salario anual<br><sup>{leyenda}</sup>"
    )

    g2.update_layout(
        xaxis_title="Años de Experiencia",
        yaxis_title="Salario Anual"
    )

    # -----------------------------
    # GRÁFICO 3 – Educación
    # -----------------------------
    g3 = px.box(
        dff,
        x="education_level",
        y="salary",
        color="education_level",
        category_orders={"education_level": orden_educacion},
        title=f"🎓 Impacto del nivel educativo<br><sup>{leyenda}</sup>"
    )

    g3.update_layout(
        xaxis_title="Nivel Educativo",
        yaxis_title="Salario Anual"
    )

    # -----------------------------
    # GRÁFICO 4 – Modalidad Pie
    # -----------------------------
    df_pie = dff["remote_work"].value_counts().reset_index()
    df_pie.columns = ["modalidad", "cantidad"]

    g4 = px.pie(
        df_pie,
        names="modalidad",
        values="cantidad",
        hole=0.45,
        title=f"🏠 Modalidades de trabajo<br><sup>{leyenda}</sup>"
    )

    # -----------------------------
    # GRÁFICO 5 – Industria Treemap
    # -----------------------------
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
        title=f"🏭 Salario anual por industria<br><sup>{leyenda}</sup>"
    )

    # -----------------------------
    # GRÁFICO 6 – Habilidades
    # -----------------------------
    df_skills = (
        dff.groupby("skills_count")
        .agg(
            salario_promedio=("salary", "mean"),
            cantidad_personas=("salary", "count")
        )
        .reset_index()
    )

    g6 = px.scatter(
        df_skills,
        x="skills_count",
        y="salario_promedio",
        size="cantidad_personas",
        title=f"🧠 Habilidades e impacto en el salario anual<br><sup>{leyenda}</sup>"
    )

    g6.update_layout(
        xaxis_title="Cantidad de Habilidades",
        yaxis_title="Salario Promedio Anual"
    )

    # -----------------------------
    # GRÁFICO 7 – Modalidad Box
    # -----------------------------
    g7 = px.box(
        dff,
        x="remote_work",
        y="salary",
        color="remote_work",
        title=f"💻 Salario anual según modalidad<br><sup>{leyenda}</sup>"
    )

    g7.update_layout(
        xaxis_title="Modalidad",
        yaxis_title="Salario Anual"
    )

    # -----------------------------
    # ESTILO GENERAL
    # -----------------------------
    figs = [g_map, g1, g2, g3, g4, g5, g6, g7]

    for fig in figs:
        fig.update_layout(
            font_family=FONT,
            paper_bgcolor="rgba(255,255,255,.55)",
            plot_bgcolor="rgba(255,255,255,.18)",
            title_x=0.5,
            margin=dict(l=20, r=20, t=55, b=20)
        )

    g_map.update_layout(height=620)

    return cards, g_map, g1, g2, g3, g4, g5, g6, g7

# ==========================================================
# RUN (Render)
# ==========================================================
port = int(os.environ.get("PORT", 8050))
app.run(host="0.0.0.0", port=port)

