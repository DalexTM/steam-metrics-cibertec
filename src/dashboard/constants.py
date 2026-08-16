# type: ignore

import streamlit as st

PALETA_PRECIOS = {
    "Gratis ($0)": "#00ff88",
    "Económico ($0.01 - $9.99)": "#00d2ff",
    "Estándar ($10.00 - $29.99)": "#ffc107",
    "Premium ($30.00+)": "#ff3366",
}

PALETA_DISCREPANCIA = {
    "Infravalorado por la Crítica": "#00ff88",
    "Consenso Crítica vs Comunidad": "#00d2ff",
    "Sobrevalorado por la Crítica": "#ff3366",
}

PALETA_NEON_DISCRETA = [
    "#00ff88",
    "#00d2ff",
    "#ffc107",
    "#ff3366",
    "#b537f2",
    "#00e5ff",
    "#ff9100",
    "#76ff03",
    "#ff1744",
    "#e040fb",
]


def aplicar_estilos():
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #0e141d;
            color: #c6d4df;
        }
        [data-testid="stSidebar"] {
            background-color: #171d25;
            border-right: 1px solid #2a3545;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.8rem;
            font-weight: 700;
            color: #66c0f4;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 0.9rem;
            color: #a3b9cc;
            font-weight: 600;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #171d25;
            padding: 6px;
            border-radius: 8px;
            border: 1px solid #2a3545;
        }
        .stTabs [data-baseweb="tab"] {
            color: #a3b9cc;
            font-weight: 600;
            border-radius: 6px;
            padding: 8px 16px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #2a475e !important;
            color: #ffffff !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header():
    st.markdown(
        """
        <div style="display: flex; align-items: center; justify-content: space-between; background: linear-gradient(90deg, #1b2838 0%, #2a475e 50%, #0f1c29 100%); padding: 18px 24px; border-radius: 12px; margin-bottom: 20px; border-left: 6px solid #66c0f4; border-right: 6px solid #66cc33;">
            <div>
                <h1 style="color: #ffffff; margin: 0; font-size: 1.8rem; font-weight: 800; letter-spacing: 0.5px;">
                    <span style="color: #66c0f4;">Steam</span> &amp; <span style="color: #66cc33;">Metacritic</span> Analytics
                </h1>
                <p style="color: #c6d4df; margin: 4px 0 0 0; font-size: 0.95rem;">
                    Plataforma de Inteligencia Comercial y Desempeño de Videojuegos · CIBERTEC
                </p>
            </div>
            <div style="display: flex; gap: 10px;">
                <span style="background: rgba(102, 192, 244, 0.15); color: #66c0f4; border: 1px solid #66c0f4; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 700;">STEAM API</span>
                <span style="background: rgba(102, 204, 51, 0.15); color: #66cc33; border: 1px solid #66cc33; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 700;">METACRITIC KAGGLE</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
