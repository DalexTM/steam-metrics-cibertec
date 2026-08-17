import gc
import streamlit as st

from src.dashboard.constants import aplicar_estilos, render_header
from src.dashboard.loader import cargar_datos_gold
from src.dashboard.components.sidebar import render_sidebar
from src.dashboard.components.kpi_cards import render_kpis
from src.dashboard.views import (
    tab1_critica_ventas,
    tab2_discrepancia,
    tab3_generos_rentables,
    tab4_satisfaccion_tiempo,
    tab5_estrategia_precios,
    tab6_generos_ccu,
    tab7_explorador_datos,
    tab8_correlaciones,
)

st.set_page_config(
    page_title="Steam & Metacritic Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    aplicar_estilos()
    render_header()

    df = cargar_datos_gold()

    if df is None:
        st.error(
            "No se encontró el archivo de la Capa Gold (data/gold/steam_metrics_gold.parquet). "
            "Por favor ejecute la consolidación previamente."
        )
        return

    df_filtrado = render_sidebar(df)
    render_kpis(df_filtrado)

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(
        [
            "1. Crítica vs Éxito Comercial",
            "2. Discrepancia Crítica vs Comunidad",
            "3. Géneros más Rentables",
            "4. Satisfacción vs Tiempo de Juego",
            "5. Estrategia de precios",
            "6. Géneros vs Peak CCU",
            "7. Explorador de Datos",
            "8. Correlaciones",
        ]
    )

    with tab1:
        tab1_critica_ventas.render(df_filtrado)

    with tab2:
        tab2_discrepancia.render(df_filtrado)

    with tab3:
        tab3_generos_rentables.render(df_filtrado)

    with tab4:
        tab4_satisfaccion_tiempo.render(df_filtrado)

    with tab5:
        tab5_estrategia_precios.render(df_filtrado)

    with tab6:
        tab6_generos_ccu.render(df_filtrado)

    with tab7:
        tab7_explorador_datos.render(df_filtrado)

    with tab8:
        tab8_correlaciones.render(df_filtrado)

    gc.collect()


if __name__ == "__main__":
    main()
