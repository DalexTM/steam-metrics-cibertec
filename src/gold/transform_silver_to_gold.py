import os
import logging
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

carpeta_logs = "logs"
ruta_log = os.path.join(carpeta_logs, "transform_silver_to_gold.log")

logger = logging.getLogger("transform_silver_to_gold")
logger.setLevel(logging.INFO)
if not logger.handlers:
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh = logging.FileHandler(ruta_log, encoding="utf-8")
    fh.setFormatter(formatter)
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(sh)

DIRECTORIO_ENTRADA = os.path.join("data", "silver")
DIRECTORIO_SALIDA = os.path.join("data", "gold")
ARCHIVO_ENTRADA = os.path.join(DIRECTORIO_ENTRADA, "silver.parquet")
ARCHIVO_SALIDA = os.path.join(DIRECTORIO_SALIDA, "steam_metrics_gold.parquet")


def calcular_duenos_promedio(owners_str: str) -> float:
    if not isinstance(owners_str, str) or ".." not in owners_str:
        return 0.0
    partes = owners_str.split("..")
    if len(partes) != 2:
        return 0.0
    try:
        low = float(partes[0].replace(",", "").strip())
        high = float(partes[1].replace(",", "").strip())
        return (low + high) / 2.0
    except Exception:
        return 0.0


def categorizar_precio(precio: float) -> str:
    if precio == 0.0:
        return "Gratis ($0)"
    elif precio < 10.0:
        return "Económico ($0.01 - $9.99)"
    elif precio < 30.0:
        return "Estándar ($10.00 - $29.99)"
    else:
        return "Premium ($30.00+)"


def categorizar_discrepancia(gap: float) -> str:
    if gap > 15.0:
        return "Infravalorado por la Crítica"
    elif gap < -15.0:
        return "Sobrevalorado por la Crítica"
    else:
        return "Consenso Crítica vs Comunidad"


def procesar_silver_a_gold():
    logger.info("========================================")
    logger.info("INICIANDO PIPELINE: SILVER -> GOLD")
    logger.info("========================================")

    logger.info(f"Cargando dataset Silver desde: {ARCHIVO_ENTRADA}")
    df = pd.read_parquet(ARCHIVO_ENTRADA)
    logger.info(f"Registros cargados: {len(df):,} filas y {len(df.columns)} columnas.")

    logger.info("Calculando estimaciones comerciales de ventas e ingresos...")
    df["estimated_owners_avg"] = df["owners"].apply(calcular_duenos_promedio)
    df["estimated_revenue_usd"] = (df["estimated_owners_avg"] * df["price_usd"]).round(
        2
    )

    logger.info("Asegurando consistencia en tasa de aprobación y discrepancia...")
    total_rev = df["positive"] + df["negative"]
    df["total_reviews"] = total_rev.astype(np.int32)
    df["approval_rate"] = np.where(
        total_rev > 0,
        (df["positive"] / total_rev) * 100.0,
        df["approval_rate"].fillna(0.0),
    ).round(2)

    df["Metacritic_score"] = df["Metacritic_score"].round(2)
    df["score_gap"] = (df["approval_rate"] - df["Metacritic_score"]).round(2)
    df["discrepancy_category"] = df["score_gap"].apply(categorizar_discrepancia)

    logger.info("Calculando horas promedio de juego y rangos...")
    df["playtime_hours"] = (df["Average_playtime_forever"] / 60.0).round(2)

    logger.info("Categorizando estrategia de precios...")
    df["is_free"] = df["price_usd"] == 0.0
    df["price_category"] = df["price_usd"].apply(categorizar_precio)

    logger.info("Normalizando géneros y categorías de juego...")
    df["Genres"] = df["Genres"].astype(str).str.strip()
    df["Categories"] = df["Categories"].astype(str).str.strip()

    logger.info("Escribiendo archivo Parquet en capa Gold...")

    tabla = pa.Table.from_pandas(df, preserve_index=False)
    pq.write_table(tabla, ARCHIVO_SALIDA, compression="snappy")

    tamano_mb = os.path.getsize(ARCHIVO_SALIDA) / (1024 * 1024)
    logger.info(f"Guardado exitoso: {ARCHIVO_SALIDA} ({tamano_mb:.2f} MB)")
    logger.info("========================================")
    logger.info("PIPELINE GOLD FINALIZADO CON ÉXITO")
    logger.info("========================================")
    return ARCHIVO_SALIDA


if __name__ == "__main__":
    procesar_silver_a_gold()
