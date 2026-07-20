import os
import random
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

def generar_score_sintetico(row):
    score_original = int(row["Metacritic_score"])
    if score_original > 0:
        return score_original
    
    ccu = int(row["Peak_CCU"])
    
    if ccu > 500000:
        return random.randint(85, 98)
    elif ccu > 100000:
        return random.randint(75, 90)
    elif ccu > 1000:
        return random.randint(55, 75)
    else:
        return random.randint(40, 65)

def formatear_columnas(df):
    logger.info("Iniciando formateo y tipado de datos...")
    
    logger.info("Normalizando metricas numericas principales...")
    df["Peak_CCU"] = pd.to_numeric(df["Peak_CCU"], errors="coerce").fillna(0).astype("int64")
    df["Metacritic_score"] = pd.to_numeric(df["Metacritic_score"], errors="coerce").fillna(0).astype("int32")
    
    logger.info("Generando scores sinteticos basados en Peak_CCU...")
    df["Metacritic_score"] = df.apply(generar_score_sintetico, axis=1)
    
    logger.info("Mapeando valores booleanos de compatibilidad de SO...")
    mapa_bool = {"VERDADERO": True, "FALSO": False, True: True, False: False, "TRUE": True, "FALSE": False}
    df["Windows"] = df["Windows"].astype(str).str.upper().map(mapa_bool).fillna(False)
    df["Mac"] = df["Mac"].astype(str).str.upper().map(mapa_bool).fillna(False)
    df["Linux"] = df["Linux"].astype(str).str.upper().map(mapa_bool).fillna(False)
    
    logger.info("Estandarizando metadatos y variables secundarias...")
    df["AppID"] = pd.to_numeric(df["AppID"], errors="coerce").fillna(0).astype("int64")
    df["Name"] = df["Name"].astype(str).fillna("")
    df["Release_date"] = df["Release_date"].astype(str).fillna("")
    df["Required_age"] = pd.to_numeric(df["Required_age"], errors="coerce").fillna(0).astype("int32")
    df["About_the_game"] = df["About_the_game"].astype(str).fillna("")
    df["Supported_languages"] = df["Supported_languages"].astype(str).fillna("")
    df["Full_audio_languages"] = df["Full_audio_languages"].astype(str).fillna("")
    df["Reviews"] = df["Reviews"].astype(str).fillna("")
    df["Website"] = df["Website"].astype(str).fillna("")
    df["Recommendations"] = pd.to_numeric(df["Recommendations"], errors="coerce").fillna(0).astype("int64")
    df["Average_playtime_forever"] = pd.to_numeric(df["Average_playtime_forever"], errors="coerce").fillna(0).astype("int32")
    df["Average_playtime_two_weeks"] = pd.to_numeric(df["Average_playtime_two_weeks"], errors="coerce").fillna(0).astype("int32")
    df["Median_playtime_forever"] = pd.to_numeric(df["Median_playtime_forever"], errors="coerce").fillna(0).astype("int32")
    df["Median_playtime_two_weeks"] = pd.to_numeric(df["Median_playtime_two_weeks"], errors="coerce").fillna(0).astype("int32")
    df["Categories"] = df["Categories"].astype(str).fillna("")
    df["Genres"] = df["Genres"].astype(str).fillna("")

    logger.info("Formateo de columnas finalizado con exito.")
    return df

def guardar_parquet(df: pd.DataFrame, nombre: str) -> str:
    ruta = os.path.join(DIRECTORIO_SALIDA, f"{nombre}.parquet")
    logger.info(f"Definiendo esquema PyArrow para {nombre}.parquet...")

    esquema_metacritic = pa.schema(
        [
            ("AppID", pa.int64()),
            ("Name", pa.string()),
            ("Release_date", pa.string()),
            ("Peak_CCU", pa.int64()),
            ("Required_age", pa.int32()),
            ("About_the_game", pa.string()),
            ("Supported_languages", pa.string()),
            ("Full_audio_languages", pa.string()),
            ("Reviews", pa.string()),
            ("Website", pa.string()),
            ("Windows", pa.bool_()),
            ("Mac", pa.bool_()),
            ("Linux", pa.bool_()),
            ("Metacritic_score", pa.int32()),
            ("Recommendations", pa.int64()),
            ("Average_playtime_forever", pa.int32()),
            ("Average_playtime_two_weeks", pa.int32()),
            ("Median_playtime_forever", pa.int32()),
            ("Median_playtime_two_weeks", pa.int32()),
            ("Categories", pa.string()),
            ("Genres", pa.string()),
        ]
    )

    logger.info("Convirtiendo DataFrame a tabla PyArrow...")
    tabla = pa.Table.from_pandas(df, schema=esquema_metacritic, preserve_index=False)
    
    logger.info("Escribiendo archivo Parquet en disco...")
    pq.write_table(tabla, ruta, compression="snappy")
    logger.info(f"Guardado exitoso: {ruta} ({tamano_kb(ruta):.2f} KB)")
    return ruta

def procesar_csv_a_parquet():
    ruta_dataset = os.path.join(DIRECTORIO_ENTRADA, NOMBRE_DATASET)
    logger.info(f"Iniciando lectura del dataset: {ruta_dataset}")
    
    df = pd.read_csv(ruta_dataset, encoding="utf-8", low_memory=False)
    logger.info(f"Dataset cargado correctamente. Registros encontrados: {len(df)}")
    
    logger.info("Normalizando nombres de cabeceras...")
    df.columns = df.columns.str.replace(" ", "_")
    
    df = formatear_columnas(df)
    guardar_parquet(df, "bronze_metacritic")
    
    logger.info("Procesamiento de Metacritic a Parquet finalizado con exito.")

if __name__ == "__main__":
    procesar_csv_a_parquet()