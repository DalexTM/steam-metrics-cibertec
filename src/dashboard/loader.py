# type: ignore

import os
import pandas as pd
import streamlit as st


@st.cache_data
def cargar_datos_gold() -> pd.DataFrame | None:
    ruta_gold = os.path.join("data", "gold", "steam_metrics_gold.parquet")
    if not os.path.exists(ruta_gold):
        return None
    return pd.read_parquet(ruta_gold)
