# type: ignore

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def render(df_filtrado: pd.DataFrame) -> None:
    st.subheader("Mapa de Correlación Estadística entre Métricas Key")
    st.write(
        "Análisis cuantitativo mediante el Coeficiente de Correlación de Pearson entre las variables "
        "numéricas del dataset (Score, Aprobación, Precio, Horas, CCU e Ingresos)."
    )

    total_juegos = len(df_filtrado)

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
        st.plotly_chart(fig_heatmap, width="stretch")
    else:
        st.warning("No hay datos disponibles para los filtros seleccionados.")
