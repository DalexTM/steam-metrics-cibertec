# type: ignore

import pandas as pd
import streamlit as st


def render_sidebar(df: pd.DataFrame) -> pd.DataFrame:
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
    return df_filtrado
