# type: ignore

import pandas as pd
import plotly.express as px
import streamlit as st
from src.dashboard.constants import PALETA_NEON_DISCRETA


def render(df_filtrado: pd.DataFrame) -> None:
    st.subheader(
        "¿Cuáles son los géneros más rentables y cuáles concentran el mayor volumen de jugadores en el mercado?"
    )
    st.write(
        "Identificación de los géneros comerciales de mayor volumen financiero y su "
        "concentración de usuarios en el mercado."
    )

    total_juegos = len(df_filtrado)

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
                "N/A"
                if pd.isna(x)
                else (
                    f"${x / 1_000_000_000:.1f}B"
                    if x >= 1_000_000_000
                    else f"${x / 1_000_000:.1f}M"
                )
            )
        )

        df_generos_ccu = generos_agg.copy()
        df_generos_ccu["Texto_CCU"] = df_generos_ccu["Peak_CCU_Promedio"].apply(
            lambda x: f"{int(x):,}" if pd.notna(x) else "0"
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
            fig_generos_ingresos.update_traces(textposition="outside", cliponaxis=False)
            fig_generos_ingresos.update_layout(
                yaxis={"categoryorder": "total ascending"},
                height=520,
                margin=dict(r=80),
                paper_bgcolor="#171d25",
                plot_bgcolor="#171d25",
            )
            st.plotly_chart(fig_generos_ingresos, width="stretch")

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
            st.plotly_chart(fig_generos_ccu, width="stretch")

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
        st.plotly_chart(fig_box_precio, width="stretch")
    else:
        st.warning("No hay datos disponibles para los filtros seleccionados.")
