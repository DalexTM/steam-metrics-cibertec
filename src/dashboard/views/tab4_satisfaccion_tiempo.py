# type: ignore

import pandas as pd
import plotly.express as px
import streamlit as st
from src.dashboard.constants import PALETA_PRECIOS


def render(df_filtrado: pd.DataFrame) -> None:
    st.subheader(
        "¿Cuál es el nivel de satisfacción de la comunidad "
        "en comparación con el tiempo de juego registrado por usuario?"
    )

    st.write(
        "Se relaciona el tiempo promedio de juego registrado por usuario "
        "con la tasa de aprobación de la comunidad. Cada punto representa "
        "un videojuego con tiempo de juego registrado."
    )

    # ============================================================
    # 1. FILTRAR DATOS VÁLIDOS
    # ============================================================

    df_satisfaccion = (
        df_filtrado[
            (df_filtrado["playtime_hours"] >= 0)
            & (df_filtrado["approval_rate"] >= 0)
            & (df_filtrado["approval_rate"] <= 100)
        ]
        .dropna(subset=["playtime_hours", "approval_rate", "name"])
        .copy()
    )

    # ============================================================
    # 2. VERIFICAR DATOS
    # ============================================================

    if len(df_satisfaccion) >= 2:

        # ========================================================
        # 3. CANTIDAD DE JUEGOS CON Y SIN TIEMPO
        # ========================================================

        total_juegos_satisfaccion = len(df_satisfaccion)

        juegos_con_tiempo = df_satisfaccion[
            df_satisfaccion["playtime_hours"] > 0
        ].shape[0]

        juegos_sin_tiempo = total_juegos_satisfaccion - juegos_con_tiempo

        # ========================================================
        # 4. PORCENTAJES
        # ========================================================

        porcentaje_con_tiempo = juegos_con_tiempo / total_juegos_satisfaccion * 100

        porcentaje_sin_tiempo = juegos_sin_tiempo / total_juegos_satisfaccion * 100

        # ========================================================
        # 5. APROBACIÓN PROMEDIO
        # ========================================================

        satisfaccion_promedio = df_satisfaccion["approval_rate"].mean()

        # ========================================================
        # 6. SI EXISTEN SUFICIENTES JUEGOS CON TIEMPO
        # ========================================================

        if juegos_con_tiempo >= 2:

            # ====================================================
            # 7. TIEMPO PROMEDIO
            # ====================================================

            tiempo_promedio = df_satisfaccion.loc[
                df_satisfaccion["playtime_hours"] > 0, "playtime_hours"
            ].mean()

            # ====================================================
            # 8. CORRELACIÓN PEARSON
            # ====================================================

            datos_con_tiempo = df_satisfaccion.loc[
                df_satisfaccion["playtime_hours"] > 0,
                ["playtime_hours", "approval_rate"],
            ]

            correlacion_pearson = datos_con_tiempo["playtime_hours"].corr(
                datos_con_tiempo["approval_rate"], method="pearson"
            )

            # ====================================================
            # 9. PERCENTIL 99
            # ====================================================

            percentil_99 = df_satisfaccion.loc[
                df_satisfaccion["playtime_hours"] > 0, "playtime_hours"
            ].quantile(0.99)

            # ====================================================
            # 10. VALORES EXTREMOS
            # ====================================================

            juegos_valores_extremos = (
                (df_satisfaccion["playtime_hours"] > percentil_99)
                & (df_satisfaccion["playtime_hours"] > 0)
            ).sum()

            porcentaje_valores_extremos = (
                juegos_valores_extremos / juegos_con_tiempo * 100
            )

            # ====================================================
            # 11. KPIs
            # ====================================================

            k1, k2, k3, k4 = st.columns(4)

            k1.metric("Tiempo Promedio", f"{tiempo_promedio:,.1f} h")

            k2.metric("Tiempo Registrado", f"{porcentaje_con_tiempo:.1f}%")

            k3.metric("Correlación Pearson", f"{correlacion_pearson:.2f}")

            k4.metric("Valores Extremos", f"{juegos_valores_extremos:,}")

            # ====================================================
            # 12. PREPARAR DATOS PARA EL SCATTER
            # ====================================================

            df_scatter = df_satisfaccion.loc[
                (df_satisfaccion["playtime_hours"] > 0)
                & (df_satisfaccion["playtime_hours"] <= percentil_99)
            ].copy()

            # ====================================================
            # 13. GRÁFICO 1
            # ====================================================

            fig_satisfaccion = px.scatter(
                df_scatter,
                x="playtime_hours",
                y="approval_rate",
                size="total_reviews",
                color="price_category",
                color_discrete_map=PALETA_PRECIOS,
                hover_name="name",
                hover_data={
                    "playtime_hours": ":,.2f",
                    "approval_rate": ":.2f",
                    "total_reviews": ":,",
                    "Peak_CCU": ":,",
                },
                title=("Tiempo de Juego vs " "Satisfacción de la Comunidad"),
                labels={
                    "playtime_hours": ("Tiempo de Juego Registrado (horas)"),
                    "approval_rate": ("Aprobación de la Comunidad (%)"),
                    "price_category": "Rango de Precio",
                    "total_reviews": "Total de Reseñas",
                },
                template="plotly_dark",
                opacity=0.65,
                size_max=30,
                render_mode="webgl",
            )

            fig_satisfaccion.update_xaxes(title="Tiempo de Juego Registrado (horas)")

            fig_satisfaccion.update_layout(
                height=560,
                paper_bgcolor="#171d25",
                plot_bgcolor="#171d25",
            )

            st.plotly_chart(fig_satisfaccion, width="stretch")

            # ====================================================
            # 14. INFORMACIÓN SOBRE VALORES EXTREMOS
            # ====================================================

            st.caption(
                f"El análisis de correlación considera únicamente "
                f"los {juegos_con_tiempo:,} videojuegos con tiempo "
                f"de juego registrado ({porcentaje_con_tiempo:.1f}% "
                f"del total). El percentil 99 corresponde a "
                f"{percentil_99:,.1f} horas. Los "
                f"{juegos_valores_extremos:,} videojuegos que "
                f"superan este valor ({porcentaje_valores_extremos:.1f}% "
                f"de los juegos con tiempo registrado) se excluyen "
                f"únicamente de la visualización."
            )

            # ====================================================
            # 15. COBERTURA DEL TIEMPO
            # ====================================================

            st.caption(
                f"De los {total_juegos_satisfaccion:,} videojuegos "
                f"analizados, {juegos_con_tiempo:,} "
                f"({porcentaje_con_tiempo:.1f}%) cuentan con tiempo "
                f"de juego registrado y {juegos_sin_tiempo:,} "
                f"({porcentaje_sin_tiempo:.1f}%) no presentan "
                f"tiempo registrado."
            )

            # ====================================================
            # 16. SEGUNDO GRÁFICO
            # NIVELES DE TIEMPO
            # ====================================================

            st.subheader(
                "¿Cómo se distribuyen los videojuegos "
                "según su nivel de tiempo de juego?"
            )

            st.write(
                "Los videojuegos con tiempo registrado se agrupan "
                "en diferentes niveles para identificar dónde se "
                "concentra la mayor cantidad de títulos y comparar "
                "su aprobación promedio."
            )

            # ====================================================
            # 17. CREAR NIVELES DE TIEMPO
            # ====================================================

            df_niveles_tiempo = df_satisfaccion.loc[
                df_satisfaccion["playtime_hours"] > 0
            ].copy()

            df_niveles_tiempo["nivel_tiempo"] = pd.cut(
                df_niveles_tiempo["playtime_hours"],
                bins=[0, 1, 5, 20, 50, 100, float("inf")],
                labels=[
                    "Muy bajo (0-1 h)",
                    "Bajo (1-5 h)",
                    "Medio (5-20 h)",
                    "Alto (20-50 h)",
                    "Muy alto (50-100 h)",
                    "Extremo (100+ h)",
                ],
                include_lowest=True,
            )

            # ====================================================
            # 18. AGRUPAR NIVELES
            # ====================================================

            niveles_agg = (
                df_niveles_tiempo.groupby("nivel_tiempo", observed=True)
                .agg(
                    Videojuegos=("name", "count"),
                    Aprobacion_Promedio=("approval_rate", "mean"),
                    Tiempo_Promedio=("playtime_hours", "mean"),
                )
                .reset_index()
            )

            niveles_agg["Porcentaje"] = (
                niveles_agg["Videojuegos"] / juegos_con_tiempo * 100
            )

            niveles_agg["Etiqueta"] = niveles_agg.apply(
                lambda row: (
                    f"{int(row['Videojuegos']):,} ({row['Porcentaje']:.1f}%)"
                    if pd.notna(row["Videojuegos"]) and pd.notna(row["Porcentaje"])
                    else "0 (0.0%)"
                ),
                axis=1,
            )

            # ====================================================
            # 19. GRÁFICO DE NIVELES
            # ====================================================

            fig_niveles = px.bar(
                niveles_agg,
                x="nivel_tiempo",
                y="Videojuegos",
                color="Aprobacion_Promedio",
                color_continuous_scale="Viridis",
                text="Etiqueta",
                hover_data={
                    "Videojuegos": ":,",
                    "Porcentaje": ":.1f",
                    "Aprobacion_Promedio": ":.1f",
                    "Tiempo_Promedio": ":.1f",
                },
                title=("Distribución de Videojuegos por " "Nivel de Tiempo de Juego"),
                labels={
                    "nivel_tiempo": ("Nivel de Tiempo Registrado"),
                    "Videojuegos": ("Cantidad de Videojuegos"),
                    "Aprobacion_Promedio": ("Aprobación Promedio (%)"),
                    "Porcentaje": "Porcentaje (%)",
                    "Tiempo_Promedio": ("Tiempo Promedio (horas)"),
                },
                template="plotly_dark",
            )

            fig_niveles.update_traces(textposition="outside", cliponaxis=False)

            fig_niveles.update_layout(
                height=520,
                paper_bgcolor="#171d25",
                plot_bgcolor="#171d25",
                coloraxis_colorbar=dict(title="Aprobación (%)"),
            )

            st.plotly_chart(fig_niveles, width="stretch")

            # ====================================================
            # 20. TABLA RESUMEN
            # ====================================================

            st.subheader("Resumen por nivel de tiempo de juego")

            df_niveles_tabla = niveles_agg.copy()

            df_niveles_tabla["Aprobación Promedio"] = df_niveles_tabla[
                "Aprobacion_Promedio"
            ].map(lambda x: f"{x:.1f}%")

            df_niveles_tabla["Tiempo Promedio"] = df_niveles_tabla[
                "Tiempo_Promedio"
            ].map(lambda x: f"{x:.1f} h")

            df_niveles_tabla["Porcentaje"] = df_niveles_tabla["Porcentaje"].map(
                lambda x: f"{x:.1f}%"
            )

            df_niveles_tabla = df_niveles_tabla.rename(
                columns={"nivel_tiempo": "Nivel de Tiempo"}
            )[
                [
                    "Nivel de Tiempo",
                    "Videojuegos",
                    "Porcentaje",
                    "Aprobación Promedio",
                    "Tiempo Promedio",
                ]
            ]

            st.dataframe(df_niveles_tabla, width="stretch", hide_index=True)

            # ====================================================
            # 21. HALLAZGO
            # ====================================================

            nivel_mayor = niveles_agg.loc[niveles_agg["Videojuegos"].idxmax()]

            nivel_mayor_aprobacion = niveles_agg.loc[
                niveles_agg["Aprobacion_Promedio"].idxmax()
            ]

            st.info(
                f"**Hallazgo:** el nivel **"
                f"{nivel_mayor['nivel_tiempo']}** concentra "
                f"la mayor cantidad de videojuegos, con "
                f"({nivel_mayor['Porcentaje']:.1f}%)**. "
                f"El nivel con mayor aprobación promedio es "
                f"**{nivel_mayor_aprobacion['nivel_tiempo']}**, "
                f"con **"
                f"{nivel_mayor_aprobacion['Aprobacion_Promedio']:.1f}%**."
            )

            # ====================================================
            # 22. INTERPRETACIÓN DE PEARSON
            # ====================================================

            if correlacion_pearson >= 0.5:

                interpretacion_pearson = (
                    "Se observa una relación positiva "
                    "moderada/fuerte: los videojuegos con mayor "
                    "tiempo de juego tienden a presentar mayor "
                    "aprobación."
                )

            elif correlacion_pearson >= 0.2:

                interpretacion_pearson = (
                    "Se observa una relación positiva "
                    "débil/moderada: el tiempo de juego presenta "
                    "cierta asociación con la aprobación, aunque "
                    "no la explica por sí solo."
                )

            elif correlacion_pearson <= -0.5:

                interpretacion_pearson = (
                    "Se observa una relación negativa "
                    "moderada/fuerte: un mayor tiempo de juego "
                    "tiende a asociarse con menor aprobación."
                )

            elif correlacion_pearson <= -0.2:

                interpretacion_pearson = (
                    "Se observa una relación negativa "
                    "débil/moderada entre tiempo de juego "
                    "y aprobación."
                )

            else:

                interpretacion_pearson = (
                    "La relación lineal es débil: el tiempo "
                    "de juego no presenta una asociación "
                    "importante con la aprobación de la comunidad."
                )

            st.info(f"**Hallazgo según Pearson:** {interpretacion_pearson}")

        else:

            st.warning(
                "No hay suficientes videojuegos con tiempo "
                "de juego registrado para realizar el análisis."
            )

    else:

        st.warning(
            "No hay suficientes datos válidos para comparar "
            "satisfacción y tiempo de juego."
        )
