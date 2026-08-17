# type: ignore

import pandas as pd
import streamlit as st


def render_kpis(df_filtrado: pd.DataFrame) -> None:
    st.subheader("Indicadores Clave (KPIs)")
    col1, col2, col3, col4 = st.columns(4)

    total_juegos = len(df_filtrado)
    metacritic_promedio = (
        df_filtrado["Metacritic_score"].mean() if total_juegos > 0 else 0.0
    )
    if pd.isna(metacritic_promedio):
        metacritic_promedio = 0.0

    aprobacion_promedio = (
        df_filtrado["approval_rate"].mean() if total_juegos > 0 else 0.0
    )
    if pd.isna(aprobacion_promedio):
        aprobacion_promedio = 0.0

    ingresos_totales_millones = (
        (df_filtrado["estimated_revenue_usd"].sum() / 1_000_000)
        if total_juegos > 0
        else 0.0
    )
    if pd.isna(ingresos_totales_millones):
        ingresos_totales_millones = 0.0

    col1.metric("🎮 Videojuegos Analizados", f"{total_juegos:,}")
    col2.metric("⭐ Metacritic Promedio", f"{metacritic_promedio:.1f}")
    col3.metric("👍 Aprobación Comunidad", f"{aprobacion_promedio:.1f}%")
    col4.metric("💰 Ingresos Estimados", f"${ingresos_totales_millones:,.2f} M")
