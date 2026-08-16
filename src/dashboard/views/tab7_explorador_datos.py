# type: ignore

import pandas as pd
import streamlit as st


def render(df_filtrado: pd.DataFrame) -> None:
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
