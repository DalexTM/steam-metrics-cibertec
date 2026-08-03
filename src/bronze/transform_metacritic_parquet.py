import os
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import logging

carpeta_logs = "logs"
ruta_log = os.path.join(carpeta_logs, "transform_metacritic_parquet.log")

logger = logging.getLogger("transform_metacritic_parquet")
logger.setLevel(logging.INFO)
if not logger.handlers:
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh = logging.FileHandler(ruta_log, encoding="utf-8")
    fh.setFormatter(formatter)
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(sh)

DIRECTORIO_ENTRADA = os.path.join("data", "raw", "metacritic")
DIRECTORIO_SALIDA = os.path.join("data", "bronze")
NOMBRE_DATASET = "metacritic.csv"

def tamano_kb(ruta: str) -> float:
    return os.path.getsize(ruta) / 1024

def formatear_columnas(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Iniciando formateo de columnas a string...")
    for col in df.columns:
        df[col] = df[col].fillna("").astype(str)

    logger.info("Formateo de columnas a string finalizado con exito.")
    return df

def guardar_parquet(df: pd.DataFrame, nombre: str) -> str:
    ruta = os.path.join(DIRECTORIO_SALIDA, f"{nombre}.parquet")
    logger.info(f"Definiendo esquema PyArrow para {nombre}.parquet...")

    esquema_metacritic = pa.schema(
        [
            ("AppID", pa.string()),
            ("Name", pa.string()),
            ("Release_date", pa.string()),
            ("Peak_CCU", pa.string()),
            ("Required_age", pa.string()),
            ("About_the_game", pa.string()),
            ("Supported_languages", pa.string()),
            ("Full_audio_languages", pa.string()),
            ("Reviews", pa.string()),
            ("Website", pa.string()),
            ("Windows", pa.string()),
            ("Mac", pa.string()),
            ("Linux", pa.string()),
            ("Metacritic_score", pa.string()),
            ("Recommendations", pa.string()),
            ("Average_playtime_forever", pa.string()),
            ("Average_playtime_two_weeks", pa.string()),
            ("Median_playtime_forever", pa.string()),
            ("Median_playtime_two_weeks", pa.string()),
            ("Categories", pa.string()),
            ("Genres", pa.string()),
        ]
    )

    logger.info("Convirtiendo DataFrame a tabla PyArrow...")
    tabla = pa.Table.from_pandas(df, schema=esquema_metacritic, preserve_index=False)

    logger.info("Escribiendo archivo Parquet en disco...")
    os.makedirs(DIRECTORIO_SALIDA, exist_ok=True)
    pq.write_table(tabla, ruta, compression="snappy")
    logger.info(f"Guardado exitoso: {ruta} ({tamano_kb(ruta):.2f} KB)")
    return ruta

def procesar_csv_a_parquet():
    ruta_dataset = os.path.join(DIRECTORIO_ENTRADA, NOMBRE_DATASET)
    logger.info(f"Iniciando lectura del dataset: {ruta_dataset}")

    df = pd.read_csv(ruta_dataset, encoding="utf-8", low_memory=False, dtype=str)
    logger.info(f"Dataset cargado correctamente. Registros encontrados: {len(df)}")

    logger.info("Normalizando nombres de cabeceras...")
    df.columns = df.columns.str.replace(" ", "_")

    df = formatear_columnas(df)
    guardar_parquet(df, "bronze_metacritic")

    logger.info("Procesamiento de Metacritic a Parquet finalizado con exito.")

if __name__ == "__main__":
    procesar_csv_a_parquet()