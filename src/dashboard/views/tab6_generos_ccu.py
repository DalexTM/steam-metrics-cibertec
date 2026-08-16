# type: ignore

import pandas as pd
import plotly.express as px
import streamlit as st


def render(df_filtrado: pd.DataFrame) -> None:
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
    df_generos_tab6["Genres"] = df_generos_tab6["Genres"].astype(str).str.split(",")
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

        min_juegos_genero = 10
        generos_agg_tab6 = generos_agg_tab6.loc[
            generos_agg_tab6["Videojuegos"] >= min_juegos_genero
        ]
        generos_agg_tab6 = generos_agg_tab6.sort_values(
            "Peak_CCU_Promedio", ascending=False
        ).head(15)

        if not generos_agg_tab6.empty:
            generos_agg_tab6["Etiqueta_CCU"] = generos_agg_tab6[
                "Peak_CCU_Promedio"
            ].apply(lambda x: f"{int(x):,}")

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
