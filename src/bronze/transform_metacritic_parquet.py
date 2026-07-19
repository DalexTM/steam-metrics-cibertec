import os
import random
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import logging

carpeta_logs = "logs"
ruta_log = os.path.join(carpeta_logs, "transform_metacritic_parquet.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(ruta_log, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

DIRECTORIO_ENTRADA = os.path.join("data", "raw", "metacritic")
DIRECTORIO_SALIDA = os.path.join("data", "bronze")
NOMBRE_EXCEL = "metacritic.xlsx"

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

def guardar_parquet(df: pd.DataFrame, nombre: str) -> str:
    ruta = os.path.join(DIRECTORIO_SALIDA, f"{nombre}.parquet")

    esquema_kaggle = pa.schema(
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

    tabla = pa.Table.from_pandas(df, schema=esquema_kaggle, preserve_index=False)
    pq.write_table(tabla, ruta, compression="snappy")
    logging.info(f"Guardado: {ruta} ({tamano_kb(ruta):.2f} KB)")
    return ruta

def procesar_a_parquet():
    ruta_excel = os.path.join(DIRECTORIO_ENTRADA, NOMBRE_EXCEL)
    logging.info(f"Leyendo dataset de Excel: {ruta_excel}...")
    
    df = pd.read_excel(ruta_excel)
    df.columns = df.columns.str.replace(" ", "_")

    df["Peak_CCU"] = pd.to_numeric(df["Peak_CCU"], errors="coerce").fillna(0).astype("int64")
    df["Metacritic_score"] = pd.to_numeric(df["Metacritic_score"], errors="coerce").fillna(0).astype("int32")

    logging.info("Generando puntuaciones sinteticas de Metacritic basadas en el Peak CCU...")
    df["Metacritic_score"] = df.apply(generar_score_sintetico, axis=1)

    mapa_bool = {"VERDADERO": True, "FALSO": False, True: True, False: False, "TRUE": True, "FALSE": False}
    df["Windows"] = df["Windows"].astype(str).str.upper().map(mapa_bool).fillna(False)
    df["Mac"] = df["Mac"].astype(str).str.upper().map(mapa_bool).fillna(False)
    df["Linux"] = df["Linux"].astype(str).str.upper().map(mapa_bool).fillna(False)

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

    guardar_parquet(df, "bronze_metacritic")

if __name__ == "__main__":
    procesar_a_parquet()