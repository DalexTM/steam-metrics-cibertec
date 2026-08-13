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

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "1. Crítica vs Éxito Comercial",
            "2. Discrepancia Crítica vs Comunidad",
            "3. Géneros más Rentables",
            "4. Explorador de Datos",
            "5. Correlaciones",
        ]
    )

    with tab1:
        st.subheader("Relación entre Calificación de la Crítica y Éxito Comercial")
        st.write(
            "Análisis para determinar si los juegos con mejores puntajes en Metacritic logran "
            "mayores ventas estimadas e interacción en jugadores simultáneos en hora pico."
        )

        if total_juegos > 0:
            assert isinstance(df_filtrado, pd.DataFrame)
            fig_scatter_ventas = px.scatter(
                df_filtrado,
                x="Metacritic_score",
                y="estimated_revenue_usd",
                size="Peak_CCU",
                color="price_category",
                hover_name="name",
                hover_data={"price_usd": True, "Peak_CCU": True, "approval_rate": True},
                title="Metacritic Score vs Ingresos Estimados USD (Tamaño = Peak CCU)",
                labels={
                    "Metacritic_score": "Calificación Metacritic",
                    "estimated_revenue_usd": "Ingresos Estimados (USD)",
                    "price_category": "Rango de Precio",
                },
                template="plotly_dark",
            )
            fig_scatter_ventas.update_layout(
                height=500, paper_bgcolor="#171d25", plot_bgcolor="#171d25"
            )
            st.plotly_chart(fig_scatter_ventas, use_container_width=True)

            col_sub1, col_sub2 = st.columns(2)

            with col_sub1:
                top_ventas = df_filtrado.sort_values(
                    by="estimated_revenue_usd", ascending=False
                ).head(10)
                fig_top_ventas = px.bar(
                    top_ventas,
                    x="estimated_revenue_usd",
                    y="name",
                    orientation="h",
                    color="Metacritic_score",
                    title="Top 10 Videojuegos por Ingresos Estimados (USD)",
                    labels={
                        "estimated_revenue_usd": "Ingresos Estimados (USD)",
                        "name": "Videojuego",
                    },
                    template="plotly_dark",
                )
                fig_top_ventas.update_layout(
                    yaxis={"categoryorder": "total ascending"},
                    height=400,
                    paper_bgcolor="#171d25",
                    plot_bgcolor="#171d25",
                )
                st.plotly_chart(fig_top_ventas, use_container_width=True)

            with col_sub2:
                top_ccu = df_filtrado.sort_values(by="Peak_CCU", ascending=False).head(
                    10
                )
                fig_top_ccu = px.bar(
                    top_ccu,
                    x="Peak_CCU",
                    y="name",
                    orientation="h",
                    color="Metacritic_score",
                    title="Top 10 Videojuegos por Jugadores Simultáneos en Hora Pico",
                    labels={"Peak_CCU": "Peak CCU", "name": "Videojuego"},
                    template="plotly_dark",
                )
                fig_top_ccu.update_layout(
                    yaxis={"categoryorder": "total ascending"},
                    height=400,
                    paper_bgcolor="#171d25",
                    plot_bgcolor="#171d25",
                )
                st.plotly_chart(fig_top_ccu, use_container_width=True)
        else:
            st.warning("No hay datos disponibles para los filtros seleccionados.")

    with tab2:
        st.subheader(
            "Discrepancia entre Crítica Especializada (Metacritic) y Comunidad (Steam)"
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
        st.subheader("Análisis de Géneros más Rentables y Volumen de Jugadores")
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

            col_g1, col_g2 = st.columns(2)

            with col_g1:
                fig_generos_ingresos = px.bar(
                    generos_agg,
                    x="Ingresos_Totales",
                    y="Genres",
                    orientation="h",
                    color="Ingresos_Totales",
                    title="Top 15 Géneros más Rentables (Ingresos Estimados USD)",
                    labels={
                        "Ingresos_Totales": "Ingresos Estimados (USD)",
                        "Genres": "Género",
                    },
                    template="plotly_dark",
                )
                fig_generos_ingresos.update_layout(
                    yaxis={"categoryorder": "total ascending"},
                    height=450,
                    paper_bgcolor="#171d25",
                    plot_bgcolor="#171d25",
                )
                st.plotly_chart(fig_generos_ingresos, use_container_width=True)

            with col_g2:
                fig_generos_ccu = px.bar(
                    generos_agg,
                    x="Peak_CCU_Promedio",
                    y="Genres",
                    orientation="h",
                    color="Peak_CCU_Promedio",
                    title="Top 15 Géneros por Promedio de Jugadores Simultáneos (Peak CCU)",
                    labels={
                        "Peak_CCU_Promedio": "Peak CCU Promedio",
                        "Genres": "Género",
                    },
                    template="plotly_dark",
                )
                fig_generos_ccu.update_layout(
                    yaxis={"categoryorder": "total ascending"},
                    height=450,
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
                title="Distribución y Dispersión de Precios (USD) por Top 10 Géneros",
                labels={"price_usd": "Precio (USD)", "Genres": "Género"},
                template="plotly_dark",
                points="outliers",
            )
            fig_box_precio.update_layout(
                showlegend=False,
                height=450,
                paper_bgcolor="#171d25",
                plot_bgcolor="#171d25",
            )
            st.plotly_chart(fig_box_precio, use_container_width=True)
        else:
            st.warning("No hay datos disponibles para los filtros seleccionados.")

    with tab4:
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

    with tab5:
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
