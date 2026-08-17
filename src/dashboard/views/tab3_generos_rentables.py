# type: ignore

import pandas as pd
import plotly.express as px
import streamlit as st
from src.dashboard.constants import PALETA_NEON_DISCRETA


def render(df_filtrado: pd.DataFrame) -> None:
    st.subheader(
        "¿Cuáles son los géneros más rentables y cómo se distribuye su volumen de mercado?"
    )
    st.write(
        "Identificación de los géneros comerciales de mayor volumen financiero "
        "(desanidados por categoría individual) y la dispersión de sus precios de venta."
    )

    total_juegos = len(df_filtrado)

    if total_juegos > 0:
        df_generos_tab3 = (
            df_filtrado[["appid", "name", "Genres", "estimated_revenue_usd", "price_usd"]]
            .dropna(subset=["Genres", "estimated_revenue_usd", "price_usd"])
            .copy()
        )
        df_generos_tab3["Genres"] = (
            df_generos_tab3["Genres"].astype(str).str.split(",")
        )
        df_generos_tab3 = df_generos_tab3.explode("Genres")
        df_generos_tab3["Genres"] = df_generos_tab3["Genres"].str.strip()
        df_generos_tab3 = df_generos_tab3.loc[
            (df_generos_tab3["Genres"] != "")
            & (~df_generos_tab3["Genres"].str.lower().isin(["free to play", "free_to_play"]))
        ]

        if not df_generos_tab3.empty:
            generos_agg = (
                df_generos_tab3.groupby("Genres", observed=True)
                .agg(
                    Ingresos_Totales=("estimated_revenue_usd", "sum"),
                    Total_Juegos=("appid", "nunique"),
                    Precio_Promedio=("price_usd", "mean"),
                    Precio_Mediano=("price_usd", "median"),
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

            fig_generos_ingresos = px.bar(
                df_generos_ingresos.sort_values("Ingresos_Totales"),
                x="Ingresos_Totales",
                y="Genres",
                orientation="h",
                color="Ingresos_Totales",
                color_continuous_scale="Viridis",
                text="Texto_Ingresos",
                hover_data={"Total_Juegos": ":,", "Precio_Promedio": ":.2f"},
                title="Top 15 Géneros más Rentables (Ingresos Estimados USD)",
                labels={
                    "Ingresos_Totales": "Ingresos Estimados (USD)",
                    "Genres": "Género",
                    "Total_Juegos": "Cantidad de Videojuegos",
                    "Precio_Promedio": "Precio Promedio (USD)",
                },
                template="plotly_dark",
            )
            fig_generos_ingresos.update_traces(textposition="outside", cliponaxis=False)
            fig_generos_ingresos.update_layout(
                height=530,
                margin=dict(r=80),
                paper_bgcolor="#171d25",
                plot_bgcolor="#171d25",
            )
            st.plotly_chart(fig_generos_ingresos, width="stretch")

            top10_nombres = generos_agg["Genres"].head(10).tolist()
            df_top10_box = df_generos_tab3[df_generos_tab3["Genres"].isin(top10_nombres)]

            fig_box_precio = px.box(
                df_top10_box,
                x="Genres",
                y="price_usd",
                color="Genres",
                color_discrete_sequence=PALETA_NEON_DISCRETA,
                category_orders={"Genres": top10_nombres},
                title="Distribución y Dispersión de Precios (USD) en el Top 10 Géneros más Rentables",
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

            # ====================================================
            # HALLAZGO
            # ====================================================
            genero_top_ingresos = generos_agg.iloc[0]

            if genero_top_ingresos["Ingresos_Totales"] >= 1_000_000_000:
                ingreso_str = (
                    f"\\${genero_top_ingresos['Ingresos_Totales'] / 1_000_000_000:.2f}B"
                )
            else:
                ingreso_str = (
                    f"\\${genero_top_ingresos['Ingresos_Totales'] / 1_000_000:.1f}M"
                )

            precio_prom_str = f"\\${genero_top_ingresos['Precio_Promedio']:.2f}"
            juegos_str = f"{int(genero_top_ingresos['Total_Juegos']):,}"

            st.info(
                f"**Hallazgo:** el género individual más rentable en ingresos totales es **{genero_top_ingresos['Genres']}** "
                f"con **{ingreso_str} USD** acumulados a través de **{juegos_str} videojuegos** (Precio promedio: {precio_prom_str} USD)."
            )
        else:
            st.warning("No hay datos disponibles para los filtros seleccionados.")
    else:
        st.warning("No hay datos disponibles para los filtros seleccionados.")
