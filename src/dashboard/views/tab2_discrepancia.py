# type: ignore

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from src.dashboard.constants import PALETA_DISCREPANCIA


def render(df_filtrado: pd.DataFrame) -> None:
    st.subheader(
        "¿Qué discrepancia existe entre la opinión de la crítica especializada (Metacritic) y la satisfacción de la comunidad (Reseñas de Steam)?"
    )
    st.write(
        "Comparación directa entre la nota de Metacritic y la tasa de aprobación de los jugadores de Steam "
        "para identificar videojuegos sobrevalorados o infravalorados por los analistas."
    )

    total_juegos = len(df_filtrado)

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
        st.plotly_chart(fig_discrepancia, width="stretch")

        conteo_discrepancia = (
            df_filtrado["discrepancy_category"]
            .value_counts()
            .reset_index()
            .rename(columns={"discrepancy_category": "Categoria", "count": "Cantidad"})
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
        st.plotly_chart(fig_pie_discrepancia, width="stretch")
    else:
        st.warning("No hay datos disponibles para los filtros seleccionados.")
