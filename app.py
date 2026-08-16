import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Steam & Metacritic Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #0e141d;
        color: #c6d4df;
    }
    [data-testid="stSidebar"] {
        background-color: #171d25;
        border-right: 1px solid #2a3545;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #66c0f4;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        color: #a3b9cc;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #171d25;
        padding: 6px;
        border-radius: 8px;
        border: 1px solid #2a3545;
    }
    .stTabs [data-baseweb="tab"] {
        color: #a3b9cc;
        font-weight: 600;
        border-radius: 6px;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2a475e !important;
        color: #ffffff !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


PALETA_PRECIOS = {
    "Gratis ($0)": "#00ff88",
    "Económico ($0.01 - $9.99)": "#00d2ff",
    "Estándar ($10.00 - $29.99)": "#ffc107",
    "Premium ($30.00+)": "#ff3366",
}

PALETA_DISCREPANCIA = {
    "Infravalorado por la Crítica": "#00ff88",
    "Consenso Crítica vs Comunidad": "#00d2ff",
    "Sobrevalorado por la Crítica": "#ff3366",
}

PALETA_NEON_DISCRETA = [
    "#00ff88",
    "#00d2ff",
    "#ffc107",
    "#ff3366",
    "#b537f2",
    "#00e5ff",
    "#ff9100",
    "#76ff03",
    "#ff1744",
    "#e040fb",
]


@st.cache_data
def cargar_datos_gold() -> pd.DataFrame | None:
    ruta_gold = os.path.join("data", "gold", "steam_metrics_gold.parquet")
    if not os.path.exists(ruta_gold):
        return None
    return pd.read_parquet(ruta_gold)


def main():
    st.markdown(
        """
        <div style="display: flex; align-items: center; justify-content: space-between; background: linear-gradient(90deg, #1b2838 0%, #2a475e 50%, #0f1c29 100%); padding: 18px 24px; border-radius: 12px; margin-bottom: 20px; border-left: 6px solid #66c0f4; border-right: 6px solid #66cc33;">
            <div>
                <h1 style="color: #ffffff; margin: 0; font-size: 1.8rem; font-weight: 800; letter-spacing: 0.5px;">
                    <span style="color: #66c0f4;">Steam</span> &amp; <span style="color: #66cc33;">Metacritic</span> Analytics
                </h1>
                <p style="color: #c6d4df; margin: 4px 0 0 0; font-size: 0.95rem;">
                    Plataforma de Inteligencia Comercial y Desempeño de Videojuegos · CIBERTEC
                </p>
            </div>
            <div style="display: flex; gap: 10px;">
                <span style="background: rgba(102, 192, 244, 0.15); color: #66c0f4; border: 1px solid #66c0f4; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 700;">STEAM API</span>
                <span style="background: rgba(102, 204, 51, 0.15); color: #66cc33; border: 1px solid #66cc33; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 700;">METACRITIC KAGGLE</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df = cargar_datos_gold()

    if df is None:
        st.error(
            "No se encontró el archivo de la Capa Gold (data/gold/steam_metrics_gold.parquet). "
            "Por favor ejecute la consolidación previamente."
        )
        return

    st.sidebar.header("Filtros del Dataset")

    generos_disponibles = sorted(df["Genres"].dropna().unique().tolist())
    generos_seleccionados = st.sidebar.multiselect(
        "Filtrar por Género:",
        options=generos_disponibles,
        default=[],
    )

    categorias_precio = sorted(df["price_category"].dropna().unique().tolist())
    categorias_precio_sel = st.sidebar.multiselect(
        "Filtrar por Categoría de Precio:",
        options=categorias_precio,
        default=[],
    )

    st.sidebar.subheader("Rango Numérico de Precio (USD)")
    col_p1, col_p2 = st.sidebar.columns(2)
    p_min = col_p1.number_input(
        "Precio Mín ($)", min_value=0.0, max_value=1000.0, value=0.0, step=5.0
    )
    p_max = col_p2.number_input(
        "Precio Máx ($)", min_value=0.0, max_value=1000.0, value=60.0, step=5.0
    )

    year_min = int(df["release_year"].min())
    year_max = int(df["release_year"].max())
    rango_year = st.sidebar.slider(
        "Año de Lanzamiento:",
        min_value=year_min,
        max_value=year_max,
        value=(year_min, year_max),
        step=1,
    )

    plataformas = st.sidebar.multiselect(
        "Plataforma Compatible:",
        options=["Windows", "Mac", "Linux"],
        default=[],
    )

    min_reviews = st.sidebar.number_input(
        "Mínimo de Reseñas en Steam:",
        min_value=0,
        max_value=50000,
        value=0,
        step=50,
    )

    score_min = float(df["Metacritic_score"].min())
    score_max = float(df["Metacritic_score"].max())
    rango_score = st.sidebar.slider(
        "Rango Metacritic Score:",
        min_value=score_min,
        max_value=score_max,
        value=(score_min, score_max),
        step=1.0,
    )

    df_filtrado = df.copy()

    if generos_seleccionados:
        df_filtrado = df_filtrado.loc[df_filtrado["Genres"].isin(generos_seleccionados)]

    if categorias_precio_sel:
        df_filtrado = df_filtrado.loc[
            df_filtrado["price_category"].isin(categorias_precio_sel)
        ]

    if plataformas:
        for plat in plataformas:
            if plat in df_filtrado.columns:
                df_filtrado = df_filtrado.loc[df_filtrado[plat] == True]

    cond_year = (df_filtrado["release_year"] >= rango_year[0]) & (
        df_filtrado["release_year"] <= rango_year[1]
    )
    cond_reviews = df_filtrado["total_reviews"] >= min_reviews
    cond_precio = (df_filtrado["price_usd"] >= p_min) & (
        df_filtrado["price_usd"] <= p_max
    )
    cond_score = (df_filtrado["Metacritic_score"] >= rango_score[0]) & (
        df_filtrado["Metacritic_score"] <= rango_score[1]
    )
    df_filtrado = df_filtrado.loc[cond_year & cond_reviews & cond_precio & cond_score]

    st.success(
        f"{len(df_filtrado):,} videojuegos filtrados correctamente desde la Capa Gold."
    )

    st.subheader("Indicadores Clave (KPIs)")
    col1, col2, col3, col4 = st.columns(4)

    total_juegos = len(df_filtrado)
    metacritic_promedio = (
        df_filtrado["Metacritic_score"].mean() if total_juegos > 0 else 0.0
    )
    aprobacion_promedio = (
        df_filtrado["approval_rate"].mean() if total_juegos > 0 else 0.0
    )
    ingresos_totales_millones = (
        (df_filtrado["estimated_revenue_usd"].sum() / 1_000_000)
        if total_juegos > 0
        else 0.0
    )

    col1.metric("🎮 Videojuegos Analizados", f"{total_juegos:,}")
    col2.metric("⭐ Metacritic Promedio", f"{metacritic_promedio:.1f}")
    col3.metric("👍 Aprobación Comunidad", f"{aprobacion_promedio:.1f}%")
    col4.metric("💰 Ingresos Estimados", f"${ingresos_totales_millones:,.2f} M")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(
        [
            "1. Crítica vs Éxito Comercial",
            "2. Discrepancia Crítica vs Comunidad",
            "3. Géneros más Rentables",
            "4. Satisfacción vs Tiempo de Juego",
            "5. Estrategia de precios",
            "6. Géneros vs Peak CCU",
            "7. Explorador de Datos",
            "8. Correlaciones",
        ]
    )

    with tab1:
        st.subheader(
            "¿Existe una relación directa entre la calificación de la crítica y el éxito comercial estimado en ventas y jugadores?"
        )
        st.write(
            "Análisis para determinar si los juegos con mejores puntajes en Metacritic logran "
            "mayores ventas estimadas e interacción en jugadores simultáneos en hora pico."
        )

        if total_juegos > 0:
            assert isinstance(df_filtrado, pd.DataFrame)
            df_scatter = df_filtrado.loc[
                (df_filtrado["total_reviews"] >= 5)
                & (df_filtrado["estimated_revenue_usd"] > 0)
            ].copy()
            df_scatter["estimated_revenue_milli"] = (
                df_scatter["estimated_revenue_usd"] / 1_000_000
            ).round(2)

            fig_scatter_ventas = px.scatter(
                df_scatter,
                x="Metacritic_score",
                y="estimated_revenue_milli",
                size="Peak_CCU",
                color="price_category",
                color_discrete_map=PALETA_PRECIOS,
                hover_name="name",
                hover_data={"price_usd": True, "Peak_CCU": True, "approval_rate": True},
                title="Metacritic Score vs Ingresos Estimados (Millones USD) - Tamaño = Peak CCU",
                labels={
                    "Metacritic_score": "Calificación Metacritic",
                    "estimated_revenue_milli": "Ingresos Estimados (Millones USD)",
                    "price_category": "Rango de Precio",
                },
                template="plotly_dark",
                size_max=48,
                opacity=0.85,
                log_y=True,
            )
            fig_scatter_ventas.update_traces(
                marker=dict(line=dict(width=0.6, color="#0e141d"))
            )
            fig_scatter_ventas.update_xaxes(range=[40, 100])
            fig_scatter_ventas.update_yaxes(
                tickvals=[0.01, 0.1, 1, 10, 100, 1000, 4000],
                ticktext=[
                    "$0.01M",
                    "$0.1M",
                    "$1M",
                    "$10M",
                    "$100M",
                    "$1,000M",
                    "$4,000M",
                ],
            )
            fig_scatter_ventas.update_layout(
                height=530, paper_bgcolor="#171d25", plot_bgcolor="#171d25"
            )
            st.plotly_chart(fig_scatter_ventas, use_container_width=True)

            col_sub1, col_sub2 = st.columns(2)

            with col_sub1:
                top_ventas = (
                    df_filtrado.sort_values(by="estimated_revenue_usd", ascending=False)
                    .head(10)
                    .copy()
                )
                top_ventas["Texto_Ventas"] = top_ventas["estimated_revenue_usd"].apply(
                    lambda x: (
                        f"${x / 1_000_000_000:.1f}B"
                        if x >= 1_000_000_000
                        else f"${x / 1_000_000:.1f}M"
                    )
                )

                fig_top_ventas = px.bar(
                    top_ventas,
                    x="estimated_revenue_usd",
                    y="name",
                    orientation="h",
                    color="Metacritic_score",
                    color_continuous_scale="Viridis",
                    text="Texto_Ventas",
                    title="Top 10 Videojuegos por Ingresos Estimados (USD)",
                    labels={
                        "estimated_revenue_usd": "Ingresos Estimados (USD)",
                        "name": "Videojuego",
                        "Metacritic_score": "Metacritic Score",
                    },
                    template="plotly_dark",
                )
                fig_top_ventas.update_traces(textposition="outside", cliponaxis=False)
                fig_top_ventas.update_layout(
                    yaxis={"categoryorder": "total ascending"},
                    height=450,
                    margin=dict(r=80),
                    paper_bgcolor="#171d25",
                    plot_bgcolor="#171d25",
                )
                st.plotly_chart(fig_top_ventas, use_container_width=True)

            with col_sub2:
                top_ccu = (
                    df_filtrado.sort_values(by="Peak_CCU", ascending=False)
                    .head(10)
                    .copy()
                )
                top_ccu["Texto_CCU"] = top_ccu["Peak_CCU"].apply(
                    lambda x: f"{int(x):,}"
                )

                fig_top_ccu = px.bar(
                    top_ccu,
                    x="Peak_CCU",
                    y="name",
                    orientation="h",
                    color="Metacritic_score",
                    color_continuous_scale="Viridis",
                    text="Texto_CCU",
                    title="Top 10 Videojuegos por Jugadores Simultáneos en Hora Pico",
                    labels={
                        "Peak_CCU": "Peak CCU",
                        "name": "Videojuego",
                        "Metacritic_score": "Metacritic Score",
                    },
                    template="plotly_dark",
                )
                fig_top_ccu.update_traces(textposition="outside", cliponaxis=False)
                fig_top_ccu.update_layout(
                    yaxis={"categoryorder": "total ascending"},
                    height=450,
                    margin=dict(r=80),
                    paper_bgcolor="#171d25",
                    plot_bgcolor="#171d25",
                )
                st.plotly_chart(fig_top_ccu, use_container_width=True)
        else:
            st.warning("No hay datos disponibles para los filtros seleccionados.")

    with tab2:
        st.subheader(
            "¿Qué discrepancia existe entre la opinión de la crítica especializada (Metacritic) y la satisfacción de la comunidad (Reseñas de Steam)?"
        )
        st.write(
            "Comparación directa entre la nota de Metacritic y la tasa de aprobación de los jugadores de Steam "
            "para identificar videojuegos sobrevalorados o infravalorados por los analistas."
        )

        if total_juegos > 0:
            fig_discrepancia = px.scatter(
                df_filtrado,
                x="Metacritic_score",
                y="approval_rate",
                color="discrepancy_category",
                color_discrete_map=PALETA_DISCREPANCIA,
                hover_name="name",
                hover_data={"score_gap": True, "total_reviews": True},
                title="Metacritic Score vs Tasa de Aprobación de la Comunidad (%)",
                labels={
                    "Metacritic_score": "Puntaje Metacritic (Crítica)",
                    "approval_rate": "Aprobación Comunidad (%)",
                    "discrepancy_category": "Categoría de Discrepancia",
                },
                template="plotly_dark",
            )

            fig_discrepancia.add_trace(
                go.Scatter(
                    x=[0, 100],
                    y=[0, 100],
                    mode="lines",
                    name="Línea de Consenso (1:1)",
                    line=dict(color="#a3b9cc", dash="dash"),
                )
            )
            fig_discrepancia.update_layout(
                height=500, paper_bgcolor="#171d25", plot_bgcolor="#171d25"
            )
            st.plotly_chart(fig_discrepancia, use_container_width=True)

            conteo_discrepancia = (
                df_filtrado["discrepancy_category"]
                .value_counts()
                .reset_index()
                .rename(
                    columns={"discrepancy_category": "Categoria", "count": "Cantidad"}
                )
            )
            fig_pie_discrepancia = px.pie(
                conteo_discrepancia,
                names="Categoria",
                values="Cantidad",
                color="Categoria",
                color_discrete_map=PALETA_DISCREPANCIA,
                title="Distribución de Discrepancia Crítica vs Comunidad",
                template="plotly_dark",
                hole=0.4,
            )
            fig_pie_discrepancia.update_layout(
                height=400, paper_bgcolor="#171d25", plot_bgcolor="#171d25"
            )
            st.plotly_chart(fig_pie_discrepancia, use_container_width=True)
        else:
            st.warning("No hay datos disponibles para los filtros seleccionados.")

    with tab3:
        st.subheader(
            "¿Cuáles son los géneros más rentables y cuáles concentran el mayor volumen de jugadores en el mercado?"
        )
        st.write(
            "Identificación de los géneros comerciales de mayor volumen financiero y su "
            "concentración de usuarios en el mercado."
        )

        if total_juegos > 0:
            generos_agg = (
                df_filtrado.groupby("Genres", observed=False)
                .agg(
                    Ingresos_Totales=("estimated_revenue_usd", "sum"),
                    Peak_CCU_Promedio=("Peak_CCU", "mean"),
                    Total_Juegos=("appid", "count"),
                    Precio_Promedio=("price_usd", "mean"),
                )
                .reset_index()
                .sort_values(by="Ingresos_Totales", ascending=False)
                .head(15)
            )

            df_generos_ingresos = generos_agg.copy()
            df_generos_ingresos["Texto_Ingresos"] = df_generos_ingresos[
                "Ingresos_Totales"
            ].apply(
                lambda x: (
                    f"${x / 1_000_000_000:.1f}B"
                    if x >= 1_000_000_000
                    else f"${x / 1_000_000:.1f}M"
                )
            )

            df_generos_ccu = generos_agg.copy()
            df_generos_ccu["Texto_CCU"] = df_generos_ccu["Peak_CCU_Promedio"].apply(
                lambda x: f"{int(x):,}"
            )

            col_g1, col_g2 = st.columns(2)

            with col_g1:
                fig_generos_ingresos = px.bar(
                    df_generos_ingresos,
                    x="Ingresos_Totales",
                    y="Genres",
                    orientation="h",
                    color="Ingresos_Totales",
                    color_continuous_scale="Viridis",
                    text="Texto_Ingresos",
                    title="Top 15 Géneros más Rentables (Ingresos Estimados USD)",
                    labels={
                        "Ingresos_Totales": "Ingresos Estimados (USD)",
                        "Genres": "Género",
                    },
                    template="plotly_dark",
                )
                fig_generos_ingresos.update_traces(
                    textposition="outside", cliponaxis=False
                )
                fig_generos_ingresos.update_layout(
                    yaxis={"categoryorder": "total ascending"},
                    height=520,
                    margin=dict(r=80),
                    paper_bgcolor="#171d25",
                    plot_bgcolor="#171d25",
                )
                st.plotly_chart(fig_generos_ingresos, use_container_width=True)

            with col_g2:
                fig_generos_ccu = px.bar(
                    df_generos_ccu,
                    x="Peak_CCU_Promedio",
                    y="Genres",
                    orientation="h",
                    color="Peak_CCU_Promedio",
                    color_continuous_scale="Viridis",
                    text="Texto_CCU",
                    title="Top 15 Géneros por Promedio de Jugadores Simultáneos (Peak CCU)",
                    labels={
                        "Peak_CCU_Promedio": "Peak CCU Promedio",
                        "Genres": "Género",
                    },
                    template="plotly_dark",
                )
                fig_generos_ccu.update_traces(textposition="outside", cliponaxis=False)
                fig_generos_ccu.update_layout(
                    yaxis={"categoryorder": "total ascending"},
                    height=520,
                    margin=dict(r=70),
                    paper_bgcolor="#171d25",
                    plot_bgcolor="#171d25",
                )
                st.plotly_chart(fig_generos_ccu, use_container_width=True)

            top10_nombres = generos_agg["Genres"].head(10).tolist()
            df_top10_box = df_filtrado[df_filtrado["Genres"].isin(top10_nombres)]

            fig_box_precio = px.box(
                df_top10_box,
                x="Genres",
                y="price_usd",
                color="Genres",
                color_discrete_sequence=PALETA_NEON_DISCRETA,
                title="Distribución y Dispersión de Precios (USD) por Top 10 Géneros",
                labels={"price_usd": "Precio (USD)", "Genres": "Género"},
                template="plotly_dark",
                points="outliers",
            )
            fig_box_precio.update_layout(
                showlegend=False,
                height=460,
                paper_bgcolor="#171d25",
                plot_bgcolor="#171d25",
            )
            st.plotly_chart(fig_box_precio, use_container_width=True)
        else:
            st.warning("No hay datos disponibles para los filtros seleccionados.")


    with tab4:

        st.subheader(
        "¿Cuál es el nivel de satisfacción de la comunidad "
        "en comparación con el tiempo de juego registrado por usuario?"
    )

        st.write(
        "Se relaciona el tiempo promedio de juego registrado por usuario "
        "con la tasa de aprobación de la comunidad. Cada punto representa "
        "un videojuego con tiempo de juego registrado."
    )

    # ============================================================
    # 1. FILTRAR DATOS VÁLIDOS
    # ============================================================

    df_satisfaccion = df_filtrado.loc[
        (df_filtrado["playtime_hours"] >= 0)
        & (df_filtrado["approval_rate"] >= 0)
        & (df_filtrado["approval_rate"] <= 100)
    ].dropna(
        subset=[
            "playtime_hours",
            "approval_rate",
            "name"
        ]
    ).copy()

    # ============================================================
    # 2. VERIFICAR DATOS
    # ============================================================

    if len(df_satisfaccion) >= 2:

        # ========================================================
        # 3. CANTIDAD DE JUEGOS CON Y SIN TIEMPO
        # ========================================================

        total_juegos_satisfaccion = len(df_satisfaccion)

        juegos_con_tiempo = (
            df_satisfaccion[
                df_satisfaccion["playtime_hours"] > 0
            ].shape[0]
        )

        juegos_sin_tiempo = (
            total_juegos_satisfaccion
            - juegos_con_tiempo
        )

        # ========================================================
        # 4. PORCENTAJES
        # ========================================================

        porcentaje_con_tiempo = (
            juegos_con_tiempo
            / total_juegos_satisfaccion
            * 100
        )

        porcentaje_sin_tiempo = (
            juegos_sin_tiempo
            / total_juegos_satisfaccion
            * 100
        )

        # ========================================================
        # 5. APROBACIÓN PROMEDIO
        # ========================================================

        satisfaccion_promedio = (
            df_satisfaccion["approval_rate"].mean()
        )

        # ========================================================
        # 6. SI EXISTEN SUFICIENTES JUEGOS CON TIEMPO
        # ========================================================

        if juegos_con_tiempo >= 2:

            # ====================================================
            # 7. TIEMPO PROMEDIO
            # ====================================================

            tiempo_promedio = (
                df_satisfaccion.loc[
                    df_satisfaccion["playtime_hours"] > 0,
                    "playtime_hours"
                ].mean()
            )


            # ====================================================
            # 8. CORRELACIÓN PEARSON
            # ====================================================

            datos_con_tiempo = df_satisfaccion.loc[
                df_satisfaccion["playtime_hours"] > 0,
                [
                    "playtime_hours",
                    "approval_rate"
                ]
            ]

            correlacion_pearson = (
                datos_con_tiempo[
                    "playtime_hours"
                ].corr(
                    datos_con_tiempo[
                        "approval_rate"
                    ],
                    method="pearson"
                )
            )

            # ====================================================
            # 9. PERCENTIL 99
            # ====================================================

            percentil_99 = (
                df_satisfaccion.loc[
                    df_satisfaccion["playtime_hours"] > 0,
                    "playtime_hours"
                ].quantile(0.99)
            )

            # ====================================================
            # 10. VALORES EXTREMOS
            # ====================================================

            juegos_valores_extremos = (
                (
                    df_satisfaccion[
                        "playtime_hours"
                    ] > percentil_99
                )
                & (
                    df_satisfaccion[
                        "playtime_hours"
                    ] > 0
                )
            ).sum()
            
            porcentaje_valores_extremos = (
                juegos_valores_extremos
                / juegos_con_tiempo
                * 100
            )

            # ====================================================
            # 11. KPIs
            # ====================================================

            k1, k2, k3, k4 = st.columns(4)

            k1.metric(
                "Tiempo Promedio",
                f"{tiempo_promedio:,.1f} h"
            )

            k2.metric(
                "Tiempo Registrado",
                f"{porcentaje_con_tiempo:.1f}%"
            )

            k3.metric(
                "Correlación Pearson",
                f"{correlacion_pearson:.2f}"
            )

            k4.metric(
                "Valores Extremos",
                f"{juegos_valores_extremos:,}"
            )

            # ====================================================
            # 12. PREPARAR DATOS PARA EL SCATTER
            # ====================================================

            df_scatter = df_satisfaccion.loc[
                (df_satisfaccion["playtime_hours"] > 0)
                & (
                    df_satisfaccion["playtime_hours"]
                    <= percentil_99
                )
            ].copy()

            # ====================================================
            # 13. GRÁFICO 1
            # ====================================================

            fig_satisfaccion = px.scatter(
                df_scatter,
                x="playtime_hours",
                y="approval_rate",
                size="total_reviews",
                color="price_category",
                color_discrete_map=PALETA_PRECIOS,
                hover_name="name",
                hover_data={
                    "playtime_hours": ":,.2f",
                    "approval_rate": ":.2f",
                    "total_reviews": ":,",
                    "Peak_CCU": ":,",
                },
                title=(
                    "Tiempo de Juego vs "
                    "Satisfacción de la Comunidad"
                ),
                labels={
                    "playtime_hours": (
                        "Tiempo de Juego Registrado (horas)"
                    ),
                    "approval_rate": (
                        "Aprobación de la Comunidad (%)"
                    ),
                    "price_category": "Rango de Precio",
                    "total_reviews": "Total de Reseñas",
                },
                template="plotly_dark",
                opacity=0.65,
                size_max=30,
            )

            fig_satisfaccion.update_xaxes(
                title="Tiempo de Juego Registrado (horas)"
            )

            fig_satisfaccion.update_layout(
                height=560,
                paper_bgcolor="#171d25",
                plot_bgcolor="#171d25",
            )

            st.plotly_chart(
                fig_satisfaccion,
                use_container_width=True
            )

            # ====================================================
            # 14. INFORMACIÓN SOBRE VALORES EXTREMOS
            # ====================================================

            st.caption(
                f"El análisis de correlación considera únicamente "
                f"los {juegos_con_tiempo:,} videojuegos con tiempo "
                f"de juego registrado ({porcentaje_con_tiempo:.1f}% "
                f"del total). El percentil 99 corresponde a "
                f"{percentil_99:,.1f} horas. Los "
                f"{juegos_valores_extremos:,} videojuegos que "
                f"superan este valor ({porcentaje_valores_extremos:.1f}% "
                f"de los juegos con tiempo registrado) se excluyen "
                f"únicamente de la visualización."
            )

            # ====================================================
            # 15. COBERTURA DEL TIEMPO
            # ====================================================

            st.caption(
                f"De los {total_juegos_satisfaccion:,} videojuegos "
                f"analizados, {juegos_con_tiempo:,} "
                f"({porcentaje_con_tiempo:.1f}%) cuentan con tiempo "
                f"de juego registrado y {juegos_sin_tiempo:,} "
                f"({porcentaje_sin_tiempo:.1f}%) no presentan "
                f"tiempo registrado."
            )

            # ====================================================
            # 16. SEGUNDO GRÁFICO
            # NIVELES DE TIEMPO
            # ====================================================

            st.subheader(
                "¿Cómo se distribuyen los videojuegos "
                "según su nivel de tiempo de juego?"
            )

            st.write(
                "Los videojuegos con tiempo registrado se agrupan "
                "en diferentes niveles para identificar dónde se "
                "concentra la mayor cantidad de títulos y comparar "
                "su aprobación promedio."
            )

            # ====================================================
            # 17. CREAR NIVELES DE TIEMPO
            # ====================================================

            df_niveles_tiempo = df_satisfaccion.loc[
                df_satisfaccion["playtime_hours"] > 0
            ].copy()

            df_niveles_tiempo["nivel_tiempo"] = pd.cut(
                df_niveles_tiempo["playtime_hours"],
                bins=[
                    0,
                    1,
                    5,
                    20,
                    50,
                    100,
                    float("inf")
                ],
                labels=[
                    "Muy bajo (0-1 h)",
                    "Bajo (1-5 h)",
                    "Medio (5-20 h)",
                    "Alto (20-50 h)",
                    "Muy alto (50-100 h)",
                    "Extremo (100+ h)"
                ],
                include_lowest=True
            )

            # ====================================================
            # 18. AGRUPAR NIVELES
            # ====================================================

            niveles_agg = (
                df_niveles_tiempo
                .groupby(
                    "nivel_tiempo",
                    observed=False
                )
                .agg(
                    Videojuegos=("name", "count"),
                    Aprobacion_Promedio=(
                        "approval_rate",
                        "mean"
                    ),
                    Tiempo_Promedio=(
                        "playtime_hours",
                        "mean"
                    )
                )
                .reset_index()
            )

            niveles_agg["Porcentaje"] = (
                niveles_agg["Videojuegos"]
                / juegos_con_tiempo
                * 100
            )

            niveles_agg["Etiqueta"] = (
                niveles_agg.apply(
                    lambda row:
                    f"{int(row['Videojuegos']):,} "
                    f"({row['Porcentaje']:.1f}%)",
                    axis=1
                )
            )

            # ====================================================
            # 19. GRÁFICO DE NIVELES
            # ====================================================

            fig_niveles = px.bar(
                niveles_agg,
                x="nivel_tiempo",
                y="Videojuegos",
                color="Aprobacion_Promedio",
                color_continuous_scale="Viridis",
                text="Etiqueta",
                hover_data={
                    "Videojuegos": ":,",
                    "Porcentaje": ":.1f",
                    "Aprobacion_Promedio": ":.1f",
                    "Tiempo_Promedio": ":.1f"
                },
                title=(
                    "Distribución de Videojuegos por "
                    "Nivel de Tiempo de Juego"
                ),
                labels={
                    "nivel_tiempo": (
                        "Nivel de Tiempo Registrado"
                    ),
                    "Videojuegos": (
                        "Cantidad de Videojuegos"
                    ),
                    "Aprobacion_Promedio": (
                        "Aprobación Promedio (%)"
                    ),
                    "Porcentaje": "Porcentaje (%)",
                    "Tiempo_Promedio": (
                        "Tiempo Promedio (horas)"
                    )
                },
                template="plotly_dark"
            )

            fig_niveles.update_traces(
                textposition="outside",
                cliponaxis=False
            )

            fig_niveles.update_layout(
                height=520,
                paper_bgcolor="#171d25",
                plot_bgcolor="#171d25",
                coloraxis_colorbar=dict(
                    title="Aprobación (%)"
                )
            )

            st.plotly_chart(
                fig_niveles,
                use_container_width=True
            )

            # ====================================================
            # 20. TABLA RESUMEN
            # ====================================================

            st.subheader(
                "Resumen por nivel de tiempo de juego"
            )

            df_niveles_tabla = niveles_agg.copy()

            df_niveles_tabla[
                "Aprobación Promedio"
            ] = df_niveles_tabla[
                "Aprobacion_Promedio"
            ].map(
                lambda x: f"{x:.1f}%"
            )

            df_niveles_tabla[
                "Tiempo Promedio"
            ] = df_niveles_tabla[
                "Tiempo_Promedio"
            ].map(
                lambda x: f"{x:.1f} h"
            )

            df_niveles_tabla[
                "Porcentaje"
            ] = df_niveles_tabla[
                "Porcentaje"
            ].map(
                lambda x: f"{x:.1f}%"
            )

            df_niveles_tabla = (
                df_niveles_tabla[
                    [
                        "nivel_tiempo",
                        "Videojuegos",
                        "Porcentaje",
                        "Aprobación Promedio",
                        "Tiempo Promedio"
                    ]
                ]
                .rename(
                    columns={
                        "nivel_tiempo":
                            "Nivel de Tiempo"
                    }
                )
            )

            st.dataframe(
                df_niveles_tabla,
                use_container_width=True,
                hide_index=True
            )

            # ====================================================
            # 21. HALLAZGO
            # ====================================================

            nivel_mayor = niveles_agg.loc[
                niveles_agg["Videojuegos"].idxmax()
            ]

            nivel_mayor_aprobacion = niveles_agg.loc[
                niveles_agg[
                    "Aprobacion_Promedio"
                ].idxmax()
            ]

            st.info(
                f"**Hallazgo:** el nivel **"
                f"{nivel_mayor['nivel_tiempo']}** concentra "
                f"la mayor cantidad de videojuegos, con "
                f"({nivel_mayor['Porcentaje']:.1f}%)**. "
                f"El nivel con mayor aprobación promedio es "
                f"**{nivel_mayor_aprobacion['nivel_tiempo']}**, "
                f"con **"
                f"{nivel_mayor_aprobacion['Aprobacion_Promedio']:.1f}%**."
            )

            # ====================================================
            # 22. INTERPRETACIÓN DE PEARSON
            # ====================================================

            if correlacion_pearson >= 0.5:

                interpretacion_pearson = (
                    "Se observa una relación positiva "
                    "moderada/fuerte: los videojuegos con mayor "
                    "tiempo de juego tienden a presentar mayor "
                    "aprobación."
                )

            elif correlacion_pearson >= 0.2:

                interpretacion_pearson = (
                    "Se observa una relación positiva "
                    "débil/moderada: el tiempo de juego presenta "
                    "cierta asociación con la aprobación, aunque "
                    "no la explica por sí solo."
                )

            elif correlacion_pearson <= -0.5:

                interpretacion_pearson = (
                    "Se observa una relación negativa "
                    "moderada/fuerte: un mayor tiempo de juego "
                    "tiende a asociarse con menor aprobación."
                )

            elif correlacion_pearson <= -0.2:

                interpretacion_pearson = (
                    "Se observa una relación negativa "
                    "débil/moderada entre tiempo de juego "
                    "y aprobación."
                )

            else:

                interpretacion_pearson = (
                    "La relación lineal es débil: el tiempo "
                    "de juego no presenta una asociación "
                    "importante con la aprobación de la comunidad."
                )

            st.info(
                f"**Hallazgo según Pearson:** "
                f"{interpretacion_pearson}"
            )

        else:

            st.warning(
                "No hay suficientes videojuegos con tiempo "
                "de juego registrado para realizar el análisis."
            )

    else:

        st.warning(
            "No hay suficientes datos válidos para comparar "
            "satisfacción y tiempo de juego."
        )
    

    with tab5:

        st.subheader(
            "¿Cómo se distribuyen los videojuegos en Steam según su estrategia de precios (gratuito vs. rangos comerciales)?"
        )
        st.write(
            "Analiza cómo se distribuyen los videojuegos según su estrategia de precios, "
            "la distribución real de los precios y la relación entre precio y aprobación "
            "de la comunidad."
        )

        if total_juegos > 0:
            # ========================================================
            # GRÁFICO 1: DISTRIBUCIÓN POR ESTRATEGIA DE PRECIO
            # ========================================================

         st.markdown("### 1. Distribución por estrategia de precio")
         st.caption("¿Qué estrategia de precio domina el catálogo?")

        orden_precios = [
                "Gratis ($0)",
                "Económico ($0.01 - $9.99)",
                "Estándar ($10.00 - $29.99)",
                "Premium ($30.00+)",
            ]

        df_precios = (
                df_filtrado["price_category"]
                .value_counts()
                .reindex(orden_precios, fill_value=0)
                .rename_axis("Estrategia de Precio")
                .reset_index(name="Videojuegos")
            )

        total_precios = int(df_precios["Videojuegos"].sum())

        if total_precios > 0:
                df_precios["Porcentaje"] = (
                    df_precios["Videojuegos"] / total_precios * 100
        )

        df_precios["Etiqueta"] = df_precios.apply(
                    lambda row: (
                        f"{int(row['Videojuegos']):,} "
                        f"({row['Porcentaje']:.1f}%)"
                    ),
                    axis=1,
                )

        fig_precios = px.bar(
                    df_precios,
                    x="Estrategia de Precio",
                    y="Videojuegos",
                    color="Estrategia de Precio",
                    color_discrete_map=PALETA_PRECIOS,
                    text="Etiqueta",
                    title="Distribución de Videojuegos por Estrategia de Precio",
                    labels={
                        "Estrategia de Precio": "Estrategia de Precio",
                        "Videojuegos": "Cantidad de Videojuegos",
                    },
                    template="plotly_dark",
                )

        fig_precios.update_traces(
                    textposition="outside",
                    cliponaxis=False,
                )

        fig_precios.update_layout(
                    showlegend=False,
                    height=500,
                    paper_bgcolor="#171d25",
                    plot_bgcolor="#171d25",
                    margin=dict(t=70, l=40, r=40, b=60),
                )

        st.plotly_chart(
                    fig_precios,
                    use_container_width=True,
                )

        categoria_mayor = df_precios.loc[
                    df_precios["Videojuegos"].idxmax(),
                    "Estrategia de Precio",
                ]

        porcentaje_mayor = df_precios.loc[
                    df_precios["Videojuegos"].idxmax(),
                    "Porcentaje",
                ]

        st.info(
                    f"**Hallazgo:** la estrategia **{categoria_mayor}** "
                    f"concentra la mayor proporción del catálogo filtrado, "
                    f"con **{porcentaje_mayor:.1f}%** de los videojuegos."
                )

            # ========================================================
            # GRÁFICO 2: DISTRIBUCIÓN REAL DEL PRECIO
            # ========================================================

        st.markdown("### 2. Distribución real del precio")
        st.caption("¿Cómo se distribuyen los precios de los videojuegos?")

        df_hist_precio = df_filtrado[
                ["name", "price_usd"]
            ].dropna(subset=["price_usd"]).copy()

        df_hist_precio["price_usd"] = pd.to_numeric(
                df_hist_precio["price_usd"],
                errors="coerce",
            )

        df_hist_precio = df_hist_precio[
                df_hist_precio["price_usd"] >= 0
            ]

        if not df_hist_precio.empty:
                fig_hist_precio = px.histogram(
                    df_hist_precio,
                    x="price_usd",
                    nbins=40,
                    title="Distribución de Precios de los Videojuegos",
                    labels={
                        "price_usd": "Precio (USD)",
                        "count": "Cantidad de Videojuegos",
                    },
                    template="plotly_dark",
                )

                fig_hist_precio.update_traces(
                    marker_line_width=0.5,
                    marker_line_color="#0e141d",
                )

                fig_hist_precio.update_layout(
                    height=500,
                    paper_bgcolor="#171d25",
                    plot_bgcolor="#171d25",
                    margin=dict(t=70, l=40, r=40, b=60),
                )

                st.plotly_chart(
                    fig_hist_precio,
                    use_container_width=True,
                )

                precio_promedio = df_hist_precio["price_usd"].mean()
                precio_mediano = df_hist_precio["price_usd"].median()
                precio_maximo = df_hist_precio["price_usd"].max()

                col_p1, col_p2, col_p3 = st.columns(3)

                col_p1.metric(
                    "Precio promedio",
                    f"${precio_promedio:.2f}",
                )
                col_p2.metric(
                    "Precio mediano",
                    f"${precio_mediano:.2f}",
                )
                col_p3.metric(
                    "Precio máximo",
                    f"${precio_maximo:,.2f}",
                )

            # ========================================================
            # GRÁFICO 3: PRECIO VS APROBACIÓN
            # ========================================================

        st.markdown("### 3. Precio vs aprobación")
        st.caption(
                "¿Existe relación entre el precio de un videojuego "
                "y la aprobación de los usuarios?"
            )

        df_scatter_precio = df_filtrado[
                [
                    "name",
                    "price_usd",
                    "approval_rate",
                    "total_reviews",
                    "Metacritic_score",
                    "price_category",
                ]
            ].dropna(
                subset=[
                    "price_usd",
                    "approval_rate",
                ]
            ).copy()

        df_scatter_precio["price_usd"] = pd.to_numeric(
                df_scatter_precio["price_usd"],
                errors="coerce",
            )

        df_scatter_precio["approval_rate"] = pd.to_numeric(
                df_scatter_precio["approval_rate"],
                errors="coerce",
            )

        df_scatter_precio = df_scatter_precio[
                (df_scatter_precio["price_usd"] >= 0)
                & (df_scatter_precio["approval_rate"] >= 0)
                & (df_scatter_precio["approval_rate"] <= 100)
            ]

        if len(df_scatter_precio) > 1:
                correlacion_precio_aprobacion = (
                    df_scatter_precio["price_usd"].corr(
                        df_scatter_precio["approval_rate"]
                    )
                )

                fig_precio_aprobacion = px.scatter(
                    df_scatter_precio,
                    x="price_usd",
                    y="approval_rate",
                    size="total_reviews",
                    color="price_category",
                    color_discrete_map=PALETA_PRECIOS,
                    hover_name="name",
                    hover_data={
                        "price_usd": ":.2f",
                        "approval_rate": ":.1f",
                        "total_reviews": ":,",
                        "Metacritic_score": True,
                    },
                    title="Precio vs Aprobación de la Comunidad",
                    labels={
                        "price_usd": "Precio (USD)",
                        "approval_rate": "Aprobación de la Comunidad (%)",
                        "price_category": "Estrategia de Precio",
                        "total_reviews": "Total de Reseñas",
                        "Metacritic_score": "Metacritic",
                    },
                    template="plotly_dark",
                    opacity=0.70,
                )

                fig_precio_aprobacion.update_yaxes(
                    range=[0, 100],
                )

                fig_precio_aprobacion.update_layout(
                    height=560,
                    paper_bgcolor="#171d25",
                    plot_bgcolor="#171d25",
                    margin=dict(t=70, l=40, r=40, b=60),
                )

                st.plotly_chart(
                    fig_precio_aprobacion,
                    use_container_width=True,
                )

                if correlacion_precio_aprobacion >= 0.7:
                    interpretacion_precio = (
                        "existe una relación lineal positiva fuerte"
                    )
                elif correlacion_precio_aprobacion >= 0.2:
                    interpretacion_precio = (
                        "existe una relación lineal positiva moderada"
                    )
                elif correlacion_precio_aprobacion > -0.2:
                    interpretacion_precio = (
                        "la relación lineal es débil o prácticamente inexistente"
                    )
                elif correlacion_precio_aprobacion > -0.7:
                    interpretacion_precio = (
                        "existe una relación lineal negativa moderada"
                    )
                else:
                    interpretacion_precio = (
                        "existe una relación lineal negativa fuerte"
                    )

                st.info(
                    f"**Hallazgo:** el coeficiente de correlación de Pearson "
                    f"entre precio y aprobación es **"
                    f"{correlacion_precio_aprobacion:.2f}**. "
                    f"En este conjunto de datos, {interpretacion_precio} "
                    f"entre ambas variables."
                )
        else:
                st.warning(
                    "No hay suficientes datos válidos para analizar "
                    "la relación entre precio y aprobación."
                )



    with tab6:
        st.subheader(
            "¿Cuáles son los géneros de juego que logran retener un mayor número de usuarios simultáneos en hora pico?"
        )
        st.write(
            "Se descomponen los géneros de cada videojuego y se calcula el **Peak CCU promedio** "
            "por género. Se exige un mínimo de juegos por género para evitar que un solo título "
            "distorsione el resultado. **Nota:** Peak CCU mide concurrencia en hora pico; no representa "
            "retención longitudinal de usuarios."
        )

        df_generos_tab6 = df_filtrado.dropna(subset=["Genres", "Peak_CCU"]).copy()
        df_generos_tab6["Genres"] = (
            df_generos_tab6["Genres"]
            .astype(str)
            .str.split(",")
        )
        df_generos_tab6 = df_generos_tab6.explode("Genres")
        df_generos_tab6["Genres"] = df_generos_tab6["Genres"].str.strip()
        df_generos_tab6 = df_generos_tab6.loc[df_generos_tab6["Genres"] != ""]

        if not df_generos_tab6.empty:
            generos_agg_tab6 = (
                df_generos_tab6.groupby("Genres", observed=False)
                .agg(
                    Peak_CCU_Promedio=("Peak_CCU", "mean"),
                    Videojuegos=("appid", "nunique"),
                    Peak_CCU_Mediano=("Peak_CCU", "median"),
                )
                .reset_index()
            )

            # Evita que géneros presentes en muy pocos juegos dominen el ranking.
            min_juegos_genero = 10
            generos_agg_tab6 = generos_agg_tab6.loc[
                generos_agg_tab6["Videojuegos"] >= min_juegos_genero
            ]
            generos_agg_tab6 = generos_agg_tab6.sort_values(
                "Peak_CCU_Promedio", ascending=False
            ).head(15)

            if not generos_agg_tab6.empty:
                generos_agg_tab6["Etiqueta_CCU"] = generos_agg_tab6["Peak_CCU_Promedio"].apply(
                    lambda x: f"{int(x):,}"
                )

                fig_generos = px.bar(
                    generos_agg_tab6.sort_values("Peak_CCU_Promedio"),
                    x="Peak_CCU_Promedio",
                    y="Genres",
                    orientation="h",
                    color="Peak_CCU_Promedio",
                    color_continuous_scale="Viridis",
                    text="Etiqueta_CCU",
                    hover_data={"Videojuegos": ":,", "Peak_CCU_Mediano": ":,"},
                    title="Top 15 Géneros por Promedio de Usuarios Simultáneos (Peak CCU)",
                    labels={
                        "Peak_CCU_Promedio": "Peak CCU Promedio",
                        "Genres": "Género de Juego",
                        "Videojuegos": "Cantidad de Videojuegos",
                        "Peak_CCU_Mediano": "Peak CCU Mediano",
                    },
                    template="plotly_dark",
                )
                fig_generos.update_traces(textposition="outside", cliponaxis=False)
                fig_generos.update_layout(
                    height=620,
                    margin=dict(r=80),
                    coloraxis_showscale=False,
                    paper_bgcolor="#171d25",
                    plot_bgcolor="#171d25",
                )
                st.plotly_chart(fig_generos, use_container_width=True)

                genero_lider = generos_agg_tab6.iloc[0]
                st.info(
                    f"**Hallazgo:** el género **{genero_lider['Genres']}** presenta el mayor Peak CCU promedio, con aproximadamente **{genero_lider['Peak_CCU_Promedio']:,.0f} usuarios simultáneos**, considerando géneros con al menos {min_juegos_genero} videojuegos."
                )
            else:
                st.warning(
                    "No hay géneros con al menos 10 videojuegos dentro de los filtros seleccionados."
                )
        else:
            st.warning("No hay datos válidos para analizar los géneros y el Peak CCU.")


    with tab7:

        st.subheader("Explorador de Datos Interactivos")
        st.write(
            "Visualización y búsqueda directa sobre la tabla consolidada en la Capa Gold."
        )

        busqueda = st.text_input(
            "Buscar por nombre de juego:", placeholder="Ej: Counter-Strike"
        ).strip()

        df_tabla = df_filtrado.copy()
        if busqueda:
            df_tabla = df_tabla[
                df_tabla["name"].str.contains(busqueda, case=False, na=False)
            ]

        st.dataframe(df_tabla, use_container_width=True, height=450)

    with tab8:
        st.subheader("Mapa de Correlación Estadística entre Métricas Key")
        st.write(
            "Análisis cuantitativo mediante el Coeficiente de Correlación de Pearson entre las variables "
            "numéricas del dataset (Score, Aprobación, Precio, Horas, CCU e Ingresos)."
        )

        if total_juegos > 0:
            columnas_num = [
                "Metacritic_score",
                "approval_rate",
                "price_usd",
                "playtime_hours",
                "Peak_CCU",
                "estimated_revenue_usd",
                "total_reviews",
            ]
            # pyrefly: ignore
            matriz_corr = df_filtrado[columnas_num].corr().round(2)

            fig_heatmap = go.Figure(
                data=go.Heatmap(
                    z=matriz_corr.values,
                    x=[
                        "Metacritic Score",
                        "Aprobación (%)",
                        "Precio (USD)",
                        "Horas Jugadas",
                        "Peak CCU",
                        "Ingresos Estimados",
                        "Total Reseñas",
                    ],
                    y=[
                        "Metacritic Score",
                        "Aprobación (%)",
                        "Precio (USD)",
                        "Horas Jugadas",
                        "Peak CCU",
                        "Ingresos Estimados",
                        "Total Reseñas",
                    ],
                    colorscale="RdBu_r",
                    zmin=-1.0,
                    zmax=1.0,
                    zmid=0,
                    text=matriz_corr.values.round(2),
                    texttemplate="%{text}",
                    textfont={"size": 12},
                    hoverongaps=False,
                )
            )
            fig_heatmap.update_layout(
                height=520,
                paper_bgcolor="#171d25",
                plot_bgcolor="#171d25",
                font=dict(color="#c6d4df"),
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.warning("No hay datos disponibles para los filtros seleccionados.")



if __name__ == "__main__":
    main()
