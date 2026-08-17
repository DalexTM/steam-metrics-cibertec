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

        # ====================================================
        # HALLAZGOS DE CORRELACIÓN
        # ====================================================
        corr_ingresos_reviews = matriz_corr.loc[
            "estimated_revenue_usd", "total_reviews"
        ]
        corr_ccu_ingresos = matriz_corr.loc["estimated_revenue_usd", "Peak_CCU"]
        corr_critica_ventas = matriz_corr.loc[
            "Metacritic_score", "estimated_revenue_usd"
        ]
        corr_precio_aprobacion = matriz_corr.loc["price_usd", "approval_rate"]

        st.info(
            f"**Hallazgos Clave de Correlación:**\n\n"
            f"• **Éxito Comercial y Popularidad:** La relación lineal más fuerte se da entre **Ingresos Estimados y Total de Reseñas** (r = **{corr_ingresos_reviews:.2f}**) "
            f"y **Peak CCU con Ingresos** (r = **{corr_ccu_ingresos:.2f}**), demostrando que el tamaño de la base de jugadores activos y el volumen de reseñas explican directamente la escala de monetización.\n\n"
            f"• **Crítica Especializada vs Ingresos:** La correlación entre **Metacritic Score e Ingresos** es de **{corr_critica_ventas:.2f}**, indicando que las altas calificaciones de la prensa favorecen la visibilidad pero no determinan por sí solas el éxito en ventas masivas.\n\n"
            f"• **Precio vs Aprobación:** La relación entre **Precio y Aprobación de la Comunidad** es de **{corr_precio_aprobacion:.2f}**, confirmando que el precio no perjudica la satisfacción del jugador siempre que el título entregue valor proporcional a su costo."
        )
    else:
        st.warning("No hay datos disponibles para los filtros seleccionados.")
