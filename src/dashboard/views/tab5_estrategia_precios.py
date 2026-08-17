# type: ignore

import pandas as pd
import plotly.express as px
import streamlit as st
from src.dashboard.constants import PALETA_PRECIOS


def render(df_filtrado: pd.DataFrame) -> None:
    st.subheader(
        "¿Cómo se distribuyen los videojuegos en Steam según su estrategia de precios (gratuito vs. rangos comerciales)?"
    )
    st.write(
        "Analiza cómo se distribuyen los videojuegos según su estrategia de precios, "
        "la distribución real de los precios y la relación entre precio y aprobación "
        "de la comunidad."
    )

    total_juegos = len(df_filtrado)

    if total_juegos > 0:
        # ========================================================
        # GRÁFICO 1: DISTRIBUCIÓN POR ESTRATEGIA DE PRECIO
        # ========================================================

        st.markdown("### 1. Distribución por estrategia de precio")
        st.caption("¿Qué estrategia de precio domina el catálogo?")

        orden_precios = [
            "Gratis ($0)",
            "Económico ($0.01 - $9.99)",
            "Estándar ($10.00 - $29.99)",
            "Premium ($30.00+)",
        ]

        df_precios = (
            df_filtrado["price_category"]
            .value_counts()
            .reindex(orden_precios, fill_value=0)
            .rename_axis("Estrategia de Precio")
            .reset_index(name="Videojuegos")
        )

        total_precios = int(df_precios["Videojuegos"].sum())

        if total_precios > 0:
            df_precios["Porcentaje"] = df_precios["Videojuegos"] / total_precios * 100

        df_precios["Etiqueta"] = df_precios.apply(
            lambda row: (
                f"{int(row['Videojuegos']):,} ({row['Porcentaje']:.1f}%)"
                if pd.notna(row.get("Videojuegos")) and pd.notna(row.get("Porcentaje"))
                else f"{int(row.get('Videojuegos', 0)):,} (0.0%)"
            ),
            axis=1,
        )

        fig_precios = px.bar(
            df_precios,
            x="Estrategia de Precio",
            y="Videojuegos",
            color="Estrategia de Precio",
            color_discrete_map=PALETA_PRECIOS,
            text="Etiqueta",
            title="Distribución de Videojuegos por Estrategia de Precio",
            labels={
                "Estrategia de Precio": "Estrategia de Precio",
                "Videojuegos": "Cantidad de Videojuegos",
            },
            template="plotly_dark",
        )

        fig_precios.update_traces(
            textposition="outside",
            cliponaxis=False,
        )

        fig_precios.update_layout(
            showlegend=False,
            height=500,
            paper_bgcolor="#171d25",
            plot_bgcolor="#171d25",
            margin=dict(t=70, l=40, r=40, b=60),
        )

        st.plotly_chart(
            fig_precios,
            width="stretch",
        )

        categoria_mayor = df_precios.loc[
            df_precios["Videojuegos"].idxmax(),
            "Estrategia de Precio",
        ]

        porcentaje_mayor = df_precios.loc[
            df_precios["Videojuegos"].idxmax(),
            "Porcentaje",
        ]

        st.info(
            f"**Hallazgo:** la estrategia **{categoria_mayor}** "
            f"concentra la mayor proporción del catálogo filtrado, "
            f"con **{porcentaje_mayor:.1f}%** de los videojuegos."
        )

        # ========================================================
        # GRÁFICO 2: DISTRIBUCIÓN REAL DEL PRECIO
        # ========================================================

        st.markdown("### 2. Distribución real del precio")
        st.caption("¿Cómo se distribuyen los precios de los videojuegos?")

        df_hist_precio = (
            df_filtrado[["name", "price_usd"]].dropna(subset=["price_usd"]).copy()
        )

        df_hist_precio["price_usd"] = pd.to_numeric(
            df_hist_precio["price_usd"],
            errors="coerce",
        )

        df_hist_precio = df_hist_precio[df_hist_precio["price_usd"] >= 0]

        if not df_hist_precio.empty:
            fig_hist_precio = px.histogram(
                df_hist_precio,
                x="price_usd",
                nbins=40,
                title="Distribución de Precios de los Videojuegos",
                labels={
                    "price_usd": "Precio (USD)",
                    "count": "Cantidad de Videojuegos",
                },
                template="plotly_dark",
            )

            fig_hist_precio.update_traces(
                marker_line_width=0.5,
                marker_line_color="#0e141d",
            )

            fig_hist_precio.update_layout(
                height=500,
                paper_bgcolor="#171d25",
                plot_bgcolor="#171d25",
                margin=dict(t=70, l=40, r=40, b=60),
            )

            st.plotly_chart(
                fig_hist_precio,
                width="stretch",
            )

            precio_promedio = df_hist_precio["price_usd"].mean()
            precio_mediano = df_hist_precio["price_usd"].median()
            precio_maximo = df_hist_precio["price_usd"].max()

            col_p1, col_p2, col_p3 = st.columns(3)

            col_p1.metric(
                "Precio promedio",
                f"${precio_promedio:.2f}",
            )
            col_p2.metric(
                "Precio mediano",
                f"${precio_mediano:.2f}",
            )
            col_p3.metric(
                "Precio máximo",
                f"${precio_maximo:,.2f}",
            )

        # ========================================================
        # GRÁFICO 3: PRECIO VS APROBACIÓN
        # ========================================================

        st.markdown("### 3. Precio vs aprobación")
        st.caption(
            "¿Existe relación entre el precio de un videojuego "
            "y la aprobación de los usuarios?"
        )

        df_scatter_precio = (
            df_filtrado[
                [
                    "name",
                    "price_usd",
                    "approval_rate",
                    "total_reviews",
                    "Metacritic_score",
                    "price_category",
                ]
            ]
            .dropna(
                subset=[
                    "price_usd",
                    "approval_rate",
                ]
            )
            .copy()
        )

        df_scatter_precio["price_usd"] = pd.to_numeric(
            df_scatter_precio["price_usd"],
            errors="coerce",
        )

        df_scatter_precio["approval_rate"] = pd.to_numeric(
            df_scatter_precio["approval_rate"],
            errors="coerce",
        )

        df_scatter_precio = df_scatter_precio[
            (df_scatter_precio["price_usd"] >= 0)
            & (df_scatter_precio["approval_rate"] >= 0)
            & (df_scatter_precio["approval_rate"] <= 100)
        ]

        if len(df_scatter_precio) > 1:
            correlacion_precio_aprobacion = df_scatter_precio["price_usd"].corr(
                df_scatter_precio["approval_rate"]
            )

            fig_precio_aprobacion = px.scatter(
                df_scatter_precio,
                x="price_usd",
                y="approval_rate",
                size="total_reviews",
                color="price_category",
                color_discrete_map=PALETA_PRECIOS,
                hover_name="name",
                hover_data={
                    "price_usd": ":.2f",
                    "approval_rate": ":.1f",
                    "total_reviews": ":,",
                    "Metacritic_score": True,
                },
                title="Precio vs Aprobación de la Comunidad",
                labels={
                    "price_usd": "Precio (USD)",
                    "approval_rate": "Aprobación de la Comunidad (%)",
                    "price_category": "Estrategia de Precio",
                    "total_reviews": "Total de Reseñas",
                    "Metacritic_score": "Metacritic",
                },
                category_orders={
                    "price_category": [
                        "Premium ($30.00+)",
                        "Estándar ($10.00 - $29.99)",
                        "Económico ($0.01 - $9.99)",
                        "Gratis ($0)",
                    ]
                },
                template="plotly_dark",
                opacity=0.70,
                render_mode="webgl",
            )

            fig_precio_aprobacion.update_yaxes(
                range=[0, 100],
            )

            fig_precio_aprobacion.update_layout(
                height=560,
                paper_bgcolor="#171d25",
                plot_bgcolor="#171d25",
                margin=dict(t=70, l=40, r=40, b=60),
            )

            st.plotly_chart(
                fig_precio_aprobacion,
                width="stretch",
            )

            if correlacion_precio_aprobacion >= 0.7:
                interpretacion_precio = "existe una relación lineal positiva fuerte"
            elif correlacion_precio_aprobacion >= 0.2:
                interpretacion_precio = "existe una relación lineal positiva moderada"
            elif correlacion_precio_aprobacion > -0.2:
                interpretacion_precio = (
                    "la relación lineal es débil o prácticamente inexistente"
                )
            elif correlacion_precio_aprobacion > -0.7:
                interpretacion_precio = "existe una relación lineal negativa moderada"
            else:
                interpretacion_precio = "existe una relación lineal negativa fuerte"

            st.info(
                f"**Hallazgo:** el coeficiente de correlación de Pearson "
                f"entre precio y aprobación es **"
                f"{correlacion_precio_aprobacion:.2f}**. "
                f"En este conjunto de datos, {interpretacion_precio} "
                f"entre ambas variables."
            )
        else:
            st.warning(
                "No hay suficientes datos válidos para analizar "
                "la relación entre precio y aprobación."
            )
    else:
        st.warning("No hay datos disponibles para los filtros seleccionados.")
