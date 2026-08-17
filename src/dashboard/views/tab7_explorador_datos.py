# type: ignore

import pandas as pd
import streamlit as st


def render(df_filtrado: pd.DataFrame) -> None:
    st.subheader("Explorador de Datos Interactivos")
    st.write(
        "Visualización y búsqueda directa sobre la tabla consolidada en la Capa Gold."
    )

    if df_filtrado.empty:
        st.warning("No hay datos disponibles para los filtros seleccionados.")
        return

    col_busqueda, col_limite = st.columns([3, 1])

    with col_busqueda:
        busqueda = st.text_input(
            "Buscar por nombre de juego:",
            placeholder="Ej: Counter-Strike, Dota, Portal...",
        ).strip()

    with col_limite:
        limite_filas = st.selectbox(
            "Registros a mostrar:",
            options=[100, 500, 1000, 2500, 5000, "Todos"],
            index=2,  # 1,000 por defecto
        )

    columnas_clave = [
        "name",
        "release_year",
        "price_usd",
        "Metacritic_score",
        "approval_rate",
        "Peak_CCU",
        "estimated_revenue_usd",
        "Genres",
        "developer",
        "publisher",
    ]
    cols_a_usar = [c for c in columnas_clave if c in df_filtrado.columns]
    df_tabla = df_filtrado[cols_a_usar]

    if busqueda and "name" in df_filtrado.columns:
        filtro_nombre = (
            df_filtrado["name"].astype(str).str.contains(busqueda, case=False, na=False)
        )
        df_tabla = df_tabla.loc[filtro_nombre]

    total_registros = len(df_tabla)

    if limite_filas != "Todos" and total_registros > int(limite_filas):
        df_mostrar = df_tabla.head(int(limite_filas)).reset_index(drop=True)
    else:
        df_mostrar = df_tabla.reset_index(drop=True)

    st.dataframe(df_mostrar, width="stretch", height=480, hide_index=True)
