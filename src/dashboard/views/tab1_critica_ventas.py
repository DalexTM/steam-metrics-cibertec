# type: ignore

import pandas as pd
import plotly.express as px
import streamlit as st
from src.dashboard.constants import PALETA_PRECIOS


def render(df_filtrado: pd.DataFrame) -> None:
    st.subheader(
        "¿Existe una relación directa entre la calificación de la crítica y el éxito comercial estimado en ventas y jugadores?"
    )
    st.write(
        "Análisis para determinar si los juegos con mejores puntajes en Metacritic logran "
        "mayores ventas estimadas e interacción en jugadores simultáneos en hora pico."
    )

    total_juegos = len(df_filtrado)

    if total_juegos > 0:
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
        st.plotly_chart(fig_scatter_ventas, width="stretch")

        col_sub1, col_sub2 = st.columns(2)

        with col_sub1:
            top_ventas = (
                df_filtrado.sort_values(by="estimated_revenue_usd", ascending=False)
                .head(10)
                .copy()
            )
            top_ventas["Texto_Ventas"] = top_ventas["estimated_revenue_usd"].apply(
                lambda x: (
                    "N/A"
                    if pd.isna(x)
                    else (
                        f"${x / 1_000_000_000:.1f}B"
                        if x >= 1_000_000_000
                        else f"${x / 1_000_000:.1f}M"
                    )
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
            st.plotly_chart(fig_top_ventas, width="stretch")

        with col_sub2:
            top_ccu = (
                df_filtrado.sort_values(by="Peak_CCU", ascending=False).head(10).copy()
            )
            top_ccu["Texto_CCU"] = top_ccu["Peak_CCU"].apply(
                lambda x: f"{int(x):,}" if pd.notna(x) else "0"
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
            st.plotly_chart(fig_top_ccu, width="stretch")
    else:
        st.warning("No hay datos disponibles para los filtros seleccionados.")
