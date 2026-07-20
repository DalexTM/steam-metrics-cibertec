import json
import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import logging

carpeta_logs = "logs"
ruta_log = os.path.join(carpeta_logs, "transform_steamspy_parquet.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(ruta_log, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

DIRECTORIO_ENTRADA = os.path.join("data", "raw", "steamspy")
DIRECTORIO_SALIDA = os.path.join("data", "bronze")

def tamanio_kb(ruta: str) -> float:
    return os.path.getsize(ruta) / 1024

def formatear_columnas(df):
    logging.info("Iniciando formateo y tipado de datos...")

    logging.info("Normalizando identificadores y texto...")
    df["appid"] = pd.to_numeric(df["appid"], errors="coerce").fillna(0).astype("int64")
    df["name"] = df["name"].astype(str)
    df["developer"] = df["developer"].astype(str)
    df["publisher"] = df["publisher"].astype(str)
    df["score_rank"] = df["score_rank"].astype(str)
    df["owners"] = df["owners"].astype(str)

    logging.info("Estandarizando metricas de votos y puntuaciones...")
    df["positive"] = pd.to_numeric(df["positive"], errors="coerce").fillna(0).astype("int32")
    df["negative"] = pd.to_numeric(df["negative"], errors="coerce").fillna(0).astype("int32")
    df["userscore"] = pd.to_numeric(df["userscore"], errors="coerce").fillna(0).astype("int32")

    logging.info("Formateando tiempos de juego y usuarios concurrentes...")
    df["average_forever"] = pd.to_numeric(df["average_forever"], errors="coerce").fillna(0).astype("int32")
    df["average_2weeks"] = pd.to_numeric(df["average_2weeks"], errors="coerce").fillna(0).astype("int32")
    df["median_forever"] = pd.to_numeric(df["median_forever"], errors="coerce").fillna(0).astype("int32")
    df["median_2weeks"] = pd.to_numeric(df["median_2weeks"], errors="coerce").fillna(0).astype("int32")
    df["ccu"] = pd.to_numeric(df["ccu"], errors="coerce").fillna(0).astype("int32")

    logging.info("Ajustando precios y descuentos...")
    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0.0).astype("float32")
    df["initialprice"] = pd.to_numeric(df["initialprice"], errors="coerce").fillna(0.0).astype("float32")
    df["discount"] = pd.to_numeric(df["discount"], errors="coerce").fillna(0).astype("int32")

    logging.info("Formateo de columnas finalizado con exito.")
    return df

def guardar_parquet(df: pd.DataFrame, nombre: str) -> str:
    ruta = os.path.join(DIRECTORIO_SALIDA, f"{nombre}.parquet")

    logging.info(f"Definiendo esquema PyArrow para {nombre}.parquet...")
    esquema_steamspy = pa.schema(
        [
            ("appid", pa.int64()),
            ("name", pa.string()),
            ("developer", pa.string()),
            ("publisher", pa.string()),
            ("score_rank", pa.string()),
            ("positive", pa.int32()),
            ("negative", pa.int32()),
            ("userscore", pa.int32()),
            ("owners", pa.string()),
            ("average_forever", pa.int32()),
            ("average_2weeks", pa.int32()),
            ("median_forever", pa.int32()),
            ("median_2weeks", pa.int32()),
            ("price", pa.float32()),
            ("initialprice", pa.float32()),
            ("discount", pa.int32()),
            ("ccu", pa.int32()),
        ]
    )

    df = formatear_columnas(df)

    logging.info("Convirtiendo DataFrame consolidado a tabla PyArrow...")
    tabla = pa.Table.from_pandas(df, schema=esquema_steamspy, preserve_index=False)
    
    logging.info("Escribiendo archivo Parquet en disco...")
    pq.write_table(tabla, ruta, compression="snappy")
    logging.info(f"Guardado exitoso: {ruta} ({tamanio_kb(ruta):.2f} KB)")
    return ruta

def procesar_json_a_parquet():
    
    logging.info(f"Buscando archivos JSON en la ruta: {DIRECTORIO_ENTRADA}")
    archivos = sorted(
        [f for f in os.listdir(DIRECTORIO_ENTRADA) if f.endswith(".json")],
        key=lambda x: int(x.replace("page_", "").replace(".json", ""))
    )

    if not archivos:
        logging.warning("No se encontraron archivos JSON para procesar.")
        return

    logging.info(f"Se encontraron {len(archivos)} archivos JSON. Iniciando lectura y unificacion...")
    dataframes_acumulados = []

    for archivo in archivos:
        ruta_archivo = os.path.join(DIRECTORIO_ENTRADA, archivo)
        try:
            logging.info(f"Procesando archivo: {archivo}")
            with open(ruta_archivo, "r", encoding="utf-8") as f:
                contenido_json = json.load(f)

            df_pagina = pd.DataFrame(contenido_json).T
            df_pagina = df_pagina.reset_index(drop=True)

            dataframes_acumulados.append(df_pagina)
        except Exception as e:
            logging.error(f"Error al procesar el archivo {archivo}: {e}")
            continue

    if dataframes_acumulados:
        logging.info("Concatenando estructuras JSON en un solo DataFrame...")
        df_steamspy_total = pd.concat(dataframes_acumulados, ignore_index=True)
        logging.info(f"Consolidacion completa. Registros totales: {len(df_steamspy_total)}")
        guardar_parquet(df_steamspy_total, "bronze_steamspy")
        logging.info("Procesamiento de SteamSpy a Parquet finalizado con exito.")
    else:
        logging.warning("No se pudo estructurar ninguna informacion.")

if __name__ == "__main__":
    procesar_json_a_parquet()